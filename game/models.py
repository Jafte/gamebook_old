import logging
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


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
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    author = models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name=_('author'),
                               related_name='created_games', on_delete=models.CASCADE)

    class Meta:
        ordering = ['pk']

    def __str__(self):
        return self.name

    def start_new_game(self, user):
        Session.active.filter(user=user, game=self).update(status = Session.STATUS_FINISHED)

        session = Session(
            status=Session.STATUS_ACTIVE,
            user=user,
            game=self,
        )
        session.save()

        for character in self.characters.all():
            session_character = character.create_new(session)

            if not session.active_character:
                session.active_character = session_character
                session.save()

        return session


class Character(models.Model):
    created_at = models.DateTimeField(_("Date created"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Date updated"), auto_now=True)
    game = models.ForeignKey(to='Game', verbose_name=_('game'), related_name='characters', on_delete=models.CASCADE)
    name = models.CharField(verbose_name=_('name'), max_length=250)
    description = models.TextField(verbose_name=_('description'), blank=True)
    start_scene = models.ForeignKey(to='Scene', verbose_name=_('start scene'), related_name='scene_start_characters',
                                    null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['game', 'pk']

    def __str__(self):
        return "%s (%s)" % (self.name, self.game)

    def create_new(self, session):
        if self.start_scene:
            start_scene = self.start_scene
        else:
            start_scene = session.game.scenes.first()

        session_character = SessionCharacter(
            character = self,
            session = session,
            current_scene = start_scene
        )
        session_character.save()

        for property in self.properties.all():
            session_property = SessionCharacterProperty(
                character=session_character,
                property=property,
                current_value_s=property.value_s,
                current_value_n=property.value_n,
            )
            session_property.save()

        return session_character


class CharacterProperty(models.Model):
    TYPE_STRING, TYPE_NUMBER = 'S', 'N'
    TYPE_CHOICES = (
        (TYPE_STRING, _('String')),
        (TYPE_NUMBER, _('Number')),
    )
    created_at = models.DateTimeField(_("Date created"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Date updated"), auto_now=True)
    character = models.ForeignKey(to='Character', verbose_name=_('character'), null=True,
                                  related_name='properties', on_delete=models.CASCADE)
    type = models.CharField(max_length=1, choices=TYPE_CHOICES, default=TYPE_NUMBER)
    name = models.CharField(verbose_name=_('name'), max_length=100)
    value_s = models.CharField(verbose_name=_('value string'), max_length=100, blank=True)
    value_n = models.FloatField(verbose_name=_('value number'), blank=True)

    class Meta:
        ordering = ['character', 'pk']

    def __str__(self):
        return "%s (%s)" % (self.name, self.type)

    def get_session_data(self, session_character):
        obj, created = SessionCharacterProperty.objects.get_or_create(
            property=self,
            character=session_character
        )
        if created:
            obj.current_value_s = self.value_s
            obj.current_value_n = self.value_n
            obj.save()

        return obj

    def set_visible(self, session_character):
        logger.debug("Cant change visibility for CharacterProperty, fire by %s" % session_character)

    def set_invisible(self, session_character):
        logger.debug("Cant change visibility for CharacterProperty, fire by %s" % session_character)

    def set_value(self, session_character, value):
        session_data = self.get_session_data(session_character)
        if self.type == CharacterProperty.TYPE_STRING:
            session_data.current_value_s = "%s" % value
        elif self.type == CharacterProperty.TYPE_NUMBER:
            session_data.current_value_n = "%d" % value
        else:
            logger.debug("Not found CharacterProperty type %s" % self.type)

        session_data.save()


class SessionCharacter(models.Model):
    created_at = models.DateTimeField(_("Date created"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Date updated"), auto_now=True)
    character = models.ForeignKey(to='Character', verbose_name=_('character'),
                                  related_name='in_games', on_delete=models.CASCADE)
    current_scene = models.ForeignKey(to='Scene', verbose_name=_('current scene'),
                                      related_name='scene_characters', on_delete=models.CASCADE)
    session = models.ForeignKey(to='Session', verbose_name=_('session'), related_name='characters',
                                on_delete=models.CASCADE)

    class Meta:
        unique_together = (
            ("character", "session"),
        )

    def __str__(self):
        return "%s: %s" % (self.session, self.character)

    def get_scene_vision(self):
        result = []

        blocks = self.current_scene.blocks.all()
        for block in blocks:
            session_data = block.get_session_data(self)

            if session_data.current_is_visible:
                result.append(block.content)

        return "\n\n".join(result)

    def get_scene_actions(self):
        result = []

        actions = self.current_scene.actions.all()
        for action in actions:
            session_data = action.get_session_data(self)
            if session_data.current_is_visible:
                result.append({'id': action.pk, 'content': action.content})

        return result

    def go_to_scene(self, scene):
        if isinstance(scene, Scene):
            self.current_scene = scene
            self.save()
        else:
            logger.debug("Cant go_to_scene %s" % scene)


class SessionCharacterProperty(models.Model):
    created_at = models.DateTimeField(_("Date created"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Date updated"), auto_now=True)
    character = models.ForeignKey(to='SessionCharacter', verbose_name=_('character'),
                                  related_name='properties', on_delete=models.CASCADE)
    property = models.ForeignKey(to='CharacterProperty', verbose_name=_('property'),
                                 related_name='in_games', on_delete=models.CASCADE)
    current_value_s = models.CharField(verbose_name=_('current value string'), max_length=100, blank=True)
    current_value_n = models.FloatField(verbose_name=_('current value number'), blank=True)

    class Meta:
        unique_together = (
            ("character", "property"),
        )

    def __str__(self):
        return "%s: %s" % (self.character, self.property)


class Scene(models.Model):
    created_at = models.DateTimeField(_("Date created"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Date updated"), auto_now=True)
    game = models.ForeignKey(to='Game', verbose_name=_('game'), related_name='scenes', on_delete=models.CASCADE)
    name = models.CharField(verbose_name=_('name'), max_length=250)
    order = models.SmallIntegerField(verbose_name=_('order'), default=100)
    description = models.TextField(verbose_name=_('description'), blank=True)

    class Meta:
        ordering = ['game', 'order', 'pk']

    def __str__(self):
        return "%s" % self.name

    def set_visible(self, session_character):
        logger.debug("Cant change visibility for scene, fire by %s" % session_character)

    def set_invisible(self, session_character):
        logger.debug("Cant change visibility for scene, fire by %s" % session_character)

    def set_value(self, session_character, value):
        logger.debug("Cant change value for Scene, fire by %s" % session_character)


class Block(models.Model):
    created_at = models.DateTimeField(_("Date created"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Date updated"), auto_now=True)
    game = models.ForeignKey(to='Game', verbose_name=_('game'), related_name='blocks', on_delete=models.CASCADE)
    scene = models.ForeignKey(to='Scene', verbose_name=_('scene'), related_name='blocks', null=True,
                              on_delete=models.SET_NULL)
    order = models.SmallIntegerField(verbose_name=_('order'), default=100)
    content = models.TextField(verbose_name=_('content'))
    is_visible = models.BooleanField(verbose_name=_('is visible?'), default=True)

    class Meta:
        ordering = ['game', 'scene', 'order', 'pk']

    def __str__(self):
        return "%s: %s" % (self.scene, self.content[:50])

    def get_session_data(self, session_character):
        obj, created = SessionBlock.objects.get_or_create(
            block=self,
            character=session_character
        )
        if created:
            obj.current_is_visible = self.is_visible
            obj.save()

        return obj

    def set_visible(self, session_character):
        session_data = self.get_session_data(session_character)
        session_data.current_is_visible = True
        session_data.save()

    def set_invisible(self, session_character):
        session_data = self.get_session_data(session_character)
        session_data.current_is_visible = False
        session_data.save()

    def set_value(self, session_character, value):
        logger.debug("Cant change value for Block, fire by %s" % session_character)


class SessionBlock(models.Model):
    created_at = models.DateTimeField(_("Date created"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Date updated"), auto_now=True)
    block = models.ForeignKey(to='Block', verbose_name=_('block'), related_name='sessions_blocks',
                              on_delete=models.CASCADE)
    character = models.ForeignKey(to='SessionCharacter', verbose_name=_('character'),
                                  related_name='sessions_blocks', on_delete=models.CASCADE)
    current_is_visible = models.BooleanField(verbose_name=_('current is visible?'), default=True)

    class Meta:
        unique_together = (
            ("block", "character"),
        )


class Action(models.Model):
    created_at = models.DateTimeField(_("Date created"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Date updated"), auto_now=True)
    game = models.ForeignKey(to=Game, verbose_name=_('game'), related_name='actions', on_delete=models.CASCADE,
                             editable=False)
    scene = models.ForeignKey(to=Scene, verbose_name=_('scene'), related_name='actions', null=True,
                              on_delete=models.SET_NULL)
    order = models.SmallIntegerField(verbose_name=_('order'), default=100)
    content = models.TextField(verbose_name=_('content'))
    is_visible = models.BooleanField(verbose_name=_('is visible?'), default=True)

    class Meta:
        ordering = ['game', 'scene', 'order', 'pk']

    def __str__(self):
        return "%s: %s" % (self.scene, self.content)

    def save(self, *args, **kwargs):
        self.game = self.scene.game
        super(Action, self).save(*args, **kwargs)

    def get_session_data(self, session_character):
        obj, created = SessionAction.objects.get_or_create(
            action=self,
            character=session_character
        )
        if created:
            obj.current_is_visible = self.is_visible
            obj.save()

        return obj

    def set_visible(self, session_character):
        session_data = self.get_session_data(session_character)
        session_data.current_is_visible = True
        session_data.save()

    def set_invisible(self, session_character):
        session_data = self.get_session_data(session_character)
        session_data.current_is_visible = False
        session_data.save()

    def set_value(self, session_character, value):
        logger.debug("Cant change value for Action, fire by %s" % session_character)

    def check_vision(self, session_character):
        try:
            session_data = session_character.sessions_actions.get(action=self)
            return session_data.current_is_visible
        except SessionAction.DoesNotExist:
            return self.is_visible

        return False

    def fire_after_effects(self, session_character):
        if self.check_vision(session_character):
            logger.debug("Fire action %s for character %s" % (self, session_character))
            for af in self.after_effects.all():
                af.process(session_character)
        else:
            logger.debug("Try to fire not visible action %s for character %s" % (self, session_character))


class SessionAction(models.Model):
    created_at = models.DateTimeField(_("Date created"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Date updated"), auto_now=True)
    action = models.ForeignKey(to='Action', verbose_name=_('action'), related_name='sessions_actions',
                               on_delete=models.CASCADE)
    character = models.ForeignKey(to='SessionCharacter', verbose_name=_('character'),
                                  related_name='sessions_actions', on_delete=models.CASCADE)
    current_is_visible = models.BooleanField(verbose_name=_('current is visible?'), default=True)

    class Meta:
        unique_together = (
            ("action", "character"),
        )


class AfterEffect(models.Model):
    created_at = models.DateTimeField(_("Date created"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Date updated"), auto_now=True)
    action = models.ForeignKey(to=Action, related_name='after_effects', on_delete=models.CASCADE)

    go_to_scene = models.ForeignKey(to=Scene, related_name='after_effects', on_delete=models.CASCADE, blank=True,
                                    null=True)

    hide_block = models.ForeignKey(to=Block, related_name='hide_after_effects', on_delete=models.CASCADE, blank=True,
                                   null=True)
    show_block = models.ForeignKey(to=Block, related_name='show_after_effects', on_delete=models.CASCADE, blank=True,
                                   null=True)

    clear_scene_blocks = models.ForeignKey(to=Scene, related_name='clear_blocks_after_effects',
                                           on_delete=models.CASCADE, blank=True, null=True)
    clear_scene_actions = models.ForeignKey(to=Scene, related_name='clear_action_after_effects',
                                            on_delete=models.CASCADE, blank=True, null=True)

    hide_action = models.ForeignKey(to=Action, related_name='hide_after_effects', on_delete=models.CASCADE, blank=True,
                                    null=True)
    show_action = models.ForeignKey(to=Action, related_name='show_after_effects', on_delete=models.CASCADE, blank=True,
                                    null=True)

    set_property = models.ForeignKey(to=CharacterProperty, related_name='value_after_effects', on_delete=models.CASCADE,
                                     blank=True, null=True)
    set_property_value = models.TextField(verbose_name=_('after effect action value'), blank=True)

    class Meta:
        unique_together = (
            ("action", "go_to_scene"),
            ("action", "hide_block"),
            ("action", "show_block"),
            ("action", "hide_action"),
            ("action", "show_action"),
            ("action", "set_property"),
            ("action", "clear_scene_blocks"),
            ("action", "clear_scene_actions"),
        )

    def __str__(self):
        effects = []
        if self.go_to_scene:
            effects.append('go to scene %s' % self.go_to_scene)

        if self.hide_block:
            effects.append('hide block %s' % self.hide_block)
        if self.show_block:
            effects.append('show block %s' % self.show_block)

        if self.hide_action:
            effects.append('hide action %s' % self.hide_action)
        if self.show_action:
            effects.append('show action %s' % self.show_action)

        if self.set_property:
            effects.append('set property %s to %s' % (self.set_property, self.set_property_value))

        return "%s: %s" % (self.action, ", ".join(effects))

    def process(self, session_character):
        if self.go_to_scene:
            session_character.go_to_scene(self.go_to_scene)

        if self.hide_block:
            self.hide_block.set_invisible(session_character)
        if self.show_block:
            self.show_block.set_visible(session_character)

        if self.hide_action:
            self.hide_action.set_invisible(session_character)
        if self.show_action:
            self.show_action.set_visible(session_character)

        if self.set_property:
            self.set_property.set_value(session_character, self.set_property_value)

        if self.clear_scene_blocks:
            for block in self.clear_scene_blocks.blocks.all():
                block.set_invisible(session_character)

        if self.clear_scene_actions:
            for action in self.clear_scene_actions.actions.all():
                action.set_invisible(session_character)


# Игровая сессия конкретного юзера внутри квеста.
# может быть несколько, так как он может несколько раз играть в один и тот же квест
class Session(models.Model):
    STATUS_ACTIVE, STATUS_FINISHED = 'a', 'f'
    STATUS_CHOICES = (
        (STATUS_ACTIVE, _('active')),
        (STATUS_FINISHED, _('finished')),
    )

    created_at = models.DateTimeField(_("Date created"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Date updated"), auto_now=True)
    game = models.ForeignKey(to='Game', verbose_name=_('game'), related_name='users_sessions', on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    user = models.ForeignKey(to='telegrambot.User', verbose_name=_('user'),
                             related_name='games_sessions', on_delete=models.CASCADE)

    active_character = models.ForeignKey(to='SessionCharacter', verbose_name=_('active character'),
                                         related_name='active_sessions',
                                         null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return "%s in %s" % (self.user, self.game)

    def get_game_data(self):
        logger.debug("Get game data for session %s with active active_character %s" % (self, self.active_character))
        return {
            'vision': self.active_character.get_scene_vision(),
            'actions': self.active_character.get_scene_actions(),
        }

    def fire_action(self, action_pk):
        logger.debug("Fire some action for session %s with active active_character %s" % (self, self.active_character))

        try:
            action = self.active_character.current_scene.actions.get(pk=action_pk)
            action.fire_after_effects(self.active_character)
            return action
        except Action.DoesNotExist:
            logger.debug("Not found action with pk %s in scene %S" % (action_pk, self.active_character.current_scene))

        return False

    def finish_game(self):
        self.status = self.STATUS_FINISHED
        self.save()
