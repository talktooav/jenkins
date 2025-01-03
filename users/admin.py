from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import UserRegisterForm

User = get_user_model()


class UserAdmin(BaseUserAdmin):
    # forms to be add and change user interaction
    #form = UserAdminChangeForm
    add_form = UserRegisterForm

    #field to be used to display the user model
    list_display = ('email', 'admin')
    list_filter  = ('admin', 'staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('first_name', 'last_name', 'email', 'password')}),
        # ('Full name', {'fields': ()}),
        # ('Permissions', {'fields': ('admin', 'staff', 'is_active',)}),
        ('Administration', {'fields': ('groups',)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'email', 'password1', 'password2', 'user_type', 'groups')}
        ),
    )
    search_fields = ('email', 'first_name', 'last_name',)
    ordering = ('email',)
    filter_horizontal = ()
# ~ admin.site.unregister(User)
# ~ admin.site.register(User, UserAdmin)
