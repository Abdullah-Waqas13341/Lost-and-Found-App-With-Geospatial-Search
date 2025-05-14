from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter
from .views import LostItemViewSet
from .views import choose_lost_or_found, report_lost_item, report_found_item,item_list,solr_search

# Set up the router for the API views (Lost Item ViewSet)
router = DefaultRouter()
router.register(r'items', LostItemViewSet)

# URL patterns for authentication (register, login, logout)
urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    # path('logout/', views.logout, name='logout'),
    path('choose/', choose_lost_or_found, name='choose_lost_or_found'),
    path('report/lost/', report_lost_item, name='report_lost_item'),
    path('report/found/', report_found_item, name='report_found_item'),
    path('items/', solr_search, name='item_list'),
]

# This includes the API routes for lost item management
urlpatterns += router.urls
