import json
import logging

from django.db import models
from django.db.models import Q
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse


logger = logging.getLogger(__name__)


class Game(models.Model):
    STATUS_DRAFT, STATUS_PUBLISHED = 'd', 'p'
    STATUS_CHOICES = (
        (STATUS_DRAFT, _('draft')),
        (STATUS_PUBLISHED, _('published')),
    )

    created_at = models.DateTimeField(_("Date created"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Date updated"), auto_now=True)
    name = models.CharField(verbose_name=_('name'), max_length=250)
    description = models.TextField(verbose_name=_('description'), blank=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES,
                              default=STATUS_DRAFT)
    author = models.ForeignKey(to=settings.AUTH_USER_MODEL,
                               verbose_name=_('author'),
                               related_name='created_games',
                               on_delete=models.CASCADE)

    class Meta:
        ordering = ['pk']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('game_detail', args=(self.pk, ))

    def can_create_new_character(self):
        if self.characters.count() == 0:
            return True

        return False

    def can_create_new_scene(self):
        return True

    def get_user_game(self, user):
        session, created = Session.objects.get_or_create(
            user=user,
            game=self,
            status=Session.STATUS_ACTIVE
        )

        if created:
            for character in self.characters.all():
                session_character = character.create_new(session)

                if not session.active_character:
                    session.active_character = session_character
                    session.save()

        return session


class Character(models.Model):
    created_at = models.DateTimeField(_("Date created"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Date updated"), auto_now=True)
    game = models.ForeignKey(to='Game', verbose_name=_('game'),
                             related_name='characters',
                             on_delete=models.CASCADE)
    name = models.CharField(verbose_name=_('name'), max_length=250)
    description = models.TextField(verbose_name=_('description'), blank=True)
    start_scene = models.ForeignKey(to='Scene', verbose_name=_('start scene'),
                                    related_name='scene_start_characters',
                                    null=True, blank=True,
                                    on_delete=models.SET_NULL)

    class Meta:
        ordering = ['game', 'pk']

    def __str__(self):
        return "%s (%s)" % (self.name, self.game)

    def get_absolute_url(self):
        return reverse('character_detail', args=(self.game.pk, self.pk, ))

    def create_new(self, session):
        if self.start_scene:
            start_scene = self.start_scene
        else:
            start_scene = session.game.scenes.first()

        session_character = SessionCharacter(
            character=self,
            session=session,
            current_scene=start_scene
        )
        session_character.save()
        return session_character


class Property(models.Model):
    created_at = models.DateTimeField(_("Date created"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Date updated"), auto_now=True)
    game = models.ForeignKey(to='Game', verbose_name=_('game'),
                             related_name='properties',
                             on_delete=models.CASCADE)
    character = models.ForeignKey(to='Character', verbose_name=_('character'),
                                  null=True, blank=True,
                                  related_name='properties',
                                  on_delete=models.CASCADE)
    scene = models.ForeignKey(to='Scene', verbose_name=_('scene'),
                              null=True, blank=True,
                              related_name='properties',
                              on_delete=models.CASCADE)

    name = models.CharField(verbose_name=_('name'), max_length=100)
    value = models.CharField(verbose_name=_('value'),
                             max_length=100, blank=True)

    class Meta:
        ordering = ['character', 'pk']

    def __str__(self):
        return "%s (%s)" % (self.name, self.type)

    def get_session_value(self, session_character):
        try:
            query = Q(character__isnull=True)
            query.add(Q(character=session_character.character), Q.OR)
            query.add(Q(property=self), Q.AND)
            query.add(Q(session=session_character.session), Q.AND)

            session_property = SessionProperty.objects.get(query)

            return session_property.value
        except SessionProperty.DoesNotExist:
            return self.value

    def set_value(self, value, session_character=None):
        session_data, created = SessionProperty.objects.get_or_create(
            property=self,
            Session=session_character.session,
            defaults={
                'current_value': value,
                'character': session_character
            }
        )
        if not created:
            session_data.current_value = value


class SessionCharacter(models.Model):
    created_at = models.DateTimeField(_("Date created"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Date updated"), auto_now=True)
    character = models.ForeignKey(to='Character', verbose_name=_('character'),
                                  related_name='in_games',
                                  on_delete=models.CASCADE)
    current_scene = models.ForeignKey(to='Scene',
                                      verbose_name=_('current scene'),
                                      related_name='scene_characters',
                                      on_delete=models.CASCADE)
    current_moment = models.ForeignKey(to='Moment',
                                       verbose_name=_('current moment'),
                                       related_name='moment_characters',
                                       on_delete=models.CASCADE)
    session = models.ForeignKey(to='Session', verbose_name=_('session'),
                                related_name='characters',
                                on_delete=models.CASCADE)

    class Meta:
        unique_together = (
            ("character", "session"),
        )

    def __str__(self):
        return "%s: %s" % (self.session, self.character)

    def get_scene_vision(self):
        result = []

        query = Q(moment__isnull=True)
        query.add(Q(moment=self.current_moment), Q.OR)
        query.add(Q(scene=self.current_scene), Q.AND)

        blocks = Block.objects.filter(query)
        for block in blocks:
            if block.check_condition(self):
                result.append(block.content)

        return "\n\n".join(result)

    def get_scene_actions(self):
        result = []

        query = Q(moment__isnull=True)
        query.add(Q(moment=self.current_moment), Q.OR)
        query.add(Q(scene=self.current_scene), Q.AND)

        actions = Action.objects.filter(query)
        for action in actions:
            if action.check_condition(self):
                result.append({'id': action.pk, 'content': action.content})

        return result

    def go_to_scene(self, scene):
        if isinstance(scene, Scene):
            self.current_scene = scene
            self.current_moment = scene.get_default_moment()
            self.save()
        else:
            logger.debug("Cant go_to_scene %s" % scene)

    def go_to_moment(self, moment):
        if isinstance(moment, Moment):
            self.current_moment = moment
            if moment.scene != self.current_scene:
                self.current_scene = moment.scene
            self.save()
        else:
            logger.debug("Cant go_to_moment %s" % moment)


class SessionProperty(models.Model):
    created_at = models.DateTimeField(_("Date created"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Date updated"), auto_now=True)
    session = models.ForeignKey(to='Session', verbose_name=_('session'),
                                related_name='properties',
                                on_delete=models.CASCADE)
    character = models.ForeignKey(to='SessionCharacter',
                                  verbose_name=_('character'),
                                  blank=True, null=True,
                                  related_name='properties',
                                  on_delete=models.CASCADE)
    property = models.ForeignKey(to='Property', verbose_name=_('property'),
                                 related_name='in_games',
                                 on_delete=models.CASCADE)
    current_value = models.CharField(verbose_name=_('current value'),
                                     max_length=100, blank=True)

    class Meta:
        unique_together = (
            ("session", "property"),
        )

    def __str__(self):
        return "%s: %s" % (self.character, self.property)


class Scene(models.Model):
    created_at = models.DateTimeField(_("Date created"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Date updated"), auto_now=True)
    game = models.ForeignKey(to='Game', verbose_name=_('game'),
                             related_name='scenes', on_delete=models.CASCADE)
    name = models.CharField(verbose_name=_('name'), max_length=250)
    order = models.SmallIntegerField(verbose_name=_('order'), default=100)
    description = models.TextField(verbose_name=_('description'), blank=True)

    class Meta:
        ordering = ['game', 'order', 'pk']

    def __str__(self):
        return "%s" % self.name

    def get_absolute_url(self):
        return reverse('scene_detail', args=(self.game.pk, self.pk, ))

    def get_default_moment(self):
        return self.moments.first()


class Moment(models.Model):
    created_at = models.DateTimeField(_("Date created"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Date updated"), auto_now=True)
    game = models.ForeignKey(to='Game', verbose_name=_('game'),
                             related_name='moments', on_delete=models.CASCADE)
    scene = models.ForeignKey(to='Scene', verbose_name=_('scene'),
                              related_name='moments', on_delete=models.CASCADE)
    name = models.CharField(verbose_name=_('name'), max_length=250)
    order = models.SmallIntegerField(verbose_name=_('order'), default=100)
    description = models.TextField(verbose_name=_('description'), blank=True)

    class Meta:
        ordering = ['scene', 'order', 'pk']

    def __str__(self):
        return "%s: %s" % (self.scene, self.name)

    def get_absolute_url(self):
        pass


class Block(models.Model):
    created_at = models.DateTimeField(_("Date created"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Date updated"), auto_now=True)
    game = models.ForeignKey(to='Game', verbose_name=_('game'),
                             related_name='blocks', on_delete=models.CASCADE)
    scene = models.ForeignKey(to='Scene', verbose_name=_('scene'),
                              related_name='blocks', null=True,
                              on_delete=models.SET_NULL)
    moment = models.ForeignKey(to='Moment', verbose_name=_('moment'),
                               related_name='blocks', blank=True, null=True,
                               on_delete=models.SET_NULL)
    order = models.SmallIntegerField(verbose_name=_('order'), default=100)
    content = models.TextField(verbose_name=_('content'))
    condition = models.TextField(verbose_name=_('condition'))

    class Meta:
        ordering = ['game', 'scene', 'order', 'pk']

    def __str__(self):
        return "%s: %s" % (self.moment, self.content[:50])

    def check_condition(self, session_character):
        condition_dict = json.loads(self.condition)
        for condition in condition_dict:
            property_pk, condition_type, condition_value = condition
            try:
                property = Property.objects.get(pk=property_pk)
                session_value = property.get_session_value(session_character)
            except Property.DoesNotExist:
                return False

            if condition_type == "==":
                if session_value == condition_value:
                    return True
            elif condition_type == ">=":
                if session_value >= condition_value:
                    return True
            elif condition_type == ">":
                if session_value > condition_value:
                    return True
            elif condition_type == "<=":
                if session_value <= condition_value:
                    return True
            elif condition_type == "<":
                if session_value < condition_value:
                    return True
            elif condition_type == "!=":
                if session_value != condition_value:
                    return True

        return False


class Action(models.Model):
    created_at = models.DateTimeField(_("Date created"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Date updated"), auto_now=True)
    game = models.ForeignKey(to=Game, verbose_name=_('game'),
                             related_name='actions', on_delete=models.CASCADE,
                             editable=False)
    scene = models.ForeignKey(to=Scene, verbose_name=_('scene'),
                              related_name='actions', null=True,
                              on_delete=models.SET_NULL)
    moment = models.ForeignKey(to='Moment', verbose_name=_('moment'),
                               related_name='actions', blank=True, null=True,
                               on_delete=models.SET_NULL)
    order = models.SmallIntegerField(verbose_name=_('order'), default=100)
    content = models.TextField(verbose_name=_('content'))
    condition = models.TextField(verbose_name=_('condition'))

    class Meta:
        ordering = ['game', 'scene', 'order', 'pk']

    def __str__(self):
        return "%s: %s" % (self.scene, self.content)

    def check_condition(self, session_character):
        condition_dict = json.loads(self.condition)
        for condition in condition_dict:
            property_pk, condition_type, condition_value = condition
            try:
                property = Property.objects.get(pk=property_pk)
                session_value = property.get_session_value(session_character)
            except Property.DoesNotExist:
                return False

            if condition_type == "==":
                if session_value == condition_value:
                    return True
            elif condition_type == ">=":
                if session_value >= condition_value:
                    return True
            elif condition_type == ">":
                if session_value > condition_value:
                    return True
            elif condition_type == "<=":
                if session_value <= condition_value:
                    return True
            elif condition_type == "<":
                if session_value < condition_value:
                    return True
            elif condition_type == "!=":
                if session_value != condition_value:
                    return True

        return False

    def fire_after_effects(self, session_character):
        if self.check_condition(session_character):
            logger.debug(
                "Fire action %s for character %s" %
                (self, session_character)
            )
            for af in self.after_effects.all():
                af.process(session_character)
        else:
            logger.debug(
                "Try to fire not visible action %s for character %s" %
                (self, session_character)
            )


class AfterEffect(models.Model):
    created_at = models.DateTimeField(_("Date created"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Date updated"), auto_now=True)
    action = models.ForeignKey(to=Action, related_name='after_effects',
                               on_delete=models.CASCADE)

    go_to_scene = models.ForeignKey(to=Scene, related_name='after_effects',
                                    on_delete=models.CASCADE, blank=True,
                                    null=True)
    go_to_moment = models.ForeignKey(to=Moment, related_name='after_effects',
                                     on_delete=models.CASCADE, blank=True,
                                     null=True)

    set_property = models.ForeignKey(to=Property,
                                     related_name='value_after_effects',
                                     on_delete=models.CASCADE,
                                     blank=True, null=True)
    set_property_value = models.TextField(
        verbose_name=_('after effect action value'), blank=True
    )

    class Meta:
        unique_together = (
            ("action", "go_to_scene"),
            ("action", "go_to_moment"),
            ("action", "set_property"),
        )

    def __str__(self):
        effects = []
        if self.go_to_scene:
            effects.append('go to scene %s' % self.go_to_scene)

        if self.hide_block:
            effects.append('hide block %s' % self.hide_block)
        if self.show_block:
            effects.append('show block %s' % self.show_block)

        if self.set_property:
            effects.append(
                'set property %s to %s' %
                (self.set_property, self.set_property_value)
            )

        return "%s: %s" % (self.action, ", ".join(effects))

    def process(self, session_character):
        if self.go_to_scene:
            session_character.go_to_scene(self.go_to_scene)
        if self.go_to_moment:
            session_character.go_to_moment(self.go_to_moment)

        if self.set_property:
            self.set_property.set_value(
                session_character,
                self.set_property_value
            )


# Игровая сессия конкретного юзера внутри квеста.
# может быть несколько, так как он может
# несколько раз играть в один и тот же квест
class Session(models.Model):
    STATUS_ACTIVE, STATUS_FINISHED = 'a', 'f'
    STATUS_CHOICES = (
        (STATUS_ACTIVE, _('active')),
        (STATUS_FINISHED, _('finished')),
    )

    created_at = models.DateTimeField(_("Date created"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Date updated"), auto_now=True)
    game = models.ForeignKey(to='Game', verbose_name=_('game'),
                             related_name='users_sessions',
                             on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    user = models.ForeignKey(to='telegrambot.User', verbose_name=_('user'),
                             related_name='games_sessions',
                             on_delete=models.CASCADE)

    active_character = models.ForeignKey(to='SessionCharacter',
                                         verbose_name=_('active character'),
                                         related_name='active_sessions',
                                         null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return "%s in %s" % (self.user, self.game)

    def get_game_data(self):
        logger.debug(
            "Get game data for session %s with active active_character %s" %
            (self, self.active_character)
        )
        return {
            'vision': self.active_character.get_scene_vision(),
            'actions': self.active_character.get_scene_actions(),
        }

    def fire_action(self, action_pk):
        logger.debug(
            "Fire some action for session %s with active active_character %s" %
            (self, self.active_character)
        )

        try:
            action = self.active_character.current_scene.actions.get(
                pk=action_pk
            )
            action.fire_after_effects(self.active_character)
            return action
        except Action.DoesNotExist:
            logger.debug(
                "Not found action with pk %s in scene %S" %
                (action_pk, self.active_character.current_scene)
            )

        return False

    def finish_game(self):
        self.status = self.STATUS_FINISHED
        self.save()


class Gamelog(models.Model):
    SOURCE_USER, SOURCE_GAME = 'u', 'g'
    SOURCE_CHOICES = (
        (SOURCE_USER, _('user')),
        (SOURCE_GAME, _('game')),
    )

    session = models.ForeignKey(to='Session', verbose_name=_('session'),
                                related_name='gamelogs',
                                on_delete=models.CASCADE)
    created_at = models.DateTimeField(_("Date created"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Date updated"), auto_now=True)
    source = models.CharField(max_length=1,
                              choices=SOURCE_CHOICES,
                              default=SOURCE_GAME)
    text = models.TextField(verbose_name=_('text'))

    class Meta:
        ordering = ['-created_at', ]
