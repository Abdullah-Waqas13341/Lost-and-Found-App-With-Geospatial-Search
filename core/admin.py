# core/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, LostItem

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ('nust_id', 'full_name')}),
    )
    list_display = ('username', 'full_name', 'email', 'nust_id', 'is_staff')
    search_fields = ('username', 'full_name', 'email', 'nust_id')

@admin.register(LostItem)
class LostItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'category', 'user', 'reported_at','location_text','location','radius','image')    
    list_filter = ('status', 'category', 'reported_at')
    search_fields = ('title', 'description', 'location_text')
    autocomplete_fields = ['user']
    ordering = ('-reported_at',)