from django.urls import path
from game.views import game, charatcer, scene, moment, block, action

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
        moment.MomentCreateView.as_view(), name="moment_create"
    ),
    path(
        'g<int:game_pk>/s<int:scene_pk>/m<int:moment_pk>/',
        moment.MomentDetailView.as_view(), name="moment_detail"
    ),
    path(
        'g<int:game_pk>/s<int:scene_pk>/m<int:moment_pk>/edit/',
        moment.MomentUpdateView.as_view(), name="moment_update"
    ),
    path(
        'g<int:game_pk>/s<int:scene_pk>/m<int:moment_pk>/delete/',
        moment.MomentDeleteView.as_view(), name="moment_delete"
    ),

    # Scene Block
    path(
        'g<int:game_pk>/s<int:scene_pk>/m<int:moment_pk>/create-block/',
        block.BlockCreateView.as_view(), name="block_create"
    ),
    path(
        'g<int:game_pk>/s<int:scene_pk>/m<int:moment_pk>/b<int:block_pk>/',
        block.BlockDetailView.as_view(), name="block_detail"
    ),
    path(
        'g<int:game_pk>/s<int:scene_pk>/m<int:moment_pk>/b<int:block_pk>/edit/',
        block.BlockUpdateView.as_view(), name="block_update"
    ),
    path(
        'g<int:game_pk>/s<int:scene_pk>/m<int:moment_pk>/b<int:block_pk>/delete/',
        block.BlockDeleteView.as_view(), name="block_delete"
    ),

    # Block Action
    path(
        'g<int:game_pk>/s<int:scene_pk>/m<int:moment_pk>/create-action/',
        action.ActionCreateView.as_view(), name="moment_action_create"
    ),
    path(
        'g<int:game_pk>/s<int:scene_pk>/m<int:moment_pk>/a<int:action_pk>/edit/',
        action.ActionUpdateView.as_view(), name="moment_action_update"
    ),
    path(
        'g<int:game_pk>/s<int:scene_pk>/m<int:moment_pk>/a<int:action_pk>/delete/',
        action.ActionDeleteView.as_view(), name="moment_action_delete"
    ),
]
