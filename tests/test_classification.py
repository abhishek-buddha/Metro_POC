"""Tests for document classification service."""
import pytest
import base64
from unittest.mock import patch, MagicMock, mock_open
from src.services.classification import DocumentClassifier


class TestDocumentClassifierKeywordDetection:
    """Test keyword-based document classification (Stage 1)."""

    @patch('src.services.classification.easyocr.Reader')
    @patch('src.services.classification.Anthropic')
    def test_classify_pan_card_with_keywords(self, mock_anthropic, mock_reader_class):
        """Test PAN card classification using keyword detection."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader
        mock_reader.readtext.return_value = [
            ([[0, 0], [100, 0], [100, 50], [0, 50]], "INCOME TAX DEPARTMENT", 0.9)
        ]

        classifier = DocumentClassifier()
        doc_type, confidence = classifier._classify_with_keywords("INCOME TAX DEPARTMENT")

        assert doc_type == "PAN_CARD"
        assert confidence == 0.95

    @patch('src.services.classification.easyocr.Reader')
    @patch('src.services.classification.Anthropic')
    def test_classify_pan_card_with_pan_keyword(self, mock_anthropic, mock_reader_class):
        """Test PAN card classification with PAN keyword."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader

        classifier = DocumentClassifier()
        doc_type, confidence = classifier._classify_with_keywords("PAN ABCDE1234F")

        assert doc_type == "PAN_CARD"
        assert confidence == 0.95

    @patch('src.services.classification.easyocr.Reader')
    @patch('src.services.classification.Anthropic')
    def test_classify_pan_card_with_permanent_account_number(self, mock_anthropic, mock_reader_class):
        """Test PAN card classification with PERMANENT ACCOUNT NUMBER keyword."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader

        classifier = DocumentClassifier()
        doc_type, confidence = classifier._classify_with_keywords("PERMANENT ACCOUNT NUMBER")

        assert doc_type == "PAN_CARD"
        assert confidence == 0.95

    @patch('src.services.classification.easyocr.Reader')
    @patch('src.services.classification.Anthropic')
    def test_classify_pan_case_insensitive(self, mock_anthropic, mock_reader_class):
        """Test PAN card classification is case insensitive."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader

        classifier = DocumentClassifier()
        doc_type, confidence = classifier._classify_with_keywords("income tax department")

        assert doc_type == "PAN_CARD"
        assert confidence == 0.95

    @patch('src.services.classification.easyocr.Reader')
    @patch('src.services.classification.Anthropic')
    def test_classify_aadhaar_card_with_keywords(self, mock_anthropic, mock_reader_class):
        """Test Aadhaar card classification using keyword detection."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader

        classifier = DocumentClassifier()
        doc_type, confidence = classifier._classify_with_keywords("AADHAAR 123456789012")

        assert doc_type == "AADHAAR_CARD"
        assert confidence == 0.95

    @patch('src.services.classification.easyocr.Reader')
    @patch('src.services.classification.Anthropic')
    def test_classify_aadhaar_with_hindi_keyword(self, mock_anthropic, mock_reader_class):
        """Test Aadhaar card classification with Hindi keyword."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader

        classifier = DocumentClassifier()
        doc_type, confidence = classifier._classify_with_keywords("आधार")

        assert doc_type == "AADHAAR_CARD"
        assert confidence == 0.95

    @patch('src.services.classification.easyocr.Reader')
    @patch('src.services.classification.Anthropic')
    def test_classify_aadhaar_with_uidai(self, mock_anthropic, mock_reader_class):
        """Test Aadhaar card classification with UIDAI keyword."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader

        classifier = DocumentClassifier()
        doc_type, confidence = classifier._classify_with_keywords("UIDAI Government of India")

        assert doc_type == "AADHAAR_CARD"
        assert confidence == 0.95

    @patch('src.services.classification.easyocr.Reader')
    @patch('src.services.classification.Anthropic')
    def test_classify_bank_document_with_keywords(self, mock_anthropic, mock_reader_class):
        """Test bank document classification using keyword detection."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader

        classifier = DocumentClassifier()
        doc_type, confidence = classifier._classify_with_keywords("BANK ACCOUNT IFSC")

        assert doc_type == "BANK_DOCUMENT"
        assert confidence == 0.95

    @patch('src.services.classification.easyocr.Reader')
    @patch('src.services.classification.Anthropic')
    def test_classify_bank_with_single_keyword(self, mock_anthropic, mock_reader_class):
        """Test bank document classification with single keyword."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader

        classifier = DocumentClassifier()
        doc_type, confidence = classifier._classify_with_keywords("BANK")

        assert doc_type == "BANK_DOCUMENT"
        assert confidence == 0.95

    @patch('src.services.classification.easyocr.Reader')
    @patch('src.services.classification.Anthropic')
    def test_classify_bank_with_branch_keyword(self, mock_anthropic, mock_reader_class):
        """Test bank document classification with BRANCH keyword."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader

        classifier = DocumentClassifier()
        doc_type, confidence = classifier._classify_with_keywords("BRANCH IFSC ACCOUNT")

        assert doc_type == "BANK_DOCUMENT"
        assert confidence == 0.95

    @patch('src.services.classification.easyocr.Reader')
    @patch('src.services.classification.Anthropic')
    def test_classify_unknown_document(self, mock_anthropic, mock_reader_class):
        """Test classification returns UNKNOWN when no keywords match."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader

        classifier = DocumentClassifier()
        doc_type, confidence = classifier._classify_with_keywords("Random document text")

        assert doc_type == "UNKNOWN"
        assert confidence == 0.0


class TestDocumentClassifierAIFallback:
    """Test AI-based classification fallback (Stage 2)."""

    @patch('src.services.classification.easyocr.Reader')
    @patch('src.services.classification.Anthropic')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake_image_data')
    def test_classify_with_ai_pan_card(self, mock_file, mock_anthropic_class, mock_reader_class):
        """Test AI-based classification returns PAN_CARD."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader

        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.content[0].text = "A"
        mock_client.messages.create.return_value = mock_response

        classifier = DocumentClassifier()
        doc_type, confidence = classifier._classify_with_ai("test.jpg")

        assert doc_type == "PAN_CARD"
        assert confidence == 0.85

    @patch('src.services.classification.easyocr.Reader')
    @patch('src.services.classification.Anthropic')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake_image_data')
    def test_classify_with_ai_aadhaar_card(self, mock_file, mock_anthropic_class, mock_reader_class):
        """Test AI-based classification returns AADHAAR_CARD."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader

        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.content[0].text = "B"
        mock_client.messages.create.return_value = mock_response

        classifier = DocumentClassifier()
        doc_type, confidence = classifier._classify_with_ai("test.jpg")

        assert doc_type == "AADHAAR_CARD"
        assert confidence == 0.85

    @patch('src.services.classification.easyocr.Reader')
    @patch('src.services.classification.Anthropic')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake_image_data')
    def test_classify_with_ai_bank_document(self, mock_file, mock_anthropic_class, mock_reader_class):
        """Test AI-based classification returns BANK_DOCUMENT."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader

        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.content[0].text = "C"
        mock_client.messages.create.return_value = mock_response

        classifier = DocumentClassifier()
        doc_type, confidence = classifier._classify_with_ai("test.jpg")

        assert doc_type == "BANK_DOCUMENT"
        assert confidence == 0.85

    @patch('src.services.classification.easyocr.Reader')
    @patch('src.services.classification.Anthropic')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake_image_data')
    def test_classify_with_ai_unknown(self, mock_file, mock_anthropic_class, mock_reader_class):
        """Test AI-based classification returns UNKNOWN for unclear documents."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader

        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.content[0].text = "D"
        mock_client.messages.create.return_value = mock_response

        classifier = DocumentClassifier()
        doc_type, confidence = classifier._classify_with_ai("test.jpg")

        assert doc_type == "UNKNOWN"
        assert confidence == 0.5

    @patch('src.services.classification.easyocr.Reader')
    @patch('src.services.classification.Anthropic')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake_image_data')
    def test_classify_with_ai_calls_vision_api(self, mock_file, mock_anthropic_class, mock_reader_class):
        """Test AI classification calls Claude Vision API with correct parameters."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader

        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.content[0].text = "A"
        mock_client.messages.create.return_value = mock_response

        classifier = DocumentClassifier()
        classifier._classify_with_ai("test.jpg")

        # Verify API was called
        assert mock_client.messages.create.called

    @patch('src.services.classification.easyocr.Reader')
    @patch('src.services.classification.Anthropic')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake_image_data')
    def test_classify_with_ai_png_format(self, mock_file, mock_anthropic_class, mock_reader_class):
        """Test AI classification with PNG file format."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader

        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.content[0].text = "A"
        mock_client.messages.create.return_value = mock_response

        classifier = DocumentClassifier()
        doc_type, confidence = classifier._classify_with_ai("test.png")

        assert doc_type == "PAN_CARD"
        assert confidence == 0.85

    @patch('src.services.classification.easyocr.Reader')
    @patch('src.services.classification.Anthropic')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake_image_data')
    def test_classify_with_ai_jpeg_format(self, mock_file, mock_anthropic_class, mock_reader_class):
        """Test AI classification with JPEG file format."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader

        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.content[0].text = "B"
        mock_client.messages.create.return_value = mock_response

        classifier = DocumentClassifier()
        doc_type, confidence = classifier._classify_with_ai("test.jpeg")

        assert doc_type == "AADHAAR_CARD"
        assert confidence == 0.85


