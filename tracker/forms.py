from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Goal


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']


class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ['weekly_target']
        labels = {'weekly_target': '週の目標回数'}
        widgets = {
            'weekly_target': forms.NumberInput(attrs={'min': 1, 'max': 7}),
        }
