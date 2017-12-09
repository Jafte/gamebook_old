from django.urls import path
from game.views import GameListView, GameCreateView, GameDetailView, GameUpdateView, GameDeleteView, \
                       CharacterCreateView, CharacterDetailView, CharacterUpdateView, CharacterDeleteView

urlpatterns = [
    path('', GameListView.as_view(), name="game_list"),

    path('create/', GameCreateView.as_view(), name="game_create"),
    path('g<int:game_pk>/', GameDetailView.as_view(), name="game_detail"),
    path('g<int:game_pk>/edit/', GameUpdateView.as_view(), name="game_update"),
    path('g<int:game_pk>/delete/', GameDeleteView.as_view(), name="game_delete"),

    path('g<int:game_pk>/create-character/', CharacterCreateView.as_view(), name="character_create"),
    path('g<int:game_pk>/ch<int:character_pk>/', CharacterDetailView.as_view(), name="character_detail"),
    path('g<int:game_pk>/ch<int:character_pk>/edit/', CharacterUpdateView.as_view(), name="character_update"),
    path('g<int:game_pk>/ch<int:character_pk>/delete/', CharacterDeleteView.as_view(), name="character_delete"),
]
