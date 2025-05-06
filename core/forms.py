from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django.contrib.gis.geos import Point
class UserRegistrationForm(UserCreationForm):
    full_name = forms.CharField(max_length=200, required=True)
    email = forms.EmailField(required=True)
    nust_id = forms.CharField(max_length=50, required=True)  # Add this line

    class Meta:
        model = User
        fields = ['username', 'full_name', 'email', 'nust_id', 'password1', 'password2']
# core/forms.py

from django import forms
from .models import LostItem

class LostItemForm(forms.ModelForm):
    latitude = forms.FloatField(widget=forms.HiddenInput(), required=False)
    longitude = forms.FloatField(widget=forms.HiddenInput(), required=False)
    radius = forms.FloatField(widget=forms.HiddenInput(), required=False)  # if you want radius in future

    class Meta:
        model = LostItem
        fields = ['title', 'description', 'category', 'location_text', 'image']

    def save(self, commit=True):
        instance = super().save(commit=False)
        lat = self.cleaned_data.get('latitude')
        lng = self.cleaned_data.get('longitude')
        if lat is not None and lng is not None:
            instance.location = Point(lng, lat)
        if commit:
            instance.save()
        return instance

