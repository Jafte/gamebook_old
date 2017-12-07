import uuid
import telegram
import json
import ast

from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from telegrambot.utils import validate_token


class State(models.Model):
    """
    Represents a state for a conversation and a bot.
    Depending the state of the chat only some actions can be performed.
    """
    created_at = models.DateTimeField(_("Date created"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Date updated"), auto_now=True)
    name = models.CharField(_('State name'), db_index=True, max_length=255,
                            help_text=_("Name of the state"))

    class Meta:
        verbose_name = _('State')
        verbose_name_plural = _('States')

    def __str__(self):
        return "%s" % self.name


class User(models.Model):
    id = models.BigIntegerField(primary_key=True)
    first_name = models.CharField(_('First name'), max_length=255)
    last_name = models.CharField(_('Last name'), max_length=255, blank=True, null=True)
    username = models.CharField(_('User name'), max_length=255, blank=True, null=True)
    is_bot = models.BooleanField(_('Is user a Bot'), default=False)
    language_code = models.CharField(_('Langiage code'), max_length=255, blank=True, null=True)
    site_user = models.ForeignKey(to=settings.AUTH_USER_MODEL , verbose_name=_('Site user'),
                                  related_name='telegram_users', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        return "%s" % self.first_name


class Chat(models.Model):
    PRIVATE, GROUP, SUPERGROUP, CHANNEL = 'private', 'group', 'supergroup', 'channel'

    TYPE_CHOICES = (
        (PRIVATE, _('Private')),
        (GROUP, _('Group')),
        (SUPERGROUP, _('Supergroup')),
        (CHANNEL, _('Channel')),
    )

    id = models.BigIntegerField(primary_key=True)
    type = models.CharField(max_length=255, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255, null=True, blank=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = _('Chat')
        verbose_name_plural = _('Chats')

    def __str__(self):
        return "%s" % (self.id)


class ChatState(models.Model):
    created_at = models.DateTimeField(_("Date created"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Date updated"), auto_now=True)
    context = models.TextField(verbose_name=_("Context"),
                               help_text=_("Context serialized to json when this state was set"), null=True,
                               blank=True)
    state = models.ForeignKey(State, verbose_name=_('State'), related_name='%(class)s_chat',
                              help_text=_("State related to the chat"), on_delete=models.CASCADE)
    chat = models.ForeignKey(Chat, db_index=True, verbose_name=_('Chat'), related_name='telegram_chatstates',
                             help_text=_("Chat in Telegram API format. https://core.telegram.org/bots/api#chat"),
                             on_delete = models.CASCADE)
    user = models.ForeignKey(User, db_index=True, verbose_name=_("Telegram User"),
                             related_name='telegram_chatstates', on_delete=models.CASCADE,
                             help_text=_("Telegram unique username"))

    class Meta:
        verbose_name = _('Telegram Chat State')
        verbose_name_plural = _('Telegram Chats States')

    def _get_context(self):
        if self.context:
            return json.loads(self.context)
        return {}

    def _set_context(self, value):
        self.context = json.dumps(value)

    ctx = property(_get_context, _set_context)

    def __str__(self):
        return "(%s:%s)" % (str(self.chat.id), self.state.name)


class Bot(models.Model):
    """
    Telegram integration (requires token to set webhook and obtain some bot info).
    Follow telegram instructions to create a bot and obtain its token `<https://core.telegram.org/bots#botfather>`_.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(_("Date created"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Date updated"), auto_now=True)
    enabled = models.BooleanField(_('Enable'), default=True, help_text=_("Enable/disable telegram bot"))
    token = models.CharField(_('Token'), max_length=100, db_index=True, unique=True,
                             validators=[validate_token],
                             help_text=_("Token provided by Telegram API https://core.telegram.org/bots"))
    user_api = models.OneToOneField(User, verbose_name=_("Telegram Bot User"), related_name='telegram_bot',
                                    on_delete=models.CASCADE, blank=True, null=True,
                                    help_text=_("Telegram API info. Automatically retrieved from Telegram"))

    class Meta:
        verbose_name = _('Telegram Bot')
        verbose_name_plural = _('Telegram Bots')

    def __init__(self, *args, **kwargs):
        super(Bot, self).__init__(*args, **kwargs)
        self._bot = None
        if self.token:
            try:
                self.init_bot()
            except telegram.bot.InvalidToken:
                raise Exception("Incorrect token %s" % self.token)

    def __str__(self):
        return "%s" % (self.user_api.first_name or self.token if self.user_api else self.token)

    def init_bot(self):
        self._bot = telegram.Bot(self.token)

    @property
    def hook_id(self):
        return str(self.id)

    @property
    def hook_url(self):
        return reverse('telegrambot_hook', args=(self.id, ))

    @property
    def null_url(self):
        return None

    def set_webhook(self, url):
        self._bot.set_webhook(url=url)

    def _get_chat_and_user(self, update):
        if update.message:
            chat = update.message.chat
            user = update.message.from_user
        elif update.callback_query:
            chat = update.callback_query.message.chat
            user = update.callback_query.from_user
        return chat, user

    def message_text(self, message):
        if message.message:
            return message.message.text
        elif message.callback_query:
            return message.callback_query.data

    def get_chat_state(self, message):
        chat, user = self._get_chat_and_user(message)
        try:
            return ChatState.objects.select_related('state', 'chat', 'user').get(chat=chat, user=user,
                                                                                         state__bot=self.bot)
        except ChatState.DoesNotExist:
            return None

    def _create_keyboard_button(self, element):
        if isinstance(element, tuple):
            if 'http' in element[1]:
                return telegram.InlineKeyboardButton(text=element[0], url=element[1])
            else:
                return telegram.InlineKeyboardButton(text=element[0], callback_data=element[1])
        else:
            return telegram.InlineKeyboardButton(text=element, callback_data=element)

    def build_keyboard(self, keyboard):
        if keyboard:
            keyboard_data = ast.literal_eval(keyboard)
            keyboard_data_redy_to_built = []

            if not isinstance(keyboard_data, list):
                row_data_redy_to_built = [self._create_keyboard_button(keyboard_data)]
                keyboard_data_redy_to_built.append(row_data_redy_to_built)
            else:
                for element in keyboard_data:
                    if not isinstance(element, list):
                        row_data_redy_to_built = [self._create_keyboard_button(element)]
                    else:
                        row_data_redy_to_built = []
                        for subelement in element:
                            row_data_redy_to_built.append(self._create_keyboard_button(subelement))

                    keyboard_data_redy_to_built.append(row_data_redy_to_built)

            built_keyboard = telegram.InlineKeyboardMarkup(keyboard_data_redy_to_built)
        else:
            built_keyboard = telegram.InlineKeyboardMarkup([])
        return built_keyboard

    def create_chat_state(self, message, target_state, context):
        chat, user = self._get_chat_and_user(message)
        ChatState.objects.create(
            chat=chat,
            user=user,
            state=target_state,
            ctx=context
        )

    def get_chat_id(self, message):
        chat, user = self._get_chat_and_user(message)
        return chat.id

    def send_message(self, chat_id, text, keyboard, update_message=None, user=None):
        parse_mode = telegram.ParseMode.HTML
        disable_web_page_preview = True
        update_message_id = None
        if update_message:
            if update_message.callback_query:
                update_message_id = update_message.callback_query.message.message_id
        texts = text.strip().split('<!--next-->')
        msgs = []
        for txt in texts:
            msgs.append((txt, None))
        if keyboard:
            msgs[-1] = (msgs[-1][0], keyboard)

        can_update = True
        for msg in msgs:
            if update_message_id and can_update:
                self._bot.edit_message_text(chat_id=chat_id, message_id=update_message_id, text=msg[0],
                                            parse_mode=parse_mode,
                                            disable_web_page_preview=disable_web_page_preview,
                                            reply_markup=msg[1])
                can_update = False
            else:
                self._bot.send_message(chat_id=chat_id, text=msg[0], parse_mode=parse_mode,
                                       disable_web_page_preview=disable_web_page_preview, reply_markup=msg[1])


class Message(models.Model):
    created_at = models.DateTimeField(_("Date created"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Date updated"), auto_now=True)
    message_id = models.BigIntegerField(_('Id'), db_index=True)  # It is no unique. Only combined with chat and bot
    from_user = models.ForeignKey(User, related_name='messages', verbose_name=_("User"), on_delete=models.CASCADE)
    date = models.DateTimeField(_('Date'))
    chat = models.ForeignKey(Chat, related_name='messages', verbose_name=_("Chat"), on_delete=models.CASCADE)
    forward_from = models.ForeignKey(User, null=True, blank=True, related_name='forwarded_from',
                                     verbose_name=_("Forward from"), on_delete=models.CASCADE)
    text = models.TextField(null=True, blank=True, verbose_name=_("Text"))

    #  TODO: complete fields with all message fields

    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['-date', ]

    def __str__(self):
        return "(%s,%s,%s)" % (self.message_id, self.chat, self.text or '(no text)')


class CallbackQuery(models.Model):
    created_at = models.DateTimeField(_("Date created"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Date updated"), auto_now=True)
    callback_id = models.CharField(_('Id'), db_index=True, max_length=255)  # It might not be unique.
    from_user = models.ForeignKey(User, related_name='callback_queries', verbose_name=_("User"), on_delete=models.CASCADE)
    message = models.ForeignKey(Message, null=True, blank=True, related_name='callback_queries',
                                verbose_name=_("Message"), on_delete=models.CASCADE)
    data = models.TextField(null=True, blank=True, verbose_name=_("Data"), max_length=255)

    class Meta:
        verbose_name = 'CallbackQuery'
        verbose_name_plural = 'CallbackQueries'

    def __str__(self):
        return "(%s,%s)" % (self.callback_id, self.data)


class Update(models.Model):
    created_at = models.DateTimeField(_("Date created"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Date updated"), auto_now=True)
    bot = models.ForeignKey(Bot, verbose_name=_("Bot"), related_name="updates", on_delete=models.CASCADE)
    update_id = models.BigIntegerField(_('Update Id'), db_index=True)
    message = models.ForeignKey(Message, null=True, blank=True, verbose_name=_('Message'),
                                related_name="updates", on_delete=models.CASCADE)
    callback_query = models.ForeignKey(CallbackQuery, null=True, blank=True, verbose_name=_("Callback Query"),
                                       related_name="updates", on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Update'
        verbose_name_plural = 'Updates'
        unique_together = ('update_id', 'bot')

    def __str__(self):
        return "(%s, %s)" % (self.bot.id, self.update_id)
