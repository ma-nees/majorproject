# services/alert_service/fraud_alerts.py
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import json
from pathlib import Path

from .notification_engine import NotificationEngine, Alert, NotificationChannel, get_notification_engine

logger = logging.getLogger(__name__)

@dataclass
class AlertRecord:
    """Stored alert for audit/logging."""
    alert_id: str
    title: str
    message: str
    severity: str
    triggered_at: str
    channel: str
    metadata: Dict

class FraudAlertManager:
    """
    Evaluates alert conditions and triggers notifications.
    Also stores alert history for later review.
    """
    
    def __init__(self, config: Optional[Dict] = None,
                 engine: Optional[NotificationEngine] = None):
        self.config = config or {}
        self.engine = engine or get_notification_engine()
        self.storage_dir = Path(self.config.get("storage_dir", "monitoring/data/alerts"))
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.alert_history_file = self.storage_dir / "alert_history.jsonl"
        
        # Alert thresholds
        self.high_risk_threshold = self.config.get("high_risk_threshold", 85)
        self.critical_risk_threshold = self.config.get("critical_risk_threshold", 95)
        self.velocity_alert_window = self.config.get("velocity_alert_window_minutes", 5)
        self.max_alerts_per_window = self.config.get("max_alerts_per_window", 10)
    
    async def check_transaction_risk(self, decision: Dict[str, Any]) -> Optional[Alert]:
        """
        Trigger alert if transaction risk score exceeds threshold.
        decision: output from risk_engine.decision_engine.evaluate_transaction
        """
        risk_score = decision.get("risk_score", 0)
        action = decision.get("action", "")
        tx_id = decision.get("transaction_id", "unknown")
        
        if risk_score >= self.critical_risk_threshold:
            title = f"CRITICAL RISK Transaction {tx_id}"
            message = f"Risk score {risk_score:.1f} exceeded critical threshold. Action: {action}"
            severity = "critical"
            channel = NotificationChannel.SLACK  # or EMAIL/WEBHOOK
            return Alert(title, message, severity, channel, metadata=decision)
        elif risk_score >= self.high_risk_threshold:
            title = f"HIGH RISK Transaction {tx_id}"
            message = f"Risk score {risk_score:.1f} above high threshold. Action: {action}"
            severity = "warning"
            channel = NotificationChannel.CONSOLE
            return Alert(title, message, severity, channel, metadata=decision)
        return None
    
    async def check_model_performance_drop(self, recent_recall: float,
                                           baseline_recall: float,
                                           threshold_drop: float = 0.05) -> Optional[Alert]:
        """
        Alert if model recall drops below baseline by threshold_drop.
        Should be called periodically (e.g., every hour) by a scheduler.
        """
        if baseline_recall - recent_recall > threshold_drop:
            title = "Model Performance Degradation"
            message = f"Recall dropped from {baseline_recall:.3f} to {recent_recall:.3f} (Δ = {baseline_recall - recent_recall:.3f})"
            severity = "warning"
            channel = NotificationChannel.EMAIL
            return Alert(title, message, severity, channel,
                         metadata={"baseline": baseline_recall, "recent": recent_recall})
        return None
    
    async def check_system_health(self, cpu_percent: float, memory_percent: float,
                                   error_rate: float) -> Optional[Alert]:
        """Alert on system resource issues."""
        alerts = []
        if cpu_percent > 85:
            alerts.append(Alert("High CPU Usage", f"CPU at {cpu_percent:.1f}%", "warning",
                                NotificationChannel.CONSOLE))
        if memory_percent > 90:
            alerts.append(Alert("High Memory Usage", f"Memory at {memory_percent:.1f}%", "warning",
                                NotificationChannel.CONSOLE))
        if error_rate > 0.05:  # >5% errors
            alerts.append(Alert("High Error Rate", f"Error rate {error_rate:.3f}", "critical",
                                NotificationChannel.SLACK))
        # Return the most severe (or first)
        return alerts[0] if alerts else None
    
    async def trigger_alert(self, alert: Alert) -> bool:
        """Send alert and store it in history."""
        success = await self.engine.send_async(alert)
        if success:
            self._store_alert(alert)
        return success
    
    def _store_alert(self, alert: Alert):
        """Append alert to JSON lines file for audit."""
        record = AlertRecord(
            alert_id=f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{hash(alert.title)}",
            title=alert.title,
            message=alert.message,
            severity=alert.severity,
            triggered_at=datetime.now().isoformat(),
            channel=alert.channel.value,
            metadata=alert.metadata or {}
        )
        with open(self.alert_history_file, 'a') as f:
            f.write(json.dumps(asdict(record)) + "\n")
        logger.info(f"Alert stored: {alert.title}")
    
    def get_recent_alerts(self, hours: int = 24) -> List[Dict]:
        """Read recent alerts from history."""
        if not self.alert_history_file.exists():
            return []
        cutoff = datetime.now().timestamp() - hours * 3600
        alerts = []
        with open(self.alert_history_file, 'r') as f:
            for line in f:
                record = json.loads(line)
                ts = datetime.fromisoformat(record['triggered_at']).timestamp()
                if ts >= cutoff:
                    alerts.append(record)
        return alerts


# Singleton instance
_alert_manager = None

def get_alert_manager() -> FraudAlertManager:
    global _alert_manager
    if _alert_manager is None:
        _alert_manager = FraudAlertManager()
    return _alert_manager