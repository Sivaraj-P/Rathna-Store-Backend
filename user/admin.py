from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from .models import User,UserActivationToken,ForgetPasswordOTP

admin.site.unregister(Group)

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email_id', 'first_name', 'last_name', 'phone_number', 'is_staff', 'is_active', 'created_at', 'updated_at')
    search_fields = ('email_id', 'first_name', 'last_name', 'phone_number')
    list_filter = ('is_staff', 'is_active')
    ordering = ('email_id',)

    fieldsets = (
        (None, {'fields': ('email_id', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone_number')}),
        ('Permissions', {'fields': ('is_active', 'is_staff')}),
        ('Important dates', {'fields': ('last_login', )}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email_id', 'first_name', 'last_name', 'phone_number', 'password1', 'password2'),
        }),
    )

admin.site.register(User, CustomUserAdmin)


class UserActivationTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_status', 'created_at', 'expire_at', 'activated_at')
    search_fields = ('user__username', 'user__email', 'token')
    list_filter = ('user_status', 'created_at', 'expire_at', 'activated_at')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'expire_at', 'activated_at') 

admin.site.register(UserActivationToken, UserActivationTokenAdmin)
admin.site.register(ForgetPasswordOTP)