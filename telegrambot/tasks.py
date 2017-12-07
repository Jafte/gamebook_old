from __future__ import absolute_import, unicode_literals

import telegrambot.caching as caching
import logging

from huey.contrib.djhuey import HUEY as djhuey
from huey.contrib.djhuey import db_task
from django.conf import settings

from .models import Update, Bot


logger = logging.getLogger(__name__)


@db_task(retries=5, retry_delay=1)
def handle_update(update_id, bot_id):
    lock_id = 'handle_update_{}_{}'.format(update_id, bot_id)

    with djhuey.lock_task(lock_id):
        try:
            update = caching.get_or_set(Update, update_id)
            telegram_bot = caching.get_or_set(Bot, bot_id)
        except Update.DoesNotExist:
            logger.error("Update %s does not exists" % update_id)
        except Bot.DoesNotExist:
            logger.error("Bot  %s does not exists or disabled" % bot_id)
        except:
            logger.error("Error handling update %s from bot %s" % (update_id, bot_id))
        else:
            try:
                telegram_bot.handle_message(update)
            except:
                logger.error("Error processing %s for bot %s" % (update, telegram_bot))
            else:
                caching.delete(Update, update)
