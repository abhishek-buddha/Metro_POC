"""Tests for format validation and name matching services."""
import pytest
from src.services.validation import (
    validate_pan,
    validate_aadhaar,
    validate_ifsc,
    validate_account_number,
    normalize_name,
    calculate_name_match,
)


class TestFormatValidation:
    """Test format validation functions."""

    # PAN validation tests
    def test_validate_pan_valid(self):
        """Test valid PAN format."""
        assert validate_pan("ABCDE1234F") is True

    def test_validate_pan_valid_different(self):
        """Test another valid PAN format."""
        assert validate_pan("ZYXWV9876A") is True

    def test_validate_pan_invalid_lowercase(self):
        """Test invalid PAN with lowercase letters."""
        assert validate_pan("abcde1234f") is False

    def test_validate_pan_invalid_short(self):
        """Test invalid PAN that's too short."""
        assert validate_pan("ABCD123E") is False

    def test_validate_pan_invalid_long(self):
        """Test invalid PAN that's too long."""
        assert validate_pan("ABCDE12345F") is False

    def test_validate_pan_invalid_letters_at_end(self):
        """Test invalid PAN with letters in digit positions."""
        assert validate_pan("ABCDEA234F") is False

    def test_validate_pan_none(self):
        """Test PAN validation with None."""
        assert validate_pan(None) is False

    def test_validate_pan_empty(self):
        """Test PAN validation with empty string."""
        assert validate_pan("") is False

    # Aadhaar validation tests
    def test_validate_aadhaar_valid(self):
        """Test valid Aadhaar format."""
        assert validate_aadhaar("123456789012") is True

    def test_validate_aadhaar_valid_with_spaces(self):
        """Test valid Aadhaar with spaces."""
        assert validate_aadhaar("1234 5678 9012") is True

    def test_validate_aadhaar_valid_with_various_spaces(self):
        """Test valid Aadhaar with various space patterns."""
        assert validate_aadhaar("12345678 9012") is True

    def test_validate_aadhaar_invalid_short(self):
        """Test invalid Aadhaar that's too short."""
        assert validate_aadhaar("12345678901") is False

    def test_validate_aadhaar_invalid_long(self):
        """Test invalid Aadhaar that's too long."""
        assert validate_aadhaar("1234567890123") is False

    def test_validate_aadhaar_invalid_non_digits(self):
        """Test invalid Aadhaar with non-digit characters."""
        assert validate_aadhaar("123456789ABC") is False

    def test_validate_aadhaar_none(self):
        """Test Aadhaar validation with None."""
        assert validate_aadhaar(None) is False

    def test_validate_aadhaar_empty(self):
        """Test Aadhaar validation with empty string."""
        assert validate_aadhaar("") is False

    # IFSC validation tests
    def test_validate_ifsc_valid(self):
        """Test valid IFSC format."""
        assert validate_ifsc("SBIN0001234") is True

    def test_validate_ifsc_valid_with_digits(self):
        """Test valid IFSC with digits in last 6 chars."""
        assert validate_ifsc("HDFC0000456") is True

    def test_validate_ifsc_invalid_lowercase(self):
        """Test invalid IFSC with lowercase letters."""
        assert validate_ifsc("sbin0001234") is False

    def test_validate_ifsc_invalid_no_zero(self):
        """Test invalid IFSC without required zero."""
        assert validate_ifsc("SBIN1001234") is False

    def test_validate_ifsc_invalid_short(self):
        """Test invalid IFSC that's too short."""
        assert validate_ifsc("SBIN000123") is False

    def test_validate_ifsc_invalid_long(self):
        """Test invalid IFSC that's too long."""
        assert validate_ifsc("SBIN00012345") is False

    def test_validate_ifsc_invalid_chars(self):
        """Test invalid IFSC with invalid characters."""
        assert validate_ifsc("SBIN00@1234") is False

    def test_validate_ifsc_none(self):
        """Test IFSC validation with None."""
        assert validate_ifsc(None) is False

    def test_validate_ifsc_empty(self):
        """Test IFSC validation with empty string."""
        assert validate_ifsc("") is False

    # Account number validation tests
    def test_validate_account_number_valid_9_digits(self):
        """Test valid account number with 9 digits."""
        assert validate_account_number("123456789") is True

    def test_validate_account_number_valid_18_digits(self):
        """Test valid account number with 18 digits."""
        assert validate_account_number("123456789012345678") is True

    def test_validate_account_number_valid_middle(self):
        """Test valid account number with 13 digits."""
        assert validate_account_number("1234567890123") is True

    def test_validate_account_number_invalid_short(self):
        """Test invalid account number that's too short."""
        assert validate_account_number("12345678") is False

    def test_validate_account_number_invalid_long(self):
        """Test invalid account number that's too long."""
        assert validate_account_number("1234567890123456789") is False

    def test_validate_account_number_invalid_non_digits(self):
        """Test invalid account number with non-digit characters."""
        assert validate_account_number("12345678A") is False

    def test_validate_account_number_invalid_spaces(self):
        """Test invalid account number with spaces."""
        assert validate_account_number("123456789 123") is False

    def test_validate_account_number_none(self):
        """Test account number validation with None."""
        assert validate_account_number(None) is False

    def test_validate_account_number_empty(self):
        """Test account number validation with empty string."""
        assert validate_account_number("") is False


