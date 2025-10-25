"""
Form Filling Service for Schengen Visa Application Forms
Handles automatic form filling using user data and PDF manipulation
"""

import io
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, date
from dataclasses import dataclass
from enum import Enum
import re

try:
    from pypdf import PdfReader, PdfWriter
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.colors import black
    from reportlab.lib.units import mm
except ImportError as e:
    logging.warning(f"PDF libraries not available: {e}")
    PdfReader = PdfWriter = canvas = None

logger = logging.getLogger(__name__)


class FormFieldType(str, Enum):
    TEXT = "text"
    DATE = "date"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    DROPDOWN = "dropdown"


@dataclass
class FormField:
    """Represents a form field in the PDF"""
    field_name: str
    field_type: FormFieldType
    coordinates: Tuple[float, float]  # (x, y) in points
    width: float
    height: float
    page_number: int
    value: Optional[str] = None


@dataclass
class UserFormData:
    """User data structure for form filling"""
    # Personal Information
    surname: str
    first_name: str
    date_of_birth: str  # Format: DD/MM/YYYY
    place_of_birth: str
    country_of_birth: str
    current_nationality: str
    sex: str  # "Male" or "Female"
    marital_status: str
    
    # Passport Information
    passport_type: str
    passport_number: str
    passport_issue_date: str
    passport_expiry_date: str
    passport_issued_by: str
    
    # Address Information
    current_address: str
    city: str
    postal_code: str
    country: str
    phone_number: str
    email: str
    
    # Travel Information
    purpose_of_journey: str
    intended_arrival_date: str
    intended_departure_date: str
    member_state_of_first_entry: str
    number_of_entries_requested: str
    
    # Optional fields with defaults
    surname_at_birth: Optional[str] = None
    family_members_in_eu: Optional[str] = None
    eu_residence_permit: Optional[str] = None
    previous_schengen_visa: Optional[str] = None
    fingerprints_taken: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_email: Optional[str] = None


