from django.urls import path
from . import views

app_name = 'properties'

urlpatterns = [
    # Home
    path('', views.home, name='home'),
    
    # Property listing
    path('properties/', views.property_list, name='property_list'),
    
    # Property management (landlord)
    path('properties/create/', views.property_create, name='property_create'),
    path('properties/<slug:slug>/', views.property_detail, name='property_detail'),
    path('properties/<slug:slug>/edit/', views.property_edit, name='property_edit'),
    path('properties/<slug:slug>/add-images/', views.property_add_images, name='property_add_images'),
    path('properties/<slug:slug>/delete/', views.property_delete, name='property_delete'),
    path('my-properties/', views.my_properties, name='my_properties'),
    
    # Favorites
    path('properties/<slug:slug>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('favorites/', views.favorites_list, name='favorites_list'),
    
    # Reviews
    path('properties/<slug:slug>/review/', views.add_review, name='add_review'),
    
    # Search
    path('search/', views.search, name='search'),
    path('advanced-search/', views.advanced_search, name='advanced_search'),
    
    # Categories
    path('category/<slug:slug>/', views.category_properties, name='category_properties'),
]