from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from user.forms import CreateUserForm, ChangeUserForm
from user.models import UserModel, Profile, VerifyCode


class CustomUserAdmin(UserAdmin):
    add_form = CreateUserForm
    form = ChangeUserForm
    model = UserModel
    list_display = ['username', 'email', 'email_verified',]


admin.site.register(UserModel, CustomUserAdmin)
admin.site.register(Profile)
admin.site.register(VerifyCode)

