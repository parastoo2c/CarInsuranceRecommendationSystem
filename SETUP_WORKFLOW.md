# Setup Workflow - Complete Visual Guide

Visual guide explaining what happens when you run `setup.sh` and the complete data flow.

## 📋 Table of Contents

- [Quick Answer](#quick-answer)
- [Complete Workflow Diagram](#complete-workflow-diagram)
- [What setup.sh Does](#what-setupsh-does)
- [What Gets Created](#what-gets-created)
- [Data Pipeline Explained](#data-pipeline-explained)
- [Step-by-Step Breakdown](#step-by-step-breakdown)
- [When to Rerun What](#when-to-rerun-what)

---

## Quick Answer

**Q: Does setup.sh do everything?**
**A: NO** - It does setup and data generation, but NOT database loading.

**What you need to do:**
1. Run `setup.sh` (once)
2. Start MongoDB
3. Run `load_data.py` (once)
4. Start services (every time)

---

## Complete Workflow Diagram

```
┌──────────────────────────────────────────────────────────────────────────┐
│ COMPLETE WORKFLOW │
└──────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ Step 1: Run ./scripts/setup.sh (AUTOMATIC - Run Once) │
├─────────────────────────────────────────────────────────────────────────┤
│ │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ 1.1 Create Virtual Environments │ │
│ │ • flask_service/myenv/ │ │
│ │ • django_app/myenv/ │ │
│ └──────────────────────────────────────────────────────────┘ │
│ ↓ │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ 1.2 Install Dependencies │ │
│ │ • Flask, Django, PyMongo, etc. │ │
│ └──────────────────────────────────────────────────────────┘ │
│ ↓ │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ 1.3 Fetch California Data (from Internet!) │ │
│ │ • data/fetch_external_data.py │ │
│ │ • Calls NHTSA API for vehicle data │ │
│ │ • Generates CA DOI rate configuration │ │
│ └──────────────────────────────────────────────────────────┘ │
│ ↓ │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ 1.4 Generate Plans & Signals │ │
│ │ • data/generate_seed_data.py │ │
│ │ • Creates 120+ insurance plans │ │
│ │ • Creates 300+ quality signals │ │
│ └──────────────────────────────────────────────────────────┘ │
│ ↓ │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ 1.5 Test Data Integrity │ │
│ │ • scripts/test_california_data.py │ │
│ │ • Validates all generated data │ │
│ └──────────────────────────────────────────────────────────┘ │
│ ↓ │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ 1.6 Create .env File │ │
│ │ • scripts/generate_env.py │ │
│ │ • Generates secure secret keys │ │
│ └──────────────────────────────────────────────────────────┘ │
│ │
│ ✅ OUTPUT: 5 JSON files created in data/ directory │
│ • seed_config.json │
│ • seed_insurers.json │
│ • seed_vehicles.json (⭐ from NHTSA API!) │
│ • seed_plans.json │
│ • seed_signals.json │
│ │
│ ⚠️ Data files exist but NOT in MongoDB yet! │
└─────────────────────────────────────────────────────────────────────────┘
↓
┌─────────────────────────────────────────────────────────────────────────┐
│ Step 2: Start MongoDB (MANUAL STEP - Required) │
├─────────────────────────────────────────────────────────────────────────┤
│ │
│ $ brew services start mongodb-community # macOS │
│ $ sudo systemctl start mongod # Linux │
│ │
│ ✅ MongoDB running on localhost:27017 │
└─────────────────────────────────────────────────────────────────────────┘
↓
┌─────────────────────────────────────────────────────────────────────────┐
│ Step 3: Load Data into MongoDB (MANUAL STEP - Run Once) │
├─────────────────────────────────────────────────────────────────────────┤
│ │
│ $ cd flask_service && source myenv/bin/activate │
│ $ cd ../scripts && python3 load_data.py │
│ │
│ What happens: │
│ 1. Reads seed_insurers.json → Creates insurers collection │
│ 2. Reads seed_vehicles.json → Creates vehicles collection │
│ 3. Reads seed_plans.json → Creates plans collection │
│ 4. Reads seed_signals.json → Creates signals collection │
│ 5. Maps relationships (insurer_id, plan_id) │
│ │
│ ✅ OUTPUT: Data now in MongoDB database │
│ • insurance_recommender.insurers (20 records) │
│ • insurance_recommender.vehicles (150+ records) │
│ • insurance_recommender.plans (120+ records) │
│ • insurance_recommender.signals (300+ records) │
└─────────────────────────────────────────────────────────────────────────┘
↓
┌─────────────────────────────────────────────────────────────────────────┐
│ Step 4: Start Services (MANUAL STEP - Every Time) │
├─────────────────────────────────────────────────────────────────────────┤
│ │
│ Terminal 1: Flask API │
│ $ cd flask_service && source myenv/bin/activate && python3 app.py │
│ ✅ Flask running at http://localhost:5000 │
│ │
│ Terminal 2: Django Dashboard │
│ $ cd django_app && source myenv/bin/activate │
│ $ python3 manage.py runserver │
│ ✅ Django running at http://localhost:8000 │
│ │
└─────────────────────────────────────────────────────────────────────────┘
↓
┌─────────────────────────────────────────────────────────────────────────┐
│ Step 5: Access Application 🎉 │
├─────────────────────────────────────────────────────────────────────────┤
│ │
│ Open browser: http://localhost:8000 │
│ Search for insurance plans and get recommendations! │
│ │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## What setup.sh Does

### Detailed Breakdown

| Step | What Happens | Output | Duration |
|------|-------------|---------|----------|
| 1 | Creates Flask venv | `flask_service/myenv/` | 30s |
| 2 | Creates Django venv | `django_app/myenv/` | 30s |
| 3 | Installs dependencies | Packages installed | 2-3 min |
| 4 | Fetches CA data | `fetch_external_data.py` runs | 30-60s |
| 5 | Generates plans/signals | `generate_seed_data.py` runs | 5s |
| 6 | Tests data | `test_california_data.py` runs | 3s |
| 7 | Creates .env | `.env` file created | 1s |

**Result:** ✅ Data files exist in `data/` directory, but NOT in MongoDB yet!

### What You Still Need to Do

| Step | Why Manual? | Command |
|------|-------------|---------|
| 1. Start MongoDB | May not be installed yet | `brew services start mongodb-community` |
| 2. Load data | Requires MongoDB running | `python3 scripts/load_data.py` |
| 3. Start Flask | Runtime service | `python3 app.py` |
| 4. Start Django | Runtime service | `python3 manage.py runserver` |

---

## What Gets Created

### File System Changes

```
insurance-recommender/
├── flask_service/
│ └── myenv/ ← Created by setup.sh
│ └── (Python packages)
├── django_app/
│ └── myenv/ ← Created by setup.sh
│ └── (Python packages)
├── data/
│ ├── seed_config.json ← Created by setup.sh ✨
│ ├── seed_insurers.json ← Created by setup.sh ✨
│ ├── seed_vehicles.json ← Created by setup.sh ✨ (from internet!)
│ ├── seed_plans.json ← Created by setup.sh ✨
│ └── seed_signals.json ← Created by setup.sh ✨
└── .env ← Created by setup.sh
```

### MongoDB Changes (After load_data.py)

```
MongoDB: insurance_recommender
├── insurers (collection)
│ └── 20 documents (California insurers)
├── vehicles (collection)
│ └── 150+ documents (NHTSA vehicle data)
├── plans (collection)
│ └── 120+ documents (Insurance plans)
└── signals (collection)
└── 300+ documents (Service quality metrics)
```

---

## Data Pipeline Explained

### The Three-Step Data Process

```
┌──────────────────────────────────────────────────────────────────────┐
│ DATA PIPELINE FLOW │
└──────────────────────────────────────────────────────────────────────┘

Internet (NHTSA API)
↓
╔═══════════════════════════════════════════════════════════════════╗
║ Step 1: fetch_external_data.py ║
║ ─────────────────────────────────────────────────────────────────║
║ • Calls NHTSA API: GET /vehicles/GetModelsForMakeYear ║
║ • Generates California DOI rate configuration ║
║ • Creates insurer profiles (State Farm, Geico, etc.) ║
║ ║
║ Input: Internet APIs + Published CA DOI data ║
║ Output: JSON files ║
╚═══════════════════════════════════════════════════════════════════╝
↓
Creates 3 JSON files:
• seed_config.json (CA configuration: rates, regions, profiles)
• seed_insurers.json (8 California insurers + market share)
• seed_vehicles.json (150+ vehicles from NHTSA API) ⭐
↓
╔═══════════════════════════════════════════════════════════════════╗
║ Step 2: generate_seed_data.py ║
║ ─────────────────────────────────────────────────────────────────║
║ • Reads seed_config.json ║
║ • Reads seed_insurers.json ║
║ • Reads seed_vehicles.json ║
║ • Generates 120+ insurance plans (combinations) ║
║ • Generates 300+ quality signals ║
║ ║
║ Input: 3 JSON files from Step 1 ║
║ Output: 2 more JSON files ║
╚═══════════════════════════════════════════════════════════════════╝
↓
Creates 2 more JSON files:
• seed_plans.json (120+ insurance plans for all combos)
• seed_signals.json (300+ service quality signals)
↓
⚠️ ALL 5 JSON FILES NOW EXIST IN data/
⚠️ BUT NOT IN MONGODB YET!
↓
╔═══════════════════════════════════════════════════════════════════╗
║ Step 3: load_data.py ║
║ ─────────────────────────────────────────────────────────────────║
║ • Opens seed_insurers.json → db.insurers.insert_many() ║
║ • Opens seed_vehicles.json → db.vehicles.insert_many() ║
║ • Opens seed_plans.json → db.plans.insert_many() ║
║ • Opens seed_signals.json → db.signals.insert_many() ║
║ • Maps relationships (insurer names → IDs, plan IDs → ObjectIDs) ║
║ ║
║ Input: 5 JSON files ║
║ Output: MongoDB collections ║
╚═══════════════════════════════════════════════════════════════════╝
↓
DATA NOW IN MONGODB
✅ Flask can query it!
✅ Application ready to use!
```

### Why Three Steps?

**Step 1 & 2 (Data Generation):**
- Can run without MongoDB
- Creates reusable JSON files
- Can be version controlled
- Easy to inspect and validate

**Step 3 (Data Loading):**
- Requires MongoDB running
- Can fail independently
- Can reload without regenerating
- Can load into different DB instances

---

## Step-by-Step Breakdown

### 1. fetch_external_data.py - What It Really Does

```python
# Pseudocode showing what happens

# 1. Fetch vehicle data from NHTSA (REAL API CALL!)
vehicles = requests.get("https://vpic.nhtsa.dot.gov/api/vehicles/...")
# Returns: Toyota Camry, Honda Accord, Tesla Model 3, etc.

# 2. Generate California insurance configuration
config = {
"premium_ranges": {
"Sedan": [1860, 3472], # Based on CA DOI published rates
"SUV": [2232, 3720],
"Electric": [2728, 4340]
},
"california_regions": {
"CA-N": "Northern California",
"CA-BAY": "San Francisco Bay Area",
# ...
}
}

# 3. Create California insurer profiles
insurers = [
{
"name": "State Farm",
"market_share_pct": 15.2, # Real CA DOI data
"service_score": 0.78, # Based on J.D. Power ratings
# ...
},
# ... 7 more insurers
]

# 4. Save to JSON files
save_json("seed_config.json", config)
save_json("seed_insurers.json", insurers)
save_json("seed_vehicles.json", vehicles)

# Does NOT touch MongoDB!
```

**Runtime:** 30-60 seconds
**Internet Required:** Yes (for NHTSA API)
**Output:** 3 JSON files

---

### 2. generate_seed_data.py - What It Really Does

```python
# Pseudocode showing what happens

# 1. Load configuration
config = load_json("seed_config.json")
insurers = load_json("seed_insurers.json")
vehicles = load_json("seed_vehicles.json")

# 2. Generate all possible plan combinations
plans = []
for insurer in insurers:
for vehicle_type in ["Sedan", "SUV", "Truck", "Electric"]:
for tier in ["Basic", "Standard", "Premium", "Elite"]:
for region in ["CA-N", "CA-S", "CA-BAY", "CA-SD", "CA-C"]:
plan = create_plan(
insurer=insurer,
vehicle_type=vehicle_type,
tier=tier,
region=region,
premium=calculate_premium(vehicle_type, tier, region)
)
plans.append(plan)

# Result: 120+ insurance plans

# 3. Generate quality signals for each plan
signals = []
for plan in plans:
signal = {
"plan_id": plan["plan_id"],
"claim_tat_days": random_realistic_value(20, 35),
"claim_approval_rate_pct": random_realistic_value(85, 95),
"csat_score": random_realistic_value(3.5, 4.5),
# ...
}
signals.append(signal)

# Result: 300+ quality signals

# 4. Save to JSON files
save_json("seed_plans.json", plans)
save_json("seed_signals.json", signals)

# Does NOT touch MongoDB!
```

**Runtime:** 2-5 seconds
**Internet Required:** No
**Output:** 2 JSON files

---

### 3. load_data.py - What It Really Does

```python
# Pseudocode showing what happens

# 1. Connect to MongoDB
db = MongoClient("mongodb://localhost:27017/").insurance_recommender

# 2. Load insurers
insurers = load_json("seed_insurers.json")
db.insurers.insert_many(insurers)
# Result: 20 documents in insurers collection

# 3. Load vehicles
vehicles = load_json("seed_vehicles.json")
db.vehicles.insert_many(vehicles)
# Result: 150+ documents in vehicles collection

# 4. Load plans (with insurer_id mapping)
plans = load_json("seed_plans.json")

# Map insurer names to MongoDB ObjectIDs
insurer_map = {}
for insurer in db.insurers.find():
insurer_map[insurer["name"]] = insurer["_id"]

# Update plans with proper insurer_id
for plan in plans:
plan["insurer_id"] = insurer_map[plan["insurer_name"]]

db.plans.insert_many(plans)
# Result: 120+ documents in plans collection

# 5. Load signals (with plan_id mapping)
signals = load_json("seed_signals.json")

# Map plan_ids to MongoDB ObjectIDs
plan_map = {}
for plan in db.plans.find():
plan_map[plan["plan_id"]] = plan["_id"]

# Update signals with proper plan_id
for signal in signals:
signal["plan_id"] = plan_map[signal["plan_id"]]

db.signals.insert_many(signals)
# Result: 300+ documents in signals collection

# NOW data is in MongoDB!
```

---

## When to Rerun What

### Scenario-Based Guide

| Scenario | What to Rerun | Why |
|----------|---------------|-----|
| **Fresh install** | Everything | Need complete setup |
| **Refresh California data** | `fetch_external_data.py` → `generate_seed_data.py` → `load_data.py` | Get latest NHTSA vehicles |
| **MongoDB data corrupted** | Just `load_data.py` | JSON files still good |
| **Changed code** | Nothing (just restart services) | Data unchanged |
| **New virtual env needed** | Just `setup.sh` | Environment only |
| **Added new insurer** | `generate_seed_data.py` → `load_data.py` | Regenerate plans |
| **Changed premium ranges** | `generate_seed_data.py` → `load_data.py` | Recalculate plans |

### Command Reference

**Full Refresh (Get latest data):**
```bash
cd data
python3 fetch_external_data.py # ~60s
python3 generate_seed_data.py # ~5s
cd ../flask_service && source myenv/bin/activate
cd ../scripts && python3 load_data.py # ~10s
```

**Quick Reload (Use existing config):**
```bash
cd data
python3 generate_seed_data.py # ~5s
cd ../flask_service && source myenv/bin/activate
cd ../scripts && python3 load_data.py # ~10s
```

**Just Reload (MongoDB reset):**
```bash
cd flask_service && source myenv/bin/activate
cd ../scripts && python3 load_data.py # ~10s
```

---

## Verification Checklist

### After Running setup.sh

```bash
# Check data files exist
ls -lh data/seed_*.json
# Should show 5 files:
# seed_config.json, seed_insurers.json, seed_vehicles.json,
# seed_plans.json, seed_signals.json

# Count records in JSON files
python3 -c "
import json
print('Insurers:', len(json.load(open('data/seed_insurers.json'))))
print('Vehicles:', len(json.load(open('data/seed_vehicles.json'))))
print('Plans:', len(json.load(open('data/seed_plans.json'))))
print('Signals:', len(json.load(open('data/seed_signals.json'))))
"
```

### After Running load_data.py

```bash
# Check MongoDB collections
mongosh insurance_recommender --eval "
print('Insurers:', db.insurers.countDocuments());
print('Vehicles:', db.vehicles.countDocuments());
print('Plans:', db.plans.countDocuments());
print('Signals:', db.signals.countDocuments());
"
```

---

## Common Confusion Points

### ❓ "I ran setup.sh, why is the database empty?"

**Answer:** `setup.sh` only creates JSON files. You need to run `load_data.py` to put them in MongoDB.

```
setup.sh → Creates JSON files
load_data.py → Loads JSON files into MongoDB
```

### ❓ "Can I skip load_data.py?"

**Answer:** NO - The application reads from MongoDB, not JSON files. You must load the data.

### ❓ "Why can't setup.sh just do it all?"

**Answer:** Because MongoDB needs to be running first, and `setup.sh` can't assume it's installed or started.

### ❓ "Do I need to run load_data.py every time?"

**Answer:** NO - Only once after setup, or when you want to refresh the data.

### ❓ "What if I want to update just the premiums?"

**Answer:** Edit `seed_config.json`, run `generate_seed_data.py`, then `load_data.py`.

---

## 📚 Related Documentation

- **[README.md](README.md)** - Project overview
- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Quick setup guide
- **[IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)** - Implementation details & testing
- **[data/README.md](data/README.md)** - Data generation details
- **[scripts/README.md](scripts/README.md)** - Scripts documentation