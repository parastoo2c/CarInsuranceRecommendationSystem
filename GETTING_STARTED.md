# Getting Started - Insurance Recommender System

This guide will help you set up and run the Multi-Criteria Insurance Recommender System (MCRS) on your local machine.

## Prerequisites

### Required Software

1. **Python 3.11+**
```bash
python3 --version # Should be 3.11 or higher
```

2. **MongoDB**
 

```bash
# macOS
brew install mongodb-community
brew services start mongodb-community
 

# Linux (Ubuntu/Debian)
sudo apt install mongodb
sudo systemctl start mongod
```

3. **Git** (to clone the repository)

## Quick Setup (Automated)

The easiest way to get started is using our automated setup script:

```bash
# Navigate to the project directory
cd insurance-recommender

# 1. Make setup script executable
chmod +x scripts/setup.sh

# 2. Run setup
./scripts/setup.sh
```

### What This Does:

This will:
- ✅ Create virtual environments (Flask + Django)
- ✅ Install all dependencies
- ✅ **Fetch vehicle data from NHTSA API** (real internet call!)
- ✅ Generate California insurance config (based on CA DOI published data)
- ✅ Create 50+ insurance plans and signals
- ✅ Test data integrity
- ✅ Create `.env` file with secure secret keys

### 📁 Files Created:

After running, you'll see these new files in `data/`:
- `seed_config.json` - California configuration
- `seed_insurers.json` - 8 CA insurers (State Farm, Geico, etc.)
- `seed_vehicles.json` - ⭐ Vehicle data from NHTSA API (fetched from internet)
- `seed_plans.json` - 50+ insurance plans
- `seed_signals.json` - Service quality metrics

**⚠️ NEXT STEP REQUIRED:** These files are created, but you still need to:
1. Start MongoDB
2. Run `load_data.py` to load them into the database

**Want details?** → See `WHAT_GETS_CREATED.md` for complete breakdown of what gets generated and where

### When to Run Data Fetcher Manually?

**⚠️ You DON'T need to run this if you already ran `./scripts/setup.sh`**

The automated setup already does this! Only run manually if:
- ❌ You skipped the automated setup
- 🔄 You want to refresh/update the California data
- 🐛 The automated setup failed at the data step

```bash
# Navigate to data directory
cd insurance-recommender/data

# Fetch California-specific data from external sources (NHTSA API, etc.)
# (requests library is in flask_service/requirements.txt)
python3 fetch_external_data.py

# Generate plans and signals using the fetched data
python3 generate_seed_data.py
```

**What it does:**
1. `fetch_external_data.py` - Fetches real vehicle data from NHTSA, generates California insurance rates, creates insurer profiles
2. `generate_seed_data.py` - Uses the configuration to generate 50+ insurance plans and quality signals

**Output files:**
- `seed_config.json` - California configuration
- `seed_insurers.json` - 8 California insurers
- `seed_vehicles.json` - Vehicle data from NHTSA
- `seed_plans.json` - Generated insurance plans
- `seed_signals.json` - Service quality metrics

**💡 Tip:** Check if files already exist: `ls -lh data/seed_*.json`

## Manual Setup

**⚠️ IMPORTANT: Did you already run `./scripts/setup.sh`?**

```
┌─────────────────────────────────────┐
│ Did you run ./scripts/setup.sh? │
└──────────┬──────────────────────────┘
│
┌──────┴──────┐
│ │
YES NO
│ │
│ └──> Follow Manual Setup below
│
└──> SKIP to "Loading Data" section
(Data files already created!)
```

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

### 3. Generate Seed Data (California-Specific)

**⚠️ IMPORTANT:** If you already ran `./scripts/setup.sh`, **SKIP THIS STEP** - the data is already generated!

The system fetches real-world data from external sources for California market.

