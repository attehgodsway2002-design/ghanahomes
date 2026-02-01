from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import condition
from .models import (
    Property, PropertyCategory, PropertyImage, PropertyVideo,
    Favorite, PropertyView, PropertyReview
)
from .forms import (
    PropertyForm, PropertyImageForm, PropertySearchForm,
    PropertyReviewForm
)
from subscriptions.models import Subscription


def home(request):
    """Homepage view - optimized with select_related and prefetch_related"""
    # Get featured properties, slice first, then prefetch
    featured_properties = Property.objects.filter(
        is_featured=True, 
        status='available'
    ).select_related('owner', 'category').order_by('-created_at')[:6]
    featured_properties = featured_properties.prefetch_related('images')
    
    # Get recent properties, slice first, then prefetch
    recent_properties = Property.objects.filter(
        status='available'
    ).select_related('owner', 'category').order_by('-created_at')[:8]
    recent_properties = recent_properties.prefetch_related('images')
    
    categories = PropertyCategory.objects.all()
    
    # Get property counts by region
    regions_with_counts = Property.objects.filter(
        status='available'
    ).values('region').annotate(count=Count('id'))
    
    context = {
        'featured_properties': featured_properties,
        'recent_properties': recent_properties,
        'categories': categories,
        'regions_with_counts': regions_with_counts,
    }
    
    return render(request, 'properties/home.html', context)


def property_list(request):
    """List all available properties - optimized with select_related and prefetch"""
    # Start with base queryset
    properties = Property.objects.filter(
        status='available'
    ).select_related('owner', 'category')
    
    # Apply filters BEFORE prefetch
    form = PropertySearchForm(request.GET)
    if form.is_valid():
        query = form.cleaned_data.get('query')
        property_type = form.cleaned_data.get('property_type')
        region = form.cleaned_data.get('region')
        city = form.cleaned_data.get('city')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        bedrooms = form.cleaned_data.get('bedrooms')
        bathrooms = form.cleaned_data.get('bathrooms')
        furnishing = form.cleaned_data.get('furnishing')
        
        if query:
            properties = properties.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(address__icontains=query)
            )
        
        if property_type:
            properties = properties.filter(property_type=property_type)
        
        if region:
            properties = properties.filter(region=region)
        
        if city:
            properties = properties.filter(city__icontains=city)
        
        if min_price:
            properties = properties.filter(price__gte=min_price)
        
        if max_price:
            properties = properties.filter(price__lte=max_price)
        
        if bedrooms:
            properties = properties.filter(bedrooms__gte=bedrooms)
        
        if bathrooms:
            properties = properties.filter(bathrooms__gte=bathrooms)
        
        if furnishing:
            properties = properties.filter(furnishing=furnishing)
    
    # NOW apply prefetch after all filters
    properties = properties.prefetch_related('images')
    
    # Pagination
    paginator = Paginator(properties, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'properties': page_obj,
        'form': form,
        'total_count': paginator.count,
    }
    
    return render(request, 'properties/property_list.html', context)


def property_detail(request, slug):
    """Property detail view - optimized"""
    property = get_object_or_404(
        Property.objects.select_related('owner', 'category').prefetch_related('images', 'videos'),
        slug=slug
    )
    
    # Track view
    property.increment_views()
    
    # Save view record
    ip_address = request.META.get('REMOTE_ADDR')
    PropertyView.objects.create(
        property=property,
        user=request.user if request.user.is_authenticated else None,
        ip_address=ip_address
    )
    
    # Check if user has favorited
    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(
            user=request.user,
            property=property
        ).exists()
    
    # Get related properties
    related_properties = Property.objects.filter(
        region=property.region,
        status='available'
    ).exclude(id=property.id).select_related('owner', 'category').prefetch_related('images')[:4]
    
    # Get reviews
    reviews = PropertyReview.objects.filter(property=property).select_related('user')
    
    context = {
        'property': property,
        'is_favorited': is_favorited,
        'related_properties': related_properties,
        'reviews': reviews,
        'images': property.images.all(),
        'videos': property.videos.all(),
    }
    
    return render(request, 'properties/property_detail.html', context)


