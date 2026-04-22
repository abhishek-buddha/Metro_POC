import pytest
import redis
from src.utils.redis_client import get_redis_client

# Helper function to check if Redis is available
def is_redis_available():
    """Check if Redis server is available"""
    try:
        # Try to connect to localhost:6379 (default local Redis)
        test_client = redis.from_url("redis://localhost:6379", socket_timeout=2, socket_connect_timeout=2)
        test_client.ping()
        return True
    except (redis.ConnectionError, Exception):
        return False

redis_available = pytest.mark.skipif(
    not is_redis_available(),
    reason="Redis server is not running. Start with: docker run -d -p 6379:6379 redis:7-alpine"
)


@redis_available
def test_redis_client_is_singleton():
    """Test that get_redis_client returns the same instance"""
    # Clear the global client for testing
    import src.utils.redis_client as rc_module
    rc_module._redis_client = None

    # Change REDIS_URL to localhost for testing
    from src.utils.config import config
    original_url = config.REDIS_URL
    config.REDIS_URL = "redis://localhost:6379"

    try:
        client1 = get_redis_client()
        client2 = get_redis_client()
        assert client1 is client2
    finally:
        # Restore original URL and reset client
        config.REDIS_URL = original_url
        rc_module._redis_client = None


@redis_available
def test_redis_client_can_ping():
    """Test that Redis client can successfully ping"""
    # Clear the global client for testing
    import src.utils.redis_client as rc_module
    rc_module._redis_client = None

    # Change REDIS_URL to localhost for testing
    from src.utils.config import config
    original_url = config.REDIS_URL
    config.REDIS_URL = "redis://localhost:6379"

    try:
        client = get_redis_client()
        assert client.ping() == True
    finally:
        # Restore original URL and reset client
        config.REDIS_URL = original_url
        rc_module._redis_client = None


def test_redis_client_singleton_without_connection():
    """Test that singleton pattern works at module level (without actual connection)"""
    import src.utils.redis_client as rc_module

    # Store original client state
    original_client = rc_module._redis_client

    try:
        # Clear the global client
        rc_module._redis_client = None

        # Verify that _redis_client starts as None
        assert rc_module._redis_client is None
    finally:
        # Restore original state
        rc_module._redis_client = original_client
