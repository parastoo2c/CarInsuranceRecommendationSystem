# Implementation Guide - Insurance Recommender System

Detailed technical guide for understanding and extending the system.

## Architecture Overview

The system follows a microservices architecture:

```
┌─────────────┐     HTTP/JSON      ┌──────────────┐
│   Browser   │◄──────────────────►│    Django    │
│             │                     │  Dashboard   │
└─────────────┘                     └──────┬───────┘
                                           │
                 ┌─────────────────────────┘
                 │ REST API
                 ▼
           ┌──────────┐           ┌──────────────┐
           │  Flask   │◄─────────►│   MongoDB    │
           │ Service  │  PyMongo  │   Database   │
           └──────────┘           └──────────────┘
                 │
                 │ (Optional)
                 ▼
           ┌──────────┐
           │   LLM    │
           │   APIs   │
           └──────────┘
```

## Core Components

### 1. Flask Recommendation Service

**Purpose**: Implements the TOPSIS algorithm and serves recommendation API.

**Key Files**:
- `app.py` - Main Flask application with API endpoints
- `models/topsis.py` - TOPSIS algorithm implementation
- `models/schemas.py` - Pydantic validation schemas
- `database.py` - MongoDB connection and utilities
- `extraction/llm_extractor.py` - AI data extraction

**API Endpoints**:

1. **GET /health** - Health check
   ```bash
   curl http://localhost:5000/health
   ```

2. **GET /api/stats** - Database statistics
   ```bash
   curl http://localhost:5000/api/stats
   ```

3. **POST /api/recommend** - Get recommendations
   ```bash
   curl -X POST http://localhost:5000/api/recommend \
     -H "Content-Type: application/json" \
     -d '{
       "vehicle_make": "Toyota",
       "vehicle_model": "Camry",
       "region_code": "90210",
       "top_n": 3,
       "weights": {
         "cost": 0.3,
         "coverage": 0.25,
         "service": 0.25,
         "reliability": 0.2
       }
     }'
   ```

4. **POST /api/extract** - Extract plan data
   ```bash
   curl -X POST http://localhost:5000/api/extract \
     -H "Content-Type: application/json" \
     -d '{
       "source_type": "text",
       "content": "Plan details...",
       "insurer_name": "State Farm"
     }'
   ```

### 2. TOPSIS Algorithm

**Location**: `flask_service/models/topsis.py`

**Algorithm Steps**:

1. **Decision Matrix Construction**
   ```python
   matrix = prepare_decision_matrix(plans)
   # Returns: DataFrame with criteria (cost, coverage, service, reliability)
   ```

2. **Normalization** (Vector Normalization)
   ```
   normalized_value = value / sqrt(sum(values²))
   ```

3. **Weight Application**
   ```
   weighted_value = normalized_value × weight
   ```

4. **Ideal Solutions**
   ```
   ideal = max(weighted_values)
   anti_ideal = min(weighted_values)
   ```

5. **Distance Calculation** (Euclidean)
   ```
   dist_ideal = sqrt(sum((weighted - ideal)²))
   dist_anti_ideal = sqrt(sum((weighted - anti_ideal)²))
   ```

6. **Relative Closeness** (Final Score)
   ```
   score = dist_anti_ideal / (dist_ideal + dist_anti_ideal)
   ```

**Criteria Definitions**:

| Criterion | Formula | Direction |
|-----------|---------|-----------|
| **Cost** | `1 / premium` | Higher is better |
| **Coverage** | `IDV value` | Higher is better |
| **Service** | `(1/claim_tat × 0.4) + (approval_rate × 0.3) + (csat × 0.3)` | Higher is better |
| **Reliability** | `renewal_rate × (1 - complaint_ratio)` | Higher is better |

### 3. Django Dashboard

**Purpose**: User-facing web interface for search and results.

**Key Files**:
- `dashboard/settings.py` - Django configuration
- `recommender/views.py` - View logic
- `recommender/urls.py` - URL routing
- `templates/` - HTML templates

