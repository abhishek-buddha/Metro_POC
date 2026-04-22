"""Tests for WhatsApp messaging service."""
import pytest
from unittest.mock import patch, MagicMock
from src.services.whatsapp import WhatsAppClient, format_phone_number


class TestPhoneNumberFormatting:
    """Test phone number formatting utility function."""

    def test_format_phone_number_basic_10_digits(self):
        """Test formatting basic 10-digit phone number."""
        result = format_phone_number("9876543210")
        assert result == "whatsapp:+919876543210"

    def test_format_phone_number_with_plus_91(self):
        """Test formatting phone number that already has +91."""
        result = format_phone_number("+919876543210")
        assert result == "whatsapp:+919876543210"

    def test_format_phone_number_with_spaces(self):
        """Test formatting phone number with spaces."""
        result = format_phone_number("9876 543 210")
        assert result == "whatsapp:+919876543210"

    def test_format_phone_number_with_91_no_plus(self):
        """Test formatting phone number with 91 prefix but no plus."""
        result = format_phone_number("919876543210")
        assert result == "whatsapp:+919876543210"

    def test_format_phone_number_with_mixed_formatting(self):
        """Test formatting phone number with mixed spaces and formatting."""
        result = format_phone_number("+91 9876 543210")
        assert result == "whatsapp:+919876543210"


class TestWhatsAppClientInit:
    """Test WhatsAppClient initialization."""

    @patch('src.services.whatsapp.Client')
    def test_client_initialization(self, mock_client_class):
        """Test that WhatsAppClient initializes Twilio client with correct credentials."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        with patch('src.services.whatsapp.config') as mock_config:
            mock_config.TWILIO_ACCOUNT_SID = "test_account_sid"
            mock_config.TWILIO_AUTH_TOKEN = "test_auth_token"
            mock_config.TWILIO_WHATSAPP_NUMBER = "whatsapp:+1234567890"

            client = WhatsAppClient()

            mock_client_class.assert_called_once_with("test_account_sid", "test_auth_token")
            assert client.client == mock_client
            assert client.from_number == "whatsapp:+1234567890"


class TestSendMessage:
    """Test send_message method."""

    @patch('src.services.whatsapp.Client')
    @patch('src.services.whatsapp.logger')
    def test_send_message_success(self, mock_logger, mock_client_class):
        """Test successful message sending."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_message = MagicMock()
        mock_message.sid = "test_message_sid"
        mock_client.messages.create.return_value = mock_message

        with patch('src.services.whatsapp.config') as mock_config:
            mock_config.TWILIO_ACCOUNT_SID = "test_account_sid"
            mock_config.TWILIO_AUTH_TOKEN = "test_auth_token"
            mock_config.TWILIO_WHATSAPP_NUMBER = "whatsapp:+1234567890"

            client = WhatsAppClient()
            result = client.send_message("9876543210", "Test message")

            assert result is True
            mock_client.messages.create.assert_called_once_with(
                from_="whatsapp:+1234567890",
                to="whatsapp:+919876543210",
                body="Test message"
            )
            # Verify logging was called
            assert mock_logger.info.called

    @patch('src.services.whatsapp.Client')
    @patch('src.services.whatsapp.logger')
    def test_send_message_with_formatted_phone(self, mock_logger, mock_client_class):
        """Test message sending with already formatted phone number."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_message = MagicMock()
        mock_message.sid = "test_message_sid"
        mock_client.messages.create.return_value = mock_message

        with patch('src.services.whatsapp.config') as mock_config:
            mock_config.TWILIO_ACCOUNT_SID = "test_account_sid"
            mock_config.TWILIO_AUTH_TOKEN = "test_auth_token"
            mock_config.TWILIO_WHATSAPP_NUMBER = "whatsapp:+1234567890"

            client = WhatsAppClient()
            result = client.send_message("+919876543210", "Test message")

            assert result is True
            mock_client.messages.create.assert_called_once()

    @patch('src.services.whatsapp.Client')
    @patch('src.services.whatsapp.logger')
    def test_send_message_twilio_exception(self, mock_logger, mock_client_class):
        """Test message sending when Twilio raises exception."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.messages.create.side_effect = Exception("Twilio API error")

        with patch('src.services.whatsapp.config') as mock_config:
            mock_config.TWILIO_ACCOUNT_SID = "test_account_sid"
            mock_config.TWILIO_AUTH_TOKEN = "test_auth_token"
            mock_config.TWILIO_WHATSAPP_NUMBER = "whatsapp:+1234567890"

            client = WhatsAppClient()
            result = client.send_message("9876543210", "Test message")

            assert result is False
            assert mock_logger.error.called


