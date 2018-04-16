from django.urls import path
from game.views import game, charatcer, scene, moment

urlpatterns = [
    # Game
    path(
        '',
        game.GameListView.as_view(), name="game_list"
    ),

    path(
        'create/',
        game.GameCreateView.as_view(), name="game_create"
    ),
    path(
        'g<int:game_pk>/',
        game.GameDetailView.as_view(), name="game_detail"
    ),
    path(
        'g<int:game_pk>/edit/',
        game.GameUpdateView.as_view(), name="game_update"
    ),
    path(
        'g<int:game_pk>/delete/',
        game.GameDeleteView.as_view(), name="game_delete"
    ),
    path(
        'g<int:game_pk>/play/',
        game.GamePlayView.as_view(), name="game_play"
    ),

    # Character
    path(
        'g<int:game_pk>/create-character/',
        charatcer.CharacterCreateView.as_view(), name="character_create"
    ),
    path(
        'g<int:game_pk>/ch<int:character_pk>/',
        charatcer.CharacterDetailView.as_view(), name="character_detail"
    ),
    path(
        'g<int:game_pk>/ch<int:character_pk>/edit/',
        charatcer.CharacterUpdateView.as_view(), name="character_update"
    ),
    path(
        'g<int:game_pk>/ch<int:character_pk>/delete/',
        charatcer.CharacterDeleteView.as_view(), name="character_delete"
    ),

    # Scene
    path(
        'g<int:game_pk>/create-scene/',
        scene.SceneCreateView.as_view(), name="scene_create"
    ),
    path(
        'g<int:game_pk>/s<int:scene_pk>/',
        scene.SceneDetailView.as_view(), name="scene_detail"
    ),
    path(
        'g<int:game_pk>/s<int:scene_pk>/edit/',
        scene.SceneUpdateView.as_view(), name="scene_update"
    ),
    path(
        'g<int:game_pk>/s<int:scene_pk>/delete/',
        scene.SceneDeleteView.as_view(), name="scene_delete"
    ),

    # Moment
    path(
        'g<int:game_pk>/s<int:scene_pk>/create-moment/',
        moment.MomentDetailView.as_view(), name="moment_create"
    ),
    path(
        'g<int:game_pk>/s<int:scene_pk>/m<int:moment_pk>/',
        moment.MomentDetailView.as_view(), name="moment_detail"
    ),
    path(
        'g<int:game_pk>/s<int:scene_pk>/m<int:moment_pk>/edit/',
        moment.MomentDetailView.as_view(), name="moment_update"
    ),
    path(
        'g<int:game_pk>/s<int:scene_pk>/m<int:moment_pk>/delete/',
        moment.MomentDetailView.as_view(), name="moment_delete"
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
