from django.contrib import admin
from .models import Character, ChatThread, ChatMessage, Profile, Payment

@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ('name', 'summon_count', 'created_at')
    search_fields = ('name',)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'scrolls', 'is_vip')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'reference', 'amount', 'verified')

admin.site.register(ChatThread)
admin.site.register(ChatMessage)
