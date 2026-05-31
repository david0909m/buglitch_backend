from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    list_display = (
        'id',
        'username',
        'email',
        'is_staff',
    )

    fieldsets = UserAdmin.fieldsets + (
        (
            'Buglitch',
            {
                'fields': (
                    'profile_picture',
                )
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            'Buglitch',
            {
                'fields': (
                    'profile_picture',
                )
            },
        ),
    )