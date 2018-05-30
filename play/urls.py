from django.urls import path
from play.views import PlayView

urlpatterns = [
    path(
        'g<int:game_pk>/',
        PlayView.as_view(), name="game_play"
    ),
]
