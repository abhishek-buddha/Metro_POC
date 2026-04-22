"""
Tests for FastAPI webhook application.

This module tests:
- WhatsApp webhook endpoint with Twilio signature verification
- REST API endpoints for KYC submission management
- Health check endpoint
- Authentication and error handling
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime, timezone
import json
import uuid
from io import BytesIO
from sqlalchemy.exc import IntegrityError

from src.webhook.app import app, get_db
from src.models.database import Employee, KYCSubmission, Document, AuditLog


@pytest.fixture
def test_client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def mock_redis():
    """Mock Redis client"""
    redis_mock = MagicMock()
    redis_mock.ping.return_value = True
    redis_mock.hset.return_value = 1
    redis_mock.expire.return_value = 1
    redis_mock.rpush.return_value = 1
    return redis_mock


@pytest.fixture
def mock_db_session():
    """Mock database session"""
    session_mock = MagicMock()
    session_mock.query.return_value = session_mock
    session_mock.filter.return_value = session_mock
    session_mock.filter_by.return_value = session_mock
    session_mock.first.return_value = None
    session_mock.all.return_value = []
    session_mock.count.return_value = 0
    session_mock.offset.return_value = session_mock
    session_mock.limit.return_value = session_mock
    session_mock.order_by.return_value = session_mock
    return session_mock


@pytest.fixture
def sample_employee():
    """Sample employee record"""
    emp = Employee(
        id=str(uuid.uuid4()),
        phone_number="+919876543210",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    return emp


@pytest.fixture
def sample_submission(sample_employee):
    """Sample KYC submission"""
    submission = KYCSubmission(
        id=str(uuid.uuid4()),
        employee_id=sample_employee.id,
        status="PENDING",
        submitted_at=datetime.now(timezone.utc)
    )
    submission.employee = sample_employee
    submission.documents = []
    return submission


class TestWhatsAppWebhook:
    """Tests for WhatsApp webhook endpoint"""

    @patch('builtins.open', create=True)
    @patch('src.webhook.app.get_redis_client')
    @patch('src.webhook.app.get_db')
    @patch('src.webhook.app.RequestValidator')
    @patch('src.webhook.app.requests.get')
    @patch('src.webhook.app.uuid.uuid4')
    @patch('src.webhook.app.os.makedirs')
    def test_webhook_valid_message_with_media(
        self, mock_makedirs, mock_uuid, mock_requests_get,
        mock_validator_class, mock_get_db, mock_get_redis, mock_open, test_client
    ):
        """Test webhook with valid Twilio signature and media"""
        # Setup mocks
        mock_uuid.return_value = uuid.UUID('12345678-1234-5678-1234-567812345678')
        mock_validator = MagicMock()
        mock_validator.validate.return_value = True
        mock_validator_class.return_value = mock_validator

        # Mock file open
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        # Mock media download
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"fake image data"
        mock_requests_get.return_value = mock_response

        # Mock Redis
        mock_redis = MagicMock()
        mock_redis.hset.return_value = 1
        mock_redis.expire.return_value = 1
        mock_redis.rpush.return_value = 1
        mock_redis.hget.return_value = None
        mock_get_redis.return_value = mock_redis

        # Mock database - create a generator that yields mock_db
        mock_db = MagicMock()
        mock_employee = Employee(
            id=str(uuid.uuid4()),
            phone_number="+919876543210",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_employee

        def mock_get_db_generator():
            yield mock_db

        mock_get_db.return_value = iter([mock_db])

        # Prepare request
        form_data = {
            "From": "whatsapp:+919876543210",
            "Body": "Here is my document",
            "MediaUrl0": "https://api.twilio.com/2010-04-01/Accounts/test/Media/ME123",
            "MediaContentType0": "image/jpeg",
            "NumMedia": "1"
        }

        response = test_client.post(
            "/webhook/whatsapp",
            data=form_data,
            headers={"X-Twilio-Signature": "valid_signature"}
        )

        # Assertions
        assert response.status_code == 200
        assert response.text == "OK"

        # Verify Redis operations
        assert mock_redis.hset.called
        assert mock_redis.expire.called
        assert mock_redis.rpush.called

        # Verify media download
        mock_requests_get.assert_called_once()

    @patch('src.webhook.app.get_redis_client')
    @patch('src.webhook.app.get_db')
    @patch('src.webhook.app.RequestValidator')
    def test_webhook_invalid_signature(
        self, mock_validator_class, mock_get_db, mock_get_redis, test_client
    ):
        """Test webhook with invalid Twilio signature"""
        # Setup mock validator to reject signature
        mock_validator = MagicMock()
        mock_validator.validate.return_value = False
        mock_validator_class.return_value = mock_validator

        form_data = {
            "From": "whatsapp:+919876543210",
            "Body": "Test message",
            "NumMedia": "0"
        }

        response = test_client.post(
            "/webhook/whatsapp",
            data=form_data,
            headers={"X-Twilio-Signature": "invalid_signature"}
        )

        assert response.status_code == 401
        assert "Invalid" in response.json()["detail"] and "signature" in response.json()["detail"]

    @patch('src.webhook.app.get_redis_client')
    @patch('src.webhook.app.get_db')
    @patch('src.webhook.app.RequestValidator')
    def test_webhook_no_media(
        self, mock_validator_class, mock_get_db, mock_get_redis, test_client
    ):
        """Test webhook with no media attached"""
        # Setup mocks
        mock_validator = MagicMock()
        mock_validator.validate.return_value = True
        mock_validator_class.return_value = mock_validator

        mock_redis = MagicMock()
        mock_get_redis.return_value = mock_redis

        mock_db = MagicMock()
        mock_get_db.return_value = mock_db

        form_data = {
            "From": "whatsapp:+919876543210",
            "Body": "Just a text message",
            "NumMedia": "0"
        }

        response = test_client.post(
            "/webhook/whatsapp",
            data=form_data,
            headers={"X-Twilio-Signature": "valid_signature"}
        )

        # Should still return 200 but not create job
        assert response.status_code == 200

    @patch('builtins.open', create=True)
    @patch('src.webhook.app.get_redis_client')
    @patch('src.webhook.app.get_db')
    @patch('src.webhook.app.RequestValidator')
    @patch('src.webhook.app.requests.get')
    @patch('src.webhook.app.uuid.uuid4')
    @patch('src.webhook.app.os.makedirs')
    def test_webhook_creates_employee_if_not_exists(
        self, mock_makedirs, mock_uuid, mock_requests_get,
        mock_validator_class, mock_get_db, mock_get_redis, mock_open, test_client
    ):
        """Test webhook creates new employee if doesn't exist"""
        # Setup mocks
        mock_uuid.return_value = uuid.UUID('12345678-1234-5678-1234-567812345678')
        mock_validator = MagicMock()
        mock_validator.validate.return_value = True
        mock_validator_class.return_value = mock_validator

        # Mock file open
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"fake image data"
        mock_requests_get.return_value = mock_response

        mock_redis = MagicMock()
        mock_redis.hget.return_value = None
        mock_get_redis.return_value = mock_redis

        # Mock database - no existing employee
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_get_db.return_value = iter([mock_db])

        form_data = {
            "From": "whatsapp:+919876543210",
            "Body": "Here is my document",
            "MediaUrl0": "https://api.twilio.com/2010-04-01/Accounts/test/Media/ME123",
            "MediaContentType0": "image/jpeg",
            "NumMedia": "1"
        }

        response = test_client.post(
            "/webhook/whatsapp",
            data=form_data,
            headers={"X-Twilio-Signature": "valid_signature"}
        )

        assert response.status_code == 200
        # Verify employee was added to session
        assert mock_db.add.called


