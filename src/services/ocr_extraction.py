"""OCR extraction service for PAN and Aadhaar cards."""
import re
from typing import Optional, Dict
from src.services.validation import validate_pan, validate_aadhaar
from src.utils.logger import logger


class OCRExtractor:
    """
    OCR extraction service for extracting structured data from ID documents.

    Supports:
    - PAN (Permanent Account Number) cards
    - Aadhaar cards

    Uses EasyOCR to extract text from images and regex patterns to parse fields.
    """

    def __init__(self):
        """Initialize EasyOCR reader with English and Hindi support."""
        logger.info("Initializing OCRExtractor (AI-fallback mode — EasyOCR bypassed)")

    def extract_pan_data(self, file_path: str) -> Dict:
        """
        Extract PAN card data from image.

        Required fields: PAN number, name, date of birth
        Optional fields: Father's name

        Args:
            file_path: Path to PAN card image file

        Returns:
            Dictionary with structure:
            {
                "pan_number": str or None,
                "name": str or None,
                "father_name": str or None,
                "dob": str or None (DD/MM/YYYY or DD-MM-YYYY),
                "confidence": float (0.0-1.0),
                "raw_text": str
            }

            Confidence scoring:
            - 0.9: All fields extracted
            - 0.7: Missing optional fields (father_name)
            - 0.5: Missing required fields (pan_number, name, or dob)
            - 0.0: OCR failure
        """
        try:
            logger.info(f"Extracting PAN data from {file_path}")

            # Extract text using EasyOCR
            ocr_results = self.reader.readtext(file_path)
            extracted_text = " ".join([text[1] for text in ocr_results])

            logger.info(
                "PAN OCR text extracted",
                extra={"file_path": file_path, "text_length": len(extracted_text)}
            )

            # Extract PAN number
            pan_number = self._extract_pan_number(extracted_text)

            # Extract name
            name = self._extract_name(extracted_text)

            # Extract father's name
            father_name = self._extract_father_name(extracted_text)

            # Extract date of birth
            dob = self._extract_dob(extracted_text)

            # Calculate confidence
            required_fields = [pan_number, name, dob]
            optional_fields = [father_name]

            if all(required_fields):
                confidence = 0.9 if all(optional_fields) else 0.7
            else:
                confidence = 0.5

            result = {
                "pan_number": pan_number,
                "name": name,
                "father_name": father_name,
                "dob": dob,
                "confidence": confidence,
                "raw_text": extracted_text
            }

            logger.info(
                "PAN extracted",
                extra={
                    "pan_number": pan_number,
                    "confidence": confidence,
                    "file_path": file_path
                }
            )

            return result

        except Exception as e:
            logger.error(
                f"PAN extraction failed: {str(e)}",
                extra={"file_path": file_path}
            )
            return {
                "pan_number": None,
                "name": None,
                "father_name": None,
                "dob": None,
                "confidence": 0.0,
                "raw_text": ""
            }

    def extract_aadhaar_data(self, file_path: str) -> Dict:
        """
        Extract Aadhaar card data from image.

        Required fields: Aadhaar number, name, date of birth
        Optional fields: Gender, address, pincode

        Args:
            file_path: Path to Aadhaar card image file

        Returns:
            Dictionary with structure:
            {
                "aadhaar_number": str or None (12 digits without spaces),
                "name": str or None,
                "dob": str or None (DD/MM/YYYY or DD-MM-YYYY),
                "gender": str or None (Male/Female/म/फ),
                "address": str or None,
                "pincode": str or None (6 digits),
                "confidence": float (0.0-1.0),
                "raw_text": str
            }

            Confidence scoring:
            - 0.9: All fields extracted
            - 0.7: Missing optional fields (gender/address/pincode)
            - 0.5: Missing required fields (aadhaar_number, name, or dob)
            - 0.0: OCR failure
        """
        try:
            logger.info(f"Extracting Aadhaar data from {file_path}")

            # Extract text using EasyOCR
            ocr_results = self.reader.readtext(file_path)
            extracted_text = " ".join([text[1] for text in ocr_results])

            logger.info(
                "Aadhaar OCR text extracted",
                extra={"file_path": file_path, "text_length": len(extracted_text)}
            )

            # Extract Aadhaar number
            aadhaar_number = self._extract_aadhaar_number(extracted_text)

            # Extract name
            name = self._extract_name(extracted_text)

            # Extract date of birth
            dob = self._extract_dob(extracted_text)

            # Extract gender
            gender = self._extract_gender(extracted_text)

            # Extract address
            address = self._extract_address(extracted_text)

            # Extract pincode
            pincode = self._extract_pincode(extracted_text)

            # Calculate confidence
            required_fields = [aadhaar_number, name, dob]
            optional_fields = [gender, address, pincode]

            if all(required_fields):
                confidence = 0.9 if all(optional_fields) else 0.7
            else:
                confidence = 0.5

            result = {
                "aadhaar_number": aadhaar_number,
                "name": name,
                "dob": dob,
                "gender": gender,
                "address": address,
                "pincode": pincode,
                "confidence": confidence,
                "raw_text": extracted_text
            }

            logger.info(
                "Aadhaar extracted",
                extra={
                    "aadhaar_number": aadhaar_number,
                    "confidence": confidence,
                    "file_path": file_path
                }
            )

            return result

        except Exception as e:
            logger.error(
                f"Aadhaar extraction failed: {str(e)}",
                extra={"file_path": file_path}
            )
            return {
                "aadhaar_number": None,
                "name": None,
                "dob": None,
                "gender": None,
                "address": None,
                "pincode": None,
                "confidence": 0.0,
                "raw_text": ""
            }

    def _extract_pan_number(self, text: str) -> Optional[str]:
        """
        Extract PAN number from text using regex.

        Format: 5 uppercase letters, 4 digits, 1 uppercase letter
        Example: ABCDE1234F

        Args:
            text: Extracted OCR text

        Returns:
            PAN number if found and valid, None otherwise
        """
        # Look for PAN pattern
        pattern = r'[A-Z]{5}[0-9]{4}[A-Z]'
        matches = re.findall(pattern, text)

        if matches:
            pan = matches[0]
            if validate_pan(pan):
                return pan

        return None

    def _extract_aadhaar_number(self, text: str) -> Optional[str]:
        """
        Extract Aadhaar number from text using regex.

        Format: 12 digits (may have spaces)
        Examples: 123456789012 or 1234 5678 9012

        Args:
            text: Extracted OCR text

        Returns:
            Aadhaar number without spaces if found and valid, None otherwise
        """
        # Look for Aadhaar pattern (with or without spaces)
        pattern = r'\d{4}\s?\d{4}\s?\d{4}'
        matches = re.findall(pattern, text)

        if matches:
            # Take the first match and remove spaces
            aadhaar = re.sub(r'\s', '', matches[0])
            if validate_aadhaar(aadhaar):
                return aadhaar

        return None

    def _extract_name(self, text: str) -> Optional[str]:
        """
        Extract name from text after "Name" or "नाम" label.

        Args:
            text: Extracted OCR text

        Returns:
            Name if found, None otherwise
        """
        # Case-insensitive patterns for name extraction
        patterns = [
            r'(?:Name|नाम)\s*:?\s*([A-Za-z\s]+?)(?:\s+(?:Father|पिता|Date|जन्म|DOB|Gender|लिंग|Address|पता)|$)',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                name = matches[0].strip()
                # Clean up the name
                name = re.sub(r'\s+', ' ', name)
                if name and len(name) > 1:
                    return name.upper()

        return None

    def _extract_father_name(self, text: str) -> Optional[str]:
        """
        Extract father's name from text after "Father's Name" or "पिता का नाम" label.

        Args:
            text: Extracted OCR text

        Returns:
            Father's name if found, None otherwise
        """
        patterns = [
            r"(?:Father'?s?\s+Name|पिता\s+का\s+नाम|PITA\s+KA\s+NAM)\s*:?\s*([A-Za-z\s]+?)(?:\s+(?:Date|DOB|जन्म|Gender|लिंग|Address|पता|Pincode|पिन)|$)",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                name = matches[0].strip()
                # Clean up the name
                name = re.sub(r'\s+', ' ', name)
                if name and len(name) > 1:
                    return name.upper()

        return None

    def _extract_dob(self, text: str) -> Optional[str]:
        """
        Extract date of birth from text.

        Formats: DD/MM/YYYY or DD-MM-YYYY

        Args:
            text: Extracted OCR text

        Returns:
            Date of birth if found, None otherwise
        """
        # Pattern for DD/MM/YYYY or DD-MM-YYYY
        pattern = r'\d{2}[-/]\d{2}[-/]\d{4}'
        matches = re.findall(pattern, text)

        if matches:
            return matches[0]

        return None

    def _extract_gender(self, text: str) -> Optional[str]:
        """
        Extract gender from text.

        Formats: Male, Female, म (Hindi), फ (Hindi)

        Args:
            text: Extracted OCR text

        Returns:
            Gender if found, None otherwise
        """
        patterns = [
            r'(?:Gender|gender|GENDER|लिंग)\s*:?\s*(Male|Female|M|F|म|फ)',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return matches[0]

        return None

    def _extract_address(self, text: str) -> Optional[str]:
        """
        Extract address from text after "Address" or "पता" label.

        Args:
            text: Extracted OCR text

        Returns:
            Address if found, None otherwise
        """
        patterns = [
            r'(?:Address|पता)\s*:?\s*([A-Za-z0-9\s,\.\-]+?)(?:\s+(?:Pincode|पिन\s+कोड|पिन|Pin)|$)',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                address = matches[0].strip()
                # Clean up address
                address = re.sub(r'\s+', ' ', address)
                if address:
                    return address

        return None

    def _extract_pincode(self, text: str) -> Optional[str]:
        """
        Extract 6-digit pincode from text.

        Args:
            text: Extracted OCR text

        Returns:
            6-digit pincode if found, None otherwise
        """
        # Pattern for 6-digit pincode with word boundaries
        pattern = r'\b\d{6}\b'
        matches = re.findall(pattern, text)

        if matches:
            return matches[0]

        return None
