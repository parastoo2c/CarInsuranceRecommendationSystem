"""
URL patterns for recommender app
"""

from django.urls import path
from . import views

app_name = 'recommender'

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('results/', views.results, name='results'),
    path('about/', views.about, name='about'),
]

