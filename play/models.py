import logging

from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from game.models import Action


logger = logging.getLogger(__name__)


class Session(models.Model):
    """
    Игровая сессия конкретного юзера внутри квеста.
    может быть несколько, так как он может
    несколько раз играть в один и тот же квест
    """

    STATUS_ACTIVE, STATUS_FINISHED = 'a', 'f'
    STATUS_CHOICES = (
        (STATUS_ACTIVE, _('active')),
        (STATUS_FINISHED, _('finished')),
    )

    created_at = models.DateTimeField(_("Date created"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Date updated"), auto_now=True)
    game = models.ForeignKey(
        to='game.Game',
        verbose_name=_('game'),
        related_name='users_sessions',
        on_delete=models.CASCADE
    )
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    user = models.ForeignKey(
        to=User,
        verbose_name=_('user'),
        related_name='games_sessions',
        on_delete=models.CASCADE
    )
    active_character = models.ForeignKey(
        to='SessionCharacter',
        verbose_name=_('active character'),
        related_name='active_sessions',
        null=True,
        on_delete=models.SET_NULL
    )

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


class SessionCharacter(models.Model):
    created_at = models.DateTimeField(_("Date created"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Date updated"), auto_now=True)
    character = models.ForeignKey(
        to='game.Character',
        verbose_name=_('character'),
        related_name='in_games',
        on_delete=models.CASCADE
    )
    current_scene = models.ForeignKey(
        to='game.Scene',
        verbose_name=_('current scene'),
        related_name='scene_characters',
        on_delete=models.CASCADE
    )
    current_moment = models.ForeignKey(
        to='game.Moment',
        verbose_name=_('current moment'),
        related_name='moment_characters',
        on_delete=models.CASCADE
    )
    session = models.ForeignKey(
        to='Session',
        verbose_name=_('session'),
        related_name='characters',
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = (
            ("character", "session"),
        )

    def __str__(self):
        return "%s: %s" % (self.session, self.character)

    def get_scene_vision(self):
        result = []
        blocks = self.current_moment.get_blocks_for_character(self)
        for block in blocks:
            result.append(block.content)

        return "\n\n".join(result)

    def get_scene_actions(self):
        result = []
        actions = self.current_moment.get_actions_for_character(self)
        for action in actions:
            result.append({'id': action.pk, 'content': action.content})

        return result

    def do_action(self, action_id):
        try:
            action = self.current_moment.actions.get(id=action_id)
            gl_vision = Gamelog(
                session=self.session,
                source=Gamelog.SOURCE_GAME,
                text=self.get_scene_vision()
            )
            gl_action = Gamelog(
                session=self.session,
                source=Gamelog.SOURCE_USER,
                text=action.content
            )
            action.fire_after_effects(self)
            gl_vision.save()
            gl_action.save()
            return True
        except self.current_moment.actions.DoesNotExist:
            return False

    def go_to_scene(self, scene):
        self.current_scene = scene
        self.current_moment = scene.get_default_moment()
        self.save()

    def go_to_moment(self, moment):
        self.current_moment = moment
        if moment.scene != self.current_scene:
            self.current_scene = moment.scene
        self.save()


class SessionProperty(models.Model):
    created_at = models.DateTimeField(_("Date created"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Date updated"), auto_now=True)
    session = models.ForeignKey(
        to='Session',
        verbose_name=_('session'),
        related_name='properties',
        on_delete=models.CASCADE
    )
    character = models.ForeignKey(
        to='SessionCharacter',
        verbose_name=_('character'),
        blank=True,
        null=True,
        related_name='properties',
        on_delete=models.CASCADE
    )
    property = models.ForeignKey(
        to='game.Property',
        verbose_name=_('property'),
        related_name='in_games',
        on_delete=models.CASCADE
    )
    current_value = models.CharField(
        verbose_name=_('current value'),
        max_length=100,
        blank=True
    )

    class Meta:
        unique_together = (
            ("session", "property"),
        )

    def __str__(self):
        return "%s: %s" % (self.character, self.property)


class Gamelog(models.Model):
    SOURCE_USER, SOURCE_GAME = 'u', 'g'
    SOURCE_CHOICES = (
        (SOURCE_USER, _('user')),
        (SOURCE_GAME, _('game')),
    )

    session = models.ForeignKey(
        to='Session',
        verbose_name=_('session'),
        related_name='gamelogs',
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(_("Date created"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Date updated"), auto_now=True)
    source = models.CharField(
        max_length=1,
        choices=SOURCE_CHOICES,
        default=SOURCE_GAME
    )
    text = models.TextField(verbose_name=_('text'))

    class Meta:
        ordering = ['-created_at', ]
