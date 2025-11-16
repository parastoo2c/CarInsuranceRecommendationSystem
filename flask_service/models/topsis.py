"""
TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution)
Multi-Criteria Decision Making Implementation

References:
- ScienceDirect (2024): "A Comprehensive Survey on TOPSIS Method"
- MDPI Symmetry (2024): "A Novel TOPSIS Framework"
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class TOPSISRecommender:
    """
    TOPSIS-based Multi-Criteria Recommender System
    
    Implements TOPSIS algorithm with:
    - Weighted normalization
    - Ideal and anti-ideal solutions
    - Distance-based scoring
    - Configurable criteria weights
    """
    
    def __init__(self, weights: Dict[str, float] = None):
        """
        Initialize TOPSIS recommender
        
        Args:
            weights: Dictionary of criterion weights
                    {'cost': 0.3, 'coverage': 0.25, 'service': 0.25, 'reliability': 0.2}
        """
        self.default_weights = {
            'cost': 0.30,
            'coverage': 0.25,
            'service': 0.25,
            'reliability': 0.20
        }
        self.weights = weights if weights else self.default_weights
        self._validate_weights()
    
    def _validate_weights(self):
        """Validate that weights sum to 1.0"""
        total = sum(self.weights.values())
        if not (0.99 <= total <= 1.01):
            raise ValueError(f"Weights must sum to 1.0, got {total}")
    
    def prepare_decision_matrix(self, plans: List[Dict]) -> Tuple[pd.DataFrame, List[str]]:
        """
        Prepare decision matrix from insurance plans
        
        Args:
            plans: List of insurance plan dictionaries with signals
        
        Returns:
            Tuple of (decision_matrix, plan_ids)
        """
        if not plans:
            raise ValueError("No plans provided for scoring")
        
        matrix_data = []
        plan_ids = []
        
        for plan in plans:
            signals = plan.get('signals', {})
            
            # Extract criteria values
            # Cost: lower is better (invert for maximization)
            premium = plan.get('premium_annual', 0)
            cost_value = 1 / premium if premium > 0 else 0
            
            # Coverage: higher IDV is better
            coverage_value = plan.get('coverage_idv', 0)
            
            # Service: composite of claim speed and approval rate
            claim_tat = signals.get('claim_tat_days', 30)
            claim_speed = 1 / claim_tat if claim_tat > 0 else 0
            approval_rate = signals.get('claim_approval_rate_pct', 50) / 100
            csat = signals.get('csat_score', 50) / 100
            service_value = (claim_speed * 0.4 + approval_rate * 0.3 + csat * 0.3)
            
            # Reliability: renewal rate minus complaint ratio
            renewal_rate = signals.get('renewal_rate_pct', 50) / 100
            complaint_ratio = signals.get('complaint_ratio', 0.5)
            reliability_value = renewal_rate * (1 - complaint_ratio)
            
            matrix_data.append({
                'cost': cost_value,
                'coverage': coverage_value,
                'service': service_value,
                'reliability': reliability_value
            })
            
            plan_ids.append(plan.get('_id', plan.get('plan_id')))
        
        df = pd.DataFrame(matrix_data)
        return df, plan_ids
    
    def normalize_matrix(self, matrix: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize decision matrix using vector normalization
        
        Args:
            matrix: Raw decision matrix
        
        Returns:
            Normalized matrix
        """
        normalized = matrix.copy()
        
        for col in matrix.columns:
            col_sum_sq = np.sqrt((matrix[col] ** 2).sum())
            if col_sum_sq > 0:
                normalized[col] = matrix[col] / col_sum_sq
            else:
                normalized[col] = 0
        
        return normalized
    
    def apply_weights(self, normalized_matrix: pd.DataFrame) -> pd.DataFrame:
        """
        Apply criterion weights to normalized matrix
        
        Args:
            normalized_matrix: Normalized decision matrix
        
        Returns:
            Weighted matrix
        """
        weighted = normalized_matrix.copy()
        
        for criterion, weight in self.weights.items():
            if criterion in weighted.columns:
                weighted[criterion] = normalized_matrix[criterion] * weight
        
        return weighted
    
    def calculate_ideal_solutions(self, weighted_matrix: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        """
        Calculate ideal (best) and anti-ideal (worst) solutions
        
        All criteria are beneficial (higher is better after transformation)
        
        Args:
            weighted_matrix: Weighted normalized matrix
        
        Returns:
            Tuple of (ideal_solution, anti_ideal_solution)
        """
        # For all criteria, max is ideal (we inverted cost earlier)
        ideal = weighted_matrix.max()
        anti_ideal = weighted_matrix.min()
        
        return ideal, anti_ideal
    
    def calculate_distances(
        self,
        weighted_matrix: pd.DataFrame,
        ideal: pd.Series,
        anti_ideal: pd.Series
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate Euclidean distances to ideal and anti-ideal solutions
        
        Args:
            weighted_matrix: Weighted normalized matrix
            ideal: Ideal solution vector
            anti_ideal: Anti-ideal solution vector
        
        Returns:
            Tuple of (distances_to_ideal, distances_to_anti_ideal)
        """
        dist_ideal = np.sqrt(((weighted_matrix - ideal) ** 2).sum(axis=1))
        dist_anti_ideal = np.sqrt(((weighted_matrix - anti_ideal) ** 2).sum(axis=1))
        
        return dist_ideal.values, dist_anti_ideal.values
    
    def calculate_relative_closeness(
        self,
        dist_ideal: np.ndarray,
        dist_anti_ideal: np.ndarray
    ) -> np.ndarray:
        """
        Calculate relative closeness coefficient (final TOPSIS score)
        
        Score = distance_to_anti_ideal / (distance_to_ideal + distance_to_anti_ideal)
        
        Args:
            dist_ideal: Distances to ideal solution
            dist_anti_ideal: Distances to anti-ideal solution
        
        Returns:
            Relative closeness scores (0 to 1, higher is better)
        """
        denominator = dist_ideal + dist_anti_ideal
        # Avoid division by zero
        scores = np.where(
            denominator > 0,
            dist_anti_ideal / denominator,
            0
        )
        return scores
    
    def rank_plans(self, plans: List[Dict], top_n: int = 3) -> List[Dict]:
        """
        Rank insurance plans using TOPSIS algorithm
        
        Args:
            plans: List of insurance plan dictionaries
            top_n: Number of top recommendations to return
        
        Returns:
            List of ranked plans with scores and component details
        """
        if not plans:
            logger.warning("No plans to rank")
            return []
        
        # Step 1: Prepare decision matrix
        matrix, plan_ids = self.prepare_decision_matrix(plans)
        
        # Step 2: Normalize matrix
        normalized = self.normalize_matrix(matrix)
        
        # Step 3: Apply weights
        weighted = self.apply_weights(normalized)
        
        # Step 4: Calculate ideal solutions
        ideal, anti_ideal = self.calculate_ideal_solutions(weighted)
        
        # Step 5: Calculate distances
        dist_ideal, dist_anti_ideal = self.calculate_distances(
            weighted, ideal, anti_ideal
        )
        
        # Step 6: Calculate relative closeness (final scores)
        scores = self.calculate_relative_closeness(dist_ideal, dist_anti_ideal)
        
        # Step 7: Rank and prepare results
        ranked_indices = np.argsort(scores)[::-1]  # Descending order
        
        results = []
        for rank, idx in enumerate(ranked_indices[:top_n], start=1):
            plan = plans[idx].copy()
            plan['final_score'] = float(scores[idx])
            plan['rank'] = rank
            
            # Add component scores for explainability
            plan['component_scores'] = {
                'cost': {
                    'raw': float(matrix.iloc[idx]['cost']),
                    'normalized': float(normalized.iloc[idx]['cost']),
                    'weighted': float(weighted.iloc[idx]['cost']),
                    'weight': self.weights['cost']
                },
                'coverage': {
                    'raw': float(matrix.iloc[idx]['coverage']),
                    'normalized': float(normalized.iloc[idx]['coverage']),
                    'weighted': float(weighted.iloc[idx]['coverage']),
                    'weight': self.weights['coverage']
                },
                'service': {
                    'raw': float(matrix.iloc[idx]['service']),
                    'normalized': float(normalized.iloc[idx]['service']),
                    'weighted': float(weighted.iloc[idx]['service']),
                    'weight': self.weights['service']
                },
                'reliability': {
                    'raw': float(matrix.iloc[idx]['reliability']),
                    'normalized': float(normalized.iloc[idx]['reliability']),
                    'weighted': float(weighted.iloc[idx]['reliability']),
                    'weight': self.weights['reliability']
                }
            }
            
            results.append(plan)
        
        logger.info(f"Ranked {len(results)} plans using TOPSIS")
        return results
    
    def generate_rationale(self, plan: Dict) -> str:
        """
        Generate human-readable rationale for recommendation
        
        Args:
            plan: Ranked plan with component scores
        
        Returns:
            Rationale string
        """
        scores = plan.get('component_scores', {})
        
        # Find strongest criteria
        weighted_scores = {
            k: v['weighted'] for k, v in scores.items()
        }
        top_criterion = max(weighted_scores, key=weighted_scores.get)
        
        rationales = {
            'cost': "Offers excellent premium value",
            'coverage': "Provides comprehensive coverage",
            'service': "Demonstrates strong service quality and claim handling",
            'reliability': "Shows high customer retention and low complaints"
        }
        
        base_rationale = rationales.get(top_criterion, "Balanced overall performance")
        
        return f"{base_rationale}. Overall score: {plan['final_score']:.3f}"

