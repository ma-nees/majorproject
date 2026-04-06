import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Any
import json
from datetime import datetime

# Configure structured logger
logger = logging.getLogger("fraudshield_api")
logger.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all incoming requests and their responses.
    Includes timing, status codes, and request/response bodies (sanitized).
    """
    async def dispatch(self, request: Request, call_next):
        # Start timer
        start_time = time.time()
        
        # Log request
        request_body = await self._get_request_body(request)
        sanitized_body = self._sanitize_sensitive_data(request_body)
        
        logger.info(f"REQUEST: {request.method} {request.url.path} | Body: {sanitized_body}")
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log response
        logger.info(
            f"RESPONSE: {request.method} {request.url.path} | "
            f"Status: {response.status_code} | Duration: {duration:.3f}s"
        )
        
        # Add custom headers
        response.headers["X-Response-Time"] = f"{duration:.3f}s"
        
        return response
    
    async def _get_request_body(self, request: Request) -> Dict[str, Any]:
        """Extract and parse request body without consuming it."""
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                # Reattach body for further processing
                async def receive():
                    return {"type": "http.request", "body": body}
                request._receive = receive
                return json.loads(body.decode()) if body else {}
            except Exception:
                return {}
        return {}
    
    def _sanitize_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive fields like passwords, tokens, etc."""
        if not data:
            return data
        sensitive_keys = ["password", "token", "secret", "authorization", "api_key"]
        sanitized = data.copy()
        for key in sensitive_keys:
            if key in sanitized:
                sanitized[key] = "***REDACTED***"
        return sanitized

# Optional: Function to log fraud events separately
def log_fraud_event(transaction_id: str, risk_score: float, decision: str):
    """Log fraud detection events to a dedicated logger."""
    fraud_logger = logging.getLogger("fraud_events")
    fraud_logger.setLevel(logging.WARNING)
    # Add file handler if needed
    fraud_logger.warning(
        json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "transaction_id": transaction_id,
            "risk_score": risk_score,
            "decision": decision
        })
    )