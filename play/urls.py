from django.urls import path
from play.views import PlayView

urlpatterns = [
    path(
        'g<int:game_pk>/',
        GamePlayView.as_view(), name="game_play"
    ),
]
