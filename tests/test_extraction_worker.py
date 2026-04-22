"""Tests for extraction worker."""
import json
import pytest
from unittest.mock import Mock, MagicMock, patch, call
from datetime import datetime, timezone


@pytest.fixture
def sample_job():
    """Sample job data from Redis."""
    return {
        "job_id": "test-job-123",
        "phone_number": "+919876543210",
        "file_path": "uploads/+919876543210/test-pan.jpg",
        "timestamp": "2026-04-16T10:00:00Z",
        "status": "PENDING"
    }


@pytest.fixture
def sample_pan_data():
    """Sample PAN extraction data."""
    return {
        "pan_number": "ABCDE1234F",
        "name": "JOHN DOE",
        "father_name": "ROBERT DOE",
        "dob": "15/01/1990",
        "confidence": 0.9,
        "raw_text": "INCOME TAX DEPARTMENT..."
    }


@pytest.fixture
def sample_aadhaar_data():
    """Sample Aadhaar extraction data."""
    return {
        "aadhaar_number": "123456789012",
        "name": "JOHN DOE",
        "dob": "15/01/1990",
        "gender": "Male",
        "address": "123 Main St, City",
        "pincode": "400001",
        "confidence": 0.9,
        "raw_text": "GOVERNMENT OF INDIA..."
    }


@pytest.fixture
def sample_bank_data():
    """Sample bank extraction data."""
    return {
        "account_number": "1234567890",
        "account_holder_name": "JOHN DOE",
        "ifsc_code": "SBIN0001234",
        "bank_name": "STATE BANK OF INDIA",
        "branch_name": "MAIN BRANCH",
        "account_type": "Savings",
        "micr_code": "400002001",
        "confidence": 0.9,
        "raw_response": "{...}"
    }


def test_process_job_pan_card(sample_job, sample_pan_data):
    """Test processing a PAN card document."""
    with patch('src.workers.extraction_worker._get_classifier') as mock_get_classifier, \
         patch('src.workers.extraction_worker._get_ocr_extractor') as mock_get_ocr, \
         patch('src.workers.extraction_worker._get_whatsapp_client') as mock_get_whatsapp, \
         patch('src.workers.extraction_worker.get_db') as mock_get_db:

        from src.workers.extraction_worker import process_job

        # Setup mocks
        mock_classifier = MagicMock()
        mock_ocr = MagicMock()
        mock_whatsapp = MagicMock()
        mock_db = MagicMock()

        mock_get_classifier.return_value = mock_classifier
        mock_get_ocr.return_value = mock_ocr
        mock_get_whatsapp.return_value = mock_whatsapp
        # Setup context manager mock properly
        mock_ctx = MagicMock()
        mock_ctx.__enter__.return_value = mock_db
        mock_ctx.__exit__.return_value = None
        mock_get_db.return_value = mock_ctx

        # Mock classification
        mock_classifier.classify_document.return_value = ("PAN_CARD", 0.95)

        # Mock extraction
        mock_ocr.extract_pan_data.return_value = sample_pan_data

        # Mock database queries
        mock_employee = MagicMock()
        mock_employee.id = "emp-123"
        mock_submission = MagicMock()
        mock_submission.id = "sub-123"
        mock_submission.pan_confidence = None
        mock_submission.aadhaar_confidence = None
        mock_submission.bank_confidence = None
        mock_submission.overall_confidence = None
        mock_submission.pan_name = None
        mock_submission.aadhaar_name = None
        mock_submission.bank_holder_name = None

        mock_db.query.return_value.filter_by.return_value.first.side_effect = [
            mock_employee,  # First call: get employee
            mock_submission  # Second call: get submission
        ]

        # Process job
        process_job(sample_job)

        # Verify calls
        mock_classifier.classify_document.assert_called_once_with(sample_job["file_path"])
        mock_ocr.extract_pan_data.assert_called_once_with(sample_job["file_path"])
        mock_whatsapp.send_confirmation.assert_called_once_with(
            sample_job["phone_number"],
            "sub-123"
        )

        # Verify database operations
        assert mock_db.add.called
        # Note: commit is called by context manager's __exit__, not directly
        # The successful completion of the job (confirmation sent) implies commit succeeded