class TestDocumentClassifierFullPipeline:
    """Test full classification pipeline (Stage 1 + fallback)."""

    @patch('src.services.classification.easyocr.Reader')
    @patch('src.services.classification.Anthropic')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake_image_data')
    def test_classify_document_succeeds_with_keywords(
        self, mock_file, mock_anthropic_class, mock_reader_class
    ):
        """Test full pipeline returns result from keyword detection."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader
        mock_reader.readtext.return_value = [
            ([[0, 0], [100, 0], [100, 50], [0, 50]], "INCOME TAX", 0.9)
        ]

        classifier = DocumentClassifier()
        doc_type, confidence = classifier.classify_document("test.jpg")

        assert doc_type == "PAN_CARD"
        assert confidence == 0.95

    @patch('src.services.classification.easyocr.Reader')
    @patch('src.services.classification.Anthropic')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake_image_data')
    def test_classify_document_fallback_to_ai(
        self, mock_file, mock_anthropic_class, mock_reader_class
    ):
        """Test full pipeline falls back to AI when keywords don't match."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader
        mock_reader.readtext.return_value = [
            ([[0, 0], [100, 0], [100, 50], [0, 50]], "Random document", 0.9)
        ]

        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.content[0].text = "A"
        mock_client.messages.create.return_value = mock_response

        classifier = DocumentClassifier()
        doc_type, confidence = classifier.classify_document("test.jpg")

        assert doc_type == "PAN_CARD"
        assert confidence == 0.85

    @patch('src.services.classification.easyocr.Reader')
    @patch('src.services.classification.Anthropic')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake_image_data')
    def test_classify_document_invalid_file(self, mock_file, mock_anthropic_class, mock_reader_class):
        """Test classification handles file read errors gracefully."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader
        mock_reader.readtext.side_effect = Exception("File not found")

        classifier = DocumentClassifier()

        with pytest.raises(Exception):
            classifier.classify_document("nonexistent.jpg")

    @patch('src.services.classification.easyocr.Reader')
    @patch('src.services.classification.Anthropic')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake_image_data')
    def test_classify_document_aadhaar(self, mock_file, mock_anthropic_class, mock_reader_class):
        """Test full pipeline with Aadhaar card."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader
        mock_reader.readtext.return_value = [
            ([[0, 0], [100, 0], [100, 50], [0, 50]], "AADHAAR", 0.9)
        ]

        classifier = DocumentClassifier()
        doc_type, confidence = classifier.classify_document("test.jpg")

        assert doc_type == "AADHAAR_CARD"
        assert confidence == 0.95

    @patch('src.services.classification.easyocr.Reader')
    @patch('src.services.classification.Anthropic')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake_image_data')
    def test_classify_document_bank(self, mock_file, mock_anthropic_class, mock_reader_class):
        """Test full pipeline with bank document."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader
        mock_reader.readtext.return_value = [
            ([[0, 0], [100, 0], [100, 50], [0, 50]], "IFSC ACCOUNT BANK", 0.9)
        ]

        classifier = DocumentClassifier()
        doc_type, confidence = classifier.classify_document("test.jpg")

        assert doc_type == "BANK_DOCUMENT"
        assert confidence == 0.95

    @patch('src.services.classification.easyocr.Reader')
    @patch('src.services.classification.Anthropic')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake_image_data')
    def test_classify_document_returns_tuple(self, mock_file, mock_anthropic_class, mock_reader_class):
        """Test classification returns tuple of (doc_type, confidence)."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader
        mock_reader.readtext.return_value = [
            ([[0, 0], [100, 0], [100, 50], [0, 50]], "INCOME TAX", 0.9)
        ]

        classifier = DocumentClassifier()
        result = classifier.classify_document("test.jpg")

        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], str)
        assert isinstance(result[1], float)

    @patch('src.services.classification.easyocr.Reader')
    @patch('src.services.classification.Anthropic')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake_image_data')
    def test_classify_document_confidence_range(
        self, mock_file, mock_anthropic_class, mock_reader_class
    ):
        """Test classification confidence is between 0.0 and 1.0."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader
        mock_reader.readtext.return_value = [
            ([[0, 0], [100, 0], [100, 50], [0, 50]], "INCOME TAX", 0.9)
        ]

        classifier = DocumentClassifier()
        doc_type, confidence = classifier.classify_document("test.jpg")

        assert 0.0 <= confidence <= 1.0

    @patch('src.services.classification.easyocr.Reader')
    @patch('src.services.classification.Anthropic')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake_image_data')
    def test_classify_document_valid_doc_types(
        self, mock_file, mock_anthropic_class, mock_reader_class
    ):
        """Test classification returns one of valid document types."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader
        mock_reader.readtext.return_value = [
            ([[0, 0], [100, 0], [100, 50], [0, 50]], "INCOME TAX", 0.9)
        ]

        classifier = DocumentClassifier()
        doc_type, confidence = classifier.classify_document("test.jpg")

        valid_types = {"PAN_CARD", "AADHAAR_CARD", "BANK_DOCUMENT", "UNKNOWN"}
        assert doc_type in valid_types


