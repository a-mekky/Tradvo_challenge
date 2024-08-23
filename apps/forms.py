from django import forms
from django.utils.translation import gettext_lazy as _
from .models import App
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
        labels = {
            'username': _('Username'),
            'password1': _('Password'),
            'password2': _('Confirm Password'),
        }
        help_texts = {
            'username': _('Enter your username.'),
            'password1': _('Enter your password.'),
            'password2': _('Enter the same password as above, for verification.'),
        }
        error_messages = {
            'password_mismatch': _('The two password fields didn’t match.'),
        }

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        if 'usable_password' in self.fields:
            del self.fields['usable_password']


class AddAppForm(forms.ModelForm):
    class Meta:
        model = App
        fields = ['name', 'apk_file_path']
        labels = {
            'name': _('App Name'),
            'apk_file_path': _('APK File Path'),
        }
        help_texts = {
            'name': _('Enter the name of the app.'),
            'apk_file_path': _('Upload the APK file for the app.'),
        }


class EditAppForm(forms.ModelForm):
    class Meta:
        model = App
        fields = ['name', 'apk_file_path', 'first_screen_screenshot_path', 'second_screen_screenshot_path']
        labels = {
            'name': _('App Name'),
            'apk_file_path': _('APK File Path'),
            'first_screen_screenshot_path': _('First Screen Screenshot'),
            'second_screen_screenshot_path': _('Second Screen Screenshot'),
        }
        help_texts = {
            'name': _('Enter the name of the app.'),
            'apk_file_path': _('Upload the APK file for the app.'),
            'first_screen_screenshot_path': _('Upload the first screen screenshot.'),
            'second_screen_screenshot_path': _('Upload the second screen screenshot.'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make file fields optional for edits
        self.fields['apk_file_path'].required = False
        self.fields['first_screen_screenshot_path'].required = False
        self.fields['second_screen_screenshot_path'].required = False