class TestListSubmissions:
    """Tests for GET /api/submissions endpoint"""

    @patch('src.webhook.app.get_config')
    def test_list_submissions_success(self, mock_get_config, test_client, sample_submission):
        """Test listing submissions with valid API key"""
        # Mock config
        mock_config = MagicMock()
        mock_config.API_KEY = "test_api_key"
        mock_get_config.return_value = mock_config

        # Override get_db dependency
        def mock_get_db():
            mock_db = MagicMock()
            # Mock the full chain: query().join().order_by().offset().limit().all()
            mock_query = MagicMock()
            mock_query.join.return_value = mock_query
            mock_query.order_by.return_value = mock_query
            mock_query.offset.return_value = mock_query
            mock_query.limit.return_value = mock_query
            mock_query.all.return_value = [sample_submission]
            mock_query.count.return_value = 1
            mock_db.query.return_value = mock_query
            yield mock_db

        app.dependency_overrides[get_db] = mock_get_db

        try:
            response = test_client.get(
                "/api/submissions",
                headers={"X-API-Key": "test_api_key"}
            )

            assert response.status_code == 200
            data = response.json()
            assert "submissions" in data
            assert "total" in data
            assert data["total"] == 1
        finally:
            app.dependency_overrides = {}

    def test_list_submissions_no_api_key(self, test_client):
        """Test listing submissions without API key"""
        response = test_client.get("/api/submissions")
        assert response.status_code == 422  # Missing required header

    @patch('src.webhook.app.verify_api_key')
    @patch('src.webhook.app.get_db')
    def test_list_submissions_invalid_api_key(self, mock_get_db, mock_verify, test_client):
        """Test listing submissions with invalid API key"""
        from fastapi import HTTPException
        mock_verify.side_effect = HTTPException(status_code=401, detail="Invalid API key")

        response = test_client.get(
            "/api/submissions",
            headers={"X-API-Key": "wrong_key"}
        )

        assert response.status_code == 401

    @patch('src.webhook.app.get_config')
    def test_list_submissions_with_filters(self, mock_get_config, test_client, sample_submission):
        """Test listing submissions with status and phone_number filters"""
        # Mock config
        mock_config = MagicMock()
        mock_config.API_KEY = "test_api_key"
        mock_get_config.return_value = mock_config

        # Override get_db dependency
        def mock_get_db():
            mock_db = MagicMock()
            # Mock the full chain: query().join().filter().order_by().offset().limit().all()
            mock_query = MagicMock()
            mock_query.join.return_value = mock_query
            mock_query.filter.return_value = mock_query
            mock_query.order_by.return_value = mock_query
            mock_query.offset.return_value = mock_query
            mock_query.limit.return_value = mock_query
            mock_query.all.return_value = [sample_submission]
            mock_query.count.return_value = 1
            mock_db.query.return_value = mock_query
            yield mock_db

        app.dependency_overrides[get_db] = mock_get_db

        try:
            response = test_client.get(
                "/api/submissions?status=PENDING&phone_number=%2B919876543210",
                headers={"X-API-Key": "test_api_key"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 1
        finally:
            app.dependency_overrides = {}

    @patch('src.webhook.app.get_config')
    def test_list_submissions_pagination(self, mock_get_config, test_client):
        """Test pagination parameters"""
        # Mock config
        mock_config = MagicMock()
        mock_config.API_KEY = "test_api_key"
        mock_get_config.return_value = mock_config

        # Override get_db dependency
        def mock_get_db():
            mock_db = MagicMock()
            mock_db.query.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []
            mock_db.query.return_value.count.return_value = 0
            yield mock_db

        app.dependency_overrides[get_db] = mock_get_db

        try:
            response = test_client.get(
                "/api/submissions?limit=10&offset=20",
                headers={"X-API-Key": "test_api_key"}
            )

            assert response.status_code == 200
        finally:
            app.dependency_overrides = {}


class TestGetSubmission:
    """Tests for GET /api/submissions/{id} endpoint"""

    @patch('src.webhook.app.get_config')
    def test_get_submission_success(self, mock_get_config, test_client, sample_submission):
        """Test getting specific submission"""
        # Mock config
        mock_config = MagicMock()
        mock_config.API_KEY = "test_api_key"
        mock_get_config.return_value = mock_config

        # Override get_db dependency
        def mock_get_db():
            mock_db = MagicMock()
            mock_db.query.return_value.filter.return_value.first.return_value = sample_submission
            yield mock_db

        app.dependency_overrides[get_db] = mock_get_db

        try:
            response = test_client.get(
                f"/api/submissions/{sample_submission.id}",
                headers={"X-API-Key": "test_api_key"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["id"] == sample_submission.id
            assert data["status"] == "PENDING"
        finally:
            app.dependency_overrides = {}

    @patch('src.webhook.app.get_config')
    def test_get_submission_not_found(self, mock_get_config, test_client):
        """Test getting non-existent submission"""
        # Mock config
        mock_config = MagicMock()
        mock_config.API_KEY = "test_api_key"
        mock_get_config.return_value = mock_config

        # Override get_db dependency
        def mock_get_db():
            mock_db = MagicMock()
            mock_db.query.return_value.filter.return_value.first.return_value = None
            yield mock_db

        app.dependency_overrides[get_db] = mock_get_db

        try:
            response = test_client.get(
                "/api/submissions/nonexistent-id",
                headers={"X-API-Key": "test_api_key"}
            )

            assert response.status_code == 404
        finally:
            app.dependency_overrides = {}

    def test_get_submission_no_api_key(self, test_client):
        """Test getting submission without API key"""
        response = test_client.get("/api/submissions/some-id")
        assert response.status_code == 422


class TestReviewSubmission:
    """Tests for POST /api/submissions/{id}/review endpoint"""

    @patch('src.webhook.app.get_config')
    def test_review_submission_approve(self, mock_get_config, test_client, sample_submission):
        """Test approving a submission"""
        # Mock config
        mock_config = MagicMock()
        mock_config.API_KEY = "test_api_key"
        mock_get_config.return_value = mock_config

        # Override get_db dependency
        def mock_get_db():
            mock_db = MagicMock()
            mock_db.query.return_value.filter.return_value.first.return_value = sample_submission
            yield mock_db

        app.dependency_overrides[get_db] = mock_get_db

        try:
            review_data = {
                "status": "APPROVED",
                "notes": "All documents verified"
            }

            response = test_client.post(
                f"/api/submissions/{sample_submission.id}/review",
                json=review_data,
                headers={"X-API-Key": "test_api_key"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "APPROVED"
            assert data["review_notes"] == "All documents verified"
        finally:
            app.dependency_overrides = {}

    @patch('src.webhook.app.get_config')
    def test_review_submission_reject(self, mock_get_config, test_client, sample_submission):
        """Test rejecting a submission"""
        # Mock config
        mock_config = MagicMock()
        mock_config.API_KEY = "test_api_key"
        mock_get_config.return_value = mock_config

        # Override get_db dependency
        def mock_get_db():
            mock_db = MagicMock()
            mock_db.query.return_value.filter.return_value.first.return_value = sample_submission
            yield mock_db

        app.dependency_overrides[get_db] = mock_get_db

        try:
            review_data = {
                "status": "REJECTED",
                "notes": "Document not clear"
            }

            response = test_client.post(
                f"/api/submissions/{sample_submission.id}/review",
                json=review_data,
                headers={"X-API-Key": "test_api_key"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "REJECTED"
        finally:
            app.dependency_overrides = {}

    @patch('src.webhook.app.get_config')
    def test_review_submission_not_found(self, mock_get_config, test_client):
        """Test reviewing non-existent submission"""
        # Mock config
        mock_config = MagicMock()
        mock_config.API_KEY = "test_api_key"
        mock_get_config.return_value = mock_config

        # Override get_db dependency
        def mock_get_db():
            mock_db = MagicMock()
            mock_db.query.return_value.filter.return_value.first.return_value = None
            yield mock_db

        app.dependency_overrides[get_db] = mock_get_db

        try:
            review_data = {
                "status": "APPROVED",
                "notes": "Test"
            }

            response = test_client.post(
                "/api/submissions/nonexistent-id/review",
                json=review_data,
                headers={"X-API-Key": "test_api_key"}
            )

            assert response.status_code == 404
        finally:
            app.dependency_overrides = {}

    @patch('src.webhook.app.get_config')
    def test_review_submission_invalid_status(self, mock_get_config, test_client, sample_submission):
        """Test review with invalid status"""
        # Mock config
        mock_config = MagicMock()
        mock_config.API_KEY = "test_api_key"
        mock_get_config.return_value = mock_config

        # Override get_db dependency
        def mock_get_db():
            mock_db = MagicMock()
            mock_db.query.return_value.filter.return_value.first.return_value = sample_submission
            yield mock_db

        app.dependency_overrides[get_db] = mock_get_db

        try:
            review_data = {
                "status": "INVALID_STATUS",
                "notes": "Test"
            }

            response = test_client.post(
                f"/api/submissions/{sample_submission.id}/review",
                json=review_data,
                headers={"X-API-Key": "test_api_key"}
            )

            assert response.status_code == 400
        finally:
            app.dependency_overrides = {}

    def test_review_submission_no_api_key(self, test_client):
        """Test reviewing submission without API key"""
        review_data = {
            "status": "APPROVED",
            "notes": "Test"
        }

        response = test_client.post(
            "/api/submissions/some-id/review",
            json=review_data
        )

        assert response.status_code == 422


class TestHealthCheck:
    """Tests for GET /health endpoint"""

    @patch('src.webhook.app.get_redis_client')
    @patch('src.webhook.app.get_session')
    def test_health_check_all_healthy(self, mock_get_session, mock_get_redis, test_client):
        """Test health check when all services are healthy"""
        # Mock Redis
        mock_redis = MagicMock()
        mock_redis.ping.return_value = True
        mock_get_redis.return_value = mock_redis

        # Mock database
        mock_session = MagicMock()
        mock_session.execute.return_value = None
        mock_get_session.return_value = mock_session

        response = test_client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["redis"] == "connected"
        assert data["database"] == "connected"

    @patch('src.webhook.app.get_redis_client')
    @patch('src.webhook.app.get_session')
    def test_health_check_redis_down(self, mock_get_session, mock_get_redis, test_client):
        """Test health check when Redis is down"""
        # Mock Redis failure
        mock_get_redis.side_effect = Exception("Redis connection failed")

        # Mock database
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session

        response = test_client.get("/health")

        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["redis"] == "disconnected"

    @patch('src.webhook.app.get_redis_client')
    @patch('src.webhook.app.get_session')
    def test_health_check_database_down(self, mock_get_session, mock_get_redis, test_client):
        """Test health check when database is down"""
        # Mock Redis
        mock_redis = MagicMock()
        mock_redis.ping.return_value = True
        mock_get_redis.return_value = mock_redis

        # Mock database failure
        mock_get_session.side_effect = Exception("Database connection failed")

        response = test_client.get("/health")

        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["database"] == "disconnected"


class TestFinalizeSubmission:
    """Tests for POST /api/submissions/{id}/finalize endpoint"""

    @patch('src.webhook.app.generate_employee_id')
    @patch('src.webhook.app.get_config')
    def test_finalize_submission_success(self, mock_get_config, mock_gen_emp_id, test_client, sample_submission):
        """Test successfully finalizing an APPROVED submission"""
        # Mock config
        mock_config = MagicMock()
        mock_config.API_KEY = "test_api_key"
        mock_get_config.return_value = mock_config

        # Mock employee ID generation
        mock_gen_emp_id.return_value = "EMP2026001"

        # Set submission status to APPROVED
        sample_submission.status = "APPROVED"

        # Override get_db dependency
        def mock_get_db():
            mock_db = MagicMock()
            mock_db.query.return_value.filter.return_value.first.return_value = sample_submission
            yield mock_db

        app.dependency_overrides[get_db] = mock_get_db

        try:
            finalize_data = {
                "finalized_by": "hrms_admin@metro.com",
                "notes": "Employee onboarded successfully"
            }

            response = test_client.post(
                f"/api/submissions/{sample_submission.id}/finalize",
                json=finalize_data,
                headers={"X-API-Key": "test_api_key"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "FINALIZED"
            assert data["hrms_employee_id"] == "EMP2026001"
            assert data["finalized_by"] == "hrms_admin@metro.com"
            assert "finalized_at" in data
            assert data["message"] == "Employee data finalized successfully"
        finally:
            app.dependency_overrides = {}

    @patch('src.webhook.app.get_config')
    def test_finalize_submission_not_found(self, mock_get_config, test_client):
        """Test finalizing non-existent submission"""
        # Mock config
        mock_config = MagicMock()
        mock_config.API_KEY = "test_api_key"
        mock_get_config.return_value = mock_config

        # Override get_db dependency
        def mock_get_db():
            mock_db = MagicMock()
            mock_db.query.return_value.filter.return_value.first.return_value = None
            yield mock_db

        app.dependency_overrides[get_db] = mock_get_db

        try:
            finalize_data = {
                "finalized_by": "test@metro.com",
                "notes": "Test"
            }

            response = test_client.post(
                "/api/submissions/nonexistent-id/finalize",
                json=finalize_data,
                headers={"X-API-Key": "test_api_key"}
            )

            assert response.status_code == 404
        finally:
            app.dependency_overrides = {}

    @patch('src.webhook.app.get_config')
    def test_finalize_submission_already_finalized(self, mock_get_config, test_client, sample_submission):
        """Test finalizing already finalized submission"""
        # Mock config
        mock_config = MagicMock()
        mock_config.API_KEY = "test_api_key"
        mock_get_config.return_value = mock_config

        # Set submission status to FINALIZED
        sample_submission.status = "FINALIZED"

        # Override get_db dependency
        def mock_get_db():
            mock_db = MagicMock()
            mock_db.query.return_value.filter.return_value.first.return_value = sample_submission
            yield mock_db

        app.dependency_overrides[get_db] = mock_get_db

        try:
            finalize_data = {
                "finalized_by": "test@metro.com",
                "notes": "Test"
            }

            response = test_client.post(
                f"/api/submissions/{sample_submission.id}/finalize",
                json=finalize_data,
                headers={"X-API-Key": "test_api_key"}
            )

            assert response.status_code == 400
            assert "already finalized" in response.json()["detail"].lower()
        finally:
            app.dependency_overrides = {}

    @patch('src.webhook.app.get_config')
    def test_finalize_submission_not_approved(self, mock_get_config, test_client, sample_submission):
        """Test finalizing submission that is not APPROVED"""
        # Mock config
        mock_config = MagicMock()
        mock_config.API_KEY = "test_api_key"
        mock_get_config.return_value = mock_config

        # Set submission status to PENDING
        sample_submission.status = "PENDING"

        # Override get_db dependency
        def mock_get_db():
            mock_db = MagicMock()
            mock_db.query.return_value.filter.return_value.first.return_value = sample_submission
            yield mock_db

        app.dependency_overrides[get_db] = mock_get_db

        try:
            finalize_data = {
                "finalized_by": "test@metro.com",
                "notes": "Test"
            }

            response = test_client.post(
                f"/api/submissions/{sample_submission.id}/finalize",
                json=finalize_data,
                headers={"X-API-Key": "test_api_key"}
            )

            assert response.status_code == 403
            assert "APPROVED" in response.json()["detail"]
        finally:
            app.dependency_overrides = {}

    @patch('src.webhook.app.generate_employee_id')
    @patch('src.webhook.app.get_config')
    def test_finalize_submission_retry_on_race_condition(self, mock_get_config, mock_gen_emp_id, test_client, sample_submission):
        """Test retry logic when race condition occurs"""
        # Mock config
        mock_config = MagicMock()
        mock_config.API_KEY = "test_api_key"
        mock_get_config.return_value = mock_config

        # Mock employee ID generation to fail first, succeed second
        mock_gen_emp_id.side_effect = ["EMP2026001", "EMP2026002"]

        # Set submission status to APPROVED
        sample_submission.status = "APPROVED"

        # Override get_db dependency
        def mock_get_db():
            mock_db = MagicMock()
            mock_db.query.return_value.filter.return_value.first.return_value = sample_submission

            # First commit fails, second succeeds
            commit_call_count = [0]
            def mock_commit():
                commit_call_count[0] += 1
                if commit_call_count[0] == 1:
                    raise IntegrityError("Unique constraint violation", None, None)

            mock_db.commit = mock_commit
            yield mock_db

        app.dependency_overrides[get_db] = mock_get_db

        try:
            finalize_data = {
                "finalized_by": "test@metro.com",
                "notes": "Test retry"
            }

            response = test_client.post(
                f"/api/submissions/{sample_submission.id}/finalize",
                json=finalize_data,
                headers={"X-API-Key": "test_api_key"}
            )

            assert response.status_code == 200
            # Should have called generate_employee_id twice
            assert mock_gen_emp_id.call_count == 2
        finally:
            app.dependency_overrides = {}

    def test_finalize_submission_no_api_key(self, test_client):
        """Test finalizing submission without API key"""
        finalize_data = {
            "finalized_by": "test@metro.com",
            "notes": "Test"
        }

        response = test_client.post(
            "/api/submissions/some-id/finalize",
            json=finalize_data
        )

        assert response.status_code == 422


class TestAPIKeyVerification:
    """Tests for API key verification dependency"""

    def test_missing_api_key_header(self, test_client):
        """Test request without X-API-Key header"""
        response = test_client.get("/api/submissions")
        assert response.status_code == 422  # FastAPI validation error

    @patch('src.webhook.app.config')
    @patch('src.webhook.app.get_db')
    def test_invalid_api_key(self, mock_get_db, mock_config, test_client):
        """Test request with wrong API key"""
        mock_config.API_KEY = "correct_key"

        response = test_client.get(
            "/api/submissions",
            headers={"X-API-Key": "wrong_key"}
        )

        # The verify_api_key dependency should reject this
        # Actual behavior depends on implementation
        # This test verifies the endpoint is protected
        assert response.status_code in [401, 403, 422]
