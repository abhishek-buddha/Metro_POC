import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration loaded from environment variables"""

    def __init__(self):
        # Redis
        self.REDIS_URL = self._get_required('REDIS_URL')

        # OpenAI
        self.OPENAI_API_KEY = self._get_required('OPENAI_API_KEY')

        # Twilio
        self.TWILIO_ACCOUNT_SID = self._get_required('TWILIO_ACCOUNT_SID')
        self.TWILIO_AUTH_TOKEN = self._get_required('TWILIO_AUTH_TOKEN')
        self.TWILIO_WHATSAPP_NUMBER = self._get_required('TWILIO_WHATSAPP_NUMBER')

        # Security
        self.ENCRYPTION_KEY = self._get_required('ENCRYPTION_KEY')
        self.API_KEY = self._get_required('API_KEY')

        # Database & Storage
        self.DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/kyc.db')
        self.UPLOADS_PATH = os.getenv('UPLOADS_PATH', 'uploads')

        # Logging
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    def _get_required(self, key: str) -> str:
        """Get required environment variable or raise error"""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable {key} is not set")
        return value


# Global config instance (lazy-loaded)
_config_instance = None


def get_config() -> Config:
    """Get or create global config instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance


# For backward compatibility, attempt to create config instance
# This will fail if required variables are not set, which is expected in testing
try:
    config = Config()
except ValueError:
    # Allow module to be imported even if config fails
    # This is needed for tests that need to set environment variables first
    config = None