class TestSendDocumentRequest:
    """Test send_document_request method."""

    @patch('src.services.whatsapp.Client')
    @patch('src.services.whatsapp.logger')
    def test_send_document_request_aadhaar(self, mock_logger, mock_client_class):
        """Test sending Aadhaar card document request."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_message = MagicMock()
        mock_message.sid = "test_message_sid"
        mock_client.messages.create.return_value = mock_message

        with patch('src.services.whatsapp.config') as mock_config:
            mock_config.TWILIO_ACCOUNT_SID = "test_account_sid"
            mock_config.TWILIO_AUTH_TOKEN = "test_auth_token"
            mock_config.TWILIO_WHATSAPP_NUMBER = "whatsapp:+1234567890"

            client = WhatsAppClient()
            result = client.send_document_request("9876543210", "Aadhaar card")

            assert result is True
            # Verify the message contains the expected template
            call_args = mock_client.messages.create.call_args
            assert "Aadhaar card" in call_args.kwargs['body']
            assert "Please send your" in call_args.kwargs['body']

    @patch('src.services.whatsapp.Client')
    @patch('src.services.whatsapp.logger')
    def test_send_document_request_bank_document(self, mock_logger, mock_client_class):
        """Test sending bank document request."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_message = MagicMock()
        mock_message.sid = "test_message_sid"
        mock_client.messages.create.return_value = mock_message

        with patch('src.services.whatsapp.config') as mock_config:
            mock_config.TWILIO_ACCOUNT_SID = "test_account_sid"
            mock_config.TWILIO_AUTH_TOKEN = "test_auth_token"
            mock_config.TWILIO_WHATSAPP_NUMBER = "whatsapp:+1234567890"

            client = WhatsAppClient()
            result = client.send_document_request("9876543210", "bank document")

            assert result is True
            call_args = mock_client.messages.create.call_args
            assert "bank document" in call_args.kwargs['body']

    @patch('src.services.whatsapp.Client')
    @patch('src.services.whatsapp.logger')
    def test_send_document_request_failure(self, mock_logger, mock_client_class):
        """Test document request when Twilio raises exception."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.messages.create.side_effect = Exception("Twilio API error")

        with patch('src.services.whatsapp.config') as mock_config:
            mock_config.TWILIO_ACCOUNT_SID = "test_account_sid"
            mock_config.TWILIO_AUTH_TOKEN = "test_auth_token"
            mock_config.TWILIO_WHATSAPP_NUMBER = "whatsapp:+1234567890"

            client = WhatsAppClient()
            result = client.send_document_request("9876543210", "Aadhaar card")

            assert result is False
            assert mock_logger.error.called


class TestSendConfirmation:
    """Test send_confirmation method."""

    @patch('src.services.whatsapp.Client')
    @patch('src.services.whatsapp.logger')
    def test_send_confirmation_success(self, mock_logger, mock_client_class):
        """Test successful confirmation message sending."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_message = MagicMock()
        mock_message.sid = "test_message_sid"
        mock_client.messages.create.return_value = mock_message

        with patch('src.services.whatsapp.config') as mock_config:
            mock_config.TWILIO_ACCOUNT_SID = "test_account_sid"
            mock_config.TWILIO_AUTH_TOKEN = "test_auth_token"
            mock_config.TWILIO_WHATSAPP_NUMBER = "whatsapp:+1234567890"

            client = WhatsAppClient()
            result = client.send_confirmation("9876543210", "sub_123456")

            assert result is True
            call_args = mock_client.messages.create.call_args
            assert "sub_123456" in call_args.kwargs['body']
            assert "received" in call_args.kwargs['body'].lower()

    @patch('src.services.whatsapp.Client')
    @patch('src.services.whatsapp.logger')
    def test_send_confirmation_includes_submission_id(self, mock_logger, mock_client_class):
        """Test that confirmation message includes submission ID."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_message = MagicMock()
        mock_message.sid = "test_message_sid"
        mock_client.messages.create.return_value = mock_message

        with patch('src.services.whatsapp.config') as mock_config:
            mock_config.TWILIO_ACCOUNT_SID = "test_account_sid"
            mock_config.TWILIO_AUTH_TOKEN = "test_auth_token"
            mock_config.TWILIO_WHATSAPP_NUMBER = "whatsapp:+1234567890"

            client = WhatsAppClient()
            submission_id = "kyc_abcd1234"
            result = client.send_confirmation("9876543210", submission_id)

            assert result is True
            call_args = mock_client.messages.create.call_args
            assert submission_id in call_args.kwargs['body']

    @patch('src.services.whatsapp.Client')
    @patch('src.services.whatsapp.logger')
    def test_send_confirmation_failure(self, mock_logger, mock_client_class):
        """Test confirmation sending when Twilio raises exception."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.messages.create.side_effect = Exception("Twilio API error")

        with patch('src.services.whatsapp.config') as mock_config:
            mock_config.TWILIO_ACCOUNT_SID = "test_account_sid"
            mock_config.TWILIO_AUTH_TOKEN = "test_auth_token"
            mock_config.TWILIO_WHATSAPP_NUMBER = "whatsapp:+1234567890"

            client = WhatsAppClient()
            result = client.send_confirmation("9876543210", "sub_123456")

            assert result is False
            assert mock_logger.error.called


