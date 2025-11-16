"""
Flask Microservice for Insurance Recommendation
Main application entry point
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import logging
from bson import ObjectId

from config import Config
from database import get_db, init_db
from models.topsis import TOPSISRecommender
from models.schemas import (
    RecommendationRequest,
    RecommendationResponse,
    PlanScore,
    ComponentScore,
    ErrorResponse,
    ExtractionRequest,
    ExtractedPlanData
)
from extraction.llm_extractor import LLMExtractor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)  # Enable CORS for Django frontend

# Initialize database
try:
    db = init_db()
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")
    db = None


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    db_status = "connected" if db else "disconnected"
    return jsonify({
        'status': 'healthy',
        'service': 'flask-recommender',
        'database': db_status,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/recommend', methods=['POST'])
def recommend():
    """
    Main recommendation endpoint
    
    Request Body:
        {
            "vehicle_make": "Toyota",
            "vehicle_model": "Camry",
            "vehicle_variant": "SE",
            "vehicle_year": 2022,
            "region_code": "90210",
            "city": "Beverly Hills",
            "top_n": 3,
            "weights": {
                "cost": 0.30,
                "coverage": 0.25,
                "service": 0.25,
                "reliability": 0.20
            }
        }
    
    Response:
        {
            "success": true,
            "recommendations": [...],
            "weights_used": {...},
            "metadata": {...}
        }
    """
    try:
        # Parse and validate request
        data = request.get_json()
        req = RecommendationRequest(**data)
        
        logger.info(f"Recommendation request: {req.vehicle_make} {req.vehicle_model}, region: {req.region_code}")
        
        # Get weights (use custom or default)
        weights = req.weights if req.weights else Config.DEFAULT_WEIGHTS
        
        # Fetch relevant plans from database
        plans = fetch_plans(
            vehicle_make=req.vehicle_make,
            vehicle_model=req.vehicle_model,
            region_code=req.region_code
        )
        
        if not plans:
            return jsonify(ErrorResponse(
                error="No insurance plans found",
                details={
                    "vehicle": f"{req.vehicle_make} {req.vehicle_model}",
                    "region": req.region_code,
                    "suggestion": "Try a different vehicle or region"
                }
            ).dict()), 404
        
        # Initialize TOPSIS recommender
        recommender = TOPSISRecommender(weights=weights)
        
        # Rank plans
        ranked_plans = recommender.rank_plans(plans, top_n=req.top_n)
        
        # Format response with PlanScore schema
        recommendations = []
        for plan in ranked_plans:
            comp_scores = plan['component_scores']
            
            plan_score = PlanScore(
                plan_id=str(plan.get('_id', plan.get('plan_id'))),
                insurer_name=plan.get('insurer_name', 'Unknown'),
                plan_name=plan.get('plan_name', 'Standard Plan'),
                final_score=plan['final_score'],
                rank=plan['rank'],
                cost_score=ComponentScore(
                    raw_value=comp_scores['cost']['raw'],
                    normalized=comp_scores['cost']['normalized'],
                    weight=comp_scores['cost']['weight'],
                    contribution=comp_scores['cost']['weighted']
                ),
                coverage_score=ComponentScore(
                    raw_value=comp_scores['coverage']['raw'],
                    normalized=comp_scores['coverage']['normalized'],
                    weight=comp_scores['coverage']['weight'],
                    contribution=comp_scores['coverage']['weighted']
                ),
                service_score=ComponentScore(
                    raw_value=comp_scores['service']['raw'],
                    normalized=comp_scores['service']['normalized'],
                    weight=comp_scores['service']['weight'],
                    contribution=comp_scores['service']['weighted']
                ),
                reliability_score=ComponentScore(
                    raw_value=comp_scores['reliability']['raw'],
                    normalized=comp_scores['reliability']['normalized'],
                    weight=comp_scores['reliability']['weight'],
                    contribution=comp_scores['reliability']['weighted']
                ),
                premium_annual=plan.get('premium_annual', 0),
                coverage_idv=plan.get('coverage_idv'),
                claim_tat_days=plan.get('signals', {}).get('claim_tat_days'),
                claim_approval_rate=plan.get('signals', {}).get('claim_approval_rate_pct'),
                csat_score=plan.get('signals', {}).get('csat_score'),
                renewal_rate=plan.get('signals', {}).get('renewal_rate_pct'),
                complaint_ratio=plan.get('signals', {}).get('complaint_ratio'),
                rationale=recommender.generate_rationale(plan),
                confidence=plan.get('confidence', 0.9),
                data_completeness=calculate_data_completeness(plan)
            )
            recommendations.append(plan_score)
        
        # Log query for analytics
        log_query(req, ranked_plans)
        
        # Build response
        response = RecommendationResponse(
            query_info={
                'vehicle': f"{req.vehicle_make} {req.vehicle_model}",
                'region': req.region_code,
                'top_n': req.top_n
            },
            weights_used=weights,
            recommendations=recommendations,
            metadata={
                'total_plans_evaluated': len(plans),
                'algorithm': 'TOPSIS',
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0'
            }
        )
        
        return jsonify(response.dict()), 200
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return jsonify(ErrorResponse(
            error="Invalid request data",
            details={'message': str(e)}
        ).dict()), 400
        
    except Exception as e:
        logger.error(f"Recommendation error: {e}", exc_info=True)
        return jsonify(ErrorResponse(
            error="Internal server error",
            details={'message': str(e)}
        ).dict()), 500


def fetch_plans(vehicle_make: str, vehicle_model: str, region_code: str) -> list:
    """
    Fetch insurance plans from database
    
    Args:
        vehicle_make: Vehicle manufacturer
        vehicle_model: Vehicle model
        region_code: ZIP/region code
    
    Returns:
        List of insurance plans with signals
    """
    if not db:
        logger.error("Database not initialized")
        return []
    
    try:
        plans_collection = db.get_collection(Config.COLLECTION_PLANS)
        signals_collection = db.get_collection(Config.COLLECTION_SIGNALS)
        insurers_collection = db.get_collection(Config.COLLECTION_INSURERS)
        
        # Query plans matching vehicle and region
        query = {
            'vehicle_types': {
                '$regex': f'{vehicle_make}.*{vehicle_model}',
                '$options': 'i'
            },
            'region_codes': region_code[:2]  # Match first 2 digits of ZIP
        }
        
        plans_cursor = plans_collection.find(query)
        plans = []
        
        for plan in plans_cursor:
            # Fetch associated signals
            signals = signals_collection.find_one({'plan_id': str(plan['_id'])})
            
            # Fetch insurer info
            insurer = insurers_collection.find_one({'_id': ObjectId(plan['insurer_id'])})
            
            # Merge data
            plan_data = {
                '_id': str(plan['_id']),
                'plan_id': str(plan['_id']),
                'insurer_id': str(plan['insurer_id']),
                'insurer_name': insurer['name'] if insurer else 'Unknown',
                'plan_name': plan.get('plan_name', 'Standard'),
                'premium_annual': plan.get('premium_annual', 1000),
                'coverage_idv': plan.get('idv', 0),
                'add_ons': plan.get('add_ons', []),
                'signals': signals if signals else {}
            }
            
            plans.append(plan_data)
        
        logger.info(f"Found {len(plans)} plans matching criteria")
        return plans
        
    except Exception as e:
        logger.error(f"Error fetching plans: {e}")
        return []


def calculate_data_completeness(plan: dict) -> float:
    """Calculate data completeness score"""
    required_fields = [
        'premium_annual', 'coverage_idv',
        'signals.claim_tat_days', 'signals.claim_approval_rate_pct',
        'signals.csat_score', 'signals.renewal_rate_pct', 'signals.complaint_ratio'
    ]
    
    present = 0
    for field in required_fields:
        if '.' in field:
            parts = field.split('.')
            value = plan.get(parts[0], {}).get(parts[1])
        else:
            value = plan.get(field)
        
        if value is not None:
            present += 1
    
    return present / len(required_fields)


def log_query(req: RecommendationRequest, results: list):
    """Log query for analytics"""
    if not db:
        return
    
    try:
        logs_collection = db.get_collection(Config.COLLECTION_QUERY_LOGS)
        logs_collection.insert_one({
            'timestamp': datetime.now(),
            'vehicle': f"{req.vehicle_make} {req.vehicle_model}",
            'region_code': req.region_code,
            'top_n': req.top_n,
            'results_count': len(results),
            'weights': req.weights
        })
    except Exception as e:
        logger.warning(f"Failed to log query: {e}")


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get system statistics"""
    if not db:
        return jsonify({'error': 'Database not available'}), 503
    
    try:
        stats = {
            'insurers': db.get_collection(Config.COLLECTION_INSURERS).count_documents({}),
            'plans': db.get_collection(Config.COLLECTION_PLANS).count_documents({}),
            'signals': db.get_collection(Config.COLLECTION_SIGNALS).count_documents({}),
            'vehicles': db.get_collection(Config.COLLECTION_VEHICLES).count_documents({}),
            'total_queries': db.get_collection(Config.COLLECTION_QUERY_LOGS).count_documents({})
        }
        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/extract', methods=['POST'])