def test_process_job_bank_document(sample_job, sample_bank_data):
    """Test processing a bank document."""
    with patch('src.workers.extraction_worker._get_classifier') as mock_get_classifier, \
         patch('src.workers.extraction_worker._get_ai_extractor') as mock_get_ai, \
         patch('src.workers.extraction_worker._get_whatsapp_client') as mock_get_whatsapp, \
         patch('src.workers.extraction_worker.get_db') as mock_get_db:

        from src.workers.extraction_worker import process_job

        # Setup mocks
        mock_classifier = MagicMock()
        mock_ai = MagicMock()
        mock_whatsapp = MagicMock()
        mock_db = MagicMock()

        mock_get_classifier.return_value = mock_classifier
        mock_get_ai.return_value = mock_ai
        mock_get_whatsapp.return_value = mock_whatsapp
        mock_get_db.return_value.__enter__.return_value = mock_db

        # Mock classification
        mock_classifier.classify_document.return_value = ("BANK_DOCUMENT", 0.95)

        # Mock extraction
        mock_ai.extract_bank_data.return_value = sample_bank_data

        # Mock database queries
        mock_employee = MagicMock()
        mock_employee.id = "emp-123"
        mock_submission = MagicMock()
        mock_submission.id = "sub-123"
        mock_submission.pan_confidence = None
        mock_submission.aadhaar_confidence = None
        mock_submission.bank_confidence = None
        mock_submission.overall_confidence = None
        mock_submission.pan_name = None
        mock_submission.aadhaar_name = None
        mock_submission.bank_holder_name = None

        mock_db.query.return_value.filter_by.return_value.first.side_effect = [
            mock_employee,
            mock_submission
        ]

        # Update job for bank document
        bank_job = sample_job.copy()
        bank_job["file_path"] = "uploads/+919876543210/test-bank.jpg"

        # Process job
        process_job(bank_job)

        # Verify calls
        mock_classifier.classify_document.assert_called_once_with(bank_job["file_path"])
        mock_ai.extract_bank_data.assert_called_once_with(bank_job["file_path"])
        mock_whatsapp.send_confirmation.assert_called_once()


def test_process_job_aadhaar_card(sample_job, sample_aadhaar_data):
    """Test processing an Aadhaar card."""
    with patch('src.workers.extraction_worker._get_classifier') as mock_get_classifier, \
         patch('src.workers.extraction_worker._get_ocr_extractor') as mock_get_ocr, \
         patch('src.workers.extraction_worker._get_whatsapp_client') as mock_get_whatsapp, \
         patch('src.workers.extraction_worker.get_db') as mock_get_db:

        from src.workers.extraction_worker import process_job

        # Setup mocks
        mock_classifier = MagicMock()
        mock_ocr = MagicMock()
        mock_whatsapp = MagicMock()
        mock_db = MagicMock()

        mock_get_classifier.return_value = mock_classifier
        mock_get_ocr.return_value = mock_ocr
        mock_get_whatsapp.return_value = mock_whatsapp
        mock_get_db.return_value.__enter__.return_value = mock_db

        # Mock classification
        mock_classifier.classify_document.return_value = ("AADHAAR_CARD", 0.95)

        # Mock extraction
        mock_ocr.extract_aadhaar_data.return_value = sample_aadhaar_data

        # Mock database queries
        mock_employee = MagicMock()
        mock_employee.id = "emp-123"
        mock_submission = MagicMock()
        mock_submission.id = "sub-123"
        mock_submission.pan_confidence = None
        mock_submission.aadhaar_confidence = None
        mock_submission.bank_confidence = None
        mock_submission.overall_confidence = None
        mock_submission.pan_name = None
        mock_submission.aadhaar_name = None
        mock_submission.bank_holder_name = None

        mock_db.query.return_value.filter_by.return_value.first.side_effect = [
            mock_employee,
            mock_submission
        ]

        # Update job for aadhaar
        aadhaar_job = sample_job.copy()
        aadhaar_job["file_path"] = "uploads/+919876543210/test-aadhaar.jpg"

        # Process job
        process_job(aadhaar_job)

        # Verify calls
        mock_classifier.classify_document.assert_called_once_with(aadhaar_job["file_path"])
        mock_ocr.extract_aadhaar_data.assert_called_once_with(aadhaar_job["file_path"])
        mock_whatsapp.send_confirmation.assert_called_once()


def test_process_job_low_confidence_classification(sample_job):
    """Test handling of low confidence classification."""
    with patch('src.workers.extraction_worker._get_classifier') as mock_get_classifier, \
         patch('src.workers.extraction_worker._get_whatsapp_client') as mock_get_whatsapp, \
         patch('src.workers.extraction_worker.get_db') as mock_get_db:

        from src.workers.extraction_worker import process_job

        # Setup mocks
        mock_classifier = MagicMock()
        mock_whatsapp = MagicMock()
        mock_db = MagicMock()

        mock_get_classifier.return_value = mock_classifier
        mock_get_whatsapp.return_value = mock_whatsapp
        mock_get_db.return_value.__enter__.return_value = mock_db

        # Mock low confidence classification
        mock_classifier.classify_document.return_value = ("PAN_CARD", 0.5)

        # Process job
        process_job(sample_job)

        # Verify error message sent
        mock_whatsapp.send_error.assert_called_once_with(sample_job["phone_number"])

        # Verify no database commits
        assert not mock_db.commit.called


