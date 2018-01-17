from django.contrib import admin
from game.models import Gamelog, Game, Character, SessionCharacter


@admin.register(Gamelog)
class GamelogAdmin(admin.ModelAdmin):
    list_display = ('source', 'created_at', 'text', )


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'author', 'created_at')


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ('name', 'game', 'start_scene', 'created_at')


@admin.register(SessionCharacter)
class SessionCharacterAdmin(admin.ModelAdmin):
    list_display = ('session', 'character', 'current_scene', 'created_at')