class TestNameNormalization:
    """Test name normalization function."""

    def test_normalize_name_basic(self):
        """Test basic name normalization."""
        assert normalize_name("JOHN DOE") == "JOHN DOE"

    def test_normalize_name_lowercase(self):
        """Test name normalization converts to uppercase."""
        assert normalize_name("john doe") == "JOHN DOE"

    def test_normalize_name_remove_mr(self):
        """Test removal of MR title."""
        assert normalize_name("MR JOHN SMITH") == "JOHN SMITH"

    def test_normalize_name_remove_mrs(self):
        """Test removal of MRS title."""
        assert normalize_name("MRS JANE SMITH") == "JANE SMITH"

    def test_normalize_name_remove_dr(self):
        """Test removal of DR title."""
        assert normalize_name("DR JAMES WILSON") == "JAMES WILSON"

    def test_normalize_name_remove_shri(self):
        """Test removal of SHRI title."""
        # Note: KUMAR is also removed as a suffix, so result is just "RAJESH"
        assert normalize_name("SHRI RAJESH KUMAR") == "RAJESH"

    def test_normalize_name_remove_smt(self):
        """Test removal of SMT title."""
        assert normalize_name("SMT PRIYA SHARMA") == "PRIYA SHARMA"

    def test_normalize_name_remove_kumar(self):
        """Test removal of KUMAR suffix."""
        assert normalize_name("JOHN KUMAR") == "JOHN"

    def test_normalize_name_remove_kumari(self):
        """Test removal of KUMARI suffix."""
        assert normalize_name("JANE KUMARI") == "JANE"

    def test_normalize_name_multiple_titles(self):
        """Test removal of multiple titles (case insensitive)."""
        assert normalize_name("Mr. Dr. JOHN SMITH") == "JOHN SMITH"

    def test_normalize_name_extra_spaces(self):
        """Test removal of extra spaces."""
        assert normalize_name("JOHN    DOE") == "JOHN DOE"

    def test_normalize_name_special_chars(self):
        """Test removal of special characters."""
        assert normalize_name("JOHN-DOE'S") == "JOHN DOES"

    def test_normalize_name_with_periods(self):
        """Test removal of periods from titles."""
        assert normalize_name("MR. JOHN SMITH") == "JOHN SMITH"

    def test_normalize_name_complex_case(self):
        """Test complex normalization with multiple issues."""
        assert normalize_name("Mr. Dr. JOHN  KUMAR-SINGH") == "JOHN SINGH"

    def test_normalize_name_leading_trailing_spaces(self):
        """Test removal of leading/trailing spaces."""
        assert normalize_name("  JOHN DOE  ") == "JOHN DOE"

    def test_normalize_name_none(self):
        """Test normalization with None."""
        assert normalize_name(None) == ""

    def test_normalize_name_empty(self):
        """Test normalization with empty string."""
        assert normalize_name("") == ""

    def test_normalize_name_case_insensitive_title_removal(self):
        """Test that title removal is case insensitive."""
        assert normalize_name("mr john smith") == "JOHN SMITH"
        assert normalize_name("Mr John Smith") == "JOHN SMITH"
        assert normalize_name("MR JOHN SMITH") == "JOHN SMITH"


