import logging, json
import telegrambot.caching as caching
from datetime import datetime

from django.http import HttpResponse
from django.views import View
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Bot, User, Chat, Message, Update, CallbackQuery
from .tasks import handle_update


logger = logging.getLogger(__name__)


class OnlyTextMessages(Exception):
    pass


@method_decorator(csrf_exempt, name='dispatch')
class HookView(View):
    def get_bot(self, bot_id):
        try:
            return get_object_or_404(Bot, id=bot_id, enabled=True)
        except Bot.DoesNotExist:
            return None

    def get(self, request, bot_id):
        bot = self.get_bot(bot_id)
        return HttpResponse('ok')

    def post(self, request, bot_id):
        bot = self.get_bot(bot_id)
        update_data = json.loads(request.body.decode("utf-8"))
        try:
            update = self.create_update(update_data, bot)
            if bot.enabled:
                handle_update(update.id, bot.id)
            else:
                logger.error("Update %s ignored by disabled bot %s" % (update, bot.token))
        except OnlyTextMessages:
            logger.warning("Not text message %s for bot %s" % (request.body, bot_id))
            return HttpResponse()
        else:
            return HttpResponse()

    def create_update(self, update_data, bot):
        """Catch update json and save all this shit"""
        if 'message' in update_data:
            try:
                user = caching.get_or_set(
                    User,
                    update_data['message']['from']['id']
                )
            except User.DoesNotExist:
                user, _ = User.objects.get_or_create(**update_data['message']['from'])

            try:
                chat = caching.get_or_set(
                    Chat,
                    update_data['message']['chat']['id']
                )
            except Chat.DoesNotExist:
                chat, _ = Chat.objects.get_or_create(**update_data['message']['chat'])

            if 'text' not in update_data['message']:
                raise OnlyTextMessages

            message, _ = Message.objects.get_or_create(
                message_id=update_data['message']['message_id'],
                from_user=user,
                date=datetime.fromtimestamp(update_data['message']['date']),
                chat=chat,
                text=update_data['message']['text']
            )
            update, _ = Update.objects.get_or_create(
                bot=bot,
                update_id=update_data['update_id'],
                message=message
            )
        elif 'callback_query' in update_data:
            # Message may be not present if it is very old
            if 'message' in update_data['callback_query']:
                try:
                    user = caching.get_or_set(
                        User,
                        update_data['callback_query']['message']['from']['id']
                    )
                except User.DoesNotExist:
                    user, _ = User.objects.get_or_create(
                        **update_data['callback_query']['message']['from']
                    )

                try:
                    chat = caching.get_or_set(
                        Chat,
                        update_data['callback_query']['message']['chat']['id']
                    )
                except Chat.DoesNotExist:
                    chat, _ = Chat.objects.get_or_create(
                        **update_data['callback_query']['message']['chat']
                    )

                message, _ = Message.objects.get_or_create(
                    message_id=update_data['callback_query']['message']['message_id'],
                    from_user=user,
                    date=datetime.fromtimestamp(update_data['callback_query']['message']['date']),
                    chat=chat,
                    text=update_data['callback_query']['message']['text']
                )
            else:
                message = None

            try:
                user = caching.get_or_set(
                    User,
                    update_data['callback_query']['from']['id']
                )
            except User.DoesNotExist:
                user, _ = User.objects.get_or_create(**update_data['callback_query']['from'])

            callback_query, _ = CallbackQuery.objects.get_or_create(
                callback_id=update_data['callback_query']['id'],
                from_user=user,
                message=message,
                data=update_data['callback_query']['data']
            )

            update, _ = Update.objects.get_or_create(
                bot=bot,
                update_id=update_data['update_id'],
                callback_query=callback_query
            )

        else:
            logger.error("Not valid message %s" % update_data)
            raise OnlyTextMessages

        caching.set(update)
        return update
