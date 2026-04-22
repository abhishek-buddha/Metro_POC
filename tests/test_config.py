import pytest
from src.utils.config import Config


def test_config_loads_from_environment(monkeypatch):
    monkeypatch.setenv('REDIS_URL', 'redis://localhost:6379')
    monkeypatch.setenv('ANTHROPIC_API_KEY', 'test-key')
    monkeypatch.setenv('TWILIO_ACCOUNT_SID', 'test-sid')
    monkeypatch.setenv('TWILIO_AUTH_TOKEN', 'test-token')
    monkeypatch.setenv('TWILIO_WHATSAPP_NUMBER', 'test-number')
    monkeypatch.setenv('ENCRYPTION_KEY', 'test-encryption-key')
    monkeypatch.setenv('API_KEY', 'test-api-key')

    config = Config()
    assert config.REDIS_URL == 'redis://localhost:6379'
    assert config.ANTHROPIC_API_KEY == 'test-key'


def test_config_raises_on_missing_required(monkeypatch):
    # Clear all required environment variables
    monkeypatch.delenv('REDIS_URL', raising=False)
    monkeypatch.delenv('ANTHROPIC_API_KEY', raising=False)
    monkeypatch.delenv('TWILIO_ACCOUNT_SID', raising=False)
    monkeypatch.delenv('TWILIO_AUTH_TOKEN', raising=False)
    monkeypatch.delenv('TWILIO_WHATSAPP_NUMBER', raising=False)
    monkeypatch.delenv('ENCRYPTION_KEY', raising=False)
    monkeypatch.delenv('API_KEY', raising=False)

    with pytest.raises(ValueError):
        Config()
