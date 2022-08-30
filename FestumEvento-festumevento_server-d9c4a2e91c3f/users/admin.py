from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import User,OtpLog


# Register your models here.

class CustomUserAdmin(UserAdmin):
    list_filter = ('admin',)
    search_fields = ('email',)  # Contain only fields in your `custom-user-model` intended for searching
    fieldsets = (
        (None, {'fields': ('name', 'email', 'mobile', 'role', 'country_code')}),
        ('Personal info', {'fields': ()}),
        ('Permissions', {'fields': ('admin',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name', 'email', 'password1', 'password2', 'mobile', 'role', 'country_code')}
         ),
    )
    ordering = ('email',)  # Contain only fields in your `custom-user-model` intended to ordering
    filter_horizontal = ()  # Leave it empty. You have neither `groups` or `user_permissions`
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ('name', 'email', 'mobile', 'role', 'country_code')
    # fieldsets = UserAdmin.fieldsets + (
    #     (None, {'fields': ('email',)}),
    # )


myUser = get_user_model()
admin.site.register(myUser, CustomUserAdmin)
admin.site.register(OtpLog)

admin.site.unregister(Group)
