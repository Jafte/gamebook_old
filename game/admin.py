from django.contrib import admin
from game.models import Game, Character, Scene, Moment, Block, Action


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'author', 'created_at')


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ('name', 'game', 'start_scene', 'created_at')


@admin.register(Scene)
class SceneAdmin(admin.ModelAdmin):
    list_display = ('name', 'game', 'created_at')
