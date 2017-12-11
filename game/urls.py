from django.urls import path
from game.views.game import GameListView, GameCreateView, GameDetailView, GameUpdateView, GameDeleteView, GamePlayView
from game.views.charatcer import CharacterCreateView, CharacterDetailView, CharacterUpdateView, CharacterDeleteView
from game.views.scene import SceneCreateView, SceneDetailView, SceneUpdateView, SceneDeleteView

urlpatterns = [
    # Game
    path('', GameListView.as_view(), name="game_list"),

    path(
        'create/',
        GameCreateView.as_view(), name="game_create"
    ),
    path(
        'g<int:game_pk>/',
        GameDetailView.as_view(), name="game_detail"
    ),
    path(
        'g<int:game_pk>/edit/',
        GameUpdateView.as_view(), name="game_update"
    ),
    path(
        'g<int:game_pk>/delete/',
        GameDeleteView.as_view(), name="game_delete"
    ),
    path(
        'g<int:game_pk>/play/',
        GamePlayView.as_view(), name="game_play"
    ),

    # Character
    path(
        'g<int:game_pk>/create-character/',
        CharacterCreateView.as_view(), name="character_create"
    ),
    path(
        'g<int:game_pk>/ch<int:character_pk>/',
        CharacterDetailView.as_view(), name="character_detail"
    ),
    path(
        'g<int:game_pk>/ch<int:character_pk>/edit/',
        CharacterUpdateView.as_view(), name="character_update"
    ),
    path(
        'g<int:game_pk>/ch<int:character_pk>/delete/',
        CharacterDeleteView.as_view(), name="character_delete"
    ),

    # Scene
    path(
        'g<int:game_pk>/create-scene/',
        SceneCreateView.as_view(), name="scene_create"
    ),
    path(
        'g<int:game_pk>/s<int:scene_pk>/',
        SceneDetailView.as_view(), name="scene_detail"
    ),
    path(
        'g<int:game_pk>/s<int:scene_pk>/edit/',
        SceneUpdateView.as_view(), name="scene_update"
    ),
    path(
        'g<int:game_pk>/s<int:scene_pk>/delete/',
        SceneDeleteView.as_view(), name="scene_delete"
    ),

    # Scene Block
#    path('g<int:game_pk>/s<int:scene_pk>/create-block/', SceneCreateView.as_view(), name="scene_block_create"),
#    path('g<int:game_pk>/s<int:scene_pk>/b<int:block_pk>/', SceneDetailView.as_view(), name="scene_block_detail"),
#    path('g<int:game_pk>/s<int:scene_pk>/b<int:block_pk>/edit/', SceneUpdateView.as_view(), name="scene_block_update"),
#    path('g<int:game_pk>/s<int:scene_pk>/b<int:block_pk>/delete/', SceneDeleteView.as_view(), name="scene_block_delete"),

    # Scene Action
#    path('g<int:game_pk>/s<int:scene_pk>/create-action/', SceneCreateView.as_view(), name="scene_action_create"),
#    path('g<int:game_pk>/s<int:scene_pk>/a<int:action_pk>/', SceneDetailView.as_view(), name="scene_action_detail"),
#    path('g<int:game_pk>/s<int:scene_pk>/a<int:action_pk>/edit/', SceneUpdateView.as_view(), name="scene_action_update"),
#    path('g<int:game_pk>/s<int:scene_pk>/a<int:action_pk>/delete/', SceneDeleteView.as_view(), name="scene_action_delete"),
]
