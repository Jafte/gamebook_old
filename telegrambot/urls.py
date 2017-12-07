from django.urls import path
from .views import HookView


urlpatterns = [
    path('<uuid:bot_id>/', HookView.as_view(), name='telegrambot_hook'),
]
