"""
Flask Service Configuration
Manages environment variables and application settings
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""
    
    # Flask settings
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_ENV', 'development') == 'development'
    PORT = int(os.getenv('FLASK_PORT', 5000))
    
    # MongoDB settings
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    MONGODB_DB_NAME = os.getenv('MONGODB_DB_NAME', 'insurance_recommender')
    
    # Collections
    COLLECTION_INSURERS = 'insurers'
    COLLECTION_PLANS = 'plans'
    COLLECTION_SIGNALS = 'signals'
    COLLECTION_VEHICLES = 'vehicles'
    COLLECTION_QUERY_LOGS = 'query_logs'
    
    # LLM API Keys
    HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY', '')
    TOGETHER_AI_API_KEY = os.getenv('TOGETHER_AI_API_KEY', '')
    
    # JWT settings
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-change-in-production')
    
    # Redis (optional)
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'False').lower() == 'true'
    
    # Recommendation settings
    DEFAULT_TOP_N = 3
    MAX_TOP_N = 10
    
    # TOPSIS default weights (λ₁, λ₂, λ₃, λ₄)
    DEFAULT_WEIGHTS = {
        'cost': 0.30,          # λ₁: Cost efficiency
        'coverage': 0.25,      # λ₂: Coverage adequacy
        'service': 0.25,       # λ₃: Service quality
        'reliability': 0.20    # λ₄: Reliability/retention
    }


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    CACHE_ENABLED = True


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

