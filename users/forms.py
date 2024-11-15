from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
from django import forms
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'bio', 'contact_number', 'profession')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'bio', 'contact_number', 'profession')
class EventForm(forms.Form):
    summary = forms.CharField(label='Event Summary', max_length=200)
    start_time = forms.DateTimeField(label='Start Time')
    end_time = forms.DateTimeField(label='End Time')