import logging
import telegrambot.caching
import json

from django.http import HttpResponse
from django.views import View
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Bot


logger = logging.getLogger(__name__)


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
        received_json_data = json.loads(request.body.decode("utf-8"))
        logger.info(received_json_data)
        return HttpResponse('ok')