**Views**:

1. **index** - Landing page
2. **search** - Search form
3. **results** - Display recommendations (calls Flask API)
4. **about** - Project information

**Template Structure**:
```
templates/
├── base.html                    # Base template with nav/footer
└── recommender/
    ├── index.html              # Home page
    ├── search.html             # Search form
    ├── results.html            # Results with Chart.js
    └── about.html              # About page
```

### 4. MongoDB Database

**Collections**:

1. **insurers** - Insurance companies
   ```javascript
   {
     "_id": ObjectId,
     "name": "State Farm",
     "region_codes": ["90", "91", "92"],
     "website": "https://...",
     "phone": "1-800-...",
     "description": "..."
   }
   ```

2. **plans** - Insurance plans
   ```javascript
   {
     "_id": ObjectId,
     "insurer_id": ObjectId,
     "plan_name": "Premium Coverage",
     "vehicle_types": ["Toyota Camry SE"],
     "region_codes": ["90", "91"],
     "premium_annual": 1800.00,
     "idv": 25000.00,
     "add_ons": ["Zero Depreciation", "Roadside Assistance"]
   }
   ```

3. **signals** - Service quality metrics
   ```javascript
   {
     "_id": ObjectId,
     "plan_id": ObjectId,
     "claim_tat_days": 15,
     "claim_approval_rate_pct": 85.5,
     "csat_score": 78.3,
     "renewal_rate_pct": 82.1,
     "complaint_ratio": 0.45
   }
   ```

4. **vehicles** - Vehicle catalog
   ```javascript
   {
     "_id": ObjectId,
     "make": "Toyota",
     "model": "Camry",
     "variant": "SE",
     "year_from": 2020,
     "year_to": 2024,
     "category": "Sedan"
   }
   ```

5. **query_logs** - Analytics
   ```javascript
   {
     "_id": ObjectId,
     "timestamp": ISODate,
     "vehicle": "Toyota Camry",
     "region_code": "90210",
     "top_n": 3,
     "results_count": 3,
     "weights": {...}
   }
   ```

## Extending the System

### Adding a New Criterion

1. **Update TOPSIS Algorithm**

Edit `flask_service/models/topsis.py`:

```python
def prepare_decision_matrix(self, plans):
    # Add new criterion
    sustainability_value = plan.get('carbon_offset_pct', 0) / 100
    
    matrix_data.append({
        'cost': cost_value,
        'coverage': coverage_value,
        'service': service_value,
        'reliability': reliability_value,
        'sustainability': sustainability_value  # NEW
    })
```

2. **Update Default Weights**

Edit `flask_service/config.py`:

```python
DEFAULT_WEIGHTS = {
    'cost': 0.25,
    'coverage': 0.20,
    'service': 0.20,
    'reliability': 0.20,
    'sustainability': 0.15  # NEW
}
```

3. **Update Schemas**

Edit `flask_service/models/schemas.py`:

```python
class ComponentScore(BaseModel):
    # ... existing fields ...
    sustainability_score: ComponentScore  # NEW
```

4. **Update Frontend**

Edit `django_app/templates/recommender/results.html` to display the new criterion.

### Integrating Real Data Sources

**Example: California DMV API**

```python
# In flask_service/utils/data_sources.py

import requests

def fetch_vehicle_registration_data(vin):
    """Fetch vehicle data from external API"""
    api_url = "https://api.example.gov/vehicles"
    response = requests.get(f"{api_url}/{vin}")
    return response.json()

# Use in recommendation flow
vehicle_data = fetch_vehicle_registration_data(vin)
```

### Adding Machine Learning

**Example: XGBoost Ranking**

```python
# In flask_service/models/ml_ranker.py

import xgboost as xgb
from sklearn.model_selection import train_test_split

class MLRanker:
    def __init__(self):
        self.model = xgb.XGBRanker()
    
    def train(self, X, y):
        """Train ranking model on historical data"""
        X_train, X_test, y_train, y_test = train_test_split(X, y)
        self.model.fit(X_train, y_train)
    
    def rank(self, plans):
        """Rank plans using learned model"""
        features = self.extract_features(plans)
        scores = self.model.predict(features)
        return sorted(zip(plans, scores), key=lambda x: x[1], reverse=True)
```