def extract_plan_data():
    """
    Extract insurance plan data using AI/LLM
    
    Request Body:
        {
            "source_type": "url" or "text",
            "content": "URL or text content",
            "insurer_name": "Optional insurer hint"
        }
    
    Response:
        {
            "success": true,
            "extracted_data": {...},
            "message": "Extraction completed"
        }
    """
    try:
        data = request.get_json()
        req = ExtractionRequest(**data)
        
        logger.info(f"Extraction request: {req.source_type}")
        
        # Initialize extractor
        extractor = LLMExtractor()
        
        # Extract based on source type
        if req.source_type == 'url':
            extracted = extractor.extract_from_url(req.content, req.insurer_name)
        else:
            extracted = extractor.extract_from_text(req.content, req.insurer_name)
        
        # Validate extracted data
        plan_data = ExtractedPlanData(**extracted)
        
        # Optionally save to database
        if db and plan_data.extraction_confidence > 0.7:
            # Store in a temporary collection for review
            db.get_collection('extracted_plans').insert_one(plan_data.dict())
        
        return jsonify({
            'success': True,
            'message': 'Extraction completed',
            'extracted_data': plan_data.dict()
        }), 200
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return jsonify(ErrorResponse(
            error="Invalid request data",
            details={'message': str(e)}
        ).dict()), 400
        
    except Exception as e:
        logger.error(f"Extraction error: {e}", exc_info=True)
        return jsonify(ErrorResponse(
            error="Extraction failed",
            details={'message': str(e)}
        ).dict()), 500


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=Config.PORT,
        debug=Config.DEBUG
    )

