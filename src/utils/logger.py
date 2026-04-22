import logging
import json
import sys
from datetime import datetime

# Import config, handling both cases: when it's available and when it's not
try:
    from src.utils.config import config, get_config
    if config is not None:
        LOG_LEVEL = config.LOG_LEVEL
    else:
        LOG_LEVEL = 'INFO'
except (ImportError, ValueError):
    LOG_LEVEL = 'INFO'


class JSONFormatter(logging.Formatter):
    """Format logs as JSON for structured logging"""

    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "level": record.levelname,
            "service": getattr(record, 'service', 'kyc-system'),
            "message": record.getMessage(),
            "job_id": getattr(record, 'job_id', None),
            "phone_number": getattr(record, 'phone_number', None),
            "doc_type": getattr(record, 'doc_type', None),
            "confidence": getattr(record, 'confidence', None)
        }

        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def setup_logger(name: str) -> logging.Logger:
    """Setup logger with JSON formatting"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL))

    # Remove existing handlers
    logger.handlers = []

    # Console handler with JSON formatting
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)

    return logger


# Global logger instance
logger = setup_logger('kyc')
