"""Tests for OCR extraction service."""
import pytest
from unittest.mock import patch, MagicMock
from src.services.ocr_extraction import OCRExtractor


class TestOCRExtractorInitialization:
    """Test OCRExtractor initialization."""

    @patch('src.services.ocr_extraction.easyocr.Reader')
    def test_extractor_initializes_reader(self, mock_reader_class):
        """Test extractor initializes EasyOCR reader with correct languages."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader

        extractor = OCRExtractor()

        mock_reader_class.assert_called_once_with(['en', 'hi'])

    @patch('src.services.ocr_extraction.easyocr.Reader')
    def test_extractor_stores_reader(self, mock_reader_class):
        """Test extractor stores reader instance."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader

        extractor = OCRExtractor()

        assert extractor.reader is not None


class TestPANCardExtraction:
    """Test PAN card extraction from OCR text."""

    @patch('src.services.ocr_extraction.easyocr.Reader')
    def test_extract_pan_with_all_fields(self, mock_reader_class):
        """Test PAN extraction with all fields present."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader

        # Mock OCR result with all required fields
        mock_reader.readtext.return_value = [
            ([[0, 0], [100, 0], [100, 50], [0, 50]], "INCOME TAX DEPARTMENT", 0.9),
            ([[0, 50], [100, 50], [100, 100], [0, 100]], "ABCDE1234F", 0.95),
            ([[0, 100], [100, 100], [100, 150], [0, 150]], "Name: JOHN DOE", 0.9),
            ([[0, 150], [100, 150], [100, 200], [0, 200]], "Father's Name: RICHARD DOE", 0.9),
            ([[0, 200], [100, 200], [100, 250], [0, 250]], "Date of Birth: 01/01/1990", 0.9),
        ]

        extractor = OCRExtractor()
        result = extractor.extract_pan_data("test.jpg")

        assert result['pan_number'] == "ABCDE1234F"
        assert result['name'] == "JOHN DOE"
        assert result['father_name'] == "RICHARD DOE"
        assert result['dob'] == "01/01/1990"
        assert result['confidence'] == 0.9
        assert 'raw_text' in result

    @patch('src.services.ocr_extraction.easyocr.Reader')
    def test_extract_pan_without_fathers_name(self, mock_reader_class):
        """Test PAN extraction with missing father's name."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader

        mock_reader.readtext.return_value = [
            ([[0, 0], [100, 0], [100, 50], [0, 50]], "INCOME TAX DEPARTMENT", 0.9),
            ([[0, 50], [100, 50], [100, 100], [0, 100]], "ABCDE1234F", 0.95),
            ([[0, 100], [100, 100], [100, 150], [0, 150]], "Name: JOHN DOE", 0.9),
            ([[0, 200], [100, 200], [100, 250], [0, 250]], "Date of Birth: 01/01/1990", 0.9),
        ]

        extractor = OCRExtractor()
        result = extractor.extract_pan_data("test.jpg")

        assert result['pan_number'] == "ABCDE1234F"
        assert result['name'] == "JOHN DOE"
        assert result['father_name'] is None
        assert result['dob'] == "01/01/1990"
        assert result['confidence'] == 0.7

    @patch('src.services.ocr_extraction.easyocr.Reader')
    def test_extract_pan_missing_pan_number(self, mock_reader_class):
        """Test PAN extraction with missing PAN number (required field)."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader

        mock_reader.readtext.return_value = [
            ([[0, 100], [100, 100], [100, 150], [0, 150]], "Name: JOHN DOE", 0.9),
            ([[0, 200], [100, 200], [100, 250], [0, 250]], "Date of Birth: 01/01/1990", 0.9),
        ]

        extractor = OCRExtractor()
        result = extractor.extract_pan_data("test.jpg")

        assert result['pan_number'] is None
        assert result['name'] == "JOHN DOE"
        assert result['dob'] == "01/01/1990"
        assert result['confidence'] == 0.5

    @patch('src.services.ocr_extraction.easyocr.Reader')
    def test_extract_pan_with_hindi_labels(self, mock_reader_class):
        """Test PAN extraction with Hindi labels."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader

        mock_reader.readtext.return_value = [
            ([[0, 0], [100, 0], [100, 50], [0, 50]], "आयकर विभाग", 0.9),
            ([[0, 50], [100, 50], [100, 100], [0, 100]], "ABCDE1234F", 0.95),
            ([[0, 100], [100, 100], [100, 150], [0, 150]], "नाम: JOHN DOE", 0.9),
            ([[0, 150], [100, 150], [100, 200], [0, 200]], "पिता का नाम: RICHARD DOE", 0.9),
            ([[0, 200], [100, 200], [100, 250], [0, 250]], "जन्म तिथि: 01/01/1990", 0.9),
        ]

        extractor = OCRExtractor()
        result = extractor.extract_pan_data("test.jpg")

        assert result['pan_number'] == "ABCDE1234F"
        assert result['name'] == "JOHN DOE"
        assert result['father_name'] == "RICHARD DOE"
        assert result['dob'] == "01/01/1990"

    @patch('src.services.ocr_extraction.easyocr.Reader')
    def test_extract_pan_with_date_hyphen_format(self, mock_reader_class):
        """Test PAN extraction with DD-MM-YYYY date format."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader

        mock_reader.readtext.return_value = [
            ([[0, 50], [100, 50], [100, 100], [0, 100]], "ABCDE1234F", 0.95),
            ([[0, 100], [100, 100], [100, 150], [0, 150]], "Name: JOHN DOE", 0.9),
            ([[0, 150], [100, 150], [100, 200], [0, 200]], "Father's Name: RICHARD DOE", 0.9),
            ([[0, 200], [100, 200], [100, 250], [0, 250]], "Date of Birth: 15-06-1985", 0.9),
        ]

        extractor = OCRExtractor()
        result = extractor.extract_pan_data("test.jpg")

        assert result['dob'] == "15-06-1985"

    @patch('src.services.ocr_extraction.easyocr.Reader')
    def test_extract_pan_ocr_failure(self, mock_reader_class):
        """Test PAN extraction handles OCR failure."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader
        mock_reader.readtext.side_effect = Exception("OCR failed")

        extractor = OCRExtractor()
        result = extractor.extract_pan_data("test.jpg")

        assert result['confidence'] == 0.0
        assert result['pan_number'] is None

    @patch('src.services.ocr_extraction.easyocr.Reader')
    def test_extract_pan_returns_dict_structure(self, mock_reader_class):
        """Test PAN extraction returns correct dictionary structure."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader

        mock_reader.readtext.return_value = [
            ([[0, 0], [100, 0], [100, 50], [0, 50]], "INCOME TAX DEPARTMENT", 0.9),
            ([[0, 50], [100, 50], [100, 100], [0, 100]], "ABCDE1234F", 0.95),
        ]

        extractor = OCRExtractor()
        result = extractor.extract_pan_data("test.jpg")

        required_keys = {'pan_number', 'name', 'father_name', 'dob', 'confidence', 'raw_text'}
        assert set(result.keys()) == required_keys

    @patch('src.services.ocr_extraction.easyocr.Reader')
    def test_extract_pan_validates_with_validation_module(self, mock_reader_class):
        """Test PAN extraction uses validation module."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader

        mock_reader.readtext.return_value = [
            ([[0, 50], [100, 50], [100, 100], [0, 100]], "INVALIDPAN", 0.95),
            ([[0, 100], [100, 100], [100, 150], [0, 150]], "Name: JOHN DOE", 0.9),
        ]

        extractor = OCRExtractor()
        result = extractor.extract_pan_data("test.jpg")

        # Invalid PAN should result in pan_number being None or not validated
        assert result['confidence'] == 0.5


