from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from django.contrib.auth.models import Group

admin.site.site_header = "Catering Admin Panel"
admin.site.site_title = "Catering Admin"
admin.site.index_title = "Dashboard Manajemen Catering"

try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'is_staff', 'is_active', 'date_joined']
    list_filter = ['is_staff', 'is_active']
    search_fields = ['username', 'email']
    ordering = ['-date_joined']

admin.site.register(CustomUser, CustomUserAdmin)