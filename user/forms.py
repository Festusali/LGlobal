# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import ugettext_lazy as _

from user.models import UserModel, Profile, VerifyCode


class CreateUserForm(UserCreationForm):
    """
    Extends UserCreationForm to enable caSe-InseSiTiVe validation of 
    username.
    """
    tos = forms.BooleanField(
        label='Terms of Service', help_text='''By registering an Account with 
        Leading Wealth, I acknowledge that I have read and accepted the <a 
        href="/tos/" title="Terms and Conditions">Terms of Service</a>, <a 
        href="/privacy/#privacy" title="Privacy Policy">Privacy Policy</a> and 
        <a href="/privacy/#cookie" title="Cookie Policy">Cookie Policy</a>.'''
    )

    def clean(self):
        cleaned_data = super(CreateUserForm, self).clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        tos = cleaned_data.get('tos')
        if username and UserModel.objects.filter(
            username__iexact=username
        ).exists():
            self.add_error(
                'username', 'A user with that username already exists.'
            )
        if email and UserModel.objects.filter(email__iexact=email).exists():
            self.add_error('email', '''Email address already in use. If you 
            are the owner please login instead or request password reset.''')
        if not tos:
            self.add_error('email', '''You must accept the Terms and 
            Conditions before you can register a Leading Wealth account.''')
        
        return cleaned_data
    
    class Meta:
        model = UserModel
        fields = ["username", "email"]


class ChangeUserForm(UserChangeForm):
    """Ensure that the correct model is used for changing user details"""
    
    class Meta:
        model = UserModel
        fields = ["username", "email"]


class VerifyEmailForm(forms.ModelForm):
    """Provides form for verifying user email address."""

    class Meta:
        model = VerifyCode
        fields = ['code']


class EditProfileForm(forms.ModelForm):
    """Provides forms for editing user profile details."""

    class Meta:
        model = Profile
        fields = ['phone', 'gender', 'status', 'wallet', 'avatar']