class TestDocumentClassifierInitialization:
    """Test DocumentClassifier initialization."""

    @patch('src.services.classification.easyocr.Reader')
    @patch('src.services.classification.Anthropic')
    def test_classifier_initializes_reader(self, mock_anthropic_class, mock_reader_class):
        """Test classifier initializes EasyOCR reader with correct languages."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader

        classifier = DocumentClassifier()

        mock_reader_class.assert_called_once_with(['en', 'hi'])

    @patch('src.services.classification.easyocr.Reader')
    @patch('src.services.classification.Anthropic')
    def test_classifier_initializes_anthropic_client(self, mock_anthropic_class, mock_reader_class):
        """Test classifier initializes Anthropic client."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader

        classifier = DocumentClassifier()

        assert mock_anthropic_class.called

    @patch('src.services.classification.easyocr.Reader')
    @patch('src.services.classification.Anthropic')
    def test_classifier_stores_reader(self, mock_anthropic_class, mock_reader_class):
        """Test classifier stores reader instance."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader

        classifier = DocumentClassifier()

        assert classifier.reader is not None

    @patch('src.services.classification.easyocr.Reader')
    @patch('src.services.classification.Anthropic')
    def test_classifier_stores_client(self, mock_anthropic_class, mock_reader_class):
        """Test classifier stores Anthropic client instance."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader

        classifier = DocumentClassifier()

        assert classifier.client is not None
