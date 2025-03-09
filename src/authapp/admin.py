from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import UserRegisterForm
from .models import Profile, User


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    # form = UserUpdateForm
    add_form = UserRegisterForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('username', 'active',)
    list_filter = ('active', 'staff', 'admin',)
    search_fields = ['username']
    fieldsets = (
        ('User', {'fields': ('username', 'password')}),
        ('Permissions', {
         'fields': ('admin', 'staff', 'active',)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ("username", "password", "password2",)
        }
        ),
    )
    ordering = ('username',)
    filter_horizontal = ()


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('username',)
    list_filter = ('created',)
    ordering = ('-created',)


admin.site.register(User, UserAdmin)