def test_process_job_unknown_document_type(sample_job):
    """Test handling of unknown document type."""
    with patch('src.workers.extraction_worker._get_classifier') as mock_get_classifier, \
         patch('src.workers.extraction_worker._get_whatsapp_client') as mock_get_whatsapp, \
         patch('src.workers.extraction_worker.get_db') as mock_get_db:

        from src.workers.extraction_worker import process_job

        # Setup mocks
        mock_classifier = MagicMock()
        mock_whatsapp = MagicMock()
        mock_db = MagicMock()

        mock_get_classifier.return_value = mock_classifier
        mock_get_whatsapp.return_value = mock_whatsapp
        mock_get_db.return_value.__enter__.return_value = mock_db

        # Mock unknown classification
        mock_classifier.classify_document.return_value = ("UNKNOWN", 0.5)

        # Process job
        process_job(sample_job)

        # Verify error message sent
        mock_whatsapp.send_error.assert_called_once_with(sample_job["phone_number"])

        # Verify no database commits
        assert not mock_db.commit.called


def test_classify_and_extract_pan(sample_job, sample_pan_data):
    """Test classify_and_extract for PAN card."""
    with patch('src.workers.extraction_worker._get_classifier') as mock_get_classifier, \
         patch('src.workers.extraction_worker._get_ocr_extractor') as mock_get_ocr:

        from src.workers.extraction_worker import classify_and_extract

        # Setup mocks
        mock_classifier = MagicMock()
        mock_ocr = MagicMock()

        mock_get_classifier.return_value = mock_classifier
        mock_get_ocr.return_value = mock_ocr

        mock_classifier.classify_document.return_value = ("PAN_CARD", 0.95)
        mock_ocr.extract_pan_data.return_value = sample_pan_data

        # Call function
        doc_type, confidence, data = classify_and_extract(sample_job["file_path"])

        # Verify results
        assert doc_type == "PAN_CARD"
        assert confidence == 0.95
        assert data == sample_pan_data


def test_classify_and_extract_bank(sample_job, sample_bank_data):
    """Test classify_and_extract for bank document."""
    with patch('src.workers.extraction_worker._get_classifier') as mock_get_classifier, \
         patch('src.workers.extraction_worker._get_ai_extractor') as mock_get_ai:

        from src.workers.extraction_worker import classify_and_extract

        # Setup mocks
        mock_classifier = MagicMock()
        mock_ai = MagicMock()

        mock_get_classifier.return_value = mock_classifier
        mock_get_ai.return_value = mock_ai

        mock_classifier.classify_document.return_value = ("BANK_DOCUMENT", 0.95)
        mock_ai.extract_bank_data.return_value = sample_bank_data

        # Call function
        doc_type, confidence, data = classify_and_extract(sample_job["file_path"])

        # Verify results
        assert doc_type == "BANK_DOCUMENT"
        assert confidence == 0.95
        assert data == sample_bank_data


def test_validate_extraction_pan_all_fields(sample_pan_data):
    """Test validation with all PAN fields present."""
    from src.workers.extraction_worker import validate_extraction

    is_valid, confidence = validate_extraction(sample_pan_data, "PAN_CARD")

    assert is_valid is True
    assert confidence == 0.9


def test_validate_extraction_pan_missing_required():
    """Test validation with missing required PAN fields."""
    from src.workers.extraction_worker import validate_extraction

    data = {
        "pan_number": None,
        "name": "JOHN DOE",
        "father_name": "ROBERT DOE",
        "dob": "15/01/1990",
        "confidence": 0.5
    }

    is_valid, confidence = validate_extraction(data, "PAN_CARD")

    assert is_valid is False
    assert confidence == 0.5


def test_validate_extraction_aadhaar_all_fields(sample_aadhaar_data):
    """Test validation with all Aadhaar fields present."""
    from src.workers.extraction_worker import validate_extraction

    is_valid, confidence = validate_extraction(sample_aadhaar_data, "AADHAAR_CARD")

    assert is_valid is True
    assert confidence == 0.9


def test_validate_extraction_bank_all_fields(sample_bank_data):
    """Test validation with all bank fields present."""
    from src.workers.extraction_worker import validate_extraction

    is_valid, confidence = validate_extraction(sample_bank_data, "BANK_DOCUMENT")

    assert is_valid is True
    assert confidence == 0.9


def test_validate_extraction_low_confidence():
    """Test validation with low confidence extraction."""
    from src.workers.extraction_worker import validate_extraction

    data = {
        "pan_number": "ABCDE1234F",
        "name": "JOHN DOE",
        "dob": "15/01/1990",
        "confidence": 0.5
    }

    is_valid, confidence = validate_extraction(data, "PAN_CARD")

    # Valid but low confidence
    assert is_valid is True
    assert confidence < 0.7


