from django.contrib import admin
from game.models import Game, Character, Scene, Moment, Block, Action, AfterEffect


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'author', 'created_at')


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ('name', 'game', 'start_scene', 'created_at')


@admin.register(Scene)
class SceneAdmin(admin.ModelAdmin):
    list_display = ('name', 'game', 'created_at')


class BlockTabularInline(admin.TabularInline):
    model = Block


class AfterEffectTabularInline(admin.TabularInline):
    model = AfterEffect


@admin.register(Moment)
class MomentAdmin(admin.ModelAdmin):
    list_display = ('name', 'game', 'scene', 'created_at')
    list_filter = ('game', 'scene',)
    inlines = [
        BlockTabularInline,
    ]


@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = ('content', 'game', 'scene', 'moment', 'created_at')
    list_filter = ('game', 'scene',)
    inlines = [
        AfterEffectTabularInline,
    ]
