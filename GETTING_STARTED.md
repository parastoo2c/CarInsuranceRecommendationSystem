# Getting Started - Insurance Recommender System

This guide will help you set up and run the Multi-Criteria Insurance Recommender System (MCRS) on your local machine.

## Prerequisites

### Required Software

1. **Python 3.11+**
```bash
python3 --version # Should be 3.11 or higher
```

2. **MongoDB** (Choose one option)
 

**Option A: Local MongoDB (Recommended for development)**
```bash
# macOS
brew install mongodb-community
brew services start mongodb-community
 

# Linux (Ubuntu/Debian)
sudo apt install mongodb
sudo systemctl start mongod
```
 

**Option B: MongoDB Atlas (Cloud)**
- Sign up at [mongodb.com/atlas](https://www.mongodb.com/atlas)
- Create a free cluster
- Get connection string and update `.env`

3. **Git** (to clone the repository)

## Quick Setup (Automated)

The easiest way to get started is using our automated setup script:

```bash
# Navigate to the project directory
cd insurance-recommender

# 1. Generate .env file with secret keys
cd scripts
python3 generate_env.py
cd ..

# 2. Make setup script executable
chmod +x scripts/setup.sh

# 3. Run setup
./scripts/setup.sh
```

This will:
- Create `.env` file with secure secret keys
- Create virtual environments
- Install all dependencies
- Generate seed data

## Manual Setup

If you prefer manual setup or the automated script fails:

### 1. Setup Flask Service

```bash
cd flask_service

# Create virtual environment
python3 -m venv myenv
source myenv/bin/activate # On Windows: myenv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Deactivate
deactivate
```

### 2. Setup Django App

```bash
cd django_app

# Create virtual environment
python3 -m venv myenv
source myenv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python3 manage.py migrate

# Deactivate
deactivate
```

### 3. Generate Seed Data

```bash
cd data
python3 generate_seed_data.py
```

This creates:
- `seed_plans.json` - 50 insurance plans
- `seed_signals.json` - Service quality metrics

### 4. Configure Environment

**Option A: Auto-Generate (Easiest - Recommended)**

```bash
# Run the generator script
cd scripts
python3 generate_env.py
```

This creates a `.env` file with secure, randomly-generated secret keys automatically!

**Option B: Manual Configuration**

Create a `.env` file manually in the project root:

```bash
# MongoDB
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB_NAME=insurance_recommender

# Flask
FLASK_SECRET_KEY=your-secret-key-here
FLASK_ENV=development
FLASK_PORT=5000

# Django
DJANGO_SECRET_KEY=your-django-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
FLASK_SERVICE_URL=http://localhost:5000
```

To generate secret keys:
```bash
python3 -c 'import secrets; print(secrets.token_hex(32))'
```

## Loading Data

Load the seed data into MongoDB:

**Important:** This script needs to run from the Flask virtual environment (because it uses pymongo and flask_service modules).

```bash
# Activate Flask virtual environment
cd flask_service
source myenv/bin/activate

# Run the data loader
cd ../scripts
python3 load_data.py

# Deactivate when done
deactivate
```

Expected output:
```
Loading Seed Data into MongoDB
========================================
1. Loading insurers...
✓ Loaded 5 insurers
2. Loading vehicles...
✓ Loaded 7 vehicles
3. Loading insurance plans...
✓ Loaded 50 plans
4. Loading service quality signals...
✓ Loaded 50 signal records
```

**Note:** The script must run from Flask's myenv because it imports database modules from `flask_service/`.

## Running the Application

You need to run both Flask and Django services simultaneously in separate terminals.

### Terminal 1: Flask Service (API)

```bash
cd flask_service
source myenv/bin/activate
python3 app.py
```

Output:
```
* Running on http://127.0.0.1:5000
* Connected to MongoDB: insurance_recommender
```

### Terminal 2: Django App (Dashboard)

```bash
cd django_app
source myenv/bin/activate
python3 manage.py runserver
```

Output:
```
Starting development server at http://127.0.0.1:8000/
```

## Testing the System

### 1. Test Flask API

In a third terminal (requires Flask virtual environment for requests module):

```bash
# Activate Flask virtual environment
cd flask_service
source myenv/bin/activate

# Run the test script
cd ../scripts
python3 test_api.py

# Deactivate when done
deactivate
```

### 2. Access Web Dashboard

Open your browser and navigate to:
```
http://localhost:8000
```

### 3. Try a Sample Query

1. Click "Search"
2. Fill in the form:
- **Vehicle Make**: Toyota
- **Vehicle Model**: Camry
- **ZIP Code**: 90210
- **Year**: 2022
3. Click "Get Recommendations"

You should see Top 3 insurance plans ranked by multi-criteria scores!

## Installing Chrome Extension

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" (top right)
3. Click "Load unpacked"
4. Select the `chrome_extension` directory
5. Click the extension icon and try a search

## Docker Setup (Alternative)

If you prefer using Docker:

```bash
# Start all services
docker-compose up --build

# Access:
# - Django: http://localhost:8000
# - Flask: http://localhost:5000
# - MongoDB: localhost:27017
```

## Project Structure Overview

```
insurance-recommender/
├── flask_service/ # Recommendation API
│ ├── app.py # Main Flask app
│ ├── models/ # TOPSIS algorithm
│ ├── database.py # MongoDB connection
│ └── extraction/ # LLM data extraction
│
├── django_app/ # Web dashboard
│ ├── dashboard/ # Django project
│ ├── recommender/ # Main app
│ └── templates/ # HTML templates
│
├── chrome_extension/ # Browser extension
│ ├── manifest.json
│ ├── popup.html
│ └── popup.js
│
├── data/ # Seed data
├── scripts/ # Setup & utilities
└── docker-compose.yml # Docker configuration
```

## Troubleshooting

### MongoDB Connection Failed

**Problem**: `Failed to connect to MongoDB`

**Solution**:
```bash
# Check if MongoDB is running
brew services list | grep mongodb # macOS
sudo systemctl status mongod # Linux

# Start MongoDB
brew services start mongodb-community # macOS
sudo systemctl start mongod # Linux
```

### Port Already in Use

**Problem**: `Address already in use`

**Solution**:
```bash
# Find and kill process using the port
lsof -ti:5000 | xargs kill -9 # Flask
lsof -ti:8000 | xargs kill -9 # Django
```

### No Recommendations Found

**Problem**: Search returns no results

**Solution**:
1. Check if data is loaded: `python3 scripts/test_api.py`
2. Try a different vehicle/region combination
3. Verify MongoDB has data:
```bash
mongosh
use insurance_recommender
db.plans.countDocuments() # Should show 50
```

### Import Errors

**Problem**: `ModuleNotFoundError`

**Solution**:
```bash
# Make sure virtual environment is activated
source myenv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

## Next Steps

Now that your system is running:

1. **Explore the Dashboard**: Navigate through the search and results pages
2. **Customize Weights**: Try different preference weights in the search form
3. **Test Chrome Extension**: Quick recommendations from your browser
4. **Review the Code**: Understand the TOPSIS algorithm in `flask_service/models/topsis.py`
5. **Add More Data**: Generate additional plans in `data/generate_seed_data.py`

## Development Workflow

### Adding New Insurers

1. Edit `data/seed_insurers.json`
2. Run `python3 generate_seed_data.py`
3. Run `python3 scripts/load_data.py`

### Modifying Scoring Weights

Edit default weights in `flask_service/config.py`:
```python
DEFAULT_WEIGHTS = {
'cost': 0.30,
'coverage': 0.25,
'service': 0.25,
'reliability': 0.20
}
```

### Testing Changes

```bash
# Test Flask API
python3 scripts/test_api.py

# Test Django views
cd django_app
python3 manage.py test
```

## Resources

- **Project Proposal**: See `Parastoo - Project Proposal Draft.md`
- **API Documentation**: Check Flask `/api/` endpoints
- **TOPSIS Algorithm**: Read `flask_service/models/topsis.py`
- **MongoDB Queries**: See `flask_service/database.py`

## Getting Help

If you encounter issues:

1. Check this guide's Troubleshooting section
2. Review error messages in terminal logs
3. Verify all prerequisites are installed
4. Check MongoDB is running and accessible

## Complete Setup Checklist

After following this guide, you should have:

- ✅ Python 3.11+ installed
- ✅ MongoDB running (local or Atlas)
- ✅ `.env` file with secret keys (via `generate_env.py`)
- ✅ Virtual environments created for Flask and Django
- ✅ All dependencies installed
- ✅ Seed data generated and loaded into MongoDB
- ✅ Flask API running on port 5000
- ✅ Django dashboard on port 8000
- ✅ Chrome extension loaded (optional)
- ✅ Successful test query returning recommendations

## Quick Start Commands (After Setup)

```bash
# Terminal 1 - Flask Service
cd insurance-recommender/flask_service
source myenv/bin/activate
python3 app.py

# Terminal 2 - Django App (new terminal window)
cd insurance-recommender/django_app
source myenv/bin/activate
python3 manage.py runserver

# Browser
# Open: http://localhost:8000
```
