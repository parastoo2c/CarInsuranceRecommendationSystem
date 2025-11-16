"""
LLM-based extraction of insurance plan data from text or URLs

This module integrates with open-source LLM APIs (Hugging Face, Together AI)
to extract structured insurance plan data from unstructured sources.
"""

import requests
import re
import logging
from typing import Dict, Optional, List
from config import Config

logger = logging.getLogger(__name__)


class LLMExtractor:
    """
    Extract insurance plan details using LLM APIs
    
    Supports:
    - Hugging Face Inference API
    - Together AI API
    - Local text parsing (fallback)
    """
    
    def __init__(self):
        self.hf_api_key = Config.HUGGINGFACE_API_KEY
        self.together_api_key = Config.TOGETHER_AI_API_KEY
    
    def extract_from_text(self, text: str, insurer_hint: Optional[str] = None) -> Dict:
        """
        Extract insurance plan data from text content
        
        Args:
            text: Raw text content (brochure, website copy, etc.)
            insurer_hint: Optional insurer name hint
        
        Returns:
            Extracted plan data dictionary
        """
        logger.info("Extracting insurance data from text")
        
        # Try LLM-based extraction if API keys are available
        if self.hf_api_key:
            try:
                return self._extract_with_huggingface(text, insurer_hint)
            except Exception as e:
                logger.warning(f"Hugging Face extraction failed: {e}")
        
        if self.together_api_key:
            try:
                return self._extract_with_together(text, insurer_hint)
            except Exception as e:
                logger.warning(f"Together AI extraction failed: {e}")
        
        # Fallback to rule-based extraction
        logger.info("Using fallback rule-based extraction")
        return self._extract_with_rules(text, insurer_hint)
    
    def extract_from_url(self, url: str, insurer_hint: Optional[str] = None) -> Dict:
        """
        Extract insurance plan data from a URL
        
        Args:
            url: Website URL to extract from
            insurer_hint: Optional insurer name hint
        
        Returns:
            Extracted plan data dictionary
        """
        logger.info(f"Extracting insurance data from URL: {url}")
        
        try:
            # Fetch webpage content
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Insurance Recommender Bot)'
            })
            response.raise_for_status()
            
            # Extract text from HTML (simple approach)
            text = self._clean_html(response.text)
            
            # Extract using text method
            result = self.extract_from_text(text, insurer_hint)
            result['source_url'] = url
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to extract from URL: {e}")
            return {
                'error': str(e),
                'insurer_name': insurer_hint or 'Unknown',
                'extraction_confidence': 0.0
            }
    
    def _extract_with_huggingface(self, text: str, insurer_hint: Optional[str]) -> Dict:
        """Extract using Hugging Face Inference API"""
        
        # Create extraction prompt
        prompt = self._build_extraction_prompt(text, insurer_hint)
        
        # Call Hugging Face API (using a suitable model)
        api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
        
        headers = {"Authorization": f"Bearer {self.hf_api_key}"}
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 500,
                "temperature": 0.3,
                "return_full_text": False
            }
        }
        
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        # Parse LLM output
        if isinstance(result, list) and len(result) > 0:
            generated_text = result[0].get('generated_text', '')
            return self._parse_llm_output(generated_text, insurer_hint)
        
        raise ValueError("Invalid response from Hugging Face API")
    
    def _extract_with_together(self, text: str, insurer_hint: Optional[str]) -> Dict:
        """Extract using Together AI API"""
        
        prompt = self._build_extraction_prompt(text, insurer_hint)
        
        api_url = "https://api.together.xyz/v1/completions"
        
        headers = {
            "Authorization": f"Bearer {self.together_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "mistralai/Mistral-7B-Instruct-v0.2",
            "prompt": prompt,
            "max_tokens": 500,
            "temperature": 0.3
        }
        
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        generated_text = result['choices'][0]['text']
        
        return self._parse_llm_output(generated_text, insurer_hint)
    
    def _extract_with_rules(self, text: str, insurer_hint: Optional[str]) -> Dict:
        """
        Fallback rule-based extraction using regex patterns
        
        This is a simple baseline that looks for common patterns in insurance text
        """
        extracted = {
            'insurer_name': insurer_hint or self._extract_insurer(text),
            'plan_name': self._extract_plan_name(text),
            'premium_annual': self._extract_premium(text),
            'idv': self._extract_idv(text),
            'add_ons': self._extract_add_ons(text),
            'evidence_snippets': self._extract_evidence(text),
            'extraction_confidence': 0.6  # Lower confidence for rule-based
        }
        
        return extracted
    
    def _build_extraction_prompt(self, text: str, insurer_hint: Optional[str]) -> str:
        """Build prompt for LLM extraction"""
        
        prompt = f"""Extract insurance plan details from the following text. Return a structured JSON response.

Text:
{text[:2000]}  

Extract these fields:
- insurer_name: Name of insurance company
- plan_name: Name of the insurance plan
- premium_annual: Annual premium in dollars (number only)
- idv: Insured Declared Value in dollars (number only)
- add_ons: List of add-on coverages
- claim_tat_days: Claim turnaround time in days
- claim_approval_rate_pct: Claim approval rate as percentage

Return ONLY valid JSON, no additional text.
"""
        
        if insurer_hint:
            prompt += f"\nNote: The insurer is likely {insurer_hint}\n"
        
        return prompt
    
    def _parse_llm_output(self, text: str, insurer_hint: Optional[str]) -> Dict:
        """Parse LLM output and extract structured data"""
        
        import json
        
        try:
            # Try to parse as JSON
            # Look for JSON block in text
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                data['extraction_confidence'] = 0.85
                return data
        except:
            pass
        
        # Fallback: parse text manually
        return self._extract_with_rules(text, insurer_hint)
    
    # Helper methods for rule-based extraction
    
    def _extract_insurer(self, text: str) -> str:
        """Extract insurer name"""
        # Common insurer names
        insurers = ['State Farm', 'Geico', 'Progressive', 'Allstate', 'USAA', 
                   'Farmers', 'Liberty Mutual', 'Nationwide']
        
        text_lower = text.lower()
        for insurer in insurers:
            if insurer.lower() in text_lower:
                return insurer
        
        return 'Unknown'
    
    def _extract_plan_name(self, text: str) -> str:
        """Extract plan name"""
        patterns = [
            r'(?:Plan|Coverage|Policy):\s*([A-Z][A-Za-z\s]+)',
            r'([A-Z][a-z]+\s+(?:Plan|Coverage|Policy))'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        return 'Standard Plan'
    
    def _extract_premium(self, text: str) -> Optional[float]:
        """Extract annual premium"""
        patterns = [
            r'\$?([\d,]+)\s*(?:per\s+year|annual|yearly)',
            r'(?:Premium|Cost):\s*\$?([\d,]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1).replace(',', ''))
                except:
                    pass
        
        return None
    
    def _extract_idv(self, text: str) -> Optional[float]:
        """Extract IDV (Insured Declared Value)"""
        patterns = [
            r'IDV:\s*\$?([\d,]+)',
            r'Insured\s+Value:\s*\$?([\d,]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1).replace(',', ''))
                except:
                    pass
        
        return None
    
    def _extract_add_ons(self, text: str) -> List[str]:
        """Extract add-on coverages"""
        add_ons = []
        
        keywords = [
            'Zero Depreciation', 'Roadside Assistance', 'Engine Protection',
            'Personal Accident Cover', 'NCB Protection', 'Consumables Cover'
        ]
        
        text_lower = text.lower()
        for keyword in keywords:
            if keyword.lower() in text_lower:
                add_ons.append(keyword)
        
        return add_ons
    
    def _extract_evidence(self, text: str) -> List[str]:
        """Extract relevant evidence snippets"""
        # Extract sentences containing key insurance terms
        sentences = re.split(r'[.!?]', text)
        evidence = []
        
        keywords = ['premium', 'coverage', 'claim', 'deductible', 'idv']
        
        for sentence in sentences[:20]:  # Limit to first 20 sentences
            if any(kw in sentence.lower() for kw in keywords):
                evidence.append(sentence.strip())
                if len(evidence) >= 3:
                    break
        
        return evidence
    
    def _clean_html(self, html: str) -> str:
        """Simple HTML cleaning to extract text"""
        # Remove script and style tags
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', html)
        
        # Clean whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()

