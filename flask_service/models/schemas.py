"""
Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class RecommendationRequest(BaseModel):
    """Request schema for insurance recommendation"""
    
    vehicle_make: str = Field(..., min_length=1, description="Vehicle manufacturer")
    vehicle_model: str = Field(..., min_length=1, description="Vehicle model")
    vehicle_variant: Optional[str] = Field(None, description="Vehicle variant")
    vehicle_year: Optional[int] = Field(None, ge=2000, le=2030, description="Vehicle year")
    
    city: Optional[str] = Field(None, description="City name")
    region_code: str = Field(..., min_length=2, description="ZIP code or region code")
    
    top_n: int = Field(3, ge=1, le=10, description="Number of recommendations to return")
    
    # User preference weights (should sum to 1.0)
    weights: Optional[Dict[str, float]] = Field(
        None,
        description="Custom weights for criteria (cost, coverage, service, reliability)"
    )
    
    @field_validator('weights')
    @classmethod
    def validate_weights(cls, v):
        if v is not None:
            required_keys = {'cost', 'coverage', 'service', 'reliability'}
            if not all(k in v for k in required_keys):
                raise ValueError(f"Weights must contain all keys: {required_keys}")
            
            total = sum(v.values())
            if not (0.99 <= total <= 1.01):  # Allow small floating point errors
                raise ValueError(f"Weights must sum to 1.0, got {total}")
            
            if any(w < 0 or w > 1 for w in v.values()):
                raise ValueError("All weights must be between 0 and 1")
        
        return v


class ComponentScore(BaseModel):
    """Individual criterion score"""
    raw_value: Optional[float] = Field(None, description="Original value")
    normalized: float = Field(..., description="Normalized score (0-1)")
    weight: float = Field(..., description="Weight applied")
    contribution: float = Field(..., description="Weighted contribution to final score")


class PlanScore(BaseModel):
    """Scored insurance plan"""
    
    plan_id: str
    insurer_name: str
    plan_name: str
    
    # Overall score
    final_score: float = Field(..., ge=0, le=1, description="Final composite score")
    rank: int = Field(..., ge=1, description="Ranking position")
    
    # Component scores
    cost_score: ComponentScore
    coverage_score: ComponentScore
    service_score: ComponentScore
    reliability_score: ComponentScore
    
    # Plan details
    premium_annual: float
    coverage_idv: Optional[float] = None
    claim_tat_days: Optional[int] = None
    claim_approval_rate: Optional[float] = None
    csat_score: Optional[float] = None
    renewal_rate: Optional[float] = None
    complaint_ratio: Optional[float] = None
    
    # Explainability
    rationale: str = Field(..., description="Human-readable explanation")
    confidence: float = Field(default=1.0, ge=0, le=1, description="Confidence score")
    data_completeness: float = Field(default=1.0, ge=0, le=1, description="Data quality indicator")


class RecommendationResponse(BaseModel):
    """Response schema for recommendations"""
    
    success: bool = True
    message: str = "Recommendations generated successfully"
    
    query_info: Dict[str, Any] = Field(..., description="Query parameters used")
    weights_used: Dict[str, float] = Field(..., description="Final weights applied")
    
    recommendations: List[PlanScore]
    
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata (timestamp, version, etc.)"
    )


class ExtractionRequest(BaseModel):
    """Request schema for AI data extraction"""
    
    source_type: str = Field(..., description="Type of source: 'url' or 'text'")
    content: str = Field(..., min_length=10, description="URL or text content")
    insurer_name: Optional[str] = Field(None, description="Insurer name hint")


class ExtractedPlanData(BaseModel):
    """Extracted insurance plan data"""
    
    insurer_name: str
    plan_name: str
    premium_annual: Optional[float] = None
    idv: Optional[float] = None
    add_ons: Optional[List[str]] = None
    claim_tat_days: Optional[int] = None
    claim_approval_rate_pct: Optional[float] = None
    csat_score: Optional[float] = None
    evidence_snippets: List[str] = Field(default_factory=list)
    source_url: Optional[str] = None
    extraction_confidence: float = Field(default=0.5, ge=0, le=1)
    timestamp: datetime = Field(default_factory=datetime.now)


class ErrorResponse(BaseModel):
    """Error response schema"""
    
    success: bool = False
    error: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)

