from django.contrib import admin
from play.models import Gamelog, SessionCharacter, Session


@admin.register(Gamelog)
class GamelogAdmin(admin.ModelAdmin):
    list_display = ('source', 'created_at', 'text', )


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('game', 'status', 'user', 'active_character')


@admin.register(SessionCharacter)
class SessionCharacterAdmin(admin.ModelAdmin):
    list_display = ('session', 'character', 'current_scene', 'created_at')
