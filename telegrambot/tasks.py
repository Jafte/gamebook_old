from __future__ import absolute_import, unicode_literals
from huey.contrib.djhuey import HUEY as djhuey
from huey.contrib.djhuey import db_task
from django.conf import settings

from datetime import date, datetime

import json


@db_task(retries=5, retry_delay=1)
def handle_update(update_id, bot_id):
    lock_id = 'handle_update_{}_{}'.format(update_id, bot_id)

    with djhuey.lock_task(lock_id):
        pass
