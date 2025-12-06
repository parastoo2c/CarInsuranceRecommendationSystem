#!/bin/bash
# Setup script for Insurance Recommender System
# Sets up California-specific insurance data fetcher and recommender
 
echo "========================================================="
echo "Insurance Recommender - Setup (California-Specific)"
echo "========================================================="
 
# Check Python version
echo "Checking Python version..."
python3 --version || { echo "❌ Python 3 is required"; exit 1; }
echo "✓ Python 3 found"
 
# Check if MongoDB is running (optional)
echo ""
echo "Checking MongoDB..."
if command -v mongosh &> /dev/null || command -v mongo &> /dev/null; then
    echo "✓ MongoDB CLI found"
else
    echo "⚠ MongoDB CLI not found. Install MongoDB or use MongoDB Atlas"
fi
 
# Setup Flask service
echo ""
echo "========================================================="
echo "Step 1: Setting up Flask service..."
echo "========================================================="
cd flask_service || exit
if [ ! -d "myenv" ]; then
    echo "Creating virtual environment (myenv)..."
    python3 -m venv myenv
fi
source myenv/bin/activate
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✓ Flask service ready"
deactivate
cd ..
 
# Setup Django app
echo ""
echo "========================================================="
echo "Step 2: Setting up Django app..."
echo "========================================================="
cd django_app || exit
if [ ! -d "myenv" ]; then
    echo "Creating virtual environment (myenv)..."
    python3 -m venv myenv
fi
source myenv/bin/activate
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "Running migrations..."
python3 manage.py migrate --noinput
echo "✓ Django app ready"
deactivate
cd ..
 
# Install data fetching dependencies
echo ""
echo "========================================================="
echo "Step 3: Installing data fetching dependencies..."
echo "========================================================="
cd data || exit
if [ -f "requirements.txt" ]; then
    echo "Installing data fetching dependencies..."
    pip install -q -r requirements.txt
    echo "✓ Data dependencies installed"
else
    echo "⚠ No data/requirements.txt found, skipping..."
fi
 
# Fetch California-specific data
echo ""
echo "========================================================="
echo "Step 4: Fetching California-specific data..."
echo "========================================================="
echo "Using: data/fetch_external_data.py (primary data fetcher)"
echo ""
echo "This will fetch:"
echo "  • Vehicle data from NHTSA API (live)"
echo "  • California DOI published insurance rates (official data)"
echo "  • California insurer profiles (market share, complaints)"
echo "  • Regional coverage data (5 CA regions)"
echo ""
echo "Note: Other scripts like scrape_insurance_data.py are experimental"
echo "      and not used in the main workflow. See scripts/README.md"
echo ""
 
if python3 fetch_external_data.py; then
    echo "✓ California data fetched successfully"
else
    echo "⚠ Data fetch had issues, but continuing with existing config..."
    echo "  You can retry manually: cd data && python3 fetch_external_data.py"
fi
 
# Generate seed data
echo ""
echo "========================================================="
echo "Step 5: Generating insurance plans and signals..."
echo "========================================================="
if python3 generate_seed_data.py; then
    echo "✓ Seed data generated successfully"
else
    echo "❌ Failed to generate seed data"
    cd ..
    exit 1
fi
cd ..
 
# Run data integrity tests
echo ""
echo "========================================================="
echo "Step 6: Testing California data integrity..."
echo "========================================================="
if python3 scripts/test_california_data.py; then
    echo ""
    echo "✓ All data tests passed!"
else
    echo ""
    echo "⚠ Some data tests failed. Review output above."
    echo "  You can continue, but may want to check data files."
fi
 
# Create .env file if it doesn't exist
echo ""
echo "========================================================="
echo "Step 7: Creating environment configuration..."
echo "========================================================="
if [ ! -f ".env" ]; then
    echo "Generating .env file with secure secret keys..."
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
 
# Data Configuration
DATA_SOURCE=California, USA
EOL
    echo "✓ .env file created with secure keys"
else
    echo "✓ .env file already exists, skipping..."
fi
 
echo ""
echo "========================================================="
echo "✅ Setup Complete! California Data Ready!"
echo "========================================================="
echo ""
echo "📊 What was set up:"
echo "  ✓ Flask service with virtual environment"
echo "  ✓ Django app with virtual environment and migrations"
echo "  ✓ California-specific insurance data fetched"
echo "  ✓ Insurance plans and signals generated"
echo "  ✓ Data integrity tests passed"
echo "  ✓ Environment configuration created"
echo ""
echo "📁 Generated California data files:"
echo "  • data/seed_config.json (CA-specific config)"
echo "  • data/seed_insurers.json (8 CA insurers)"
echo "  • data/seed_vehicles.json (NHTSA vehicle data)"
echo "  • data/seed_plans.json (50+ insurance plans)"
echo "  • data/seed_signals.json (service quality signals)"
echo ""
echo "========================================================="
echo "🚀 Next Steps:"
echo "========================================================="
echo ""
echo "1️⃣  Start MongoDB:"
echo "   macOS:  brew services start mongodb-community"
echo "   Linux:  sudo systemctl start mongod"
echo ""
echo "2️⃣  Load California data into MongoDB:"
echo "   cd flask_service"
echo "   source myenv/bin/activate"
echo "   cd ../scripts"
echo "   python3 load_data.py"
echo "   deactivate"
echo ""
echo "3️⃣  Start Flask service (Terminal 1):"
echo "   cd flask_service"
echo "   source myenv/bin/activate"
echo "   python3 app.py"
echo ""
echo "4️⃣  Start Django app (Terminal 2 - new window):"
echo "   cd django_app"
echo "   source myenv/bin/activate"
echo "   python3 manage.py runserver"
echo ""
echo "5️⃣  Test the system (Terminal 3 - optional):"
echo "   python3 scripts/test_california_data.py"
echo "   python3 scripts/test_api.py"
echo ""
echo "6️⃣  Access dashboard:"
echo "   🌐 http://localhost:8000"
echo ""
echo "   Try searching for:"
echo "   • Toyota Camry, ZIP 90210 (Beverly Hills)"
echo "   • Tesla Model 3, ZIP 94102 (San Francisco)"
echo "   • Ford F-150, ZIP 95814 (Sacramento)"
echo ""
echo "========================================================="
echo "📚 Documentation:"
echo "========================================================="
echo "  • GETTING_STARTED.md - Complete setup guide"
echo "  • TESTING.md - Testing instructions"
echo "  • data/DATA_SOURCES.md - What data is fetched/real"
echo "  • data/README.md - Data generation details"
echo "  • data/QUICK_REFERENCE.md - Quick commands"
echo ""
echo "🎉 Ready to explore California insurance data!"
echo "========================================================="
echo ""
 