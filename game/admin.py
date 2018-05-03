from django.contrib import admin
from game.models import Game, Character


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'author', 'created_at')


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ('name', 'game', 'start_scene', 'created_at')
