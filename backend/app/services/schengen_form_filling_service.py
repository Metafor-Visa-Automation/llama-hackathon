"""
Schengen Visa Application Form Filling Service
Automatically fills Schengen visa form fields using AI and user/application data
Uses Groq's Llama 4 Scout model and generates Word documents
"""

import os
import logging
from typing import Dict, Any, Optional
from groq import Groq
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class SchengenFormFillingService:
    """Service for automatically filling Schengen visa application forms"""
    
    # Schengen form field definitions
    FORM_FIELDS = {
        "field1": "Surname (Family name)",
        "field2": "Surname at birth",
        "field3": "First name(s)",
        "field4": "Date of birth",
        "field5": "Place of birth",
        "field6": "Country of birth",
        "field7": "Current nationality",
        "field8": "Nationality at birth",
        "field9": "Other nationalities",
        "field10": "Parental authority/legal guardian",
        "field11": "National identity number",
        "field12": "Other travel document type",
        "field13": "Travel document number",
        "field14": "Travel document issue date",
        "field15": "Travel document valid until",
        "field16": "Travel document issued by",
        "field17": "EU family member surname",
        "field18": "EU family member first name",
        "field19": "EU family member DOB",
        "field20": "EU family member nationality",
        "field21": "EU family member document number",
        "field22": "Home address and email",
        "field23": "Telephone number",
        "field24": "Residence permit number",
        "field25": "Residence permit number (duplicate)",
        "field26": "Residence permit valid until",
        "field27": "Current occupation",
        "field28": "Employer details",
        "field29": "Other purpose specification",
        "field30": "Additional information on purpose",
        "field31": "Member State(s) of destination",
        "field32": "Member State of first entry",
        "field33": "Intended date of arrival",
        "field34": "Intended date of departure",
        "field35": "Previous fingerprint date",
        "field36": "Previous visa sticker number",
        "field37": "Entry permit issued by",
        "field38": "Entry permit valid from",
        "field39": "Entry permit valid until",
        "field40": "Inviting person name/hotel",
        "field41": "Inviting person address",
        "field42": "Inviting person telephone",
        "field43": "Inviting company/organization",
        "field44": "Contact person details",
        "field45": "Company telephone",
        "field46": "Other means of support",
        "field47": "Sponsor specification",
        "field48": "Other sponsor specification",
        "field49": "Sponsor means of support",
        # Official use only fields
        "field50": "Date of application",
        "field51": "Application number",
        "field52": "Border name",
        "field53": "Other location",
        "field54": "File handler",
        "field55": "Other documents",
        "field56": "Visa valid from",
        "field57": "Visa valid until",
        "field58": "Number of days",
        "field59": "Place and date",
        "field60": "Signature placeholder",
        "field61": "Guardian signature placeholder"
    }
    
    def __init__(self):
        """Initialize Groq client"""
        try:
            api_key = "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"
            if not api_key:
                logger.warning("GROQ_API_KEY not found in environment variables")
                self.client = None
            else:
                self.client = Groq(api_key=api_key)
                logger.info("Schengen Form Filling service initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Groq client: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if form filling service is available"""
        return self.client is not None
    
    def _build_form_filling_prompt(
        self,
        user_data: Dict[str, Any],
        application_data: Dict[str, Any]
    ) -> str:
        """
        Build comprehensive prompt for form filling
        
        Args:
            user_data: User profile data
            application_data: Visa application data
            
        Returns:
            Formatted prompt string
        """
        prompt = """You are an expert at filling Schengen visa application forms accurately.

Your task is to fill a Harmonised Schengen Visa Application Form using the provided user and application data.

IMPORTANT INSTRUCTIONS:
1. Fill ONLY the fields for which you have clear, accurate information
2. Leave fields empty (null or empty string) if data is not available or uncertain
3. Use EXACT date format: DD-MM-YYYY (e.g., "15-03-1995")
4. For checkboxes, return true/false values
5. Be precise and match official document requirements
6. Do not make assumptions or fabricate data
7. For address fields, format properly with commas and line breaks
8. For phone numbers, include country code (e.g., "+90 555 123 4567")

USER DATA:
"""
        # Add user data
        if user_data.get("surname"):
            prompt += f"Surname: {user_data['surname']}\n"
        if user_data.get("name"):
            prompt += f"First Name(s): {user_data['name']}\n"
        if user_data.get("date_of_birth"):
            prompt += f"Date of Birth: {user_data['date_of_birth']}\n"
        if user_data.get("place_of_birth"):
            prompt += f"Place of Birth: {user_data['place_of_birth']}\n"
        if user_data.get("nationality"):
            prompt += f"Nationality: {user_data['nationality']}\n"
        if user_data.get("passport_number"):
            prompt += f"Passport Number: {user_data['passport_number']}\n"
        if user_data.get("passport_issue_date"):
            prompt += f"Passport Issue Date: {user_data['passport_issue_date']}\n"
        if user_data.get("passport_expiry_date"):
            prompt += f"Passport Expiry Date: {user_data['passport_expiry_date']}\n"
        if user_data.get("tc_kimlik_no"):
            prompt += f"National ID Number: {user_data['tc_kimlik_no']}\n"
        if user_data.get("email"):
            prompt += f"Email: {user_data['email']}\n"
        if user_data.get("phone"):
            prompt += f"Phone: {user_data['phone']}\n"
        if user_data.get("profile_type"):
            prompt += f"Profile Type: {user_data['profile_type']}\n"
        
        prompt += "\nAPPLICATION DATA:\n"
        
        # Add application data
        if application_data.get("destination_country"):
            prompt += f"Destination Country: {application_data['destination_country']}\n"
        if application_data.get("purpose"):
            prompt += f"Purpose of Travel: {application_data['purpose']}\n"
        if application_data.get("travel_dates"):
            prompt += f"Travel Dates: {application_data['travel_dates']}\n"
        if application_data.get("duration"):
            prompt += f"Duration: {application_data['duration']}\n"
        if application_data.get("entry_type"):
            prompt += f"Entry Type: {application_data['entry_type']}\n"
        
        prompt += """
SCHENGEN FORM FIELD MAPPINGS:
- field1: Surname (Family name) from user surname
- field2: Surname at birth (if different, otherwise same as field1)
- field3: First name(s) from user name
- field4: Date of birth in DD-MM-YYYY format
- field5: Place of birth
- field6: Country of birth
- field7: Current nationality
- field8: Nationality at birth (if different)
- field9: Other nationalities (if applicable)
- field11: National identity number (TC Kimlik No for Turkish citizens)
- field13: Passport number
- field14: Passport issue date (DD-MM-YYYY)
- field15: Passport expiry date (DD-MM-YYYY)
- field16: Country that issued passport
- field22: Full home address with email
- field23: Telephone number with country code
- field27: Current occupation
- field30: Additional information about purpose of stay
- field31: Member State(s) of destination
- field32: Member State of first entry
- field33: Intended arrival date (DD-MM-YYYY)
- field34: Intended departure date (DD-MM-YYYY)

CHECKBOXES (return as boolean):
- sex_male: true if male, false if female
- sex_female: true if female, false if male
- civil_status_single, civil_status_married, etc.
- passport_type_ordinary: usually true for regular passports
- purpose_tourism, purpose_business, purpose_study, etc.
- entry_single, entry_two, entry_multiple
- cost_by_applicant, cost_by_sponsor
- means_cash, means_credit_card, means_travellers_cheques, etc.

Return a JSON object with ALL applicable fields. Include ONLY fields you can fill with confidence.
Format: {
  "field1": "YILMAZ",
  "field3": "AHMET",
  "field4": "15-03-1995",
  "sex_male": true,
  "sex_female": false,
  ...
}

Return ONLY the JSON object, no explanations.
"""
        return prompt
    
    def fill_schengen_form(
        self,
        user_data: Dict[str, Any],
        application_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Fill Schengen visa application form using AI
        
        Args:
            user_data: User profile data
            application_data: Visa application data
            
        Returns:
            Dict containing filled form fields and metadata
        """
        if not self.is_available():
            raise ValueError("Form filling service is not available. Please set GROQ_API_KEY.")
        
        try:
            logger.info(f"Filling Schengen form for user {user_data.get('email')}")
            
            # Build prompt
            prompt = self._build_form_filling_prompt(user_data, application_data)
            
            # Call Groq API
            logger.info("Sending request to Groq Llama 4 Scout for form filling...")
            
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert assistant for filling official visa application forms. You provide accurate, structured data in JSON format based on user information. You never fabricate data and only fill fields where information is clearly available."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                response_format={"type": "json_object"},
                temperature=0.1,  # Very low for accuracy
                max_tokens=4000
            )
            
            # Parse response
            response_text = chat_completion.choices[0].message.content
            filled_fields = json.loads(response_text)
            
            # Count filled fields
            field_count = len([v for v in filled_fields.values() if v not in [None, "", False]])
            
            logger.info(f"Successfully filled {field_count} form fields")
            
            return {
                "success": True,
                "filled_fields": filled_fields,
                "metadata": {
                    "form_type": "schengen_visa_application",
                    "fields_filled": field_count,
                    "total_fields": len(self.FORM_FIELDS),
                    "model": "meta-llama/llama-4-scout-17b-16e-instruct",
                    "filled_at": datetime.utcnow().isoformat(),
                    "user_email": user_data.get("email"),
                    "destination": application_data.get("destination_country")
                }
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return {
                "success": False,
                "error": f"Invalid JSON response from AI: {str(e)}",
                "filled_fields": {}
            }
        except Exception as e:
            logger.error(f"Error filling form: {e}")
            return {
                "success": False,
                "error": f"Failed to fill form: {str(e)}",
                "filled_fields": {}
            }
    
    def get_form_field_descriptions(self) -> Dict[str, str]:
        """Get descriptions of all form fields"""
        return self.FORM_FIELDS.copy()
    
    def validate_filled_form(self, filled_fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate filled form fields
        
        Args:
            filled_fields: Dictionary of filled form fields
            
        Returns:
            Validation results with errors and warnings
        """
        errors = []
        warnings = []
        
        # Required fields for Schengen visa
        required_fields = [
            "field1",   # Surname
            "field3",   # First name
            "field4",   # Date of birth
            "field7",   # Nationality
            "field13",  # Passport number
            "field15",  # Passport expiry
            "field22",  # Address
            "field23",  # Phone
            "field31",  # Destination
            "field33",  # Arrival date
            "field34"   # Departure date
        ]
        
        for field in required_fields:
            if not filled_fields.get(field):
                errors.append(f"Required field {field} ({self.FORM_FIELDS.get(field)}) is missing")
        
        # Date format validation
        date_fields = ["field4", "field14", "field15", "field33", "field34"]
        for field in date_fields:
            if filled_fields.get(field):
                value = filled_fields[field]
                if not self._validate_date_format(value):
                    errors.append(f"Field {field} has invalid date format. Expected DD-MM-YYYY, got: {value}")
        
        # Passport expiry check
        if filled_fields.get("field15"):
            # Passport should be valid for at least 3 months after intended departure
            warnings.append("Please verify passport is valid for at least 3 months after departure date")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "fields_checked": len(required_fields)
        }
    
    def _validate_date_format(self, date_str: str) -> bool:
        """Validate if date string is in DD-MM-YYYY format"""
        try:
            datetime.strptime(date_str, "%d-%m-%Y")
            return True
        except:
            return False
    
    def generate_word_document(
        self,
        filled_fields: Dict[str, Any],
        output_filename: Optional[str] = None
    ) -> str:
        """
        Generate a Word document with filled form data using the template
        
        Args:
            filled_fields: Dictionary of filled form fields
            output_filename: Optional custom filename
            
        Returns:
            Path to the generated Word document
        """
        try:
            from app.services.word_document_service import WordDocumentService
            
            # Initialize Word document service
            word_service = WordDocumentService()
            
            # Convert filled fields to the format expected by WordDocumentService
            # Map our field names (field1, field3, etc.) to FIELD1, FIELD3, etc.
            user_data = {}
            
            # Map all numeric fields
            for key, value in filled_fields.items():
                if key.startswith("field"):
                    # Extract number from field name (e.g., "field1" -> "1")
                    field_num = key.replace("field", "")
                    field_key = f"FIELD{field_num.upper()}"
                    
                    # Only add non-empty string values (skip None, empty strings, and booleans)
                    if value and not isinstance(value, bool):
                        user_data[field_key] = str(value)
            
            logger.info(f"Converted {len(user_data)} fields for Word document")
            
            # Generate the document using the template
            output_path = word_service.edit_document(
                user_data=user_data,
                filename=output_filename
            )
            
            logger.info(f"Word document generated successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating Word document: {e}")
            raise Exception(f"Failed to generate Word document: {str(e)}")
