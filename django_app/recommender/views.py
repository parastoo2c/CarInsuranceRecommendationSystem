"""
Views for Insurance Recommender Dashboard
"""

from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
import requests
import logging

logger = logging.getLogger(__name__)


def index(request):
    """Landing page with overview"""
    return render(request, 'recommender/index.html')


def search(request):
    """Search form for insurance recommendations"""
    # Vehicle options (could be fetched from Flask API)
    vehicle_makes = ['Toyota', 'Honda', 'Ford', 'Tesla', 'Chevrolet']
    
    context = {
        'vehicle_makes': vehicle_makes,
    }
    return render(request, 'recommender/search.html', context)


def results(request):
    """Display recommendation results"""
    if request.method != 'POST':
        return redirect('recommender:search')
    
    # Extract form data
    vehicle_make = request.POST.get('vehicle_make')
    vehicle_model = request.POST.get('vehicle_model')
    vehicle_variant = request.POST.get('vehicle_variant', '')
    vehicle_year = request.POST.get('vehicle_year')
    region_code = request.POST.get('region_code')
    city = request.POST.get('city', '')
    top_n = int(request.POST.get('top_n', 3))
    
    # Get custom weights if provided
    weight_cost = float(request.POST.get('weight_cost', 0.30))
    weight_coverage = float(request.POST.get('weight_coverage', 0.25))
    weight_service = float(request.POST.get('weight_service', 0.25))
    weight_reliability = float(request.POST.get('weight_reliability', 0.20))
    
    weights = {
        'cost': weight_cost,
        'coverage': weight_coverage,
        'service': weight_service,
        'reliability': weight_reliability
    }
    
    # Prepare request payload
    payload = {
        'vehicle_make': vehicle_make,
        'vehicle_model': vehicle_model,
        'vehicle_variant': vehicle_variant,
        'vehicle_year': int(vehicle_year) if vehicle_year else None,
        'region_code': region_code,
        'city': city,
        'top_n': top_n,
        'weights': weights
    }
    
    try:
        # Call Flask recommendation API
        flask_url = f"{settings.FLASK_SERVICE_URL}/api/recommend"
        logger.info(f"Calling Flask API: {flask_url}")
        
        response = requests.post(
            flask_url,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            context = {
                'success': True,
                'recommendations': data.get('recommendations', []),
                'query_info': data.get('query_info', {}),
                'weights_used': data.get('weights_used', {}),
                'metadata': data.get('metadata', {}),
                'vehicle': f"{vehicle_make} {vehicle_model}",
                'region': region_code
            }
            
            return render(request, 'recommender/results.html', context)
        
        elif response.status_code == 404:
            messages.error(request, 'No insurance plans found for the selected vehicle and region.')
            return redirect('recommender:search')
        
        else:
            error_data = response.json()
            messages.error(request, f"Error: {error_data.get('error', 'Unknown error')}")
            return redirect('recommender:search')
    
    except requests.exceptions.ConnectionError:
        logger.error("Failed to connect to Flask service")
        messages.error(request, 'Recommendation service is currently unavailable. Please try again later.')
        return redirect('recommender:search')
    
    except requests.exceptions.Timeout:
        logger.error("Flask service timeout")
        messages.error(request, 'Request timed out. Please try again.')
        return redirect('recommender:search')
    
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}", exc_info=True)
        messages.error(request, 'An unexpected error occurred. Please try again.')
        return redirect('recommender:search')


def about(request):
    """About page with project information"""
    return render(request, 'recommender/about.html')