@login_required
def property_create(request):
    """Create new property listing"""
    if not request.user.is_landlord():
        messages.error(request, 'Only landlords/agents can post properties.')
        return redirect('properties:home')
    
    # Check subscription
    try:
        subscription = Subscription.objects.get(user=request.user)
        if not subscription.can_add_property():
            plan_name = subscription.plan.name if subscription.plan else 'Current'
            messages.warning(
                request, 
                f'You have reached your property limit ({subscription.plan.property_limit}) for the {plan_name} plan. '
                'Please upgrade your plan to add more properties.'
            )
            return redirect('subscriptions:plans')
    except Subscription.DoesNotExist:
        messages.warning(request, 'Please subscribe to a plan to post properties.')
        return redirect('subscriptions:plans')
    
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            property = form.save(commit=False)
            property.owner = request.user
            property.save()
            
            # Handle multiple image uploads
            images = request.FILES.getlist('images')
            for idx, img in enumerate(images):
                prop_image = PropertyImage(property=property, image=img)
                # Set first image as primary if no primary exists
                if not property.images.filter(is_primary=True).exists() and idx == 0:
                    prop_image.is_primary = True
                prop_image.save()
            
            # Update subscription count
            subscription.property_count += 1
            subscription.save()
            
            # Send admin notification for new property listing
            try:
                from accounts.email_utils import send_admin_property_listed
                send_admin_property_listed(property, request)
            except Exception as e:
                print(f"Error sending admin property notification: {e}")
            
            messages.success(request, f'Property created successfully with {len(images)} image(s)!')
            return redirect('properties:property_detail', slug=property.slug)
    else:
        form = PropertyForm()
    
    context = {
        'form': form,
        'subscription': subscription,
        'properties_posted': subscription.property_count,
        'properties_limit': subscription.plan.property_limit,
        'properties_remaining': max(0, subscription.plan.property_limit - subscription.property_count),
    }
    
    return render(request, 'properties/property_form.html', context)


@login_required
def property_edit(request, slug):
    """Edit existing property"""
    property = get_object_or_404(Property, slug=slug, owner=request.user)
    
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=property)
        if form.is_valid():
            form.save()
            messages.success(request, 'Property updated successfully!')
            return redirect('properties:property_detail', slug=property.slug)
    else:
        form = PropertyForm(instance=property)
    
    context = {
        'form': form,
        'property': property,
        'images': property.images.all(),
        'videos': property.videos.all(),
    }
    
    return render(request, 'properties/property_edit.html', context)


@login_required
def property_add_images(request, slug):
    """Handle upload of one or more images for a property (landlord only)."""
    property = get_object_or_404(Property, slug=slug, owner=request.user)

    if request.method != 'POST':
        return redirect('properties:property_edit', slug=property.slug)

    # Accept multiple files from input name 'images'
    images = request.FILES.getlist('images')
    created = 0
    for idx, img in enumerate(images):
        prop_image = PropertyImage(property=property, image=img)
        # If there is no primary image, mark the first uploaded as primary
        if not property.images.filter(is_primary=True).exists() and idx == 0:
            prop_image.is_primary = True
        prop_image.save()
        created += 1

    if created:
        messages.success(request, f'Successfully uploaded {created} image(s).')
    else:
        messages.warning(request, 'No images were uploaded.')

    return redirect('properties:property_edit', slug=property.slug)


@login_required
def property_delete(request, slug):
    """Delete property"""
    property = get_object_or_404(Property, slug=slug, owner=request.user)
    
    if request.method == 'POST':
        # Update subscription count
        try:
            subscription = Subscription.objects.get(user=request.user)
            subscription.property_count -= 1
            subscription.save()
        except Subscription.DoesNotExist:
            pass
        
        property.delete()
        messages.success(request, 'Property deleted successfully!')
        return redirect('properties:my_properties')
    
    return render(request, 'properties/property_confirm_delete.html', {'property': property})


