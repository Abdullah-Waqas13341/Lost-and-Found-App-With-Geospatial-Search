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

from django import forms
from django.contrib.gis.geos import Point
from .models import LostItem

# Predefined lost item categories
COMMON_CATEGORIES = [
    ('wallet', 'Wallet'),
    ('keys', 'Keys'),
    ('phone', 'Phone'),
    ('laptop', 'Laptop'),
    ('bag', 'Bag'),
    ('id_card', 'ID Card'),
    ('usb', 'USB Drive'),
    ('headphones', 'Headphones'),
    ('book', 'Book'),
    ('calculator', 'Calculator'),
    ('glasses', 'Glasses'),
    ('watch', 'Watch'),
    ('notebook', 'Notebook'),
    ('pen', 'Pen'),
    ('jacket', 'Jacket'),
    ('earbuds', 'Earbuds'),
    ('bottle', 'Water Bottle'),
    ('powerbank', 'Powerbank'),
    ('other', 'Other'),
]

# Predefined NUST H-12 locations
NUST_LOCATIONS = [
    # Schools & Important Buildings
    #Server
    ('seecs', 'SEECS'),
    ('c2', 'C2'),
    ('nbs', 'NBS'),
    #Server
    ('nice', 'NICE'),
    ('ric', 'RIC'),
    #Server
    ('smme', 'SMME'),
    ('sports_complex', 'Sports Complex'),
    ('swiming_pool', 'Swimming Pool'),
    ('c4', 'C4'),
    #Server
    ('scme', 'SCME'),
    ('c1', 'C1'),
    ('igs', 'IGIS'),
    ('sada', 'SADA'),
    ('nbs_ground', 'NBS Ground'),
    ('helipad_ground', 'Helipad_Ground'),
    #Server
    ('library', 'Central Library'),
    ('masjid', 'Main Masjid'),
    ('rims', 'Rims Building'),
    ('iaec', 'IAEC'),
    #Server
    ('south_edge_cafe', 'South Edge Cafe'),
    ('main_office', 'Main Office'),
    ('library_lawn', 'Library Lawn'),
    ('convocation_ground', 'Convocation Ground'),
    #Server
    ('gate1', 'Main Gate 1'),
    ('gate2', 'Gate 2'),
    ('gate10', 'Gate 10'),


    # Male Hostels
    ('rumi_hostel', 'Rumi Hostel - PG Students'),
    ('johar_hostel', 'Johar Hostel - PG Students'),
    ('ghazali_hostel', 'Ghazali Hostel - UG Students'),
    ('beruni_hostel', 'Beruni Hostel - UG Students'),
    ('razi_hostel', 'Razi Hostel - UG Students'),
    ('rahmat_hostel', 'Rahmat Hostel - UG Students'),
    ('attar_hostel', 'Attar Hostel - UG Students'),
    ('liaquat_hostel', 'Liaquat Hostel - UG Students'),
    ('hajveri_hostel', 'Hajveri Hostel - UG Students'),
    ('zakariya_hostel', 'Zakariya Hostel - UG Students'),

    # Female Hostels
    ('fatima_block1_pg', 'Fatima Hostel Block-I - PG Students'),
    ('fatima_block2_pg', 'Fatima Hostel Block-II - PG Students'),
    ('fatima_block1_ug', 'Fatima Hostel Block-I - UG Students'),
    ('zainab_hostel', 'Zainab Hostel - UG Students'),
    ('ayesha_hostel', 'Ayesha Hostel - UG Students'),
    ('khadija_hostel', 'Khadija Hostel - UG Students'),
    ('amna_hostel', 'Amna Hostel - UG Students'),

    # Other option
    ('other', 'Other'),
]

class LostItemForm(forms.ModelForm):
    category = forms.ChoiceField(choices=COMMON_CATEGORIES, required=True)
    custom_category = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Specify category'}), label='Other Category')

    location_text = forms.ChoiceField(choices=NUST_LOCATIONS, required=True, label='Location')
    custom_location = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Specify location'}), label='Other Location')

    latitude = forms.FloatField(widget=forms.HiddenInput(), required=False)
    longitude = forms.FloatField(widget=forms.HiddenInput(), required=False)
    radius = forms.FloatField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = LostItem
        fields = ['title', 'description', 'category', 'custom_category', 'location_text', 'custom_location', 'image']

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get('category') == 'other' and not cleaned_data.get('custom_category'):
            self.add_error('custom_category', 'Please specify the category.')

        if cleaned_data.get('location_text') == 'other' and not cleaned_data.get('custom_location'):
            self.add_error('custom_location', 'Please specify the location.')

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Use custom category if selected
        if self.cleaned_data['category'] == 'other':
            instance.category = self.cleaned_data['custom_category']

        # Use custom location if selected
        if self.cleaned_data['location_text'] == 'other':
            instance.location_text = self.cleaned_data['custom_location']

        # Save coordinates as Point
        lat = self.cleaned_data.get('latitude')
        lng = self.cleaned_data.get('longitude')
        if lat is not None and lng is not None:
            instance.location = Point(lng, lat)
        # Save radius
        radius = self.cleaned_data.get('radius')
        if radius is not None:
            instance.radius = radius
        if commit:
            instance.save()
        return instance

