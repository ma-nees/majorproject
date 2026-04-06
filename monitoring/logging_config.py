# monitoring/logging_config.py
import logging
import logging.config
import json
import sys
from pathlib import Path
from datetime import datetime

# JSON formatter for structured logging (good for ELK, Splunk)
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        # Add any extra attributes
        for key, value in record.__dict__.items():
            if key not in ['args', 'asctime', 'created', 'exc_info', 'exc_text', 'filename',
                           'funcName', 'id', 'levelname', 'levelno', 'lineno', 'module',
                           'msecs', 'message', 'msg', 'name', 'pathname', 'process',
                           'processName', 'relativeCreated', 'stack_info', 'thread', 'threadName']:
                log_entry[key] = value
        return json.dumps(log_entry)


def setup_logging(log_level: str = "INFO", 
                  log_to_file: bool = True,
                  log_to_console: bool = True,
                  json_format: bool = True):
    """
    Configure logging for the entire application.
    Call this once at startup (e.g., in api/main.py).
    """
    log_dir = Path("logs")
    if log_to_file:
        log_dir.mkdir(exist_ok=True)
    
    handlers = []
    if log_to_console:
        handlers.append("console")
    if log_to_file:
        handlers.append("file")
    
    formatter = "json" if json_format else "standard"
    
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
            "json": {
                "()": JSONFormatter
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": formatter,
                "stream": sys.stdout
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": log_level,
                "formatter": formatter,
                "filename": log_dir / "fraud_detection.log",
                "maxBytes": 10485760,  # 10 MB
                "backupCount": 5,
                "encoding": "utf8"
            }
        },
        "loggers": {
            "": {  # root logger
                "handlers": handlers,
                "level": log_level,
                "propagate": True
            },
            "uvicorn": {
                "handlers": handlers,
                "level": "INFO",
                "propagate": False
            },
            "ml_pipeline": {
                "handlers": handlers,
                "level": log_level,
                "propagate": False
            },
            "anomaly_detection": {
                "handlers": handlers,
                "level": log_level,
                "propagate": False
            },
            "risk_engine": {
                "handlers": handlers,
                "level": log_level,
                "propagate": False
            }
        }
    }
    
    logging.config.dictConfig(config)
    
    # Optional: add a startup log message
    logger = logging.getLogger(__name__)
    logger.info("Logging configured with level=%s, file=%s, console=%s, json=%s",
                log_level, log_to_file, log_to_console, json_format)


def get_logger(name: str) -> logging.Logger:
    """Convenience function to get a logger instance."""
    return logging.getLogger(name)


# Example usage in any module:
# from monitoring.logging_config import get_logger
# logger = get_logger(__name__)
# logger.info("Transaction processed", extra={"transaction_id": "123", "amount": 100})