def test_store_in_database_pan(sample_job, sample_pan_data):
    """Test storing PAN data in database."""
    with patch('src.workers.extraction_worker.encrypt_field') as mock_encrypt, \
         patch('src.workers.extraction_worker.get_db') as mock_get_db:

        from src.workers.extraction_worker import store_in_database

        # Setup mocks
        mock_db = MagicMock()
        mock_get_db.return_value.__enter__.return_value = mock_db
        mock_encrypt.return_value = "encrypted_pan"

        # Mock employee and submission
        mock_employee = MagicMock()
        mock_employee.id = "emp-123"
        mock_submission = MagicMock()
        mock_submission.id = "sub-123"
        mock_submission.pan_confidence = None
        mock_submission.aadhaar_confidence = None
        mock_submission.bank_confidence = None
        mock_submission.overall_confidence = None
        mock_submission.pan_name = None
        mock_submission.aadhaar_name = None
        mock_submission.bank_holder_name = None

        mock_db.query.return_value.filter_by.return_value.first.side_effect = [
            mock_employee,
            mock_submission
        ]

        # Call function
        submission_id = store_in_database(sample_job, sample_pan_data, "PAN_CARD", 0.9)

        # Verify encryption called
        mock_encrypt.assert_called_once_with("ABCDE1234F")

        # Verify submission_id returned
        assert submission_id == "sub-123"


def test_store_in_database_aadhaar(sample_job, sample_aadhaar_data):
    """Test storing Aadhaar data in database."""
    with patch('src.workers.extraction_worker.mask_aadhaar') as mock_mask, \
         patch('src.workers.extraction_worker.get_db') as mock_get_db:

        from src.workers.extraction_worker import store_in_database

        # Setup mocks
        mock_db = MagicMock()
        mock_get_db.return_value.__enter__.return_value = mock_db
        mock_mask.return_value = "9012"

        # Mock employee and submission
        mock_employee = MagicMock()
        mock_employee.id = "emp-123"
        mock_submission = MagicMock()
        mock_submission.id = "sub-123"
        mock_submission.pan_confidence = None
        mock_submission.aadhaar_confidence = None
        mock_submission.bank_confidence = None
        mock_submission.overall_confidence = None
        mock_submission.pan_name = None
        mock_submission.aadhaar_name = None
        mock_submission.bank_holder_name = None

        mock_db.query.return_value.filter_by.return_value.first.side_effect = [
            mock_employee,
            mock_submission
        ]

        # Call function
        submission_id = store_in_database(sample_job, sample_aadhaar_data, "AADHAAR_CARD", 0.9)

        # Verify masking called
        mock_mask.assert_called_once_with("123456789012")

        # Verify submission_id returned
        assert submission_id == "sub-123"


def test_send_notifications():
    """Test sending WhatsApp notifications."""
    with patch('src.workers.extraction_worker._get_whatsapp_client') as mock_get_whatsapp:

        from src.workers.extraction_worker import send_notifications

        # Setup mock
        mock_whatsapp = MagicMock()
        mock_get_whatsapp.return_value = mock_whatsapp

        # Call function
        send_notifications("+919876543210", "sub-123")

        # Verify call
        mock_whatsapp.send_confirmation.assert_called_once_with(
            "+919876543210",
            "sub-123"
        )


def test_process_job_extraction_failure(sample_job):
    """Test handling of extraction failure."""
    with patch('src.workers.extraction_worker._get_classifier') as mock_get_classifier, \
         patch('src.workers.extraction_worker._get_ocr_extractor') as mock_get_ocr, \
         patch('src.workers.extraction_worker._get_whatsapp_client') as mock_get_whatsapp, \
         patch('src.workers.extraction_worker.get_db') as mock_get_db:

        from src.workers.extraction_worker import process_job

        # Setup mocks
        mock_classifier = MagicMock()
        mock_ocr = MagicMock()
        mock_whatsapp = MagicMock()
        mock_db = MagicMock()

        mock_get_classifier.return_value = mock_classifier
        mock_get_ocr.return_value = mock_ocr
        mock_get_whatsapp.return_value = mock_whatsapp
        mock_get_db.return_value.__enter__.return_value = mock_db

        # Mock successful classification but extraction raises exception
        mock_classifier.classify_document.return_value = ("PAN_CARD", 0.95)
        mock_ocr.extract_pan_data.side_effect = Exception("OCR failed")

        # Process job - should handle exception gracefully
        process_job(sample_job)

        # Verify error message sent
        mock_whatsapp.send_error.assert_called_once_with(sample_job["phone_number"])
