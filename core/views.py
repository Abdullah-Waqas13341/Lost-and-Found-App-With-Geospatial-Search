
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
from .utils import get_core_for_location
from django.contrib.gis.measure import D
import requests
from django.shortcuts import render
from .models import LostItem
from .utils import get_core_for_location

from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from .forms import LostItemForm
import requests

from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from .forms import LostItemForm
import requests
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
        item.location = Point(lng, lat)
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



def solr_search(request):
    category = request.GET.get('category', '')
    location = request.GET.get('location', '')
    latitude = request.GET.get('latitude')
    longitude = request.GET.get('longitude')
    radius = request.GET.get('radius')
    results = []

    # Only show items if a search was performed
    search_performed = any([category, location, latitude, longitude, radius])

    if search_performed:
        # If location is "other" and coordinates are provided, use only coordinates/radius
        if location == "other" and latitude and longitude and radius:
            results = LostItem.objects.filter(status='FOUND')
            if category:
                results = results.filter(category__icontains=category)
            try:
                # Note: Point expects (lng, lat)
                center = Point(float(longitude), float(latitude))
                results = results.filter(location__distance_lte=(center, D(m=float(radius))))
            except Exception as e:
                print("Spatial filter error:", e)
                results = results.none()
        else:
            # Normal Solr core/location logic
            core = get_core_for_location(location) if location else None

            if core:
                solr_url = f'http://localhost:8983/solr/{core}/select'
                query = '*:*'
                filters = []
                if category:
                    filters.append(f'category:{category}')
                if location:
                    filters.append(f'location:{location}')
                fq = ' AND '.join(filters) if filters else None

                params = {'q': query, 'wt': 'json'}
                if fq:
                    params['fq'] = fq

                try:
                    resp = requests.get(solr_url, params=params)
                    if resp.status_code == 200:
                        docs = resp.json()['response']['docs']
                        for doc in docs:
                            try:
                                item = LostItem.objects.get(id=doc['id'])
                                results.append(item)
                            except LostItem.DoesNotExist:
                                continue
                except Exception as e:
                    print("Solr error:", e)
                    results = []
            else:
                # Fallback: show found items matching filters if no location/core
                results = LostItem.objects.filter(status='FOUND').order_by('-reported_at')
                if category:
                    results = results.filter(category__icontains=category)
                if location:
                    results = results.filter(location_text__icontains=location)

            # If coordinates/radius are also provided, further filter results
            if latitude and longitude and radius:
                try:
                    center = Point(float(longitude), float(latitude))
                    results = results.filter(location__distance_lte=(center, D(m=float(radius))))
                except Exception as e:
                    print("Spatial filter error:", e)
                    results = results.none()
    else:
        results = LostItem.objects.none()

    # Prepare items for JSON serialization (for the map)
    items_for_json = []
    for item in results:
        items_for_json.append({
            "id": item.id,
            "title": item.title,
            "category": item.category,
            "location_text": item.location_text,
            "location": item.location.geojson if item.location else None,
            "radius": item.radius,
            "image_url": item.image.url if item.image else "",
        })

    form = LostItemForm()

    return render(request, 'core/item_list.html', {
        'items_qs': results,
        'items': items_for_json,
        'form': form,
        'search_performed': search_performed,
    })



# Create your views here.
