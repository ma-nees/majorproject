# risk_engine/rule_based_checks.py
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class RuleBasedChecker:
    """
    Applies a set of predefined heuristic rules.
    Each rule returns a violation string if triggered, else None.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        config can override rule parameters like max_amount, velocity_window, etc.
        """
        self.config = config or {}
        self.max_amount_normal = self.config.get('max_amount_normal', 10000.0)
        self.max_amount_suspicious = self.config.get('max_amount_suspicious', 50000.0)
        self.velocity_window_minutes = self.config.get('velocity_window_minutes', 60)
        self.max_transactions_per_window = self.config.get('max_transactions_per_window', 5)
        self.night_hours = self.config.get('night_hours', (0, 6))  # 12am-6am
        self.blacklisted_countries = self.config.get('blacklisted_countries', ['XX', 'YY'])
        self.blacklisted_devices = set(self.config.get('blacklisted_devices', []))
    
    def check_amount(self, amount: float) -> Optional[str]:
        """Rule: amount exceeds thresholds."""
        if amount > self.max_amount_suspicious:
            return f"AMOUNT_EXTREME: {amount} > {self.max_amount_suspicious}"
        elif amount > self.max_amount_normal:
            return f"AMOUNT_HIGH: {amount} > {self.max_amount_normal}"
        return None
    
    def check_velocity(self, user_id: str, current_time: datetime,
                       transaction_history: List[Dict]) -> Optional[str]:
        """
        Rule: too many transactions in recent window.
        Requires a history of user transactions (could be from behavior_monitor).
        """
        cutoff = current_time - timedelta(minutes=self.velocity_window_minutes)
        recent = [t for t in transaction_history if t['timestamp'] >= cutoff]
        if len(recent) >= self.max_transactions_per_window:
            return f"VELOCITY_HIGH: {len(recent)} txns in last {self.velocity_window_minutes} min"
        return None
    
    def check_time(self, timestamp: datetime) -> Optional[str]:
        """Rule: transaction at unusual hour (night)."""
        hour = timestamp.hour
        if self.night_hours[0] <= hour < self.night_hours[1]:
            return f"UNUSUAL_HOUR: transaction at {hour}:00"
        return None
    
    def check_country(self, country_code: str) -> Optional[str]:
        """Rule: transaction from blacklisted country."""
        if country_code and country_code.upper() in self.blacklisted_countries:
            return f"BLACKLISTED_COUNTRY: {country_code}"
        return None
    
    def check_device(self, device_id: str) -> Optional[str]:
        """Rule: device is blacklisted (known fraud device)."""
        if device_id and device_id in self.blacklisted_devices:
            return f"BLACKLISTED_DEVICE: {device_id}"
        return None
    
    def check_ip_risk(self, ip_address: str, proxy_check_service=None) -> Optional[str]:
        """
        Optional: check if IP is a known proxy/VPN.
        Placeholder – integrate with external API if needed.
        """
        # In production, call a service like ipinfo.io or maxmind
        return None
    
    def check_all(self, transaction: Dict[str, Any],
                  transaction_history: Optional[List[Dict]] = None) -> List[str]:
        """
        Run all rules on a transaction.
        Returns list of violation strings.
        """
        violations = []
        
        # Amount rule
        amount = transaction.get('amount', 0)
        v = self.check_amount(amount)
        if v:
            violations.append(v)
        
        # Time rule
        ts = transaction.get('timestamp')
        if ts:
            if isinstance(ts, str):
                ts = datetime.fromisoformat(ts)
            v = self.check_time(ts)
            if v:
                violations.append(v)
        
        # Country rule
        country = transaction.get('country_code') or transaction.get('location')
        if country:
            v = self.check_country(country)
            if v:
                violations.append(v)
        
        # Device rule
        device = transaction.get('device_id')
        if device:
            v = self.check_device(device)
            if v:
                violations.append(v)
        
        # Velocity rule (requires history)
        user_id = transaction.get('user_id')
        if user_id and transaction_history is not None:
            ts = transaction.get('timestamp')
            if ts and isinstance(ts, str):
                ts = datetime.fromisoformat(ts)
            v = self.check_velocity(user_id, ts, transaction_history)
            if v:
                violations.append(v)
        
        return violations
    
    def calculate_rule_score(self, violations: List[str]) -> float:
        """
        Convert list of violations to a rule score (0-100).
        More severe rules give higher scores.
        """
        if not violations:
            return 0.0
        
        score = 0.0
        for v in violations:
            if "EXTREME" in v:
                score += 40
            elif "HIGH" in v or "VELOCITY" in v:
                score += 25
            elif "BLACKLISTED" in v:
                score += 30
            else:
                score += 15
        # Cap at 100
        return min(100.0, score)


# Singleton for easy import
_rule_checker = None

def get_rule_checker() -> RuleBasedChecker:
    global _rule_checker
    if _rule_checker is None:
        _rule_checker = RuleBasedChecker()
    return _rule_checker