class TestAadhaarCardExtraction:
    """Test Aadhaar card extraction from OCR text."""

    @patch('src.services.ocr_extraction.easyocr.Reader')
    def test_extract_aadhaar_with_all_fields(self, mock_reader_class):
        """Test Aadhaar extraction with all fields present."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader

        mock_reader.readtext.return_value = [
            ([[0, 0], [100, 0], [100, 50], [0, 50]], "AADHAAR", 0.9),
            ([[0, 50], [100, 50], [100, 100], [0, 100]], "1234 5678 9012", 0.95),
            ([[0, 100], [100, 100], [100, 150], [0, 150]], "Name: JOHN DOE", 0.9),
            ([[0, 150], [100, 150], [100, 200], [0, 200]], "Date of Birth: 01/01/1990", 0.9),
            ([[0, 200], [100, 200], [100, 250], [0, 250]], "Gender: Male", 0.9),
            ([[0, 250], [100, 250], [100, 300], [0, 300]], "Address: 123 Main St, City", 0.9),
            ([[0, 300], [100, 300], [100, 350], [0, 350]], "Pincode: 400001", 0.9),
        ]

        extractor = OCRExtractor()
        result = extractor.extract_aadhaar_data("test.jpg")

        assert result['aadhaar_number'] == "123456789012"
        assert result['name'] == "JOHN DOE"
        assert result['dob'] == "01/01/1990"
        assert result['gender'] == "Male"
        assert result['address'] == "123 Main St, City"
        assert result['pincode'] == "400001"
        assert result['confidence'] == 0.9
        assert 'raw_text' in result

    @patch('src.services.ocr_extraction.easyocr.Reader')
    def test_extract_aadhaar_without_optional_fields(self, mock_reader_class):
        """Test Aadhaar extraction with missing optional fields (gender, address, pincode)."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader

        mock_reader.readtext.return_value = [
            ([[0, 50], [100, 50], [100, 100], [0, 100]], "123456789012", 0.95),
            ([[0, 100], [100, 100], [100, 150], [0, 150]], "Name: JOHN DOE", 0.9),
            ([[0, 150], [100, 150], [100, 200], [0, 200]], "Date of Birth: 01/01/1990", 0.9),
        ]

        extractor = OCRExtractor()
        result = extractor.extract_aadhaar_data("test.jpg")

        assert result['aadhaar_number'] == "123456789012"
        assert result['name'] == "JOHN DOE"
        assert result['dob'] == "01/01/1990"
        assert result['gender'] is None
        assert result['address'] is None
        assert result['pincode'] is None
        assert result['confidence'] == 0.7

    @patch('src.services.ocr_extraction.easyocr.Reader')
    def test_extract_aadhaar_missing_required_field(self, mock_reader_class):
        """Test Aadhaar extraction with missing required field (name or dob)."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader

        mock_reader.readtext.return_value = [
            ([[0, 50], [100, 50], [100, 100], [0, 100]], "123456789012", 0.95),
            ([[0, 150], [100, 150], [100, 200], [0, 200]], "Date of Birth: 01/01/1990", 0.9),
        ]

        extractor = OCRExtractor()
        result = extractor.extract_aadhaar_data("test.jpg")

        assert result['aadhaar_number'] == "123456789012"
        assert result['name'] is None
        assert result['dob'] == "01/01/1990"
        assert result['confidence'] == 0.5

    @patch('src.services.ocr_extraction.easyocr.Reader')
    def test_extract_aadhaar_with_spaces_in_number(self, mock_reader_class):
        """Test Aadhaar extraction handles spaces in Aadhaar number."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader

        mock_reader.readtext.return_value = [
            ([[0, 50], [100, 50], [100, 100], [0, 100]], "1234 5678 9012", 0.95),
            ([[0, 100], [100, 100], [100, 150], [0, 150]], "Name: JOHN DOE", 0.9),
            ([[0, 150], [100, 150], [100, 200], [0, 200]], "Date of Birth: 01/01/1990", 0.9),
        ]

        extractor = OCRExtractor()
        result = extractor.extract_aadhaar_data("test.jpg")

        assert result['aadhaar_number'] == "123456789012"

    @patch('src.services.ocr_extraction.easyocr.Reader')
    def test_extract_aadhaar_with_hindi_gender(self, mock_reader_class):
        """Test Aadhaar extraction with Hindi gender markers."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader

        mock_reader.readtext.return_value = [
            ([[0, 50], [100, 50], [100, 100], [0, 100]], "123456789012", 0.95),
            ([[0, 100], [100, 100], [100, 150], [0, 150]], "Name: JOHN DOE", 0.9),
            ([[0, 150], [100, 150], [100, 200], [0, 200]], "Date of Birth: 01/01/1990", 0.9),
            ([[0, 200], [100, 200], [100, 250], [0, 250]], "Gender: म", 0.9),
        ]

        extractor = OCRExtractor()
        result = extractor.extract_aadhaar_data("test.jpg")

        assert result['gender'] == "म"

    @patch('src.services.ocr_extraction.easyocr.Reader')
    def test_extract_aadhaar_ocr_failure(self, mock_reader_class):
        """Test Aadhaar extraction handles OCR failure."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader
        mock_reader.readtext.side_effect = Exception("OCR failed")

        extractor = OCRExtractor()
        result = extractor.extract_aadhaar_data("test.jpg")

        assert result['confidence'] == 0.0
        assert result['aadhaar_number'] is None

    @patch('src.services.ocr_extraction.easyocr.Reader')
    def test_extract_aadhaar_returns_dict_structure(self, mock_reader_class):
        """Test Aadhaar extraction returns correct dictionary structure."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader

        mock_reader.readtext.return_value = [
            ([[0, 50], [100, 50], [100, 100], [0, 100]], "123456789012", 0.95),
        ]

        extractor = OCRExtractor()
        result = extractor.extract_aadhaar_data("test.jpg")

        required_keys = {'aadhaar_number', 'name', 'dob', 'gender', 'address', 'pincode', 'confidence', 'raw_text'}
        assert set(result.keys()) == required_keys

    @patch('src.services.ocr_extraction.easyocr.Reader')
    def test_extract_aadhaar_with_hindi_labels(self, mock_reader_class):
        """Test Aadhaar extraction with Hindi labels."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader

        mock_reader.readtext.return_value = [
            ([[0, 50], [100, 50], [100, 100], [0, 100]], "123456789012", 0.95),
            ([[0, 100], [100, 100], [100, 150], [0, 150]], "नाम: JOHN DOE", 0.9),
            ([[0, 150], [100, 150], [100, 200], [0, 200]], "जन्म तिथि: 01/01/1990", 0.9),
            ([[0, 200], [100, 200], [100, 250], [0, 250]], "लिंग: पुरुष", 0.9),
            ([[0, 250], [100, 250], [100, 300], [0, 300]], "पता: 123 Main St, City", 0.9),
            ([[0, 300], [100, 300], [100, 350], [0, 350]], "पिन कोड: 400001", 0.9),
        ]

        extractor = OCRExtractor()
        result = extractor.extract_aadhaar_data("test.jpg")

        assert result['aadhaar_number'] == "123456789012"
        assert result['name'] == "JOHN DOE"
        assert result['dob'] == "01/01/1990"

    @patch('src.services.ocr_extraction.easyocr.Reader')
    def test_extract_aadhaar_with_female_gender(self, mock_reader_class):
        """Test Aadhaar extraction with Female gender."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader

        mock_reader.readtext.return_value = [
            ([[0, 50], [100, 50], [100, 100], [0, 100]], "123456789012", 0.95),
            ([[0, 100], [100, 100], [100, 150], [0, 150]], "Name: JANE DOE", 0.9),
            ([[0, 150], [100, 150], [100, 200], [0, 200]], "Date of Birth: 01/01/1990", 0.9),
            ([[0, 200], [100, 200], [100, 250], [0, 250]], "Gender: Female", 0.9),
        ]

        extractor = OCRExtractor()
        result = extractor.extract_aadhaar_data("test.jpg")

        assert result['gender'] == "Female"

    @patch('src.services.ocr_extraction.easyocr.Reader')
    def test_extract_aadhaar_validates_with_validation_module(self, mock_reader_class):
        """Test Aadhaar extraction uses validation module."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader

        mock_reader.readtext.return_value = [
            ([[0, 50], [100, 50], [100, 100], [0, 100]], "12345", 0.95),  # Invalid
            ([[0, 100], [100, 100], [100, 150], [0, 150]], "Name: JOHN DOE", 0.9),
            ([[0, 150], [100, 150], [100, 200], [0, 200]], "Date of Birth: 01/01/1990", 0.9),
        ]

        extractor = OCRExtractor()
        result = extractor.extract_aadhaar_data("test.jpg")

        assert result['confidence'] == 0.5
