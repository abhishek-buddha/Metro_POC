"""Tests for AI extraction service using Claude Vision."""
import pytest
import json
from unittest.mock import patch, MagicMock
from src.services.ai_extraction import AIExtractor


class TestAIExtractorInitialization:
    """Test AIExtractor initialization."""

    @patch('src.services.ai_extraction.Anthropic')
    def test_extractor_initializes_anthropic_client(self, mock_anthropic_class):
        """Test extractor initializes Anthropic client."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        extractor = AIExtractor()

        assert mock_anthropic_class.called
        assert extractor.client is not None


class TestBankDataExtractionAllFields:
    """Test bank data extraction with all fields present."""

    @patch('src.services.ai_extraction.Anthropic')
    @patch('builtins.open', create=True)
    def test_extract_bank_data_all_fields(self, mock_open, mock_anthropic_class):
        """Test bank extraction with all required and optional fields."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        # Mock file open to return fake image data
        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = b'fake_image_data'
        mock_open.return_value = mock_file

        # Mock API response with all fields
        json_response = {
            "account_number": "12345678901234",
            "account_holder_name": "JOHN DOE",
            "ifsc_code": "ABCD0123456",
            "bank_name": "ABC Bank",
            "branch_name": "Main Branch",
            "account_type": "Savings",
            "micr_code": "123456789"
        }

        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=json.dumps(json_response))]
        mock_client.messages.create.return_value = mock_response

        extractor = AIExtractor()
        result = extractor.extract_bank_data("test_passbook.jpg")

        assert result['account_number'] == "12345678901234"
        assert result['account_holder_name'] == "JOHN DOE"
        assert result['ifsc_code'] == "ABCD0123456"
        assert result['bank_name'] == "ABC Bank"
        assert result['branch_name'] == "Main Branch"
        assert result['account_type'] == "Savings"
        assert result['micr_code'] == "123456789"
        assert result['confidence'] == 0.9
        assert 'raw_response' in result

    @patch('src.services.ai_extraction.Anthropic')
    @patch('builtins.open', create=True)
    def test_extract_bank_data_missing_optional_fields(self, mock_open, mock_anthropic_class):
        """Test bank extraction with missing optional fields."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = b'fake_image_data'
        mock_open.return_value = mock_file

        # Mock API response with missing optional fields
        json_response = {
            "account_number": "12345678901234",
            "account_holder_name": "JANE DOE",
            "ifsc_code": "SBIN0000123",
            "bank_name": None,
            "branch_name": None,
            "account_type": None,
            "micr_code": None
        }

        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=json.dumps(json_response))]
        mock_client.messages.create.return_value = mock_response

        extractor = AIExtractor()
        result = extractor.extract_bank_data("test_statement.jpg")

        assert result['account_number'] == "12345678901234"
        assert result['account_holder_name'] == "JANE DOE"
        assert result['ifsc_code'] == "SBIN0000123"
        assert result['bank_name'] is None
        assert result['branch_name'] is None
        assert result['account_type'] is None
        assert result['micr_code'] is None
        assert result['confidence'] == 0.7

    @patch('src.services.ai_extraction.Anthropic')
    @patch('builtins.open', create=True)
    def test_extract_bank_data_missing_required_fields(self, mock_open, mock_anthropic_class):
        """Test bank extraction with missing required fields."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = b'fake_image_data'
        mock_open.return_value = mock_file

        # Mock API response with missing required field
        json_response = {
            "account_number": None,
            "account_holder_name": "JOHN DOE",
            "ifsc_code": "ABCD0123456",
            "bank_name": "ABC Bank",
            "branch_name": "Main Branch",
            "account_type": "Savings",
            "micr_code": None
        }

        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=json.dumps(json_response))]
        mock_client.messages.create.return_value = mock_response

        extractor = AIExtractor()
        result = extractor.extract_bank_data("test_cheque.jpg")

        assert result['account_number'] is None
        assert result['account_holder_name'] == "JOHN DOE"
        assert result['confidence'] == 0.5

    @patch('src.services.ai_extraction.Anthropic')
    @patch('builtins.open', create=True)
    def test_extract_bank_data_json_parsing_error(self, mock_open, mock_anthropic_class):
        """Test bank extraction with JSON parsing error."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = b'fake_image_data'
        mock_open.return_value = mock_file

        # Mock invalid JSON response
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Invalid JSON {not valid")]
        mock_client.messages.create.return_value = mock_response

        extractor = AIExtractor()
        result = extractor.extract_bank_data("test.jpg")

        assert result['confidence'] == 0.0
        assert result['account_number'] is None
        assert result['account_holder_name'] is None

    @patch('src.services.ai_extraction.Anthropic')
    @patch('builtins.open', create=True)
    def test_extract_bank_data_api_error(self, mock_open, mock_anthropic_class):
        """Test bank extraction with API error."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = b'fake_image_data'
        mock_open.return_value = mock_file

        # Mock API error
        mock_client.messages.create.side_effect = Exception("API Error")

        extractor = AIExtractor()
        result = extractor.extract_bank_data("test.jpg")

        assert result['confidence'] == 0.0
        assert result['account_number'] is None

    @patch('src.services.ai_extraction.Anthropic')
    @patch('builtins.open', create=True)
    def test_extract_bank_data_validates_account_number(self, mock_open, mock_anthropic_class):
        """Test bank extraction validates account number format."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = b'fake_image_data'
        mock_open.return_value = mock_file

        # Mock response with invalid account number (too short)
        json_response = {
            "account_number": "12345",  # Invalid - less than 9 digits
            "account_holder_name": "JOHN DOE",
            "ifsc_code": "ABCD0123456",
            "bank_name": "ABC Bank",
            "branch_name": "Main Branch",
            "account_type": "Savings",
            "micr_code": None
        }

        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=json.dumps(json_response))]
        mock_client.messages.create.return_value = mock_response

        extractor = AIExtractor()
        result = extractor.extract_bank_data("test.jpg")

        assert result['confidence'] == 0.5  # Validation failed

    @patch('src.services.ai_extraction.Anthropic')
    @patch('builtins.open', create=True)
    def test_extract_bank_data_validates_ifsc(self, mock_open, mock_anthropic_class):
        """Test bank extraction validates IFSC code format."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = b'fake_image_data'
        mock_open.return_value = mock_file

        # Mock response with invalid IFSC
        json_response = {
            "account_number": "12345678901234",
            "account_holder_name": "JOHN DOE",
            "ifsc_code": "INVALID",  # Invalid IFSC format
            "bank_name": "ABC Bank",
            "branch_name": "Main Branch",
            "account_type": "Savings",
            "micr_code": None
        }

        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=json.dumps(json_response))]
        mock_client.messages.create.return_value = mock_response

        extractor = AIExtractor()
        result = extractor.extract_bank_data("test.jpg")

        assert result['confidence'] == 0.5  # Validation failed

    @patch('src.services.ai_extraction.Anthropic')
    @patch('builtins.open', create=True)
    def test_extract_bank_data_calls_vision_api(self, mock_open, mock_anthropic_class):
        """Test that bank extraction calls Claude Vision API with correct parameters."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = b'fake_image_data'
        mock_open.return_value = mock_file

        json_response = {
            "account_number": "12345678901234",
            "account_holder_name": "JOHN DOE",
            "ifsc_code": "ABCD0123456",
            "bank_name": "ABC Bank",
            "branch_name": "Main Branch",
            "account_type": "Savings",
            "micr_code": None
        }

        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=json.dumps(json_response))]
        mock_client.messages.create.return_value = mock_response

        extractor = AIExtractor()
        extractor.extract_bank_data("test.jpg")

        # Verify API was called
        assert mock_client.messages.create.called

    @patch('src.services.ai_extraction.Anthropic')
    @patch('builtins.open', create=True)
    def test_extract_bank_data_png_format(self, mock_open, mock_anthropic_class):
        """Test bank extraction with PNG file format."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = b'fake_image_data'
        mock_open.return_value = mock_file

        json_response = {
            "account_number": "12345678901234",
            "account_holder_name": "JOHN DOE",
            "ifsc_code": "ABCD0123456",
            "bank_name": "ABC Bank",
            "branch_name": "Main Branch",
            "account_type": "Savings",
            "micr_code": None
        }

        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=json.dumps(json_response))]
        mock_client.messages.create.return_value = mock_response

        extractor = AIExtractor()
        result = extractor.extract_bank_data("test.png")

        assert result['account_number'] == "12345678901234"
        assert result['confidence'] == 0.9

    @patch('src.services.ai_extraction.Anthropic')
    @patch('builtins.open', create=True)
    def test_extract_bank_data_returns_dict_structure(self, mock_open, mock_anthropic_class):
        """Test bank extraction returns correct dictionary structure."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = b'fake_image_data'
        mock_open.return_value = mock_file

        json_response = {
            "account_number": "12345678901234",
            "account_holder_name": "JOHN DOE",
            "ifsc_code": "ABCD0123456",
            "bank_name": "ABC Bank",
            "branch_name": "Main Branch",
            "account_type": "Savings",
            "micr_code": None
        }

        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=json.dumps(json_response))]
        mock_client.messages.create.return_value = mock_response

        extractor = AIExtractor()
        result = extractor.extract_bank_data("test.jpg")

        required_keys = {
            'account_number', 'account_holder_name', 'ifsc_code', 'bank_name',
            'branch_name', 'account_type', 'micr_code', 'confidence', 'raw_response'
        }
        assert set(result.keys()) == required_keys

    @patch('src.services.ai_extraction.Anthropic')
    @patch('builtins.open', create=True)
    def test_extract_bank_data_strips_whitespace(self, mock_open, mock_anthropic_class):
        """Test bank extraction strips whitespace from extracted fields."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = b'fake_image_data'
        mock_open.return_value = mock_file

        json_response = {
            "account_number": " 12345678901234 ",
            "account_holder_name": " JOHN DOE ",
            "ifsc_code": " ABCD0123456 ",
            "bank_name": " ABC Bank ",
            "branch_name": " Main Branch ",
            "account_type": " Savings ",
            "micr_code": " 123456789 "
        }

        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=json.dumps(json_response))]
        mock_client.messages.create.return_value = mock_response

        extractor = AIExtractor()
        result = extractor.extract_bank_data("test.jpg")

        assert result['account_number'] == "12345678901234"
        assert result['account_holder_name'] == "JOHN DOE"
        assert result['ifsc_code'] == "ABCD0123456"
        assert result['bank_name'] == "ABC Bank"
        assert result['branch_name'] == "Main Branch"
        assert result['account_type'] == "Savings"
        assert result['micr_code'] == "123456789"

    @patch('src.services.ai_extraction.Anthropic')
    @patch('builtins.open', create=True)
    def test_extract_bank_data_current_account_type(self, mock_open, mock_anthropic_class):
        """Test bank extraction with Current account type."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = b'fake_image_data'
        mock_open.return_value = mock_file

        json_response = {
            "account_number": "12345678901234",
            "account_holder_name": "JANE CORPORATION",
            "ifsc_code": "ICIC0000001",
            "bank_name": "ICICI Bank",
            "branch_name": "Corporate Branch",
            "account_type": "Current",
            "micr_code": None
        }

        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=json.dumps(json_response))]
        mock_client.messages.create.return_value = mock_response

        extractor = AIExtractor()
        result = extractor.extract_bank_data("test.jpg")

        assert result['account_type'] == "Current"
        assert result['confidence'] == 0.9

    @patch('src.services.ai_extraction.Anthropic')
    @patch('builtins.open', create=True)
    def test_extract_bank_data_file_read_error(self, mock_open, mock_anthropic_class):
        """Test bank extraction with file read error."""
        mock_anthropic_class.return_value = MagicMock()

        mock_open.side_effect = FileNotFoundError("File not found")

        extractor = AIExtractor()
        result = extractor.extract_bank_data("nonexistent.jpg")

        assert result['confidence'] == 0.0
        assert result['account_number'] is None
