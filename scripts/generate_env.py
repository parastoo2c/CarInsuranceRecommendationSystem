#!/usr/bin/env python3
"""
Generate .env file with secure secret keys
"""

import secrets

def generate_secret_key():
    """Generate a secure random secret key"""
    return secrets.token_hex(32)

def create_env_file():
    """Create .env file with generated keys"""
    
    flask_secret = generate_secret_key()
    django_secret = generate_secret_key()
    jwt_secret = generate_secret_key()
    
    env_content = f"""# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB_NAME=insurance_recommender

# Flask Configuration
FLASK_SECRET_KEY={flask_secret}
FLASK_ENV=development
FLASK_PORT=5000

# Django Configuration
DJANGO_SECRET_KEY={django_secret}
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Flask Service URL (for Django to call Flask)
FLASK_SERVICE_URL=http://localhost:5000

# JWT Authentication (optional)
JWT_SECRET_KEY={jwt_secret}

# LLM API Keys (optional - for data extraction)
# HUGGINGFACE_API_KEY=your-key-here
# TOGETHER_AI_API_KEY=your-key-here

# Redis Cache (optional)
# REDIS_URL=redis://localhost:6379/0
# CACHE_ENABLED=False
"""
    
    # Write to .env file
    env_path = '../.env'
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print("✅ .env file created successfully!")
    print(f"📁 Location: {env_path}")
    print("\n🔑 Generated Secret Keys:")
    print(f"Flask:  {flask_secret[:20]}...")
    print(f"Django: {django_secret[:20]}...")
    print(f"JWT:    {jwt_secret[:20]}...")
    print("\n⚠️  Keep these keys secret! Don't commit to Git.")

if __name__ == '__main__':
    create_env_file()