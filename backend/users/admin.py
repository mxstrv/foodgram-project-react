from django.contrib import admin

from .models import CustomUser


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
    )
    search_fields = ('username',)
    empty_value_display = '-пусто-'


admin.site.register(CustomUser, UserAdmin)