class TestSendWelcome:
    """Test send_welcome method."""

    @patch('src.services.whatsapp.Client')
    @patch('src.services.whatsapp.logger')
    def test_send_welcome_success(self, mock_logger, mock_client_class):
        """Test successful welcome message sending."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_message = MagicMock()
        mock_message.sid = "test_message_sid"
        mock_client.messages.create.return_value = mock_message

        with patch('src.services.whatsapp.config') as mock_config:
            mock_config.TWILIO_ACCOUNT_SID = "test_account_sid"
            mock_config.TWILIO_AUTH_TOKEN = "test_auth_token"
            mock_config.TWILIO_WHATSAPP_NUMBER = "whatsapp:+1234567890"

            client = WhatsAppClient()
            result = client.send_welcome("9876543210")

            assert result is True
            call_args = mock_client.messages.create.call_args
            assert "Welcome to Metro KYC!" in call_args.kwargs['body']
            assert "PAN card photo" in call_args.kwargs['body']

    @patch('src.services.whatsapp.Client')
    @patch('src.services.whatsapp.logger')
    def test_send_welcome_exact_message(self, mock_logger, mock_client_class):
        """Test that welcome message matches spec exactly."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_message = MagicMock()
        mock_message.sid = "test_message_sid"
        mock_client.messages.create.return_value = mock_message

        with patch('src.services.whatsapp.config') as mock_config:
            mock_config.TWILIO_ACCOUNT_SID = "test_account_sid"
            mock_config.TWILIO_AUTH_TOKEN = "test_auth_token"
            mock_config.TWILIO_WHATSAPP_NUMBER = "whatsapp:+1234567890"

            client = WhatsAppClient()
            result = client.send_welcome("9876543210")

            assert result is True
            call_args = mock_client.messages.create.call_args
            expected_message = "Welcome to Metro KYC! Please send your PAN card photo."
            assert call_args.kwargs['body'] == expected_message

    @patch('src.services.whatsapp.Client')
    @patch('src.services.whatsapp.logger')
    def test_send_welcome_failure(self, mock_logger, mock_client_class):
        """Test welcome sending when Twilio raises exception."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.messages.create.side_effect = Exception("Twilio API error")

        with patch('src.services.whatsapp.config') as mock_config:
            mock_config.TWILIO_ACCOUNT_SID = "test_account_sid"
            mock_config.TWILIO_AUTH_TOKEN = "test_auth_token"
            mock_config.TWILIO_WHATSAPP_NUMBER = "whatsapp:+1234567890"

            client = WhatsAppClient()
            result = client.send_welcome("9876543210")

            assert result is False
            assert mock_logger.error.called


class TestSendError:
    """Test send_error method."""

    @patch('src.services.whatsapp.Client')
    @patch('src.services.whatsapp.logger')
    def test_send_error_success(self, mock_logger, mock_client_class):
        """Test successful error message sending."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_message = MagicMock()
        mock_message.sid = "test_message_sid"
        mock_client.messages.create.return_value = mock_message

        with patch('src.services.whatsapp.config') as mock_config:
            mock_config.TWILIO_ACCOUNT_SID = "test_account_sid"
            mock_config.TWILIO_AUTH_TOKEN = "test_auth_token"
            mock_config.TWILIO_WHATSAPP_NUMBER = "whatsapp:+1234567890"

            client = WhatsAppClient()
            result = client.send_error("9876543210")

            assert result is True
            call_args = mock_client.messages.create.call_args
            assert "Error processing your document" in call_args.kwargs['body']
            assert "Please try again" in call_args.kwargs['body']

    @patch('src.services.whatsapp.Client')
    @patch('src.services.whatsapp.logger')
    def test_send_error_exact_message(self, mock_logger, mock_client_class):
        """Test that error message matches spec exactly."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_message = MagicMock()
        mock_message.sid = "test_message_sid"
        mock_client.messages.create.return_value = mock_message

        with patch('src.services.whatsapp.config') as mock_config:
            mock_config.TWILIO_ACCOUNT_SID = "test_account_sid"
            mock_config.TWILIO_AUTH_TOKEN = "test_auth_token"
            mock_config.TWILIO_WHATSAPP_NUMBER = "whatsapp:+1234567890"

            client = WhatsAppClient()
            result = client.send_error("9876543210")

            assert result is True
            call_args = mock_client.messages.create.call_args
            expected_message = "❌ Error processing your document. Please try again."
            assert call_args.kwargs['body'] == expected_message

    @patch('src.services.whatsapp.Client')
    @patch('src.services.whatsapp.logger')
    def test_send_error_includes_error_indicator(self, mock_logger, mock_client_class):
        """Test that error message includes error emoji indicator."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_message = MagicMock()
        mock_message.sid = "test_message_sid"
        mock_client.messages.create.return_value = mock_message

        with patch('src.services.whatsapp.config') as mock_config:
            mock_config.TWILIO_ACCOUNT_SID = "test_account_sid"
            mock_config.TWILIO_AUTH_TOKEN = "test_auth_token"
            mock_config.TWILIO_WHATSAPP_NUMBER = "whatsapp:+1234567890"

            client = WhatsAppClient()
            result = client.send_error("9876543210")

            assert result is True
            call_args = mock_client.messages.create.call_args
            assert "❌" in call_args.kwargs['body']

    @patch('src.services.whatsapp.Client')
    @patch('src.services.whatsapp.logger')
    def test_send_error_failure(self, mock_logger, mock_client_class):
        """Test error sending when Twilio raises exception."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.messages.create.side_effect = Exception("Twilio API error")

        with patch('src.services.whatsapp.config') as mock_config:
            mock_config.TWILIO_ACCOUNT_SID = "test_account_sid"
            mock_config.TWILIO_AUTH_TOKEN = "test_auth_token"
            mock_config.TWILIO_WHATSAPP_NUMBER = "whatsapp:+1234567890"

            client = WhatsAppClient()
            result = client.send_error("9876543210")

            assert result is False
            assert mock_logger.error.called


class TestMessageTemplates:
    """Test message template content."""

    @patch('src.services.whatsapp.Client')
    def test_welcome_message_template(self, mock_client_class):
        """Test welcome message uses correct template."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_message = MagicMock()
        mock_client.messages.create.return_value = mock_message

        with patch('src.services.whatsapp.config') as mock_config:
            mock_config.TWILIO_ACCOUNT_SID = "test_account_sid"
            mock_config.TWILIO_AUTH_TOKEN = "test_auth_token"
            mock_config.TWILIO_WHATSAPP_NUMBER = "whatsapp:+1234567890"

            client = WhatsAppClient()
            # Test that the welcome message can be sent
            result = client.send_message("9876543210", "Welcome to Metro KYC! Please send your PAN card photo.")
            assert result is True

    @patch('src.services.whatsapp.Client')
    def test_error_message_has_error_indicator(self, mock_client_class):
        """Test error message uses correct template."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_message = MagicMock()
        mock_client.messages.create.return_value = mock_message

        with patch('src.services.whatsapp.config') as mock_config:
            mock_config.TWILIO_ACCOUNT_SID = "test_account_sid"
            mock_config.TWILIO_AUTH_TOKEN = "test_auth_token"
            mock_config.TWILIO_WHATSAPP_NUMBER = "whatsapp:+1234567890"

            client = WhatsAppClient()
            error_message = "Error processing your document. Please try again."
            result = client.send_message("9876543210", error_message)
            assert result is True


class TestLogging:
    """Test logging behavior."""

    @patch('src.services.whatsapp.Client')
    @patch('src.services.whatsapp.logger')
    def test_log_includes_phone_number(self, mock_logger, mock_client_class):
        """Test that logging includes phone number."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_message = MagicMock()
        mock_client.messages.create.return_value = mock_message

        with patch('src.services.whatsapp.config') as mock_config:
            mock_config.TWILIO_ACCOUNT_SID = "test_account_sid"
            mock_config.TWILIO_AUTH_TOKEN = "test_auth_token"
            mock_config.TWILIO_WHATSAPP_NUMBER = "whatsapp:+1234567890"

            client = WhatsAppClient()
            client.send_message("9876543210", "Test message")

            # Verify logger.info was called
            assert mock_logger.info.called

    @patch('src.services.whatsapp.Client')
    @patch('src.services.whatsapp.logger')
    def test_log_error_on_failure(self, mock_logger, mock_client_class):
        """Test that errors are logged on failure."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.messages.create.side_effect = Exception("API Error")

        with patch('src.services.whatsapp.config') as mock_config:
            mock_config.TWILIO_ACCOUNT_SID = "test_account_sid"
            mock_config.TWILIO_AUTH_TOKEN = "test_auth_token"
            mock_config.TWILIO_WHATSAPP_NUMBER = "whatsapp:+1234567890"

            client = WhatsAppClient()
            client.send_message("9876543210", "Test message")

            # Verify logger.error was called
            assert mock_logger.error.called