@login_required
def my_properties(request):
    """List user's properties"""
    if not request.user.is_landlord():
        messages.error(request, 'Access denied.')
        return redirect('properties:home')
    
    properties = Property.objects.filter(owner=request.user).order_by('-created_at')
    
    context = {
        'properties': properties,
    }
    
    return render(request, 'properties/my_properties.html', context)


@login_required
def toggle_favorite(request, slug):
    """Add/remove property from favorites"""
    property = get_object_or_404(Property, slug=slug)
    
    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        property=property
    )
    
    if not created:
        favorite.delete()
        property.favorites_count -= 1
        property.save()
        messages.success(request, 'Property removed from favorites.')
    else:
        property.favorites_count += 1
        property.save()
        messages.success(request, 'Property added to favorites!')
    
    return redirect('properties:property_detail', slug=slug)


@login_required
def favorites_list(request):
    """List user's favorite properties"""
    favorites = Favorite.objects.filter(user=request.user).select_related('property')
    
    context = {
        'favorites': favorites,
    }
    
    return render(request, 'properties/favorites_list.html', context)


@login_required
def add_review(request, slug):
    """Add review to property"""
    property = get_object_or_404(Property, slug=slug)
    
    if request.method == 'POST':
        form = PropertyReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.property = property
            review.user = request.user
            review.save()
            
            messages.success(request, 'Review added successfully!')
            return redirect('properties:property_detail', slug=slug)
    
    return redirect('properties:property_detail', slug=slug)


def search(request):
    """Search properties"""
    form = PropertySearchForm(request.GET)
    properties = Property.objects.filter(status='available')
    
    if form.is_valid():
        # Apply search logic (same as property_list)
        pass
    
    context = {
        'properties': properties,
        'form': form,
    }
    
    return render(request, 'properties/search.html', context)


def advanced_search(request):
    """Advanced search with more filters (uses the same form fields).

    This view exists because `properties/urls.py` references it. It
    reuses `PropertySearchForm` and mirrors the filtering logic used in
    `property_list` so templates can present an advanced search page.
    """
    form = PropertySearchForm(request.GET)
    properties = Property.objects.filter(status='available').select_related('owner', 'category')

    if form.is_valid():
        query = form.cleaned_data.get('query')
        property_type = form.cleaned_data.get('property_type')
        region = form.cleaned_data.get('region')
        city = form.cleaned_data.get('city')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        bedrooms = form.cleaned_data.get('bedrooms')
        bathrooms = form.cleaned_data.get('bathrooms')
        furnishing = form.cleaned_data.get('furnishing')

        if query:
            properties = properties.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(address__icontains=query)
            )

        if property_type:
            properties = properties.filter(property_type=property_type)

        if region:
            properties = properties.filter(region=region)

        if city:
            properties = properties.filter(city__icontains=city)

        if min_price:
            properties = properties.filter(price__gte=min_price)

        if max_price:
            properties = properties.filter(price__lte=max_price)

        if bedrooms:
            properties = properties.filter(bedrooms__gte=bedrooms)

        if bathrooms:
            properties = properties.filter(bathrooms__gte=bathrooms)

        if furnishing:
            properties = properties.filter(furnishing=furnishing)

    # Pagination (reuse same pagination as list)
    paginator = Paginator(properties, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'properties': page_obj,
        'form': form,
        'total_count': properties.count(),
    }

    return render(request, 'properties/search.html', context)


def category_properties(request, slug):
    """Properties by category"""
    category = get_object_or_404(PropertyCategory, slug=slug)
    properties = Property.objects.filter(category=category, status='available')
    
    context = {
        'category': category,
        'properties': properties,
    }
    
    
    return render(request, 'properties/category_properties.html', context)