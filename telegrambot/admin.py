from django.contrib import admin
from telegrambot.models import User, State, Chat, ChatState, Bot, Message, Update, CallbackQuery

@admin.register(User)
class TelegramUserAdmin(admin.ModelAdmin):
    pass

@admin.register(Bot)
class BotAdmin(admin.ModelAdmin):
    pass

@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    pass

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    pass

@admin.register(ChatState)
class ChatStateAdmin(admin.ModelAdmin):
    pass

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    pass

@admin.register(Update)
class UpdateAdmin(admin.ModelAdmin):
    pass

@admin.register(CallbackQuery)
class CallbackQueryAdmin(admin.ModelAdmin):
    pass
