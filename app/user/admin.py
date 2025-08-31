from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

class UserAdmin(BaseUserAdmin):
    ordering = ['email']
    list_display = ['email', 'lastname', 'firstname']
    search_fields = ('id', 'email', 'lastname', 'firstname')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (('Personal Info'), {
            'fields': ('lastname', 'firstname', 'phone')}),
        (
            ('Permissions'),
            {'fields': ('is_active', 'is_staff', 'is_superuser', 'verified')}
        ),
        (('Important Info'), {'fields': ('last_login' ,)})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')
        }),
    )




admin.site.register(User, UserAdmin)