**Step 3a: Fetch California Data from Internet** (Only if you didn't run setup.sh)

```bash
cd data

# Fetch California-specific data from external sources
python3 fetch_external_data.py
```

This fetches and creates:
- `seed_config.json` - California-specific configuration (premium ranges, insurer profiles)
- `seed_vehicles.json` - Real vehicle data from NHTSA API
- `seed_insurers.json` - Top 8 California insurers by market share

**Step 3b: Generate Plans and Signals** (Only if you didn't run setup.sh)

```bash
# Generate insurance plans and quality signals
python3 generate_seed_data.py
```

This creates:
- `seed_plans.json` - 50+ insurance plans (California-adjusted rates)
- `seed_signals.json` - Service quality metrics

**Notes:**
- ✅ **Already ran setup.sh?** These files already exist - skip to step 4!
- ⚠️ If you can't access external APIs, you can skip Step 3a and run only `generate_seed_data.py`
- 🔄 **Want to refresh data?** Only then rerun these commands

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

**📍 You are here if:**
- ✅ You ran `./scripts/setup.sh` (automated setup)
- ✅ OR you completed Manual Setup steps 1-3 above

**⚠️ IMPORTANT: This step is REQUIRED - setup.sh does NOT do this!**

### Why This is Separate:
- `setup.sh` creates the JSON data files
- This step loads those files into MongoDB
- Requires MongoDB to be running first

### Before You Start:
```bash
# 1. Make sure MongoDB is running
brew services list | grep mongodb # macOS - check status
brew services start mongodb-community # macOS - start if needed
```

### Load the Data:

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

**Note:** The script must run from Flask's myenv because it imports database modules from `flask_service/`.

### About the Data

The system now uses **California-specific data**:
- Premium rates are ~24% higher than national average (based on CA Dept of Insurance)
- Insurers include California market leaders: State Farm, Geico, Progressive, Allstate, USAA, Farmers, Mercury Insurance, AAA
- Vehicle data fetched from NHTSA API
- Regional coverage for 5 California regions (Northern, Central, Southern, Bay Area, San Diego)

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

**📋 Testing Order:**
```
1. Test Data Generation ← Test JSON files exist
2. Test Flask API ← Test API endpoints
3. Manual Integration ← Test complete workflow
```

### 1. Test Data Generation (California Data)

#### Quick Test: Run Comprehensive Test Suite

First, run the automated California data test suite:

```bash
cd scripts
python3 test_california_data.py
```

This comprehensive test checks:
- ✓ All required files exist
- ✓ JSON files are valid
- ✓ Configuration has California-specific settings
- ✓ Premium ranges are realistic
- ✓ California insurers are present
- ✓ All 5 California regions have coverage
- ✓ Vehicle data is complete
- ✓ Plans and signals are properly generated

### 2. Test Flask API

Test the Flask API endpoints with California-specific queries:

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

### 3. Manual Integration Testing

#### Test Case 1: California Sedan Search

```bash
# Make sure both Flask and Django are running
# Flask: http://localhost:5000
# Django: http://localhost:8000
```

1. Open browser: `http://localhost:8000`
2. Click "Search"
3. Fill in the form:
- **Vehicle Make**: Toyota
- **Vehicle Model**: Camry
- **ZIP Code**: 90210 (Beverly Hills, CA - Southern California)
- **Year**: 2023
- **Coverage Preference**: Standard
4. Click "Get Recommendations"

**Expected Results:**
- Top 3 insurance plans displayed
- Plans from California insurers (State Farm, Geico, Progressive, etc.)
- Premium ranges: $1,860 - $3,472 (Sedan range)
- Regional codes include "CA-S" (Southern California)
- Service quality signals displayed

#### Test Case 2: Bay Area Electric Vehicle

1. Fill in the form:
- **Vehicle Make**: Tesla
- **Vehicle Model**: Model 3
- **ZIP Code**: 94102 (San Francisco - Bay Area)
- **Year**: 2024
2. Click "Get Recommendations"

**Expected Results:**
- Higher premiums: $2,728 - $4,340 (Electric range)
- Regional codes include "CA-BAY"
- Plans specific to electric vehicles

#### Test Case 3: Northern California Truck

1. Fill in the form:
- **Vehicle Make**: Ford
- **Vehicle Model**: F-150
- **ZIP Code**: 95814 (Sacramento - Northern California)
- **Year**: 2023
2. Click "Get Recommendations"

**Expected Results:**
- Truck premiums: $2,356 - $3,968
- Regional codes include "CA-N"

## Testing Checklist

After testing, verify California-specific data:

### Data Files
- ✅ All 5 seed files created (config, insurers, vehicles, plans, signals)
- ✅ `seed_config.json` has `data_source: "California, USA"`
- ✅ `seed_insurers.json` has 8 California insurers with market share
- ✅ `seed_vehicles.json` has vehicle data from NHTSA
- ✅ Data generation tests passed

### API & Application
- ✅ Django app loads without errors
- ✅ Search form accepts California ZIP codes (90210, 94102, 95814, etc.)
- ✅ Recommendations return California insurers (State Farm, Geico, etc.)
- ✅ Premium ranges match California DOI data:
- Sedan: $1,860 - $3,472
- SUV: $2,232 - $3,720
- Truck: $2,356 - $3,968
- Electric: $2,728 - $4,340
- ✅ Service quality signals are displayed
- ✅ Different vehicle types return appropriate premiums
- ✅ Market share data visible in results

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
├── data/ # Seed data (California-specific)
│ ├── fetch_external_data.py # Fetch real-world CA data
│ ├── generate_seed_data.py # Generate plans & signals
│ ├── seed_config.json # CA configuration
│ ├── seed_insurers.json # CA insurers
│ ├── seed_vehicles.json # NHTSA vehicle data
│ ├── seed_plans.json # Generated plans
│ └── seed_signals.json # Generated signals
│
└── scripts/ # Setup & utilities
```

## Troubleshooting

### MongoDB Connection Failed

**Problem**: `Failed to connect to MongoDB`

**Solution**:
```bash
# Check if MongoDB is running
brew services list | grep mongodb # macOS

# Start MongoDB
brew services start mongodb-community # macOS
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

### Data Fetching Failed

**Problem**: `fetch_external_data.py` fails to fetch data from NHTSA API

**Solution**:
```bash
# Option 1: Check internet connection and try again
python3 fetch_external_data.py

# Option 2: Use existing configuration (skip fetching)
python3 generate_seed_data.py # Uses current seed_config.json

# Option 3: Install/update requests library
pip install --upgrade requests
```

**Note**: If external APIs are unavailable, the system will use the existing `seed_config.json` configuration.

## California-Specific Data Features

The system uses real-world California market data:

### Data Sources
- **NHTSA API**: Vehicle specifications and models
- **California Department of Insurance**: Premium averages, complaint ratios
- **Market Research**: Regional pricing and insurer market share

### California Adjustments
- **Premium Rates**: ~24% higher than national average
- **Regional Coverage**: 5 California regions
- CA-N: Northern California
- CA-C: Central California
- CA-S: Southern California
- CA-BAY: San Francisco Bay Area
- CA-SD: San Diego Area
- **Top Insurers**: State Farm (15.2%), Geico (12.8%), Progressive (11.5%), and more
- **Vehicle Values**: 10-15% higher for California market demand

### Refreshing Data

To update with latest California market data:

```bash
cd data
python3 fetch_external_data.py # Fetch fresh data
python3 generate_seed_data.py # Regenerate plans
cd ../flask_service && source myenv/bin/activate
cd ../scripts && python3 load_data.py # Reload to DB
```

## Resources

### Documentation
- **Getting Started**: This file - Complete setup guide
- **Setup Workflow**: See `SETUP_WORKFLOW.md` - Complete workflow with visual flowcharts
- **Implementation Guide**: See `IMPLEMENTATION_GUIDE.md` - TOPSIS algorithm, API docs, extending the system
- **Data Documentation**: See `data/README.md` - California data sources and generation details
- **Scripts Guide**: See `scripts/README.md` - Scripts documentation and troubleshooting

### Code References
- **API Documentation**: Check Flask `/api/` endpoints
- **TOPSIS Algorithm**: Read `flask_service/models/topsis.py`
- **MongoDB Queries**: See `flask_service/database.py`
- **Data Fetcher**: See `data/fetch_external_data.py`
- **Data Generator**: See `data/generate_seed_data.py`

### Testing
- **California Data Tests**: See `scripts/test_california_data.py`
- **API Tests**: See `scripts/test_api.py`
- **Django Tests**: See `django_app/recommender/tests.py`
- **Full Testing Guide**: See `TESTING.md`

## Complete Setup Checklist

After following this guide, you should have:

- ✅ Python 3.11+ installed
- ✅ MongoDB running (local or Atlas)
- ✅ `.env` file with secret keys (via `generate_env.py`)
- ✅ Virtual environments created for Flask and Django
- ✅ All dependencies installed
- ✅ California-specific data fetched from external sources (via `fetch_external_data.py`)
- ✅ Seed data generated with California rates (via `generate_seed_data.py`)
- ✅ Data loaded into MongoDB
- ✅ Flask API running on port 5000
- ✅ Django dashboard on port 8000
- ✅ Successful test query returning California-based recommendations

## Quick Start Commands (After Setup)

### Complete Workflow (In Order!)

```bash
# ============================================================
# Step 1: Run Setup (ONE TIME)
# ============================================================
cd insurance-recommender
./scripts/setup.sh
# ✅ This creates data files but does NOT load into MongoDB

# ============================================================
# Step 2: Start MongoDB (REQUIRED)
# ============================================================
brew services start mongodb-community # macOS
# OR
sudo systemctl start mongod # Linux

# ============================================================
# Step 3: Load Data into MongoDB (REQUIRED - ONE TIME)
# ============================================================
cd insurance-recommender/flask_service
source myenv/bin/activate
cd ../scripts
python3 load_data.py
deactivate
# ✅ Now data is in MongoDB

# ============================================================
# Step 4: Verify Data (Optional but Recommended)
# ============================================================
cd insurance-recommender/flask_service
source myenv/bin/activate
cd ..
python3 scripts/verify_mongodb_data.py
deactivate

# ============================================================
# Step 5: Start Services (Every Time)
# ============================================================

# Terminal 1 - Flask Service
cd insurance-recommender/flask_service
source myenv/bin/activate
python3 app.py

# Terminal 2 - Django App (new terminal window)
cd insurance-recommender/django_app
source myenv/bin/activate
python3 manage.py runserver

# ============================================================
# Step 6: Access Application
# ============================================================
# Browser: http://localhost:8000
```

**Ready to explore!** 🚀