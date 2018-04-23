from django import forms
from django.contrib.auth.models import User
from application.models import UserStaticPrefs

class UserStaticPrefsForm(forms.ModelForm):
    class Meta:
        model = UserStaticPrefs
        fields = ('economy', 'politics', 'science', 'arts', 'sports', 'misc')