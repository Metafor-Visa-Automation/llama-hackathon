"""
Groq OCR Service - Advanced OCR using Groq's Llama Vision API
Integrates with existing OCR validation framework
"""

import os
import base64
import io
import json
from typing import Dict, Any, Optional, Tuple
from groq import Groq
from pdf2image import convert_from_bytes
from PIL import Image
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class GroqOCRService:
    """OCR service using Groq's Llama 4 Maverick model for document extraction"""
    
    def __init__(self):
        """Initialize Groq client"""
        try:
            api_key = settings.groq_api_key
            self.client = Groq(api_key=api_key)
            logger.info("Groq OCR service initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Groq client: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if Groq OCR service is available"""
        return True
    
    def _get_base64_from_bytes(self, file_data: bytes, mime_type: str) -> Tuple[str, str]:
        """
        Convert file bytes to base64, handling PDF conversion if needed
        
        Args:
            file_data: Raw file bytes
            mime_type: MIME type of the file
            
        Returns:
            Tuple of (base64_data, final_mime_type)
        """
        try:
            if mime_type == "application/pdf":
                logger.info("PDF detected, converting first page to JPEG...")
                # Convert first page to JPEG
                images = convert_from_bytes(file_data, first_page=1, last_page=1, fmt="jpeg")
                if images:
                    img_byte_arr = io.BytesIO()
                    images[0].save(img_byte_arr, format='JPEG')
                    base64_data = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
                    return base64_data, "image/jpeg"
                else:
                    raise ValueError("Failed to convert PDF to image")
            
            elif mime_type in ["image/jpeg", "image/png", "image/webp", "image/jpg"]:
                logger.info(f"Image ({mime_type}) detected")
                base64_data = base64.b64encode(file_data).decode('utf-8')
                return base64_data, mime_type
            
            else:
                # Try to handle as image anyway
                try:
                    img = Image.open(io.BytesIO(file_data))
                    img_byte_arr = io.BytesIO()
                    img.save(img_byte_arr, format='JPEG')
                    base64_data = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
                    return base64_data, "image/jpeg"
                except Exception as e:
                    raise ValueError(f"Unsupported file type: {mime_type}")
        
        except Exception as e:
            logger.error(f"Error converting file to base64: {e}")
            raise
    
    def _get_system_prompt(self, document_type: str) -> str:
        """
        Get system prompt based on document type
        
        Args:
            document_type: Type of document (passport, bank_statement, etc.)
            
        Returns:
            System prompt string
        """
        # Import schema definitions from the AI folder logic
        schemas = self._get_document_schemas()
        
        # Map backend document types to AI folder types
        type_mapping = {
            "passport": "passport",
            "bank_statement": "hesapozet",
            "travel_insurance": "sigorta",
            "property_deed": "tabusenedi",
            "tax_return": "vergi",
            "hotel_reservation": "kalacakyer",
            "invitation_letter": "businessinvitation",
            "business_letter": "businessinvitation",
            "acceptance_letter": "acceptance_letter",
            "employment_letter": "employment_letter",
            "flight_ticket": "ucakbileti",
            "ucakbileti": "ucakbileti",
            "biometric_photo": "biometrikfoto",
            "biometrikfoto": "biometrikfoto",
            "diploma": "diploma",
            "birth_certificate": "dogumsertifikasi",
            "dogumsertifikasi": "dogumsertifikasi",
            "employment_contract": "employmentcontract",
            "employmentcontract": "employmentcontract",
            "kabulmektubu": "kabulmektubu",
            "id_card": "kimlikon",
            "kimlikon": "kimlikon",
            "drivers_license": "surucuon",
            "surucuon": "surucuon",
            "language_proficiency": "languageproficiency",
            "languageproficiency": "languageproficiency",
            "marriage_certificate": "marriage",
            "marriage": "marriage",
            "medical_report": "medical",
            "medical": "medical",
            "transcript": "transkript",
            "transkript": "transkript",
            "work_permit": "workpermit",
            "workpermit": "workpermit",
        }
        
        schema_type = type_mapping.get(document_type, document_type)
        schema = schemas.get(schema_type)
        
        if not schema:
            # Return generic schema
            schema = """
            {
              "documentType": "unknown",
              "extractedText": "Full text from document",
              "keyInformation": {}
            }
            """
        
        base_prompt = """
You are a high-accuracy data extraction assistant for visa applications.
Your task is to extract all key information from the provided document image.
Return *only* a valid JSON object matching the exact schema below.
Do not add any explanatory text, comments, or markdown.
If a field is unreadable or not present, return null for that key.
Ensure all dates are in "YYYY-MM-DD" format.
Ensure all amounts are numeric values without currency symbols.

Schema:
{schema}
"""
        return base_prompt.format(schema=schema)
    
    def _get_document_schemas(self) -> Dict[str, str]:
        """Get all document schemas (from schema_manager.py logic)"""
        return {
            "passport": """
            {
              "passportType": "P",
              "countryCode": "TUR",
              "passportNumber": "U12345678",
              "surname": "YILMAZ",
              "givenName": "AHMET",
              "dateOfBirth": "1990-01-01",
              "expiryDate": "2030-10-20",
              "issueDate": "2020-10-21"
            }
            """,
            "businessinvitation": """
            {
              "invitingCompanyName": "Sample GmbH",
              "invitingCompanyAddress": "Musterstraße 1, 10117 Berlin, Germany",
              "invitingCompanyContact": "+49 30 123456",
              "invitedPersonName": "Ahmet Yılmaz",
              "invitedPersonPassport": "U12345678",
              "purposeOfVisit": "Business meetings for Project X",
              "visitStartDate": "2025-12-01",
              "visitEndDate": "2025-12-07"
            }
            """,
            "hesapozet": """
            {
              "bankName": "Garanti BBVA",
              "accountHolder": "Ahmet Yılmaz",
              "accountIBAN": "TR00 0000 0000 0000 0000 0000",
              "statementDate": "2025-10-25",
              "statementPeriod": "01.10.2025 - 25.10.2025",
              "closingBalance": 150000.75,
              "currency": "TRY"
            }
            """,
            "kalacakyer": """
            {
              "bookingPlatform": "Booking.com",
              "hotelName": "Grand Hotel Berlin",
              "hotelAddress": "123 Main St, Berlin, Germany",
              "confirmationNumber": "ABC12345",
              "guestName": "Ahmet Yılmaz",
              "checkInDate": "2025-12-01",
              "checkOutDate": "2025-12-07"
            }
            """,
            "sigorta": """
            {
              "insuranceProvider": "AXA Sigorta",
              "policyNumber": "POL987654",
              "insuredPerson": "Ahmet Yılmaz",
              "insuredPersonTCKN": "12345678901",
              "coverageStartDate": "2025-12-01",
              "coverageEndDate": "2025-12-31",
              "coverageRegion": "All Schengen Countries",
              "coverageAmount": 30000,
              "coverageCurrency": "EUR"
            }
            """,
            "tabusenedi": """
            {
              "propertyOwner": "Ahmet Yılmaz",
              "propertyType": "Mesken (Daire)",
              "propertyAddress": "Örnek Mah, Atatürk Cad, No: 1, D: 5, Ataşehir, İstanbul",
              "il": "İstanbul",
              "ilce": "Ataşehir",
              "mahalle": "Örnek",
              "ada": "123",
              "parsel": "45"
            }
            """,
            "vergi": """
            {
              "taxOffice": "Erenköy Vergi Dairesi",
              "taxpayerName": "Ahmet Yılmaz",
              "taxIDNumber_VKN": "1234567890",
              "documentType": "Vergi Levhası",
              "taxYear": "2024",
              "matrah": 200000.00,
              "tahakkukEdenVergi": 40000.00
            }
            """,
            "acceptance_letter": """
            {
              "institutionName": "Technical University of Berlin",
              "institutionAddress": "Straße des 17. Juni 135, 10623 Berlin, Germany",
              "institutionContact": "+49 30 314-0",
              "studentName": "Ahmet Yılmaz",
              "studentID": "STU123456",
              "programName": "Master of Science in Computer Science",
              "programStartDate": "2025-10-01",
              "programEndDate": "2027-09-30",
              "letterDate": "2025-08-15",
              "tuitionFee": 0,
              "currency": "EUR",
              "scholarshipInfo": "Fully funded"
            }
            """,
            "employment_letter": """
            {
              "companyName": "Tech Solutions GmbH",
              "companyAddress": "Innovation Street 10, 10115 Berlin, Germany",
              "employeeName": "Ahmet Yılmaz",
              "position": "Senior Software Engineer",
              "employmentStartDate": "2020-01-15",
              "employmentStatus": "Full-time permanent",
              "monthlySalary": 5000,
              "currency": "EUR",
              "letterDate": "2025-10-20"
            }
            """,
            "ucakbileti": """
            {
              "passengerName": "YILMAZ/AHMET MR",
              "bookingReference": "ABC123",
              "airline": "Turkish Airlines",
              "flightNumber": "TK1234",
              "departureAirport": "IST",
              "arrivalAirport": "BER",
              "departureDate": "2025-12-01",
              "departureTime": "10:30",
              "arrivalDate": "2025-12-01",
              "arrivalTime": "13:45",
              "seatNumber": "12A",
              "ticketNumber": "2354567890123"
            }
            """,
            "biometrikfoto": """
            {
              "photoType": "Biometric Passport Photo",
              "dimensions": "35mm x 45mm",
              "backgroundColor": "White",
              "faceDetected": true,
              "eyesVisible": true,
              "qualityCheck": "Passed",
              "photoDate": "2025-10-26"
            }
            """,
            "diploma": """
            {
              "institutionName": "Istanbul Technical University",
              "studentName": "Ahmet Yılmaz",
              "degreeType": "Bachelor of Science",
              "major": "Computer Engineering",
              "graduationDate": "2020-06-15",
              "diplomaNumber": "DIP-2020-12345",
              "gpa": "3.45",
              "honors": "High Honors"
            }
            """,
            "dogumsertifikasi": """
            {
              "fullName": "Ahmet Yılmaz",
              "dateOfBirth": "1995-03-15",
              "placeOfBirth": "Istanbul",
              "fatherName": "Mehmet Yılmaz",
              "motherName": "Ayşe Yılmaz",
              "tcKimlikNo": "12345678901",
              "registrationNumber": "2025/123",
              "issueDate": "2025-01-10",
              "issuingAuthority": "Istanbul Nüfus Müdürlüğü"
            }
            """,
            "employmentcontract": """
            {
              "companyName": "Tech Solutions GmbH",
              "employeeName": "Ahmet Yılmaz",
              "position": "Software Developer",
              "contractStartDate": "2025-11-01",
              "contractEndDate": "2027-10-31",
              "contractType": "Fixed-term",
              "monthlySalary": 4500,
              "currency": "EUR",
              "workingHours": "40 hours per week",
              "probationPeriod": "6 months",
              "signedDate": "2025-10-15"
            }
            """,
            "kabulmektubu": """
            {
              "institutionName": "Technical University of Munich",
              "institutionAddress": "Arcisstraße 21, 80333 München, Germany",
              "studentName": "Ahmet Yılmaz",
              "studentID": "03123456",
              "programName": "Master of Science in Electrical Engineering",
              "programStartDate": "2025-10-01",
              "programEndDate": "2027-09-30",
              "letterDate": "2025-08-20",
              "tuitionFee": 0,
              "semesterFee": 144.40,
              "currency": "EUR",
              "language": "English"
            }
            """,
            "kimlikon": """
            {
              "documentType": "National ID Card",
              "idNumber": "12345678901",
              "fullName": "AHMET YILMAZ",
              "dateOfBirth": "1995-03-15",
              "placeOfBirth": "Istanbul",
              "gender": "E",
              "nationality": "T.C.",
              "issueDate": "2020-01-15",
              "expiryDate": "2030-01-15",
              "issuingAuthority": "Istanbul Emniyet Müdürlüğü"
            }
            """,
            "surucuon": """
            {
              "documentType": "Driver's License",
              "licenseNumber": "ABC123456",
              "fullName": "AHMET YILMAZ",
              "dateOfBirth": "1995-03-15",
              "placeOfBirth": "Istanbul",
              "issueDate": "2015-07-20",
              "expiryDate": "2030-07-20",
              "licenseCategories": ["B", "A2"],
              "issuingAuthority": "Istanbul Emniyet Müdürlüğü"
            }
            """,
            "languageproficiency": """
            {
              "testName": "IELTS Academic",
              "testDate": "2025-09-15",
              "candidateName": "Ahmet Yılmaz",
              "candidateID": "12345678",
              "overallScore": 7.5,
              "listeningScore": 8.0,
              "readingScore": 7.5,
              "writingScore": 7.0,
              "speakingScore": 7.5,
              "testCenter": "British Council Istanbul",
              "certificateNumber": "IELTS-2025-123456"
            }
            """,
            "marriage": """
            {
              "marriageCertificateNumber": "2025/123",
              "groomName": "Ahmet Yılmaz",
              "groomTCKN": "12345678901",
              "groomDateOfBirth": "1995-03-15",
              "brideName": "Ayşe Demir",
              "brideTCKN": "10987654321",
              "brideDateOfBirth": "1997-05-20",
              "marriageDate": "2024-06-15",
              "marriagePlace": "Istanbul",
              "issuingAuthority": "Istanbul Evlendirme Dairesi",
              "issueDate": "2024-06-15"
            }
            """,
            "medical": """
            {
              "patientName": "Ahmet Yılmaz",
              "patientTCKN": "12345678901",
              "dateOfBirth": "1995-03-15",
              "reportDate": "2025-10-20",
              "reportType": "General Health Examination",
              "hospitalName": "Istanbul Medical Center",
              "doctorName": "Dr. Mehmet Özkan",
              "findings": "Patient is in good health",
              "diagnosis": "Healthy",
              "recommendations": "No restrictions for travel",
              "vaccinations": ["COVID-19", "Hepatitis A", "Hepatitis B"]
            }
            """,
            "transkript": """
            {
              "institutionName": "Istanbul Technical University",
              "studentName": "Ahmet Yılmaz",
              "studentNumber": "150123456",
              "program": "Computer Engineering",
              "degreeLevel": "Bachelor",
              "transcriptDate": "2025-10-15",
              "gpa": "3.45",
              "totalCredits": 240,
              "completedCredits": 240,
              "academicStatus": "Graduated"
            }
            """,
            "workpermit": """
            {
              "permitNumber": "WP-2025-123456",
              "permitType": "EU Blue Card",
              "holderName": "Ahmet Yılmaz",
              "nationality": "Turkish",
              "passportNumber": "U12345678",
              "employerName": "Tech Solutions GmbH",
              "position": "Software Engineer",
              "issueDate": "2025-11-01",
              "expiryDate": "2029-10-31",
              "issuingAuthority": "Federal Office for Migration and Refugees",
              "workLocation": "Berlin, Germany"
            }
            """
        }
    
    def _detect_document_type(self, file_data: bytes, mime_type: str, file_name: Optional[str] = None) -> str:
        """
        Automatically detect document type using AI vision
        
        Args:
            file_data: Raw file bytes
            mime_type: MIME type of the file
            file_name: Original filename (optional)
            
        Returns:
            Detected document type
        """
        try:
            logger.info(f"Auto-detecting document type for: {file_name}")
            
            # Convert to base64
            base64_image, final_mime_type = self._get_base64_from_bytes(file_data, mime_type)
            
            detection_prompt = """
You are a document classification expert for visa applications.
Analyze the provided document image and determine its type.

Return ONLY a JSON object with this exact format:
{
  "documentType": "one of: passport, bank_statement, travel_insurance, property_deed, tax_return, hotel_reservation, invitation_letter, acceptance_letter, employment_letter, employment_contract, flight_ticket, biometric_photo, diploma, birth_certificate, id_card, drivers_license, language_proficiency, marriage_certificate, medical_report, transcript, work_permit, other",
  "confidence": 0.95,
  "reasoning": "Brief explanation of why this document type was chosen"
}

Document types explained:
- passport: International travel document with photo
- bank_statement: Bank account transaction history or balance statement
- travel_insurance: Insurance policy for travel coverage
- property_deed: Real estate ownership document (Tapu Senedi)
- tax_return: Tax declaration or tax office document
- hotel_reservation: Hotel booking confirmation
- invitation_letter: Business or personal invitation letter
- acceptance_letter: University/school admission or acceptance letter
- employment_letter: Employment verification or reference letter
- employment_contract: Official employment contract document
- flight_ticket: Airline ticket or flight booking confirmation
- biometric_photo: Passport-style biometric photo
- diploma: University or school diploma/degree certificate
- birth_certificate: Official birth certificate
- id_card: National identity card (Kimlik)
- drivers_license: Driver's license (Sürücü Belgesi)
- language_proficiency: Language test certificate (IELTS, TOEFL, etc.)
- marriage_certificate: Marriage certificate
- medical_report: Medical examination or health report
- transcript: Academic transcript (Transkript)
- work_permit: Work permit or residence permit for employment
- other: Any other document type

Analyze carefully and return ONLY the JSON object.
"""
            
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": detection_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "What type of document is this?"},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:{final_mime_type};base64,{base64_image}"},
                            },
                        ],
                    }
                ],
                model="meta-llama/llama-4-maverick-17b-128e-instruct",
                response_format={"type": "json_object"},
                temperature=0.0
            )
            
            result = json.loads(chat_completion.choices[0].message.content)
            detected_type = result.get("documentType", "other")
            confidence = result.get("confidence", 0.0)
            reasoning = result.get("reasoning", "")
            
            logger.info(f"Detected document type: {detected_type} (confidence: {confidence})")
            logger.info(f"Reasoning: {reasoning}")
            
            return detected_type
            
        except Exception as e:
            logger.error(f"Error detecting document type: {e}")
            return "other"
    
    def extract_document_data(
        self,
        file_data: bytes,
        mime_type: str,
        document_type: str,
        file_name: Optional[str] = None,
        auto_detect: bool = True
    ) -> Dict[str, Any]:
        """
        Extract structured data from document using Groq Vision API
        
        Args:
            file_data: Raw file bytes
            mime_type: MIME type of the file
            document_type: Type of document (passport, bank_statement, etc.)
            file_name: Original filename (optional)
            auto_detect: If True, auto-detect document type when confidence is low (default: True)
            
        Returns:
            Dict containing extracted data and metadata
        """
        try:
            logger.info(f"Processing document: type={document_type}, filename={file_name}")
            
            # Auto-detect document type if enabled and filename doesn't provide clear indication
            original_document_type = document_type
            if auto_detect and self._should_auto_detect(file_name, document_type):
                detected_type = self._detect_document_type(file_data, mime_type, file_name)
                if detected_type != "other":
                    logger.info(f"Overriding document type from '{document_type}' to '{detected_type}'")
                    document_type = detected_type
            
            # Get system prompt for document type
            system_prompt = self._get_system_prompt(document_type)
            
            # Convert file to base64
            base64_image, final_mime_type = self._get_base64_from_bytes(file_data, mime_type)
            
            # Call Groq API
            logger.info("Sending request to Groq Llama 4 Maverick...")
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Extract all data from this document based on the system instructions."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{final_mime_type};base64,{base64_image}"
                                },
                            },
                        ],
                    }
                ],
                model="meta-llama/llama-4-maverick-17b-128e-instruct",  # Using Llama 4 Maverick
                response_format={"type": "json_object"},  # Force JSON output
                temperature=0.0  # Maximum accuracy
            )
            
            # Parse response
            json_string = chat_completion.choices[0].message.content
            extracted_data = json.loads(json_string)
            
            logger.info(f"Successfully extracted data from document: {file_name}")
            
            return {
                "success": True,
                "extracted_data": extracted_data,
                "document_type": document_type,
                "original_document_type": original_document_type,
                "auto_detected": document_type != original_document_type,
                "file_name": file_name,
                "model": "meta-llama/llama-4-maverick-17b-128e-instruct",
                "raw_response": json_string
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return {
                "success": False,
                "error": f"Invalid JSON response from OCR: {str(e)}",
                "document_type": document_type,
                "file_name": file_name
            }
        except Exception as e:
            logger.error(f"Error during OCR extraction: {e}")
            return {
                "success": False,
                "error": f"OCR extraction failed: {str(e)}",
                "document_type": document_type,
                "file_name": file_name
            }
    
    def _should_auto_detect(self, file_name: Optional[str], document_type: str) -> bool:
        """
        Determine if auto-detection should be performed based on filename and document type
        
        Args:
            file_name: Original filename
            document_type: Provided document type
            
        Returns:
            True if auto-detection should be performed
        """
        # Auto-detect if document type is generic or unclear
        if document_type in ["other", "unknown", "document"]:
            return True
        
        # Auto-detect if filename is generic or doesn't contain document type hints
        if file_name:
            lower_name = file_name.lower()
            generic_names = [
                "document", "file", "scan", "image", "photo", "picture",
                "img", "doc", "untitled", "new", "temp", "upload"
            ]
            
            # Check if filename is generic (just numbers, dates, or generic words)
            if any(generic in lower_name for generic in generic_names):
                logger.info(f"Generic filename detected: {file_name}, will auto-detect document type")
                return True
            
            # Check if filename doesn't match provided document type
            doc_type_keywords = {
                "passport": ["passport", "pasaport", "pass"],
                "bank_statement": ["bank", "banka", "hesap", "ozet", "statement"],
                "travel_insurance": ["insurance", "sigorta", "policy"],
                "property_deed": ["tapu", "deed", "property", "title"],
                "tax_return": ["vergi", "tax", "return"],
                "hotel_reservation": ["hotel", "otel", "reservation", "booking"],
                "invitation_letter": ["invitation", "davet", "invite"],
                "acceptance_letter": ["acceptance", "admission", "kabul", "offer"],
                "employment_letter": ["employment", "work", "job", "reference", "is"],
                "employment_contract": ["contract", "sozlesme", "agreement"],
                "flight_ticket": ["flight", "ticket", "ucak", "bilet", "boarding"],
                "biometric_photo": ["biometric", "photo", "foto", "picture"],
                "diploma": ["diploma", "degree", "mezuniyet"],
                "birth_certificate": ["birth", "dogum", "certificate", "sertifika"],
                "id_card": ["id", "identity", "kimlik"],
                "drivers_license": ["driver", "license", "surucu", "ehliyet"],
                "language_proficiency": ["ielts", "toefl", "language", "dil", "proficiency"],
                "marriage_certificate": ["marriage", "evlilik", "nikah"],
                "medical_report": ["medical", "health", "saglik", "rapor"],
                "transcript": ["transcript", "transkript", "akademik"],
                "work_permit": ["work", "permit", "calisma", "izin", "blue card"],
            }
            
            keywords = doc_type_keywords.get(document_type, [])
            if keywords and not any(keyword in lower_name for keyword in keywords):
                logger.info(f"Filename '{file_name}' doesn't match document type '{document_type}', will auto-detect")
                return True
        
        return False
    
    def extract_text_only(self, file_data: bytes, mime_type: str) -> str:
        """
        Extract raw text from document without structured parsing
        
        Args:
            file_data: Raw file bytes
            mime_type: MIME type of the file
            
        Returns:
            Extracted text string
        """
        try:
            # Convert to base64
            base64_image, final_mime_type = self._get_base64_from_bytes(file_data, mime_type)
            
            # Simple text extraction prompt
            system_prompt = """
Extract all visible text from this document exactly as it appears.
Maintain the original formatting and line breaks.
Return only the extracted text without any additional commentary.
"""
            
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Extract all text from this document."},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:{final_mime_type};base64,{base64_image}"},
                            },
                        ],
                    }
                ],
                model="meta-llama/llama-4-maverick-17b-128e-instruct",
                temperature=0.0
            )
            
            return chat_completion.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            raise