class FormFillingService:
    """Service for filling Schengen visa application forms"""
    
    def __init__(self):
        self.form_template_path = "schengen-visa-application-form.pdf"
        self.font_size = 9
        self.font_name = "Helvetica"
        
        # Define form field mappings for Schengen visa application
        self.form_fields = self._define_form_fields()
    
    def _define_form_fields(self) -> Dict[str, FormField]:
        """Define the form fields and their positions in the PDF"""
        # Updated coordinates based on actual Schengen visa form analysis
        # These coordinates are in points (1/72 inch) from bottom-left corner
        fields = {
            # Personal Information Section (Fields 1-11) - Based on official form
            # Based on OCRed PDF analysis: Fields are on the same line
            "surname": FormField("surname", FormFieldType.TEXT, (220, 800), 180, 12, 1),  # Field 1: Surname
            "surname_at_birth": FormField("surname_at_birth", FormFieldType.TEXT, (220, 780), 180, 12, 1),  # Field 2: Surname at birth
            "first_name": FormField("first_name", FormFieldType.TEXT, (220, 760), 180, 12, 1),  # Field 3: First names
            "date_of_birth": FormField("date_of_birth", FormFieldType.DATE, (150, 710), 90, 12, 1),
            "place_of_birth": FormField("place_of_birth", FormFieldType.TEXT, (260, 710), 140, 12, 1),
            "country_of_birth": FormField("country_of_birth", FormFieldType.TEXT, (420, 710), 90, 12, 1),
            "current_nationality": FormField("current_nationality", FormFieldType.TEXT, (150, 690), 140, 12, 1),
            "sex_male": FormField("sex_male", FormFieldType.CHECKBOX, (310, 690), 12, 12, 1),
            "sex_female": FormField("sex_female", FormFieldType.CHECKBOX, (360, 690), 12, 12, 1),
            "marital_status": FormField("marital_status", FormFieldType.TEXT, (150, 670), 140, 12, 1),
            
            # Passport Information Section (Fields 12-16)
            "passport_type": FormField("passport_type", FormFieldType.TEXT, (150, 600), 180, 12, 1),
            "passport_number": FormField("passport_number", FormFieldType.TEXT, (150, 580), 180, 12, 1),
            "passport_issue_date": FormField("passport_issue_date", FormFieldType.DATE, (150, 560), 90, 12, 1),
            "passport_expiry_date": FormField("passport_expiry_date", FormFieldType.DATE, (260, 560), 90, 12, 1),
            "passport_issued_by": FormField("passport_issued_by", FormFieldType.TEXT, (370, 560), 140, 12, 1),
            
            # Address Information Section (Fields 19-20)
            "current_address": FormField("current_address", FormFieldType.TEXT, (150, 480), 350, 25, 1),
            "phone_number": FormField("phone_number", FormFieldType.TEXT, (150, 450), 180, 12, 1),
            "email": FormField("email", FormFieldType.TEXT, (150, 430), 180, 12, 1),
            
            # Travel Information Section (Fields 23-28)
            "purpose_of_journey": FormField("purpose_of_journey", FormFieldType.TEXT, (150, 340), 180, 12, 1),
            "intended_arrival_date": FormField("intended_arrival_date", FormFieldType.DATE, (150, 250), 90, 12, 1),
            "intended_departure_date": FormField("intended_departure_date", FormFieldType.DATE, (260, 250), 90, 12, 1),
            "member_state_of_first_entry": FormField("member_state_of_first_entry", FormFieldType.TEXT, (150, 290), 180, 12, 1),
            "number_of_entries_requested": FormField("number_of_entries_requested", FormFieldType.TEXT, (150, 270), 180, 12, 1),
            
            # Additional Information Section
            "family_members_in_eu": FormField("family_members_in_eu", FormFieldType.TEXT, (120, 300), 200, 15, 1),
            "eu_residence_permit": FormField("eu_residence_permit", FormFieldType.TEXT, (120, 270), 200, 15, 1),
            "previous_schengen_visa": FormField("previous_schengen_visa", FormFieldType.TEXT, (120, 240), 200, 15, 1),
            "fingerprints_taken": FormField("fingerprints_taken", FormFieldType.TEXT, (120, 210), 200, 15, 1),
            
            # Emergency Contact Section
            "emergency_contact_name": FormField("emergency_contact_name", FormFieldType.TEXT, (120, 170), 200, 15, 1),
            "emergency_contact_phone": FormField("emergency_contact_phone", FormFieldType.TEXT, (300, 170), 150, 15, 1),
            "emergency_contact_email": FormField("emergency_contact_email", FormFieldType.TEXT, (120, 140), 200, 15, 1),
        }
        
        return fields
    
    def create_debug_form(self, user_data: UserFormData, output_path: str = "debug_filled_form.pdf") -> str:
        """
        Create a debug version of the filled form with visible field boundaries
        
        Args:
            user_data: User data to fill in the form
            output_path: Path to save the debug PDF
            
        Returns:
            Path to the debug PDF
        """
        try:
            if PdfReader is None or PdfWriter is None:
                raise ImportError("PDF processing libraries not available")
            
            # Read the template PDF
            reader = PdfReader(self.form_template_path)
            writer = PdfWriter()
            
            # Create a new PDF with form data
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                writer.add_page(page)
            
            # Create debug overlay with field boundaries
            debug_overlay = self._create_debug_overlay(user_data)
            
            # Merge overlay with original PDF
            filled_pdf = self._merge_pdfs(writer, debug_overlay)
            
            # Save debug PDF
            with open(output_path, "wb") as f:
                f.write(filled_pdf)
            
            logger.info(f"Debug form created: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error creating debug form: {str(e)}")
            raise
    
    def _create_debug_overlay(self, user_data: UserFormData) -> bytes:
        """Create debug overlay with field boundaries and text"""
        try:
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
            
            # Set font
            c.setFont(self.font_name, self.font_size)
            
            # Create a mapping of field names to numbers for display
            field_number_map = {
                "surname": "1",
                "surname_at_birth": "2",
                "first_name": "3",
                "date_of_birth": "4",
                "place_of_birth": "5",
                "country_of_birth": "6",
                "current_nationality": "7",
                "sex_male": "8",
                "sex_female": "9",
                "marital_status": "10",
                "passport_type": "11",
                "passport_number": "12",
                "passport_issue_date": "13",
                "passport_expiry_date": "14",
                "passport_issued_by": "15",
                "current_address": "16",
                "phone_number": "17",
                "email": "18",
                "purpose_of_journey": "19",
                "intended_arrival_date": "20",
                "intended_departure_date": "21",
                "member_state_of_first_entry": "22",
                "number_of_entries_requested": "23",
            }
            
            # Draw field boundaries and fill with data
            for field_name, field in self.form_fields.items():
                x, y = field.coordinates
                width, height = field.width, field.height
                
                # Draw yellow field boundary
                c.setStrokeColor("red")
                c.setFillColor("yellow")
                c.rect(x, y, width, height, fill=1, stroke=1)
                
                # Draw field number in the box
                field_number = field_number_map.get(field_name, "?")
                c.setFillColor("red")
                c.setFont("Helvetica-Bold", 10)
                c.drawString(x + 2, y + height - 2, field_number)
                
                # Get field value
                value = self._get_field_value(field_name, user_data)
                if value:
                    # Draw text
                    c.setFillColor("black")
                    c.setFont(self.font_name, self.font_size)
                    c.drawString(x + 2, y + 2, str(value))
                
                # Draw field name below the box
                c.setFillColor("blue")
                c.setFont(self.font_name, 6)
                c.drawString(x, y - 8, f"{field_number}. {field_name}")
                c.setFont(self.font_name, self.font_size)
            
            c.save()
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error creating debug overlay: {str(e)}")
            raise
    
    def _get_field_value(self, field_name: str, user_data: UserFormData) -> Optional[str]:
        """Get the value for a specific field from user data"""
        field_mapping = {
            "surname": user_data.surname,
            "surname_at_birth": user_data.surname_at_birth,
            "first_name": user_data.first_name,
            "date_of_birth": user_data.date_of_birth,
            "place_of_birth": user_data.place_of_birth,
            "country_of_birth": user_data.country_of_birth,
            "current_nationality": user_data.current_nationality,
            "sex_male": "X" if user_data.sex.lower() == "male" else "",
            "sex_female": "X" if user_data.sex.lower() == "female" else "",
            "marital_status": user_data.marital_status,
            "passport_type": user_data.passport_type,
            "passport_number": user_data.passport_number,
            "passport_issue_date": user_data.passport_issue_date,
            "passport_expiry_date": user_data.passport_expiry_date,
            "passport_issued_by": user_data.passport_issued_by,
            "current_address": user_data.current_address,
            "city": user_data.city,
            "postal_code": user_data.postal_code,
            "country": user_data.country,
            "phone_number": user_data.phone_number,
            "email": user_data.email,
            "purpose_of_journey": user_data.purpose_of_journey,
            "intended_arrival_date": user_data.intended_arrival_date,
            "intended_departure_date": user_data.intended_departure_date,
            "member_state_of_first_entry": user_data.member_state_of_first_entry,
            "number_of_entries_requested": user_data.number_of_entries_requested,
            "family_members_in_eu": user_data.family_members_in_eu,
            "eu_residence_permit": user_data.eu_residence_permit,
            "previous_schengen_visa": user_data.previous_schengen_visa,
            "fingerprints_taken": user_data.fingerprints_taken,
            "emergency_contact_name": user_data.emergency_contact_name,
            "emergency_contact_phone": user_data.emergency_contact_phone,
            "emergency_contact_email": user_data.emergency_contact_email,
        }
        
        return field_mapping.get(field_name)
    
    def fill_form(self, user_data: UserFormData, template_pdf_path: str = None) -> bytes:
        """
        Fill the Schengen visa application form with user data
        
        Args:
            user_data: User data to fill in the form
            template_pdf_path: Path to the template PDF (optional)
            
        Returns:
            Filled PDF as bytes
        """
        try:
            if PdfReader is None or PdfWriter is None:
                raise ImportError("PDF processing libraries not available")
            
            # Use provided template or default
            pdf_path = template_pdf_path or self.form_template_path
            
            # Read the template PDF
            reader = PdfReader(pdf_path)
            writer = PdfWriter()
            
            # Create a new PDF with form data
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                writer.add_page(page)
            
            # Create overlay with form data
            overlay_pdf = self._create_form_overlay(user_data)
            
            # Merge overlay with original PDF
            filled_pdf = self._merge_pdfs(writer, overlay_pdf)
            
            return filled_pdf
            
        except Exception as e:
            logger.error(f"Error filling form: {str(e)}")
            raise
    
    def _create_form_overlay(self, user_data: UserFormData) -> bytes:
        """Create PDF overlay with form data"""
        try:
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
            
            # Set font
            c.setFont(self.font_name, self.font_size)
            
            # Fill form fields
            self._fill_personal_info(c, user_data)
            self._fill_passport_info(c, user_data)
            self._fill_address_info(c, user_data)
            self._fill_travel_info(c, user_data)
            self._fill_additional_info(c, user_data)
            
            c.save()
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error creating form overlay: {str(e)}")
            raise
    
    def _fill_personal_info(self, canvas_obj, user_data: UserFormData):
        """Fill personal information section"""
        try:
            # Surname
            if "surname" in self.form_fields:
                field = self.form_fields["surname"]
                canvas_obj.drawString(field.coordinates[0], field.coordinates[1], user_data.surname)
            
            # Surname at birth
            if user_data.surname_at_birth and "surname_at_birth" in self.form_fields:
                field = self.form_fields["surname_at_birth"]
                canvas_obj.drawString(field.coordinates[0], field.coordinates[1], user_data.surname_at_birth)
            
            # First name
            if "first_name" in self.form_fields:
                field = self.form_fields["first_name"]
                canvas_obj.drawString(field.coordinates[0], field.coordinates[1], user_data.first_name)
            
            # Date of birth
            if "date_of_birth" in self.form_fields:
                field = self.form_fields["date_of_birth"]
                canvas_obj.drawString(field.coordinates[0], field.coordinates[1], user_data.date_of_birth)
            
            # Place of birth
            if "place_of_birth" in self.form_fields:
                field = self.form_fields["place_of_birth"]
                canvas_obj.drawString(field.coordinates[0], field.coordinates[1], user_data.place_of_birth)
            
            # Country of birth
            if "country_of_birth" in self.form_fields:
                field = self.form_fields["country_of_birth"]
                canvas_obj.drawString(field.coordinates[0], field.coordinates[1], user_data.country_of_birth)
            
            # Current nationality
            if "current_nationality" in self.form_fields:
                field = self.form_fields["current_nationality"]
                canvas_obj.drawString(field.coordinates[0], field.coordinates[1], user_data.current_nationality)
            
            # Sex (checkboxes)
            if user_data.sex.lower() == "male" and "sex_male" in self.form_fields:
                field = self.form_fields["sex_male"]
                canvas_obj.drawString(field.coordinates[0], field.coordinates[1], "X")
            elif user_data.sex.lower() == "female" and "sex_female" in self.form_fields:
                field = self.form_fields["sex_female"]
                canvas_obj.drawString(field.coordinates[0], field.coordinates[1], "X")
            
            # Marital status
            if "marital_status" in self.form_fields:
                field = self.form_fields["marital_status"]
                canvas_obj.drawString(field.coordinates[0], field.coordinates[1], user_data.marital_status)
                
        except Exception as e:
            logger.error(f"Error filling personal info: {str(e)}")
    
    def _fill_passport_info(self, canvas_obj, user_data: UserFormData):
        """Fill passport information section"""
        try:
            # Passport type
            if "passport_type" in self.form_fields:
                field = self.form_fields["passport_type"]
                canvas_obj.drawString(field.coordinates[0], field.coordinates[1], user_data.passport_type)
            
            # Passport number
            if "passport_number" in self.form_fields:
                field = self.form_fields["passport_number"]
                canvas_obj.drawString(field.coordinates[0], field.coordinates[1], user_data.passport_number)
            
            # Passport issue date
            if "passport_issue_date" in self.form_fields:
                field = self.form_fields["passport_issue_date"]
                canvas_obj.drawString(field.coordinates[0], field.coordinates[1], user_data.passport_issue_date)
            
            # Passport expiry date
            if "passport_expiry_date" in self.form_fields:
                field = self.form_fields["passport_expiry_date"]
                canvas_obj.drawString(field.coordinates[0], field.coordinates[1], user_data.passport_expiry_date)
            
            # Passport issued by
            if "passport_issued_by" in self.form_fields:
                field = self.form_fields["passport_issued_by"]
                canvas_obj.drawString(field.coordinates[0], field.coordinates[1], user_data.passport_issued_by)
                
        except Exception as e:
            logger.error(f"Error filling passport info: {str(e)}")
    
    def _fill_address_info(self, canvas_obj, user_data: UserFormData):
        """Fill address information section"""
        try:
            # Current address
            if "current_address" in self.form_fields:
                field = self.form_fields["current_address"]
                canvas_obj.drawString(field.coordinates[0], field.coordinates[1], user_data.current_address)
            
            # City
            if "city" in self.form_fields:
                field = self.form_fields["city"]
                canvas_obj.drawString(field.coordinates[0], field.coordinates[1], user_data.city)
            
            # Postal code
            if "postal_code" in self.form_fields:
                field = self.form_fields["postal_code"]
                canvas_obj.drawString(field.coordinates[0], field.coordinates[1], user_data.postal_code)
            
            # Country
            if "country" in self.form_fields:
                field = self.form_fields["country"]
                canvas_obj.drawString(field.coordinates[0], field.coordinates[1], user_data.country)
            
            # Phone number
            if "phone_number" in self.form_fields:
                field = self.form_fields["phone_number"]
                canvas_obj.drawString(field.coordinates[0], field.coordinates[1], user_data.phone_number)
            
            # Email
            if "email" in self.form_fields:
                field = self.form_fields["email"]
                canvas_obj.drawString(field.coordinates[0], field.coordinates[1], user_data.email)
                
        except Exception as e:
            logger.error(f"Error filling address info: {str(e)}")
    
    def _fill_travel_info(self, canvas_obj, user_data: UserFormData):
        """Fill travel information section"""
        try:
            # Purpose of journey
            if "purpose_of_journey" in self.form_fields:
                field = self.form_fields["purpose_of_journey"]
                canvas_obj.drawString(field.coordinates[0], field.coordinates[1], user_data.purpose_of_journey)
            
            # Intended arrival date
            if "intended_arrival_date" in self.form_fields:
                field = self.form_fields["intended_arrival_date"]
                canvas_obj.drawString(field.coordinates[0], field.coordinates[1], user_data.intended_arrival_date)
            
            # Intended departure date
            if "intended_departure_date" in self.form_fields:
                field = self.form_fields["intended_departure_date"]
                canvas_obj.drawString(field.coordinates[0], field.coordinates[1], user_data.intended_departure_date)
            
            # Member state of first entry
            if "member_state_of_first_entry" in self.form_fields:
                field = self.form_fields["member_state_of_first_entry"]
                canvas_obj.drawString(field.coordinates[0], field.coordinates[1], user_data.member_state_of_first_entry)
            
            # Number of entries requested
            if "number_of_entries_requested" in self.form_fields:
                field = self.form_fields["number_of_entries_requested"]
                canvas_obj.drawString(field.coordinates[0], field.coordinates[1], user_data.number_of_entries_requested)
                
        except Exception as e:
            logger.error(f"Error filling travel info: {str(e)}")
    
    def _fill_additional_info(self, canvas_obj, user_data: UserFormData):
        """Fill additional information section"""
        try:
            # Family members in EU
            if user_data.family_members_in_eu and "family_members_in_eu" in self.form_fields:
                field = self.form_fields["family_members_in_eu"]
                canvas_obj.drawString(field.coordinates[0], field.coordinates[1], user_data.family_members_in_eu)
            
            # EU residence permit
            if user_data.eu_residence_permit and "eu_residence_permit" in self.form_fields:
                field = self.form_fields["eu_residence_permit"]
                canvas_obj.drawString(field.coordinates[0], field.coordinates[1], user_data.eu_residence_permit)
            
            # Previous Schengen visa
            if user_data.previous_schengen_visa and "previous_schengen_visa" in self.form_fields:
                field = self.form_fields["previous_schengen_visa"]
                canvas_obj.drawString(field.coordinates[0], field.coordinates[1], user_data.previous_schengen_visa)
            
            # Fingerprints taken
            if user_data.fingerprints_taken and "fingerprints_taken" in self.form_fields:
                field = self.form_fields["fingerprints_taken"]
                canvas_obj.drawString(field.coordinates[0], field.coordinates[1], user_data.fingerprints_taken)
                
        except Exception as e:
            logger.error(f"Error filling additional info: {str(e)}")
    
    def _merge_pdfs(self, writer: PdfWriter, overlay_pdf: bytes) -> bytes:
        """Merge the overlay PDF with the original PDF"""
        try:
            overlay_reader = PdfReader(io.BytesIO(overlay_pdf))
            
            # Merge each page
            for page_num in range(len(writer.pages)):
                if page_num < len(overlay_reader.pages):
                    overlay_page = overlay_reader.pages[page_num]
                    writer.pages[page_num].merge_page(overlay_page)
            
            # Write to bytes
            output_buffer = io.BytesIO()
            writer.write(output_buffer)
            output_buffer.seek(0)
            
            return output_buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error merging PDFs: {str(e)}")
            raise
    
    def validate_user_data(self, user_data: UserFormData) -> Dict[str, Any]:
        """
        Validate user data before form filling
        
        Args:
            user_data: User data to validate
            
        Returns:
            Validation results
        """
        validation_result = {
            "is_valid": True,
            "issues": [],
            "recommendations": []
        }
        
        try:
            # Validate required fields
            required_fields = [
                "surname", "first_name", "date_of_birth", "place_of_birth",
                "country_of_birth", "current_nationality", "sex", "marital_status",
                "passport_type", "passport_number", "passport_issue_date",
                "passport_expiry_date", "passport_issued_by", "current_address",
                "city", "postal_code", "country", "phone_number", "email",
                "purpose_of_journey", "intended_arrival_date", "intended_departure_date",
                "member_state_of_first_entry", "number_of_entries_requested"
            ]
            
            for field in required_fields:
                if not getattr(user_data, field, None):
                    validation_result["issues"].append(f"Missing required field: {field}")
                    validation_result["is_valid"] = False
            
            # Validate date formats
            date_fields = ["date_of_birth", "passport_issue_date", "passport_expiry_date", 
                          "intended_arrival_date", "intended_departure_date"]
            
            for field in date_fields:
                value = getattr(user_data, field, None)
                if value and not self._validate_date_format(value):
                    validation_result["issues"].append(f"Invalid date format for {field}: {value}")
                    validation_result["is_valid"] = False
            
            # Validate email format
            if user_data.email and not self._validate_email(user_data.email):
                validation_result["issues"].append(f"Invalid email format: {user_data.email}")
                validation_result["is_valid"] = False
            
            # Validate phone number
            if user_data.phone_number and not self._validate_phone(user_data.phone_number):
                validation_result["issues"].append(f"Invalid phone number format: {user_data.phone_number}")
                validation_result["is_valid"] = False
            
            # Check passport expiry
            if user_data.passport_expiry_date:
                try:
                    expiry_date = datetime.strptime(user_data.passport_expiry_date, "%d/%m/%Y").date()
                    if expiry_date < date.today():
                        validation_result["issues"].append("Passport has expired")
                        validation_result["is_valid"] = False
                    elif (expiry_date - date.today()).days < 90:
                        validation_result["recommendations"].append("Passport expires within 3 months")
                except ValueError:
                    pass
            
            # Check travel dates
            if user_data.intended_arrival_date and user_data.intended_departure_date:
                try:
                    arrival = datetime.strptime(user_data.intended_arrival_date, "%d/%m/%Y").date()
                    departure = datetime.strptime(user_data.intended_departure_date, "%d/%m/%Y").date()
                    
                    if arrival >= departure:
                        validation_result["issues"].append("Departure date must be after arrival date")
                        validation_result["is_valid"] = False
                    
                    if arrival < date.today():
                        validation_result["issues"].append("Arrival date cannot be in the past")
                        validation_result["is_valid"] = False
                        
                except ValueError:
                    pass
            
        except Exception as e:
            logger.error(f"Error validating user data: {str(e)}")
            validation_result["is_valid"] = False
            validation_result["issues"].append(f"Validation error: {str(e)}")
        
        return validation_result
    
    def _validate_date_format(self, date_string: str) -> bool:
        """Validate date format DD/MM/YYYY"""
        try:
            datetime.strptime(date_string, "%d/%m/%Y")
            return True
        except ValueError:
            return False
    
    def _validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _validate_phone(self, phone: str) -> bool:
        """Validate phone number format"""
        # Remove spaces and special characters
        clean_phone = re.sub(r'[^\d+]', '', phone)
        # Check if it's a valid international phone number
        return len(clean_phone) >= 10 and clean_phone.startswith('+')
    
    def get_form_preview(self, user_data: UserFormData) -> Dict[str, Any]:
        """
        Get a preview of how the form will be filled
        
        Args:
            user_data: User data for preview
            
        Returns:
            Form preview data
        """
        try:
            preview = {
                "form_type": "Schengen Visa Application",
                "filled_fields": {},
                "validation": self.validate_user_data(user_data)
            }
            
            # Map user data to form fields
            field_mapping = {
                "surname": user_data.surname,
                "first_name": user_data.first_name,
                "date_of_birth": user_data.date_of_birth,
                "place_of_birth": user_data.place_of_birth,
                "country_of_birth": user_data.country_of_birth,
                "current_nationality": user_data.current_nationality,
                "sex": user_data.sex,
                "marital_status": user_data.marital_status,
                "passport_type": user_data.passport_type,
                "passport_number": user_data.passport_number,
                "passport_issue_date": user_data.passport_issue_date,
                "passport_expiry_date": user_data.passport_expiry_date,
                "passport_issued_by": user_data.passport_issued_by,
                "current_address": user_data.current_address,
                "city": user_data.city,
                "postal_code": user_data.postal_code,
                "country": user_data.country,
                "phone_number": user_data.phone_number,
                "email": user_data.email,
                "purpose_of_journey": user_data.purpose_of_journey,
                "intended_arrival_date": user_data.intended_arrival_date,
                "intended_departure_date": user_data.intended_departure_date,
                "member_state_of_first_entry": user_data.member_state_of_first_entry,
                "number_of_entries_requested": user_data.number_of_entries_requested
            }
            
            preview["filled_fields"] = field_mapping
            
            return preview
            
        except Exception as e:
            logger.error(f"Error getting form preview: {str(e)}")
            raise
