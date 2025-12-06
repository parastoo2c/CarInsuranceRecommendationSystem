# Implementation Guide - California Insurance Recommender

Technical details for developers extending or understanding the system implementation.

## 📋 Table of Contents

- [TOPSIS Algorithm](#topsis-algorithm)
- [Database Schema](#database-schema)
- [API Endpoints](#api-endpoints)
- [Extending the System](#extending-the-system)
- [Code Architecture](#code-architecture)

---

## TOPSIS Algorithm

The system uses TOPSIS (Technique for Order Preference by Similarity to Ideal Solution) for multi-criteria decision making.

**Location:** `flask_service/models/topsis.py`

### How It Works

1. **Normalize Criteria:**
```python
# Convert all criteria to comparable scale (0-1)
normalized_matrix = normalize(decision_matrix)
```

2. **Apply Weights:**
```python
# Apply user preferences
weighted_matrix = normalized_matrix * weights
# weights = {cost: 0.30, coverage: 0.25, service: 0.25, reliability: 0.20}
```

3. **Calculate Ideal Solutions:**
```python
# Best possible values (ideal solution)
ideal_best = max(each_criterion)
 

# Worst possible values (anti-ideal solution)
ideal_worst = min(each_criterion)
```

4. **Calculate Distances:**
```python
# Distance from ideal
distance_best = euclidean_distance(option, ideal_best)
 

# Distance from anti-ideal
distance_worst = euclidean_distance(option, anti_ideal)
```

5. **Calculate Scores:**
```python
# Closeness coefficient (0-1, higher is better)
score = distance_worst / (distance_best + distance_worst)
```

### Criteria Used

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Cost | 30% | Premium affordability |
| Coverage | 25% | Coverage comprehensiveness |
| Service | 25% | Customer service quality |
| Reliability | 20% | Claims processing reliability |

**Users can customize weights in the search form.**

---

## Database Schema

### MongoDB Collections

#### 1. Insurers Collection
```javascript
{
_id: ObjectId("..."),
name: "State Farm",
region_codes: ["CA-N", "CA-S", "CA-BAY", "CA-SD", "CA-C"],
regional_coverage: ["Bay Area", "Los Angeles", "San Diego", ...],
website: "https://www.statefarm.com",
phone: "1-800-782-8332",
description: "America's largest auto insurer...",
market_share_pct: 15.2,
service_score: 0.78,
reliability_score: 0.82
}
```

#### 2. Vehicles Collection
```javascript
{
_id: ObjectId("..."),
make: "Toyota",
model: "Camry",
year: 2024,
vehicle_type: "Passenger Car",
category: "Sedan"
}
```

#### 3. Plans Collection
```javascript
{
_id: ObjectId("..."),
plan_id: "plan_001",
insurer_id: ObjectId("..."),
insurer_name: "State Farm",
plan_name: "Drive Safe & Save",
vehicle_types: ["Sedan", "SUV"],
region_codes: ["CA-N", "CA-S"],
premium_annual: 2150.00,
idv: 25000.00,
add_ons: ["roadside_assistance", "rental_reimbursement"],
tier: "Standard",
coverage_details: {
liability: "100/300/50",
collision: true,
comprehensive: true
}
}
```

#### 4. Signals Collection
```javascript
{
_id: ObjectId("..."),
plan_id: ObjectId("..."),
claim_tat_days: 25,
claim_approval_rate_pct: 92.5,
csat_score: 4.2,
renewal_rate_pct: 88.3,
complaint_ratio: 0.65
}
```

---

## API Endpoints

### Flask Service (Port 5000)

#### 1. Health Check
```
GET /health
Response: {
"status": "healthy",
"database": "connected",
"timestamp": "2024-12-06T10:30:00Z"
}
```

#### 2. Database Statistics
```
GET /api/stats
Response: {
"insurers": 20,
"plans": 120,
"vehicles": 150,
"signals": 300
}
```

#### 3. Get Recommendations
```
POST /api/recommend
Body: {
"vehicle_make": "string",
"vehicle_model": "string",
"vehicle_year": integer,
"region_code": "string",
"city": "string",
"top_n": integer,
"weights": {
"cost": float,
"coverage": float,
"service": float,
"reliability": float
}
}

Response: {
"recommendations": [
{
"rank": 1,
"insurer": "State Farm",
"plan_name": "Drive Safe & Save",
"premium_annual": 2150.00,
"score": 8.7,
"coverage": {...},
"service_metrics": {...}
}
]
}
```

**Example Request:**
```bash
curl -X POST http://localhost:5000/api/recommend \
-H "Content-Type: application/json" \
-d '{
"vehicle_make": "Toyota",
"vehicle_model": "Camry",
"vehicle_year": 2023,
"region_code": "90210",
"city": "Beverly Hills",
"top_n": 3,
"weights": {
"cost": 0.30,
"coverage": 0.25,
"service": 0.25,
"reliability": 0.20
}
}'
```

---

## Extending the System

### Adding New Insurers

#### Method 1: Manual (Quick)

1. Edit `data/seed_insurers.json`:
```json
{
"name": "New Insurer",
"region_codes": ["CA-S"],
"regional_coverage": ["Los Angeles"],
"website": "https://example.com",
"phone": "1-800-XXX-XXXX",
"description": "Description here",
"market_share_pct": 2.5
}
```

2. Edit `data/seed_config.json` to add insurer profile:
```json
"insurer_profiles": {
"New Insurer": {
"service_score": 0.75,
"reliability_score": 0.80,
"complaint_ratio": 0.70
}
}
```

3. Regenerate and reload:
```bash
cd data
python3 generate_seed_data.py
cd ../flask_service && source myenv/bin/activate
cd ../scripts && python3 load_data.py
```

#### Method 2: Automatic (Through Fetcher)

1. Modify `data/fetch_external_data.py`:
```python
def fetch_california_insurers():
insurers = [
# ... existing insurers ...
{
"name": "New Insurer",
"market_share_pct": 2.5,
# ... other details ...
}
]
return insurers
```

2. Run full refresh:
```bash
cd data
python3 fetch_external_data.py
python3 generate_seed_data.py
cd ../flask_service && source myenv/bin/activate
cd ../scripts && python3 load_data.py
```

---

### Customizing Premium Ranges

Edit `data/seed_config.json`:

```json
"premium_ranges": {
"Sedan": [1860, 3472], // Min and max annual premium
"SUV": [2232, 3720],
"Truck": [2356, 3968],
"Electric": [2728, 4340],
"Luxury": [3500, 6000] // Add new category
}
```

Then regenerate plans:
```bash
cd data
python3 generate_seed_data.py
cd ../flask_service && source myenv/bin/activate
cd ../scripts && python3 load_data.py
```

---

### Adding New California Regions

1. Edit `data/seed_config.json`:
```json
"california_regions": {
"CA-N": "Northern California",
"CA-S": "Southern California",
"CA-BAY": "San Francisco Bay Area",
"CA-SD": "San Diego Area",
"CA-C": "Central California",
"CA-DESERT": "Desert Region" // New region
}
```

2. Update insurers to cover new region:
```json
{
"name": "State Farm",
"region_codes": ["CA-N", "CA-S", "CA-BAY", "CA-SD", "CA-C", "CA-DESERT"],
"regional_coverage": ["Bay Area", "Los Angeles", "San Diego", "Central Valley", "North Coast", "Desert"]
}
```

3. Regenerate and reload data:
```bash
cd data
python3 generate_seed_data.py
cd ../flask_service && source myenv/bin/activate
cd ../scripts && python3 load_data.py
```

---

### Modifying TOPSIS Weights

#### Change Default Weights

Edit `flask_service/config.py`:
```python
DEFAULT_WEIGHTS = {
'cost': 0.25, # Change from 0.30
'coverage': 0.30, # Change from 0.25
'service': 0.25,
'reliability': 0.20
}
```

#### Add New Criteria

1. Update database schema in `plans` collection
2. Modify TOPSIS algorithm in `flask_service/models/topsis.py`
3. Update API endpoint to accept new weight
4. Update Django form to include new criterion

---

## Code Architecture

### Directory Structure

```
insurance-recommender/
├── flask_service/ # Backend API
│ ├── app.py # Main Flask application
│ ├── config.py # Configuration
│ ├── database.py # MongoDB connection
│ ├── models/
│ │ ├── topsis.py # Recommendation algorithm
│ │ └── schemas.py # Data validation schemas
│ ├── utils/
│ │ └── data_loader.py # Data loading utilities
│ └── extraction/
│ └── llm_extractor.py # LLM-based extraction (optional)
│
├── django_app/ # Frontend Dashboard
│ ├── dashboard/ # Django project settings
│ ├── recommender/ # Main app
│ │ ├── views.py # View logic
│ │ ├── urls.py # URL routing
│ │ └── models.py # Data models
│ └── templates/ # HTML templates
│ ├── base.html
│ └── recommender/
│ ├── index.html
│ ├── search.html
│ └── results.html
│
├── data/ # Data generation
│ ├── fetch_external_data.py # Fetch from NHTSA API
│ ├── generate_seed_data.py # Generate plans/signals
│ └── seed_*.json # Generated data files
│
└── scripts/ # Utility scripts
├── setup.sh # Automated setup
├── load_data.py # Load data to MongoDB
├── generate_env.py # Generate .env file
├── test_california_data.py # Data tests
└── test_api.py # API tests
```

### Key Components

#### 1. Flask Service (API)

**Purpose:** Provides REST API for insurance recommendations

**Key Files:**
- `app.py` - Main application, defines routes
- `models/topsis.py` - Recommendation algorithm
- `database.py` - MongoDB connection and queries

**Request Flow:**
```
User Request → Flask Route → TOPSIS Algorithm → MongoDB Query → JSON Response
```

#### 2. Django App (Dashboard)

**Purpose:** Web interface for users

**Key Files:**
- `recommender/views.py` - Handle user requests
- `templates/` - HTML templates
- `static/css/` - Styling

**Request Flow:**
```
User Form → Django View → Call Flask API → Display Results
```

#### 3. Data Generation

**Purpose:** Create realistic California insurance data

**Key Scripts:**
- `fetch_external_data.py` - Fetch from NHTSA API
- `generate_seed_data.py` - Generate plans/signals

**Data Flow:**
```
NHTSA API → fetch_external_data.py → JSON files → generate_seed_data.py → More JSON files
```

---

## 📚 Related Documentation

- **[README.md](README.md)** - Project overview
- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Setup & testing guide
- **[SETUP_WORKFLOW.md](SETUP_WORKFLOW.md)** - Setup workflow with flowcharts
- **[data/README.md](data/README.md)** - Data generation details
- **[scripts/README.md](scripts/README.md)** - Scripts documentation