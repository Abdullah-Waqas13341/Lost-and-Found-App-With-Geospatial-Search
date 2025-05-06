
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django.contrib import messages
from .forms import UserRegistrationForm
from rest_framework import viewsets
from .models import LostItem
from .serializers import LostItemSerializer
from django.contrib.auth.decorators import login_required
from .forms import LostItemForm

@login_required
def choose_lost_or_found(request):
    if request.method == 'POST':
        choice = request.POST.get('choice')
        if choice == 'lost':
            return redirect('report_lost_item')
        elif choice == 'found':
            return redirect('report_found_item')
    return render(request, 'core/choose_lost_or_found.html')

class LostItemViewSet(viewsets.ModelViewSet):
    queryset = LostItem.objects.all()
    serializer_class = LostItemSerializer
from django.contrib.gis.geos import Point

def save_item_with_location(form, user, status):
    item = form.save(commit=False)
    item.user = user
    item.status = status
    lat = form.cleaned_data.get('latitude')
    lng = form.cleaned_data.get('longitude')
    radius = form.cleaned_data.get('radius')

    if lat and lng:
        item.location = Point(lng, lat)  # Note: Point(lon, lat)
    if radius:
        item.radius = radius
    item.save()
    return item

@login_required
def report_lost_item(request):
    if request.method == 'POST':
        form = LostItemForm(request.POST, request.FILES)
        if form.is_valid():
            save_item_with_location(form, request.user, 'LOST')
            return redirect('item_list')
    else:
        form = LostItemForm()
    return render(request, 'core/report_item.html', {'form': form, 'item_type': 'Lost'})

@login_required
def report_found_item(request):
    if request.method == 'POST':
        form = LostItemForm(request.POST, request.FILES)
        if form.is_valid():
            save_item_with_location(form, request.user, 'FOUND')
            return redirect('item_list')
    else:
        form = LostItemForm()
    return render(request, 'core/report_item.html', {'form': form, 'item_type': 'Found'})





def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('lost_found_choice')  # Redirect to lost/found choice page
    else:
        form = UserRegistrationForm()
    return render(request, 'core/register.html', {'form': form})




def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                # Redirect to the page where the user chooses lost or found item
                return redirect('choose_lost_or_found')  # This should match the URL pattern name
            else:
                messages.error(request, "Invalid username or password")
        else:
            messages.error(request, "Invalid username or password")
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

def map_view(request):
    # Query all lost items
    lost_items = LostItem.objects.all()  # You can filter based on certain criteria if needed

    # Pass the items to the template
    return render(request, 'core/map_view.html', {'lost_items': lost_items})

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import LostItem

@login_required
def item_list(request):
    # Get only FOUND items
    items = LostItem.objects.filter(status='FOUND').order_by('-reported_at')

    # Optional filtering based on GET parameters
    category = request.GET.get('category')
    location = request.GET.get('location')

    if category:
        items = items.filter(category__icontains=category)
    if location:
        items = items.filter(location_text__icontains=location)

    return render(request, 'core/item_list.html', {'items': items})



# Create your views here.
