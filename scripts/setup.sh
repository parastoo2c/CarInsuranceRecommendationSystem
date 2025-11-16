#!/bin/bash
# Setup script for Insurance Recommender System

echo "==================================="
echo "Insurance Recommender - Setup"
echo "==================================="

# Check Python version
echo "Checking Python version..."
python3 --version || { echo "Python 3 is required"; exit 1; }

# Check if MongoDB is running (optional)
echo "Checking MongoDB..."
if command -v mongosh &> /dev/null || command -v mongo &> /dev/null; then
    echo "✓ MongoDB CLI found"
else
    echo "⚠ MongoDB CLI not found. Install MongoDB or use MongoDB Atlas"
fi

# Setup Flask service
echo ""
echo "Setting up Flask service..."
cd flask_service || exit
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi
source venv/bin/activate
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✓ Flask service ready"
deactivate
cd ..

# Setup Django app
echo ""
echo "Setting up Django app..."
cd django_app || exit
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi
source venv/bin/activate
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✓ Django app ready"
deactivate
cd ..

# Generate seed data
echo ""
echo "Generating seed data..."
cd data || exit
python3 generate_seed_data.py
echo "✓ Seed data generated"
cd ..

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file..."
    cat > .env << EOL
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB_NAME=insurance_recommender

# Flask Configuration
FLASK_SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
FLASK_ENV=development
FLASK_PORT=5000

# Django Configuration
DJANGO_SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Flask Service URL (for Django)
FLASK_SERVICE_URL=http://localhost:5000
EOL
    echo "✓ .env file created"
fi

echo ""
echo "==================================="
echo "Setup complete!"
echo "==================================="
echo ""
echo "Next steps:"
echo "1. Start MongoDB:"
echo "   brew services start mongodb-community  # macOS"
echo "   sudo systemctl start mongod             # Linux"
echo ""
echo "2. Load seed data:"
echo "   cd scripts && python3 load_data.py"
echo ""
echo "3. Start Flask service:"
echo "   cd flask_service && source venv/bin/activate && python app.py"
echo ""
echo "4. Start Django app (in new terminal):"
echo "   cd django_app && source venv/bin/activate && python manage.py migrate && python manage.py runserver"
echo ""
echo "5. Access dashboard: http://localhost:8000"
echo ""

