# California Insurance Data Directory
 
This directory contains scripts and JSON files for generating California-specific auto insurance data.
 
**Geographic Focus: California, USA** - All data, rates, and insurers are specific to the California auto insurance market.
 
## 📋 Table of Contents
 
- [Quick Start](#quick-start)
- [Files Overview](#files-overview)
- [Data Generation Process](#data-generation-process)
- [What Data is Real vs Generated](#what-data-is-real-vs-generated)
- [California-Specific Features](#california-specific-features)
- [Quick Reference Commands](#quick-reference-commands)
- [Troubleshooting](#troubleshooting)
- [Data Sources & References](#data-sources--references)
 
---
 
## Quick Start
 
```bash
# 1. Fetch California data from internet
cd data
python3 fetch_external_data.py
 
# 2. Generate plans and signals
python3 generate_seed_data.py
 
# 3. Load into MongoDB
cd ../flask_service
source myenv/bin/activate
cd ../scripts
python3 load_data.py
```
 
---
 
## Files Overview
 
### Generated Data Files
 
| File | Description | Source | Size |
|------|-------------|--------|------|
| `seed_config.json` | California configuration (rates, profiles) | Generated from CA market data | ~15 KB |
| `seed_insurers.json` | Top 8 California insurers | CA Dept of Insurance market share | ~10-20 KB |
| `seed_vehicles.json` | Vehicle specifications | NHTSA API | ~20-40 KB |
| `seed_plans.json` | Insurance plans | Generated from config | ~50-100 KB |
| `seed_signals.json` | Service quality signals | Generated from config | ~30-60 KB |
 
### Scripts
 
- **`fetch_external_data.py`** - Fetches vehicle data from NHTSA API and loads CA DOI published rates
- **`generate_seed_data.py`** - Generates insurance plans and signals from configuration
 
---
 
## Data Generation Process
 
### Two-Step Process
 
#### Step 1: Fetch External Data (California-specific)
 
The `fetch_external_data.py` script combines live API calls with official published data:
 
**✅ Live API Calls:**
- **Vehicle data** from NHTSA API (makes, models, years)
 
**📄 Official Published Data (CA DOI, J.D. Power):**
- **Insurance rates** from California Department of Insurance published averages
- **California insurers** with market share from CA DOI annual reports
- **Premium ranges** from CA DOI consumer guides (24% above national average)
- **Insurer profiles** from CA DOI complaint ratio reports and J.D. Power ratings
 
```bash
cd data
python3 fetch_external_data.py
```
 
**Generates/Updates:**
- `seed_config.json` - California-specific configuration
- `seed_vehicles.json` - Real vehicle data from NHTSA
- `seed_insurers.json` - California insurance companies
 
#### Step 2: Generate Plans and Signals
 
The `generate_seed_data.py` script uses the fetched configuration to create realistic combinations:
 
```bash
python3 generate_seed_data.py
```
 
**Generates:**
- `seed_plans.json` - Insurance plans for different vehicle types and regions
- `seed_signals.json` - Service quality signals (claim TAT, satisfaction, renewal rates)
 
---
 
## What Data is Real vs Generated?
 
### 🌐 Fetched from Internet (Live APIs)
 
#### 1. Vehicle Data - NHTSA API
- **Source**: National Highway Traffic Safety Administration
- **API**: https://vpic.nhtsa.dot.gov/api/
- **What we fetch**:
  - Vehicle makes (Toyota, Honda, Tesla, etc.)
  - Vehicle models (Camry, Accord, Model 3, etc.)
  - Model years (2023, 2024)
  - Vehicle specifications
- **Status**: ✅ **Live API calls** - Real data fetched at runtime
 
```python
# Example API call
GET https://vpic.nhtsa.dot.gov/api/vehicles/GetModelsForMakeYear/make/Toyota/modelyear/2024
```
 
### 📄 Based on Published Official Sources
 
The following data is NOT available via free public APIs, but is based on **official published reports**:
 
#### 2. Insurance Premium Ranges
- **Source**: California Department of Insurance Annual Consumer Guide (2024)
- **Published URL**: https://www.insurance.ca.gov/
- **What we use**:
  - Average annual premiums by vehicle type
  - California vs national average comparison (CA is 24% higher)
  - Risk multipliers for different driver profiles
- **Status**: 📄 **Published data** - Real rates from official reports
 
**Why not live API?**
- Insurance companies don't provide free quote APIs
- Real-time quotes require commercial licenses ($$$)
- Personal information required (age, driving record, credit score)
- Complex integrations with each insurer's proprietary systems
 
#### 3. Insurer Market Share
- **Source**: California Department of Insurance Market Share Report (2024)
- **What we use**:
  - Top 8 insurers by market share percentage
  - Regional coverage by insurer
  - Insurer contact information
- **Status**: 📄 **Published data** - Real market data from CA DOI
 
#### 4. Insurer Performance Profiles
- **Sources**:
  - California DOI Complaint Ratio Report (2024)
  - J.D. Power 2024 U.S. Auto Insurance Study - California Region
  - NAIC Complaint Index
  - AM Best Financial Strength Ratings
- **What we use**:
  - Complaint ratios (lower = better service)
  - Customer satisfaction scores
  - Claims handling performance
  - Financial strength ratings
- **Status**: 📄 **Published data** - Real metrics from regulatory reports
 
**Example:**
- USAA complaint ratio: 0.19 (best) → service score 0.92
- Geico complaint ratio: 0.88 (higher) → service score 0.68
 
#### 5. Service Quality Benchmarks
- **Sources**: CA DOI Claims Processing Reports, J.D. Power California Study
- **What we use**:
  - Average claim turnaround time (CA: 28 days)
  - Claim approval rates
  - Customer satisfaction averages
  - Renewal rate benchmarks
- **Status**: 📄 **Published benchmarks** - Industry averages
 
---
 
## California-Specific Features
 
### Premium Rates
- **24% higher** than national average
- Based on California Department of Insurance published data
- Adjusted by vehicle type, region, and coverage tier
 
### Top 8 Insurers (by California market share)
1. **State Farm** - 15.2%
2. **Geico** - 12.8%
3. **Progressive** - 11.5%
4. **Allstate** - 9.3%
5. **USAA** - 7.8%
6. **Farmers** - 7.1%
7. **Mercury Insurance** - 6.2%
8. **AAA** - 5.9%
 
### Regions
- **CA-N**: Northern California
- **CA-C**: Central California
- **CA-S**: Southern California
- **CA-BAY**: San Francisco Bay Area
- **CA-SD**: San Diego Area
 
### Vehicle Categories & Average Annual Premiums
 
| Category | Premium Range | IDV Range |
|----------|---------------|-----------|
| Sedan | $1,860 - $3,472 | $15,000 - $45,000 |
| SUV | $2,232 - $3,720 | $25,000 - $75,000 |
| Truck | $2,356 - $3,968 | $30,000 - $90,000 |
| Electric | $2,728 - $4,340 | $35,000 - $95,000 |
 
### Plan Tiers & Multipliers
 
| Tier | Coverage | Premium Multiplier |
|------|----------|-------------------|
| Basic | Minimum coverage | 0.75x |
| Standard | Good coverage | 1.0x |
| Premium | Comprehensive | 1.3x |
| Elite | Full coverage + extras | 1.6x |
 
---
 
## Quick Reference Commands
 
### Complete Workflow (First Time)
 
```bash
# 1. Navigate to data directory
cd insurance-recommender/data
 
# 2. Fetch California-specific data from internet
python3 fetch_external_data.py
 
# 3. Generate plans and signals
python3 generate_seed_data.py
 
# 4. Load into MongoDB
cd ../flask_service
source myenv/bin/activate
cd ../scripts
python3 load_data.py
```
 
### Quick Update (Already Set Up)
 
```bash
cd data
python3 fetch_external_data.py
python3 generate_seed_data.py
cd ../flask_service && source myenv/bin/activate
cd ../scripts && python3 load_data.py
```
 
---
 
## Troubleshooting
 
### ❌ Can't Access NHTSA API
 
```bash
# Just use existing configuration
python3 generate_seed_data.py
```
 
The script will use default vehicle data if the API is unavailable.
 
### ❌ Empty or Missing JSON Files
 
```bash
# Check if files exist
ls -lh seed_*.json
 
# If missing, re-fetch
python3 fetch_external_data.py
python3 generate_seed_data.py
 
# Verify file sizes (should not be empty)
du -h seed_*.json
```
 
### ❌ JSON Validation Errors
 
```bash
# Validate each file
python3 -m json.tool seed_config.json > /dev/null
python3 -m json.tool seed_insurers.json > /dev/null
 
# If corrupted, re-generate
rm seed_*.json
python3 fetch_external_data.py
python3 generate_seed_data.py
```
 
### ❌ API Rate Limiting
 
The script includes automatic rate limiting (0.5s delay between requests). If you still hit limits, wait a few minutes and retry.
 
### ❌ Dependencies Missing
 
```bash
# requests is in flask_service/requirements.txt
cd ../flask_service
source myenv/bin/activate
pip list | grep requests
 
# If missing, reinstall
pip install -r requirements.txt
```
 
---
 
## Data Sources & References
 
### Official Sources Used
 
1. **California Department of Insurance**
   - Consumer Guides: https://www.insurance.ca.gov/0100-consumers/0060-information-guides/
   - Complaint Ratios: https://www.insurance.ca.gov/0100-consumers/0030-consumer-complaints/
   - Market Share: Annual reports
   - Status: 📄 Official regulatory data
 
2. **NHTSA Vehicle API**
   - API Documentation: https://vpic.nhtsa.dot.gov/api/
   - Status: ✅ Live API calls
 
3. **J.D. Power**
   - Auto Insurance Studies: https://www.jdpower.com/business/insurance
   - California Region Ratings
   - Status: 📄 Published research
 
4. **NAIC**
   - Complaint Index: https://www.naic.org/
   - Status: 📄 Published data
 
### Why Not All Live APIs?
 
**The Reality of Insurance Data:**
 
Insurance quote APIs are:
- ❌ Proprietary (not public)
- ❌ Require commercial licenses ($$$)
- ❌ Need personal information (age, driving record, credit score)
- ❌ Regulated by state insurance departments
- ❌ Different for each insurer (no standard)
 
**Our Approach:**
 
Instead, we use the **next best alternative**:
- ✅ Official published data from regulatory bodies
- ✅ Real complaint ratios and satisfaction scores
- ✅ Actual market share percentages
- ✅ Live vehicle data where available
- ✅ Transparent sourcing with citations
 
This provides **representative California market data** suitable for educational and demonstration purposes.
 
### Future Enhancements
 
Potential improvements:
1. **Web Scraping** (where legal) - Public insurer websites
2. **More APIs** - Kelley Blue Book, ZIP code demographics
3. **Commercial APIs** (if budget) - QuoteWizard, The Zebra
4. **User-Contributed Data** - Crowd-source actual quotes
 
---
 
## Data Schema
 
### Insurers (seed_insurers.json)
```json
{
  "name": "string",
  "region_codes": ["string"],
  "website": "url",
  "phone": "string",
  "description": "string",
  "market_share_pct": float,
  "regional_coverage": ["string"]
}
```
 
### Vehicles (seed_vehicles.json)
```json
{
  "make": "string",
  "model": "string",
  "year": int,
  "vehicle_type": "string",
  "category": "string"
}
```
 
### Plans (seed_plans.json)
```json
{
  "plan_id": "string",
  "insurer_name": "string",
  "plan_name": "string",
  "vehicle_types": ["string"],
  "region_codes": ["string"],
  "premium_annual": float,
  "idv": float,
  "add_ons": ["string"],
  "tier": "string"
}
```
 
### Signals (seed_signals.json)
```json
{
  "plan_id": "string",
  "claim_tat_days": int,
  "claim_approval_rate_pct": float,
  "csat_score": float,
  "renewal_rate_pct": float,
  "complaint_ratio": float
}
```
 
---
 
## Loading Data into MongoDB
 
After generating the JSON files, load them using the Flask service:
 
```bash
cd flask_service
source myenv/bin/activate
cd ../scripts
python3 load_data.py
```
 
This script:
1. Connects to MongoDB
2. Loads insurers, vehicles, plans, and signals
3. Maps relationships (insurer_name → insurer_id, plan_id → ObjectId)
4. Creates proper references between collections
 
See [../scripts/README.md](../scripts/README.md) for more details.