### Implementing Caching

**Redis Integration**:

```python
# In flask_service/app.py

from flask_caching import Cache

cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': Config.REDIS_URL
})

@app.route('/api/recommend', methods=['POST'])
@cache.cached(timeout=300, key_prefix=make_cache_key)
def recommend():
    # ... existing code ...
```

## Testing

### Unit Tests

**Flask Service**:

```bash
cd flask_service
pytest tests/
```

**Example Test** (`tests/test_topsis.py`):

```python
import pytest
from models.topsis import TOPSISRecommender

def test_topsis_ranking():
    recommender = TOPSISRecommender()
    
    plans = [
        {'premium_annual': 1000, 'coverage_idv': 20000, 'signals': {...}},
        {'premium_annual': 1500, 'coverage_idv': 25000, 'signals': {...}},
    ]
    
    results = recommender.rank_plans(plans, top_n=2)
    
    assert len(results) == 2
    assert results[0]['rank'] == 1
    assert results[1]['rank'] == 2
    assert results[0]['final_score'] >= results[1]['final_score']
```

### Integration Tests

```python
# tests/test_integration.py

def test_end_to_end_recommendation():
    # Load data
    db = get_db()
    loader = DataLoader(db)
    
    # Make API request
    response = requests.post('http://localhost:5000/api/recommend', json={
        'vehicle_make': 'Toyota',
        'vehicle_model': 'Camry',
        'region_code': '90210',
        'top_n': 3
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data['success'] == True
    assert len(data['recommendations']) == 3
```

## Performance Optimization

### Database Indexing

```python
# In database.py

def _create_indexes(self):
    # Compound index for common queries
    self.db[Config.COLLECTION_PLANS].create_index([
        ('vehicle_types', ASCENDING),
        ('region_codes', ASCENDING),
        ('premium_annual', ASCENDING)
    ])
```

### Query Optimization

```python
# Use projection to fetch only needed fields
plans_cursor = plans_collection.find(
    query,
    projection={
        'plan_name': 1,
        'premium_annual': 1,
        'idv': 1,
        'insurer_id': 1
    }
)
```

### Caching Strategy

1. **API-level caching** - Cache recommendation responses for 5 minutes
2. **Database query caching** - Cache frequently accessed plans
3. **Static data caching** - Cache insurers and vehicles lists

## Deployment

### Production Configuration

```python
# flask_service/config.py

class ProductionConfig(Config):
    DEBUG = False
    MONGODB_URI = os.getenv('MONGODB_ATLAS_URI')
    CACHE_ENABLED = True
```

### Environment Variables

```bash
# Production .env
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com
FLASK_SERVICE_URL=https://api.yourdomain.com
```

### Docker Deployment

```bash
# Build and push
docker-compose build
docker tag insurance-flask:latest registry.com/insurance-flask:latest
docker push registry.com/insurance-flask:latest

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

## Security Best Practices

1. **API Authentication**: Implement JWT tokens
2. **HTTPS Only**: Use SSL certificates
3. **Rate Limiting**: Prevent abuse
4. **Input Validation**: Use Pydantic schemas
5. **Environment Variables**: Never commit secrets

## Monitoring

### Logging

```python
# Add structured logging
import logging
import json

logger = logging.getLogger(__name__)

def log_recommendation(query, results):
    logger.info(json.dumps({
        'event': 'recommendation',
        'query': query,
        'results_count': len(results),
        'timestamp': datetime.now().isoformat()
    }))
```

### Metrics

Track:
- API response times
- Recommendation quality (user feedback)
- Database query performance
- Error rates

## Conclusion

This implementation provides a solid foundation for a production-ready insurance recommender system. The modular architecture allows for easy extension and customization based on specific requirements.