class TestNameMatching:
    """Test name matching calculation."""

    def test_calculate_name_match_identical(self):
        """Test name matching with identical names."""
        ratio = calculate_name_match("JOHN SMITH", "JOHN SMITH")
        assert ratio == 1.0

    def test_calculate_name_match_similar(self):
        """Test name matching with similar names."""
        ratio = calculate_name_match("JOHN SMITH", "JOHN SMYTH")
        assert 0.8 < ratio < 1.0

    def test_calculate_name_match_different(self):
        """Test name matching with different names."""
        ratio = calculate_name_match("JOHN SMITH", "JANE DOE")
        assert 0.0 <= ratio < 0.5

    def test_calculate_name_match_with_spaces(self):
        """Test name matching normalizes spaces."""
        ratio = calculate_name_match("JOHN  SMITH", "JOHN SMITH")
        assert ratio == 1.0

    def test_calculate_name_match_case_insensitive(self):
        """Test name matching is case insensitive."""
        ratio = calculate_name_match("john smith", "JOHN SMITH")
        assert ratio == 1.0

    def test_calculate_name_match_with_titles(self):
        """Test name matching removes titles before comparing."""
        ratio = calculate_name_match("MR JOHN SMITH", "JOHN SMITH")
        assert ratio == 1.0

    def test_calculate_name_match_partial(self):
        """Test name matching with partial match."""
        ratio = calculate_name_match("JOHN SMITH", "JOHN")
        assert 0.5 < ratio < 1.0

    def test_calculate_name_match_reversed(self):
        """Test name matching is symmetric."""
        ratio1 = calculate_name_match("JOHN SMITH", "SMITH JOHN")
        ratio2 = calculate_name_match("SMITH JOHN", "JOHN SMITH")
        assert ratio1 == ratio2

    def test_calculate_name_match_none_first(self):
        """Test name matching with None as first argument."""
        ratio = calculate_name_match(None, "JOHN SMITH")
        assert ratio == 0.0

    def test_calculate_name_match_none_second(self):
        """Test name matching with None as second argument."""
        ratio = calculate_name_match("JOHN SMITH", None)
        assert ratio == 0.0

    def test_calculate_name_match_both_none(self):
        """Test name matching with both arguments None."""
        ratio = calculate_name_match(None, None)
        assert ratio == 0.0

    def test_calculate_name_match_empty_first(self):
        """Test name matching with empty first argument."""
        ratio = calculate_name_match("", "JOHN SMITH")
        assert ratio == 0.0

    def test_calculate_name_match_empty_second(self):
        """Test name matching with empty second argument."""
        ratio = calculate_name_match("JOHN SMITH", "")
        assert ratio == 0.0

    def test_calculate_name_match_both_empty(self):
        """Test name matching with both arguments empty."""
        ratio = calculate_name_match("", "")
        assert ratio == 1.0

    def test_calculate_name_match_typo(self):
        """Test name matching with single typo."""
        ratio = calculate_name_match("JOHN SMITH", "JOHN SMIT")
        assert 0.7 < ratio < 1.0

    def test_calculate_name_match_extra_word(self):
        """Test name matching with extra word in name."""
        # "JOHN KUMAR SMITH" becomes "JOHN SMITH" after normalization (KUMAR is removed)
        ratio = calculate_name_match("JOHN KUMAR SMITH", "JOHN SMITH")
        assert ratio == 1.0

    def test_calculate_name_match_returns_float(self):
        """Test that name matching returns a float."""
        ratio = calculate_name_match("JOHN SMITH", "JOHN SMITH")
        assert isinstance(ratio, float)

    def test_calculate_name_match_range(self):
        """Test that name matching returns value between 0.0 and 1.0."""
        ratio = calculate_name_match("JOHN SMITH", "RANDOM NAME")
        assert 0.0 <= ratio <= 1.0
