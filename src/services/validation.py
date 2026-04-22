"""Format validation and name matching services."""
import re
from difflib import SequenceMatcher
from typing import Optional


def validate_pan(pan: Optional[str]) -> bool:
    """
    Validate PAN (Permanent Account Number) format.

    Valid format: 5 uppercase letters, 4 digits, 1 uppercase letter
    Example: ABCDE1234F

    Args:
        pan: PAN string to validate

    Returns:
        True if valid PAN format, False otherwise
    """
    if pan is None or not isinstance(pan, str):
        return False

    pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]$'
    return bool(re.match(pattern, pan))


def validate_aadhaar(aadhaar: Optional[str]) -> bool:
    """
    Validate Aadhaar number format.

    Valid format: 12 digits (spaces are stripped before validation)
    Example: 123456789012 or 1234 5678 9012

    Args:
        aadhaar: Aadhaar number string to validate

    Returns:
        True if valid Aadhaar format, False otherwise
    """
    if aadhaar is None or not isinstance(aadhaar, str):
        return False

    # Remove all whitespace
    clean = re.sub(r'\s', '', aadhaar)

    # Check if it's exactly 12 digits
    if len(clean) != 12 or not clean.isdigit():
        return False

    return True


def validate_ifsc(ifsc: Optional[str]) -> bool:
    """
    Validate IFSC (Indian Financial System Code) format.

    Valid format: 4 uppercase letters, 1 zero, 6 alphanumeric characters
    Example: SBIN0001234

    Args:
        ifsc: IFSC code string to validate

    Returns:
        True if valid IFSC format, False otherwise
    """
    if ifsc is None or not isinstance(ifsc, str):
        return False

    pattern = r'^[A-Z]{4}0[A-Z0-9]{6}$'
    return bool(re.match(pattern, ifsc))


def validate_account_number(account: Optional[str]) -> bool:
    """
    Validate bank account number format.

    Valid format: 9-18 digits

    Args:
        account: Account number string to validate

    Returns:
        True if valid account number format, False otherwise
    """
    if account is None or not isinstance(account, str):
        return False

    # Check if it only contains digits
    if not account.isdigit():
        return False

    # Check if length is between 9 and 18
    length = len(account)
    return 9 <= length <= 18


def normalize_name(name: Optional[str]) -> str:
    """
    Normalize a person's name by:
    - Converting to uppercase
    - Removing titles (MR, MRS, DR, SHRI, SMT)
    - Removing suffixes (KUMAR, KUMARI)
    - Removing special characters (keeping only alphanumeric and spaces)
    - Removing extra spaces

    Args:
        name: Name string to normalize

    Returns:
        Normalized name string, or empty string if input is None
    """
    if name is None or not isinstance(name, str):
        return ""

    # Convert to uppercase
    name = name.upper()

    # Remove periods and hyphens, replace with space
    name = re.sub(r'[.\-]', ' ', name)

    # Remove all special characters except spaces
    name = re.sub(r"[^A-Z0-9\s]", '', name)

    # Remove suffixes first (at the end) - check KUMARI before KUMAR to avoid partial matches
    suffixes = [r'\bKUMARI\b', r'\bKUMAR\b']
    for suffix in suffixes:
        name = re.sub(suffix, '', name)

    # Remove titles at the beginning
    titles = [r'\bMR\b', r'\bMRS\b', r'\bDR\b', r'\bSHRI\b', r'\bSMT\b']
    for title in titles:
        name = re.sub(title, '', name)

    # Remove extra spaces
    name = re.sub(r'\s+', ' ', name)

    # Strip leading and trailing spaces
    name = name.strip()

    return name


def calculate_name_match(name1: Optional[str], name2: Optional[str]) -> float:
    """
    Calculate similarity ratio between two names using difflib.SequenceMatcher.

    Names are normalized before comparison (titles and suffixes removed, case normalized).

    Args:
        name1: First name to compare
        name2: Second name to compare

    Returns:
        Similarity ratio between 0.0 (completely different) and 1.0 (identical)
    """
    # Handle None as input - both None returns 0.0
    if name1 is None and name2 is None:
        return 0.0

    # Handle one None
    if name1 is None or name2 is None:
        return 0.0

    # Handle empty strings - both empty returns 1.0
    if name1 == "" and name2 == "":
        return 1.0

    # Handle one empty string
    if name1 == "" or name2 == "":
        return 0.0

    # Normalize both names
    norm_name1 = normalize_name(name1)
    norm_name2 = normalize_name(name2)

    # Handle case where both normalize to empty strings (all inputs were whitespace/titles)
    if not norm_name1 and not norm_name2:
        return 1.0

    # Handle case where one normalizes to empty string
    if not norm_name1 or not norm_name2:
        return 0.0

    # Calculate and return the ratio
    matcher = SequenceMatcher(None, norm_name1, norm_name2)
    return matcher.ratio()
