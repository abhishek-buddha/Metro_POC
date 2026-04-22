"""AI extraction service for bank documents using OpenAI GPT-4 Vision API."""
import json
import base64
import mimetypes
from typing import Dict, Optional

from openai import OpenAI

from src.services.validation import validate_account_number, validate_ifsc
from src.utils.config import config
from src.utils.logger import logger


class AIExtractor:
    """
    AI extraction service for extracting structured data from bank documents.

    Uses OpenAI GPT-4 Vision API to extract data from:
    - Bank passbooks
    - Bank statements
    - Cheques

    Extracted fields:
    - account_number: Bank account number (9-18 digits)
    - account_holder_name: Full name on account
    - ifsc_code: Indian Financial System Code (11 characters)
    - bank_name: Bank name
    - branch_name: Branch name
    - account_type: Savings/Current/unknown
    - micr_code: MICR code (optional)

    Confidence scoring:
    - 0.9: All required fields valid
    - 0.7: Missing optional fields
    - 0.5: Missing required fields or validation failed
    - 0.0: JSON parsing failed or API error
    """

    # Extraction prompt for GPT-4 Vision
    EXTRACTION_PROMPT = (
        "Extract bank account details from this image. The image may be a bank passbook, bank statement, or cheque.\n"
        "\n"
        "Return ONLY a JSON object with these fields (use null for missing fields):\n"
        "{\n"
        '  "account_number": "account number (digits only)",\n'
        '  "account_holder_name": "full name on account",\n'
        '  "ifsc_code": "IFSC code (11 characters)",\n'
        '  "bank_name": "bank name",\n'
        '  "branch_name": "branch name",\n'
        '  "account_type": "Savings or Current or unknown",\n'
        '  "micr_code": "MICR code if visible (optional)"\n'
        "}\n"
        "\n"
        "Do not include any explanation, only return the JSON object."
    )

    def __init__(self):
        """Initialize OpenAI client with API key from config."""
        logger.info("Initializing AIExtractor with OpenAI")
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        logger.info("AIExtractor initialized successfully")

    def extract_bank_data(self, file_path: str) -> Dict:
        """
        Extract bank account details from an image using GPT-4 Vision API.

        Args:
            file_path: Path to bank document image file (JPEG or PNG)

        Returns:
            Dictionary with structure:
            {
                "account_number": str or None,
                "account_holder_name": str or None,
                "ifsc_code": str or None,
                "bank_name": str or None,
                "branch_name": str or None,
                "account_type": str or None (Savings/Current/unknown),
                "micr_code": str or None,
                "confidence": float (0.0-1.0),
                "raw_response": str
            }

            Confidence scoring:
            - 0.9: All required fields valid
            - 0.7: Missing optional fields (bank_name, branch_name, account_type)
            - 0.5: Missing required fields or validation failed
            - 0.0: JSON parsing failed or API error
        """
        try:
            logger.info(
                "Extracting bank data",
                extra={"file_path": file_path}
            )

            # Read image file and convert to base64
            try:
                with open(file_path, 'rb') as f:
                    image_data = f.read()
                image_base64 = base64.standard_b64encode(image_data).decode('utf-8')
                logger.info(f"Image read and encoded to base64: {file_path}")
            except Exception as e:
                logger.error(f"Failed to read image file: {str(e)}")
                return self._error_response()

            # Detect media type
            media_type, _ = mimetypes.guess_type(file_path)
            if not media_type:
                # Default to JPEG if type cannot be determined
                media_type = "image/jpeg"
            logger.info(f"Detected media type: {media_type}")

            # Call OpenAI GPT-4 Vision API
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o",  # or "gpt-4-vision-preview"
                    max_tokens=1024,
                    temperature=0,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": self.EXTRACTION_PROMPT
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:{media_type};base64,{image_base64}"
                                    }
                                }
                            ]
                        }
                    ]
                )
                logger.info("OpenAI GPT-4 Vision API response received")
            except Exception as e:
                logger.error(f"OpenAI Vision API call failed: {str(e)}")
                return self._error_response()

            # Parse JSON response
            try:
                raw_response = response.choices[0].message.content
                # Clean up markdown code blocks if present
                if raw_response.startswith("```json"):
                    raw_response = raw_response.replace("```json", "").replace("```", "").strip()
                elif raw_response.startswith("```"):
                    raw_response = raw_response.replace("```", "").strip()

                parsed_response = json.loads(raw_response)
                logger.info("JSON response parsed successfully")
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing failed: {str(e)}")
                return self._error_response()

            # Extract and clean fields
            account_number = self._clean_field(parsed_response.get('account_number'))
            account_holder_name = self._clean_field(parsed_response.get('account_holder_name'))
            ifsc_code = self._clean_field(parsed_response.get('ifsc_code'))
            bank_name = self._clean_field(parsed_response.get('bank_name'))
            branch_name = self._clean_field(parsed_response.get('branch_name'))
            account_type = self._clean_field(parsed_response.get('account_type'))
            micr_code = self._clean_field(parsed_response.get('micr_code'))

            # Validate required fields
            account_number_valid = validate_account_number(account_number)
            ifsc_code_valid = validate_ifsc(ifsc_code)

            # If any required field is missing or validation fails, confidence is 0.5
            if not account_number or not account_holder_name or not ifsc_code:
                confidence = 0.5
            elif not account_number_valid or not ifsc_code_valid:
                confidence = 0.5
            # If all required fields present and valid
            elif account_number_valid and ifsc_code_valid and account_holder_name:
                # Check if all optional fields are present
                if bank_name and branch_name and account_type:
                    confidence = 0.9
                else:
                    # Missing optional fields
                    confidence = 0.7
            else:
                confidence = 0.5

            result = {
                "account_number": account_number,
                "account_holder_name": account_holder_name,
                "ifsc_code": ifsc_code,
                "bank_name": bank_name,
                "branch_name": branch_name,
                "account_type": account_type,
                "micr_code": micr_code,
                "confidence": confidence,
                "raw_response": raw_response
            }

            logger.info(
                "Bank data extracted",
                extra={
                    "account_number": account_number,
                    "confidence": confidence,
                    "file_path": file_path
                }
            )

            return result

        except Exception as e:
            logger.error(
                f"Bank extraction failed: {str(e)}",
                extra={"file_path": file_path}
            )
            return self._error_response()

    def extract_aadhaar_data(self, file_path: str) -> Dict:
        """
        Extract Aadhaar card details from an image using GPT-4 Vision API.

        Args:
            file_path: Path to Aadhaar card image file (JPEG or PNG)

        Returns:
            Dictionary with structure:
            {
                "aadhaar_number": str or None,
                "name": str or None,
                "dob": str or None (DD/MM/YYYY format),
                "gender": str or None,
                "address": str or None,
                "confidence": float (0.0-1.0),
                "raw_response": str
            }
        """
        try:
            logger.info(
                "Extracting Aadhaar data with AI",
                extra={"file_path": file_path}
            )

            # Read image file and convert to base64
            try:
                with open(file_path, 'rb') as f:
                    image_data = f.read()
                image_base64 = base64.standard_b64encode(image_data).decode('utf-8')
            except Exception as e:
                logger.error(f"Failed to read image file: {str(e)}")
                return self._aadhaar_error_response()

            # Detect media type
            media_type, _ = mimetypes.guess_type(file_path)
            if not media_type:
                media_type = "image/jpeg"

            # Aadhaar extraction prompt
            prompt = (
                "Extract Aadhaar card details from this image.\n"
                "\n"
                "Return ONLY a JSON object with these fields (use null for missing fields):\n"
                "{\n"
                '  "aadhaar_number": "12-digit Aadhaar number (digits only, no spaces)",\n'
                '  "name": "full name as shown on card",\n'
                '  "dob": "date of birth in DD/MM/YYYY format",\n'
                '  "gender": "Male or Female",\n'
                '  "address": "full address as shown on card"\n'
                "}\n"
                "\n"
                "Do not include any explanation, only return the JSON object."
            )

            # Call OpenAI GPT-4 Vision API
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o",
                    max_tokens=1024,
                    temperature=0,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": prompt
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:{media_type};base64,{image_base64}"
                                    }
                                }
                            ]
                        }
                    ]
                )
                logger.info("OpenAI GPT-4 Vision API response received for Aadhaar")
            except Exception as e:
                logger.error(f"OpenAI Vision API call failed: {str(e)}")
                return self._aadhaar_error_response()

            # Parse JSON response
            try:
                raw_response = response.choices[0].message.content
                # Clean up markdown code blocks if present
                if raw_response.startswith("```json"):
                    raw_response = raw_response.replace("```json", "").replace("```", "").strip()
                elif raw_response.startswith("```"):
                    raw_response = raw_response.replace("```", "").strip()

                parsed_response = json.loads(raw_response)
                logger.info("JSON response parsed successfully for Aadhaar")
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing failed: {str(e)}")
                return self._aadhaar_error_response()

            # Extract and clean fields
            aadhaar_number = self._clean_field(parsed_response.get('aadhaar_number'))
            name = self._clean_field(parsed_response.get('name'))
            dob = self._clean_field(parsed_response.get('dob'))
            gender = self._clean_field(parsed_response.get('gender'))
            address = self._clean_field(parsed_response.get('address'))

            # Validate Aadhaar number (12 digits)
            aadhaar_valid = aadhaar_number and len(aadhaar_number.replace(" ", "")) == 12

            # Calculate confidence
            if aadhaar_number and name and dob:
                if aadhaar_valid:
                    confidence = 0.9  # All required fields present and valid
                else:
                    confidence = 0.5  # Aadhaar number invalid
            else:
                confidence = 0.5  # Missing required fields

            result = {
                "aadhaar_number": aadhaar_number,
                "name": name,
                "dob": dob,
                "gender": gender,
                "address": address,
                "confidence": confidence,
                "raw_response": raw_response
            }

            logger.info(
                "Aadhaar data extracted with AI",
                extra={
                    "aadhaar_number": aadhaar_number[:4] + "****" + aadhaar_number[-4:] if aadhaar_number else None,
                    "confidence": confidence,
                    "file_path": file_path
                }
            )

            return result

        except Exception as e:
            logger.error(
                f"Aadhaar AI extraction failed: {str(e)}",
                extra={"file_path": file_path}
            )
            return self._aadhaar_error_response()

    def _aadhaar_error_response(self) -> Dict:
        """Return error response for Aadhaar extraction."""
        return {
            "aadhaar_number": None,
            "name": None,
            "dob": None,
            "gender": None,
            "address": None,
            "confidence": 0.0,
            "raw_response": ""
        }

    def extract_pan_data(self, file_path: str) -> Dict:
        """
        Extract PAN card details from an image using GPT-4 Vision API.

        Args:
            file_path: Path to PAN card image file (JPEG or PNG)

        Returns:
            Dictionary with structure:
            {
                "pan_number": str or None,
                "name": str or None,
                "father_name": str or None,
                "dob": str or None (DD/MM/YYYY format),
                "confidence": float (0.0-1.0),
                "raw_response": str
            }
        """
        try:
            logger.info(
                "Extracting PAN data with AI",
                extra={"file_path": file_path}
            )

            # Read image file and convert to base64
            try:
                with open(file_path, 'rb') as f:
                    image_data = f.read()
                image_base64 = base64.standard_b64encode(image_data).decode('utf-8')
            except Exception as e:
                logger.error(f"Failed to read image file: {str(e)}")
                return self._pan_error_response()

            # Detect media type
            media_type, _ = mimetypes.guess_type(file_path)
            if not media_type:
                media_type = "image/jpeg"

            # PAN extraction prompt
            prompt = (
                "Extract PAN card details from this image.\n"
                "\n"
                "Return ONLY a JSON object with these fields (use null for missing fields):\n"
                "{\n"
                '  "pan_number": "10-character PAN number (format: ABCDE1234F)",\n'
                '  "name": "full name as shown on card",\n'
                '  "father_name": "father\'s name as shown on card",\n'
                '  "dob": "date of birth in DD/MM/YYYY format"\n'
                "}\n"
                "\n"
                "Do not include any explanation, only return the JSON object."
            )

            # Call OpenAI GPT-4 Vision API
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o",
                    max_tokens=1024,
                    temperature=0,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": prompt
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:{media_type};base64,{image_base64}"
                                    }
                                }
                            ]
                        }
                    ]
                )
                logger.info("OpenAI GPT-4 Vision API response received for PAN")
            except Exception as e:
                logger.error(f"OpenAI Vision API call failed: {str(e)}")
                return self._pan_error_response()

            # Parse JSON response
            try:
                raw_response = response.choices[0].message.content
                # Clean up markdown code blocks if present
                if raw_response.startswith("```json"):
                    raw_response = raw_response.replace("```json", "").replace("```", "").strip()
                elif raw_response.startswith("```"):
                    raw_response = raw_response.replace("```", "").strip()

                parsed_response = json.loads(raw_response)
                logger.info("JSON response parsed successfully for PAN")
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing failed: {str(e)}")
                return self._pan_error_response()

            # Extract and clean fields
            pan_number = self._clean_field(parsed_response.get('pan_number'))
            name = self._clean_field(parsed_response.get('name'))
            father_name = self._clean_field(parsed_response.get('father_name'))
            dob = self._clean_field(parsed_response.get('dob'))

            # Validate PAN number format (10 characters, alphanumeric)
            from src.services.validation import validate_pan
            pan_valid = validate_pan(pan_number) if pan_number else False

            # Calculate confidence
            if pan_number and name and dob:
                if pan_valid:
                    confidence = 0.9  # All required fields present and valid
                else:
                    confidence = 0.5  # PAN number invalid format
            else:
                confidence = 0.5  # Missing required fields

            result = {
                "pan_number": pan_number,
                "name": name,
                "father_name": father_name,
                "dob": dob,
                "confidence": confidence,
                "raw_response": raw_response
            }

            logger.info(
                "PAN data extracted with AI",
                extra={
                    "pan_number": pan_number[:4] + "****" + pan_number[-1:] if pan_number and len(pan_number) >= 5 else None,
                    "confidence": confidence,
                    "file_path": file_path
                }
            )

            return result

        except Exception as e:
            logger.error(
                f"PAN AI extraction failed: {str(e)}",
                extra={"file_path": file_path}
            )
            return self._pan_error_response()

    def _pan_error_response(self) -> Dict:
        """Return error response for PAN extraction."""
        return {
            "pan_number": None,
            "name": None,
            "father_name": None,
            "dob": None,
            "confidence": 0.0,
            "raw_response": ""
        }

    def _clean_field(self, value: Optional[str]) -> Optional[str]:
        """
        Clean a field value by stripping whitespace.

        Args:
            value: Field value to clean

        Returns:
            Cleaned value or None if value is None or empty
        """
        if value is None:
            return None
        if isinstance(value, str):
            cleaned = value.strip()
            return cleaned if cleaned else None
        return None

    def _error_response(self) -> Dict:
        """
        Return a standard error response with confidence 0.0.

        Returns:
            Dictionary with all fields as None and confidence 0.0
        """
        return {
            "account_number": None,
            "account_holder_name": None,
            "ifsc_code": None,
            "bank_name": None,
            "branch_name": None,
            "account_type": None,
            "micr_code": None,
            "confidence": 0.0,
            "raw_response": ""
        }
