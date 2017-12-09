from django.urls import path
from game.views.game import GameListView, GameCreateView, GameDetailView, GameUpdateView, GameDeleteView
from game.views.charatcer import CharacterCreateView, CharacterDetailView, CharacterUpdateView, CharacterDeleteView
from game.views.scene import SceneCreateView, SceneDetailView, SceneUpdateView, SceneDeleteView

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

    path('g<int:game_pk>/create-scene/', SceneCreateView.as_view(), name="scene_create"),
    path('g<int:game_pk>/s<int:scene_pk>/', SceneDetailView.as_view(), name="scene_detail"),
    path('g<int:game_pk>/s<int:scene_pk>/edit/', SceneUpdateView.as_view(), name="scene_update"),
    path('g<int:game_pk>/s<int:scene_pk>/delete/', SceneDeleteView.as_view(), name="scene_delete"),
]
