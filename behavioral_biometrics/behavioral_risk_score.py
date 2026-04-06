"""
Behavioral Risk Score Calculator
Combines anomalies from keystroke, mouse, and touch analysis into a unified risk score.
"""

import numpy as np
from typing import Dict, Any, List, Optional

class BehavioralRiskScorer:
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """
        Initialize with configurable weights for each modality.
        
        Default weights:
            keystroke: 0.4
            mouse: 0.35
            touch: 0.25
        """
        self.weights = weights or {
            "keystroke": 0.4,
            "mouse": 0.35,
            "touch": 0.25
        }
    
    def calculate_risk(self, behavioral_data: Dict[str, Any]) -> float:
        """
        Calculate overall behavioral risk score (0 to 1).
        
        Args:
            behavioral_data: Dictionary containing:
                - keystrokes: dict from KeystrokeAnalyzer
                - mouse: dict from MouseAnalyzer
                - touch: dict from TouchAnalyzer
                - session: optional session context
        Returns:
            Risk score between 0 (normal) and 1 (high risk)
        """
        modality_scores = {}
        
        # Keystroke risk
        if 'keystrokes' in behavioral_data:
            ks = behavioral_data['keystrokes']
            ks_risk = self._score_keystroke_anomalies(ks)
            modality_scores['keystroke'] = ks_risk
        
        # Mouse risk
        if 'mouse' in behavioral_data:
            ms = behavioral_data['mouse']
            ms_risk = self._score_mouse_anomalies(ms)
            modality_scores['mouse'] = ms_risk
        
        # Touch risk
        if 'touch' in behavioral_data:
            tc = behavioral_data['touch']
            tc_risk = self._score_touch_anomalies(tc)
            modality_scores['touch'] = tc_risk
        
        # Weighted average
        total_weight = 0
        weighted_sum = 0
        for modality, risk in modality_scores.items():
            w = self.weights.get(modality, 0.2)
            weighted_sum += risk * w
            total_weight += w
        
        if total_weight == 0:
            return 0.0
        
        base_risk = weighted_sum / total_weight
        
        # Boost risk if multiple modalities show anomalies
        anomaly_count = sum(1 for v in modality_scores.values() if v > 0.5)
        if anomaly_count >= 2:
            base_risk = min(base_risk * 1.3, 1.0)
        
        # Apply sigmoid for smoother gradient (optional)
        # risk = 1 / (1 + np.exp(-10*(base_risk - 0.5)))
        
        return round(base_risk, 4)
    
    def _score_keystroke_anomalies(self, ks_analysis: Dict) -> float:
        """Convert keystroke anomalies to a risk score."""
        anomalies = ks_analysis.get('anomalies', [])
        if not anomalies:
            return 0.0
        
        # Weight different anomaly types
        high_risk_keywords = ['bot', 'macro', 'script', 'extremely fast', 'no flight']
        medium_risk_keywords = ['inconsistent', 'slow', 'long pause']
        
        score = 0.0
        for anomaly in anomalies:
            anomaly_lower = anomaly.lower()
            if any(kw in anomaly_lower for kw in high_risk_keywords):
                score += 0.35
            elif any(kw in anomaly_lower for kw in medium_risk_keywords):
                score += 0.2
            else:
                score += 0.1
        
        # Cap at 1.0
        return min(score, 1.0)
    
    def _score_mouse_anomalies(self, mouse_analysis: Dict) -> float:
        """Convert mouse anomalies to a risk score."""
        anomalies = mouse_analysis.get('anomalies', [])
        if not anomalies:
            return 0.0
        
        high_risk = ['script', 'automation', 'impossibly high', 'perfectly straight']
        medium_risk = ['erratic', 'rapid clicking']
        
        score = 0.0
        for anomaly in anomalies:
            anomaly_lower = anomaly.lower()
            if any(kw in anomaly_lower for kw in high_risk):
                score += 0.4
            elif any(kw in anomaly_lower for kw in medium_risk):
                score += 0.25
            else:
                score += 0.1
        
        return min(score, 1.0)
    
    def _score_touch_anomalies(self, touch_analysis: Dict) -> float:
        """Convert touch anomalies to a risk score."""
        anomalies = touch_analysis.get('anomalies', [])
        if not anomalies:
            return 0.0
        
        high_risk = ['robot', 'automation', 'stylus', 'fast swipe']
        medium_risk = ['repetitive', 'multi-touch']
        
        score = 0.0
        for anomaly in anomalies:
            anomaly_lower = anomaly.lower()
            if any(kw in anomaly_lower for kw in high_risk):
                score += 0.4
            elif any(kw in anomaly_lower for kw in medium_risk):
                score += 0.25
            else:
                score += 0.1
        
        return min(score, 1.0)
    
    def get_risk_level(self, risk_score: float) -> str:
        """Map numeric risk score to human-readable level."""
        if risk_score >= 0.7:
            return "critical"
        elif risk_score >= 0.5:
            return "high"
        elif risk_score >= 0.3:
            return "medium"
        else:
            return "low"