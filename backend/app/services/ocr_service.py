"""
OCR Service for Document Analysis and Validation
Handles different document types with specific validation rules
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import logging
from .ocr_document_processor import OCRDocumentProcessor

logger = logging.getLogger(__name__)


class DocumentType(str, Enum):
    BANK_STATEMENT = "bank_statement"
    PASSPORT = "passport"
    BIOMETRIC_PHOTO = "biometric_photo"
    BIRTH_CERTIFICATE = "birth_certificate"
    BUSINESS_LETTER = "business_letter"
    HOTEL_RESERVATION = "hotel_reservation"
    INVITATION_LETTER = "invitation_letter"
    PREVIOUS_VISAS = "previous_visas"
    PROPERTY_DEED = "property_deed"
    SOCIAL_SECURITY = "social_security"
    STUDENT_CERTIFICATE = "student_certificate"
    TAX_RETURN = "tax_return"
    TRAVEL_INSURANCE = "travel_insurance"
    PAYSLIP = "payslip"
    ACADEMIC_TRANSCRIPT = "academic_transcript"
    EMPLOYMENT_CERTIFICATE = "employment_certificate"


@dataclass
class OCRValidationRule:
    """Base class for OCR validation rules"""
    enabled: bool
    description: str


@dataclass
class BankStatementValidationRules(OCRValidationRule):
    """Bank statement specific validation rules"""
    check_account_balance: bool = True
    check_bank_stamp: bool = True
    check_statement_period: bool = True
    min_months: int = 3
    min_balance_threshold: float = 1000.0  # Minimum balance in currency


@dataclass
class PassportValidationRules(OCRValidationRule):
    """Passport specific validation rules"""
    check_expiry_date: bool = True
    check_issuance_date: bool = True
    check_passport_number: bool = True
    min_pages: int = 2
    validity_months: int = 3


@dataclass
class BiometricPhotoValidationRules(OCRValidationRule):
    """Biometric photo specific validation rules"""
    check_background_color: bool = True
    check_face_visible: bool = True
    check_photo_size: bool = True
    check_recent_photo: bool = True
    photo_count: int = 2
    required_width_mm: int = 35
    required_height_mm: int = 45
    max_photo_age_months: int = 6


@dataclass
class BirthCertificateValidationRules(OCRValidationRule):
    """Birth certificate specific validation rules"""
    check_birth_date: bool = True
    check_official_stamp: bool = True
    check_parents_names: bool = True


@dataclass
class BusinessLetterValidationRules(OCRValidationRule):
    """Business letter specific validation rules"""
    check_business_purpose: bool = True
    check_company_letterhead: bool = True
    check_contact_details: bool = True
    check_signature: bool = True


@dataclass
class HotelReservationValidationRules(OCRValidationRule):
    """Hotel reservation specific validation rules"""
    check_confirmation: bool = True
    check_dates: bool = True
    check_hotel_reservation: bool = True
    check_payment_proof: bool = True


@dataclass
class InvitationLetterValidationRules(OCRValidationRule):
    """Invitation letter specific validation rules"""
    check_host_contact: bool = True
    check_host_info: bool = True
    check_invitation_dates: bool = True
    check_signature: bool = True


@dataclass
class PreviousVisasValidationRules(OCRValidationRule):
    """Previous visas specific validation rules"""
    check_validity: bool = True
    check_visa_country: bool = True
    check_visa_dates: bool = True


@dataclass
class PropertyDeedValidationRules(OCRValidationRule):
    """Property deed specific validation rules"""
    check_official_stamp: bool = True
    check_property_owner: bool = True
    check_property_value: bool = True


@dataclass
class SocialSecurityValidationRules(OCRValidationRule):
    """Social security specific validation rules"""
    check_active_status: bool = True
    check_registration_date: bool = True
    check_sgk_number: bool = True


@dataclass
class StudentCertificateValidationRules(OCRValidationRule):
    """Student certificate specific validation rules"""
    check_issue_date: bool = True
    check_school_name: bool = True
    check_school_stamp: bool = True
    check_signature: bool = True
    max_age_in_days: int = 90


@dataclass
class TaxReturnValidationRules(OCRValidationRule):
    """Tax return specific validation rules"""
    check_income_amount: bool = True
    check_tax_office_stamp: bool = True
    check_tax_year: bool = True


@dataclass
class TravelInsuranceValidationRules(OCRValidationRule):
    """Travel insurance specific validation rules"""
    check_coverage_amount: bool = True
    check_coverage_area: bool = True
    check_validity_period: bool = True


@dataclass
class OCRResult:
    """OCR processing result"""
    document_type: DocumentType
    confidence_score: float
    extracted_text: str
    validation_results: Dict[str, Any]
    issues: List[str]
    recommendations: List[str]
    metadata: Dict[str, Any]


class OCRService:
    """Main OCR service for document processing and validation"""
    
    def __init__(self):
        self.document_processor = OCRDocumentProcessor()
        self.document_type_configs = {
            DocumentType.BANK_STATEMENT: {
                "checkId": "bank_statement",
                "docDescription": "Son 3 aya ait banka hesap dökümleri",
                "docName": "Banka Hesap Dökümü",
                "ocrValidationRules": BankStatementValidationRules(
                    enabled=True,
                    description="Bank statement validation rules",
                    check_account_balance=True,
                    check_bank_stamp=True,
                    check_statement_period=True,
                    min_months=3
                ),
                "requiredFor": ["ALL"]
            },
            DocumentType.PASSPORT: {
                "checkId": "passport_general",
                "docDescription": "Son 10 yıl içinde alınmış, vize bitiş tarihinden itibaren en az 3 ay daha geçerli ve en az 2 boş sayfası bulunan pasaport",
                "docName": "Pasaport",
                "ocrValidationRules": PassportValidationRules(
                    enabled=True,
                    description="Passport validation rules",
                    check_expiry_date=True,
                    check_issuance_date=True,
                    check_passport_number=True,
                    min_pages=2,
                    validity_months=3
                ),
                "requiredFor": ["ALL"]
            },
            DocumentType.BIOMETRIC_PHOTO: {
                "checkId": "biometric_photo",
                "docDescription": "Son 6 ay içinde çekilmiş, 35×45 mm boyutlarında, beyaz arka planlı, yüzün net bir şekilde göründüğü 2 adet fotoğraf",
                "docName": "Biyometrik Fotoğraf",
                "ocrValidationRules": BiometricPhotoValidationRules(
                    enabled=True,
                    description="Biometric photo validation rules",
                    check_background_color=True,
                    check_face_visible=True,
                    check_photo_size=True,
                    check_recent_photo=True,
                    photo_count=2,
                    required_width_mm=35,
                    required_height_mm=45,
                    max_photo_age_months=6
                ),
                "requiredFor": ["ALL"]
            },
            DocumentType.BIRTH_CERTIFICATE: {
                "checkId": "birth_certificate",
                "docDescription": "Doğum belgesi veya nüfus kayıt örneği",
                "docName": "Doğum Belgesi",
                "ocrValidationRules": BirthCertificateValidationRules(
                    enabled=True,
                    description="Birth certificate validation rules",
                    check_birth_date=True,
                    check_official_stamp=True,
                    check_parents_names=True
                ),
                "requiredFor": ["ALL"]
            },
            DocumentType.BUSINESS_LETTER: {
                "checkId": "business_letter",
                "docDescription": "Şirket antetli kağıda yazılmış, seyahat amacını ve iş bağlantılarını açıklayan mektup",
                "docName": "İş Mektubu",
                "ocrValidationRules": BusinessLetterValidationRules(
                    enabled=True,
                    description="Business letter validation rules",
                    check_business_purpose=True,
                    check_company_letterhead=True,
                    check_contact_details=True,
                    check_signature=True
                ),
                "requiredFor": ["EMPLOYEE"]
            },
            DocumentType.HOTEL_RESERVATION: {
                "checkId": "hotel_reservation",
                "docDescription": "Onaylı otel rezervasyonu veya host konaklama belgesi",
                "docName": "Turist Konaklama Rezervasyonu",
                "ocrValidationRules": HotelReservationValidationRules(
                    enabled=True,
                    description="Hotel reservation validation rules",
                    check_confirmation=True,
                    check_dates=True,
                    check_hotel_reservation=True,
                    check_payment_proof=True
                ),
                "requiredFor": ["TOURIST"]
            },
            DocumentType.INVITATION_LETTER: {
                "checkId": "invitation_letter",
                "docDescription": "Gidilecek ülkedeki kişi/kurumdan alınan davetiye mektubu",
                "docName": "Davetiye Mektubu",
                "ocrValidationRules": InvitationLetterValidationRules(
                    enabled=True,
                    description="Invitation letter validation rules",
                    check_host_contact=True,
                    check_host_info=True,
                    check_invitation_dates=True,
                    check_signature=True
                ),
                "requiredFor": ["VISITOR"]
            },
            DocumentType.PREVIOUS_VISAS: {
                "checkId": "previous_visas",
                "docDescription": "Var ise önceki Schengen veya diğer ülke vizeleri",
                "docName": "Önceki Vizeler",
                "ocrValidationRules": PreviousVisasValidationRules(
                    enabled=True,
                    description="Previous visas validation rules",
                    check_validity=True,
                    check_visa_country=True,
                    check_visa_dates=True
                ),
                "requiredFor": ["ALL"]
            },
            DocumentType.PROPERTY_DEED: {
                "checkId": "property_deed",
                "docDescription": "Türkiye'deki mal varlığını gösteren tapu belgesi",
                "docName": "Tapu Belgesi",
                "ocrValidationRules": PropertyDeedValidationRules(
                    enabled=True,
                    description="Property deed validation rules",
                    check_official_stamp=True,
                    check_property_owner=True,
                    check_property_value=True
                ),
                "requiredFor": ["ALL"]
            },
            DocumentType.SOCIAL_SECURITY: {
                "checkId": "social_security",
                "docDescription": "SGK kayıt belgesi veya sosyal güvenlik kurumu belgesi",
                "docName": "Sosyal Güvenlik Belgesi",
                "ocrValidationRules": SocialSecurityValidationRules(
                    enabled=True,
                    description="Social security validation rules",
                    check_active_status=True,
                    check_registration_date=True,
                    check_sgk_number=True
                ),
                "requiredFor": ["EMPLOYEE"]
            },
            DocumentType.STUDENT_CERTIFICATE: {
                "checkId": "student_certificate",
                "docDescription": "Kayıtlı olunan okuldan alınan, en az 3 ay içinde güncellenmiş öğrenci belgesi",
                "docName": "Öğrenci Belgesi",
                "ocrValidationRules": StudentCertificateValidationRules(
                    enabled=True,
                    description="Student certificate validation rules",
                    check_issue_date=True,
                    check_school_name=True,
                    check_school_stamp=True,
                    check_signature=True,
                    max_age_in_days=90
                ),
                "requiredFor": ["STUDENT"]
            },
            DocumentType.TAX_RETURN: {
                "checkId": "tax_return",
                "docDescription": "Son yıla ait gelir vergisi beyannamesi",
                "docName": "Gelir Vergisi Beyannamesi",
                "ocrValidationRules": TaxReturnValidationRules(
                    enabled=True,
                    description="Tax return validation rules",
                    check_income_amount=True,
                    check_tax_office_stamp=True,
                    check_tax_year=True
                ),
                "requiredFor": ["EMPLOYEE"]
            },
            DocumentType.TRAVEL_INSURANCE: {
                "checkId": "travel_insurance",
                "docDescription": "Ülke makamlarının belirlediği asgari teminatı karşılayan seyahat sigortası poliçesi",
                "docName": "Seyahat Sağlık Sigortası",
                "ocrValidationRules": TravelInsuranceValidationRules(
                    enabled=True,
                    description="Travel insurance validation rules",
                    check_coverage_amount=True,
                    check_coverage_area=True,
                    check_validity_period=True
                ),
                "requiredFor": ["ALL"]
            }
        }
    
    def process_document_from_file(self, document_type: str, file_data: bytes, file_name: str = None) -> OCRResult:
        """
        Process document from file data with OCR extraction
        
        Args:
            document_type: Type of document to process
            file_data: Raw file bytes
            file_name: Original file name
            
        Returns:
            OCRResult with validation results
        """
        try:
            # Extract text using OCR
            extracted_text = self.document_processor.extract_text_from_image(file_data)
            
            if not extracted_text.strip():
                return OCRResult(
                    document_type=DocumentType(document_type),
                    confidence_score=0.0,
                    extracted_text="",
                    validation_results={},
                    issues=["No text could be extracted from the document"],
                    recommendations=["Ensure the document is clear and readable"],
                    metadata={"file_name": file_name, "extraction_failed": True}
                )
            
            # Enhance extracted text
            enhanced_text = self.document_processor.enhance_text_extraction(extracted_text, document_type)
            
            # Extract metadata
            metadata = self.document_processor.extract_document_metadata(file_data, file_name)
            
            # Validate image quality
            quality_validation = self.document_processor.validate_image_quality(file_data)
            metadata["quality_validation"] = quality_validation
            
            # Process document with validation rules
            return self.process_document(document_type, enhanced_text, metadata)
            
        except Exception as e:
            logger.error(f"Error processing document from file: {str(e)}")
            return OCRResult(
                document_type=DocumentType(document_type),
                confidence_score=0.0,
                extracted_text="",
                validation_results={},
                issues=[f"Processing error: {str(e)}"],
                recommendations=["Please check document quality and try again"],
                metadata={"error": str(e), "file_name": file_name}
            )
    
    def process_document(self, document_type: str, extracted_text: str, file_metadata: Dict[str, Any] = None) -> OCRResult:
        """
        Process document based on type and return validation results
        
        Args:
            document_type: Type of document to process
            extracted_text: Text extracted from OCR
            file_metadata: Additional file metadata
            
        Returns:
            OCRResult with validation results
        """
        try:
            doc_type = DocumentType(document_type)
            config = self.document_type_configs.get(doc_type)
            
            if not config:
                raise ValueError(f"Unsupported document type: {document_type}")
            
            # Process based on document type
            if doc_type == DocumentType.BANK_STATEMENT:
                return self._process_bank_statement(extracted_text, config, file_metadata)
            elif doc_type == DocumentType.PASSPORT:
                return self._process_passport(extracted_text, config, file_metadata)
            elif doc_type == DocumentType.BIOMETRIC_PHOTO:
                return self._process_biometric_photo(extracted_text, config, file_metadata)
            elif doc_type == DocumentType.BIRTH_CERTIFICATE:
                return self._process_birth_certificate(extracted_text, config, file_metadata)
            elif doc_type == DocumentType.BUSINESS_LETTER:
                return self._process_business_letter(extracted_text, config, file_metadata)
            elif doc_type == DocumentType.HOTEL_RESERVATION:
                return self._process_hotel_reservation(extracted_text, config, file_metadata)
            elif doc_type == DocumentType.INVITATION_LETTER:
                return self._process_invitation_letter(extracted_text, config, file_metadata)
            elif doc_type == DocumentType.PREVIOUS_VISAS:
                return self._process_previous_visas(extracted_text, config, file_metadata)
            elif doc_type == DocumentType.PROPERTY_DEED:
                return self._process_property_deed(extracted_text, config, file_metadata)
            elif doc_type == DocumentType.SOCIAL_SECURITY:
                return self._process_social_security(extracted_text, config, file_metadata)
            elif doc_type == DocumentType.STUDENT_CERTIFICATE:
                return self._process_student_certificate(extracted_text, config, file_metadata)
            elif doc_type == DocumentType.TAX_RETURN:
                return self._process_tax_return(extracted_text, config, file_metadata)
            elif doc_type == DocumentType.TRAVEL_INSURANCE:
                return self._process_travel_insurance(extracted_text, config, file_metadata)
            else:
                return self._process_generic_document(extracted_text, config, file_metadata)
                
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            return OCRResult(
                document_type=DocumentType(document_type),
                confidence_score=0.0,
                extracted_text=extracted_text,
                validation_results={},
                issues=[f"Processing error: {str(e)}"],
                recommendations=["Please check document quality and try again"],
                metadata={"error": str(e)}
            )
    
    def _process_bank_statement(self, text: str, config: Dict[str, Any], metadata: Dict[str, Any] = None) -> OCRResult:
        """Process bank statement with specific validation rules"""
        validation_rules = config["ocrValidationRules"]
        issues = []
        recommendations = []
        validation_results = {}
        
        # Extract key information
        account_info = self._extract_account_info(text)
        balance_info = self._extract_balance_info(text)
        period_info = self._extract_statement_period(text)
        bank_stamp_info = self._extract_bank_stamp(text)
        
        # Validate account balance
        if validation_rules.check_account_balance:
            balance_result = self._validate_account_balance(balance_info, validation_rules.min_balance_threshold)
            validation_results["account_balance"] = balance_result
            if not balance_result["valid"]:
                issues.extend(balance_result["issues"])
                recommendations.extend(balance_result["recommendations"])
        
        # Validate bank stamp
        if validation_rules.check_bank_stamp:
            stamp_result = self._validate_bank_stamp(bank_stamp_info)
            validation_results["bank_stamp"] = stamp_result
            if not stamp_result["valid"]:
                issues.extend(stamp_result["issues"])
                recommendations.extend(stamp_result["recommendations"])
        
        # Validate statement period
        if validation_rules.check_statement_period:
            period_result = self._validate_statement_period(period_info, validation_rules.min_months)
            validation_results["statement_period"] = period_result
            if not period_result["valid"]:
                issues.extend(period_result["issues"])
                recommendations.extend(period_result["recommendations"])
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(validation_results)
        
        return OCRResult(
            document_type=DocumentType.BANK_STATEMENT,
            confidence_score=confidence_score,
            extracted_text=text,
            validation_results=validation_results,
            issues=issues,
            recommendations=recommendations,
            metadata={
                "account_info": account_info,
                "balance_info": balance_info,
                "period_info": period_info,
                "bank_stamp_info": bank_stamp_info,
                "config": config
            }
        )
    
    def _process_passport(self, text: str, config: Dict[str, Any], metadata: Dict[str, Any] = None) -> OCRResult:
        """Process passport with specific validation rules"""
        validation_rules = config["ocrValidationRules"]
        issues = []
        recommendations = []
        validation_results = {}
        
        # Extract key information
        passport_info = self._extract_passport_info(text)
        expiry_info = self._extract_passport_dates(text)
        page_info = self._extract_passport_pages(text)
        
        # Validate expiry date
        if validation_rules.check_expiry_date:
            expiry_result = self._validate_passport_expiry(expiry_info, validation_rules.validity_months)
            validation_results["expiry_date"] = expiry_result
            if not expiry_result["valid"]:
                issues.extend(expiry_result["issues"])
                recommendations.extend(expiry_result["recommendations"])
        
        # Validate issuance date
        if validation_rules.check_issuance_date:
            issuance_result = self._validate_passport_issuance(expiry_info)
            validation_results["issuance_date"] = issuance_result
            if not issuance_result["valid"]:
                issues.extend(issuance_result["issues"])
                recommendations.extend(issuance_result["recommendations"])
        
        # Validate passport number
        if validation_rules.check_passport_number:
            number_result = self._validate_passport_number(passport_info)
            validation_results["passport_number"] = number_result
            if not number_result["valid"]:
                issues.extend(number_result["issues"])
                recommendations.extend(number_result["recommendations"])
        
        # Validate pages
        if validation_rules.min_pages > 0:
            pages_result = self._validate_passport_pages(page_info, validation_rules.min_pages)
            validation_results["pages"] = pages_result
            if not pages_result["valid"]:
                issues.extend(pages_result["issues"])
                recommendations.extend(pages_result["recommendations"])
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(validation_results)
        
        return OCRResult(
            document_type=DocumentType.PASSPORT,
            confidence_score=confidence_score,
            extracted_text=text,
            validation_results=validation_results,
            issues=issues,
            recommendations=recommendations,
            metadata={
                "passport_info": passport_info,
                "expiry_info": expiry_info,
                "page_info": page_info,
                "config": config
            }
        )
    
    def _process_biometric_photo(self, text: str, config: Dict[str, Any], metadata: Dict[str, Any] = None) -> OCRResult:
        """Process biometric photo with specific validation rules"""
        validation_rules = config["ocrValidationRules"]
        issues = []
        recommendations = []
        validation_results = {}
        
        # Extract key information
        photo_info = self._extract_photo_info(text, metadata)
        background_info = self._extract_background_info(text, metadata)
        face_info = self._extract_face_info(text, metadata)
        size_info = self._extract_photo_size_info(text, metadata)
        
        # Validate background color
        if validation_rules.check_background_color:
            background_result = self._validate_background_color(background_info)
            validation_results["background_color"] = background_result
            if not background_result["valid"]:
                issues.extend(background_result["issues"])
                recommendations.extend(background_result["recommendations"])
        
        # Validate face visibility
        if validation_rules.check_face_visible:
            face_result = self._validate_face_visibility(face_info)
            validation_results["face_visible"] = face_result
            if not face_result["valid"]:
                issues.extend(face_result["issues"])
                recommendations.extend(face_result["recommendations"])
        
        # Validate photo size
        if validation_rules.check_photo_size:
            size_result = self._validate_photo_size(size_info, validation_rules.required_width_mm, validation_rules.required_height_mm)
            validation_results["photo_size"] = size_result
            if not size_result["valid"]:
                issues.extend(size_result["issues"])
                recommendations.extend(size_result["recommendations"])
        
        # Validate recent photo
        if validation_rules.check_recent_photo:
            recent_result = self._validate_recent_photo(photo_info, validation_rules.max_photo_age_months)
            validation_results["recent_photo"] = recent_result
            if not recent_result["valid"]:
                issues.extend(recent_result["issues"])
                recommendations.extend(recent_result["recommendations"])
        
        # Validate face centering
        if validation_rules.check_face_centered:
            centered_result = self._validate_face_centering(face_info)
            validation_results["face_centered"] = centered_result
            if not centered_result["valid"]:
                issues.extend(centered_result["issues"])
                recommendations.extend(centered_result["recommendations"])
        
        # Validate neutral expression
        if validation_rules.check_neutral_expression:
            expression_result = self._validate_neutral_expression(face_info)
            validation_results["neutral_expression"] = expression_result
            if not expression_result["valid"]:
                issues.extend(expression_result["issues"])
                recommendations.extend(expression_result["recommendations"])
        
        # Validate eyes open
        if validation_rules.check_eyes_open:
            eyes_result = self._validate_eyes_open(face_info)
            validation_results["eyes_open"] = eyes_result
            if not eyes_result["valid"]:
                issues.extend(eyes_result["issues"])
                recommendations.extend(eyes_result["recommendations"])
        
        # Validate no glasses
        if validation_rules.check_no_glasses:
            glasses_result = self._validate_no_glasses(face_info)
            validation_results["no_glasses"] = glasses_result
            if not glasses_result["valid"]:
                issues.extend(glasses_result["issues"])
                recommendations.extend(glasses_result["recommendations"])
        
        # Validate no headwear
        if validation_rules.check_no_headwear:
            headwear_result = self._validate_no_headwear(face_info)
            validation_results["no_headwear"] = headwear_result
            if not headwear_result["valid"]:
                issues.extend(headwear_result["issues"])
                recommendations.extend(headwear_result["recommendations"])
        
        # Validate proper lighting
        if validation_rules.check_proper_lighting:
            lighting_result = self._validate_proper_lighting(photo_info)
            validation_results["proper_lighting"] = lighting_result
            if not lighting_result["valid"]:
                issues.extend(lighting_result["issues"])
                recommendations.extend(lighting_result["recommendations"])
        
        # Validate high resolution
        if validation_rules.check_high_resolution:
            resolution_result = self._validate_high_resolution(size_info, validation_rules.min_resolution_width, validation_rules.min_resolution_height)
            validation_results["high_resolution"] = resolution_result
            if not resolution_result["valid"]:
                issues.extend(resolution_result["issues"])
                recommendations.extend(resolution_result["recommendations"])
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(validation_results)
        
        return OCRResult(
            document_type=DocumentType.BIOMETRIC_PHOTO,
            confidence_score=confidence_score,
            extracted_text=text,
            validation_results=validation_results,
            issues=issues,
            recommendations=recommendations,
            metadata={
                "photo_info": photo_info,
                "background_info": background_info,
                "face_info": face_info,
                "size_info": size_info,
                "config": config
            }
        )
    
    def _process_birth_certificate(self, text: str, config: Dict[str, Any], metadata: Dict[str, Any] = None) -> OCRResult:
        """Process birth certificate with specific validation rules"""
        validation_rules = config["ocrValidationRules"]
        issues = []
        recommendations = []
        validation_results = {}
        
        # Extract key information
        birth_info = self._extract_birth_info(text)
        stamp_info = self._extract_birth_certificate_stamp(text)
        parents_info = self._extract_parents_info(text)
        
        # Validate birth date
        if validation_rules.check_birth_date:
            birth_date_result = self._validate_birth_date(birth_info)
            validation_results["birth_date"] = birth_date_result
            if not birth_date_result["valid"]:
                issues.extend(birth_date_result["issues"])
                recommendations.extend(birth_date_result["recommendations"])
        
        # Validate official stamp
        if validation_rules.check_official_stamp:
            stamp_result = self._validate_birth_certificate_stamp(stamp_info)
            validation_results["official_stamp"] = stamp_result
            if not stamp_result["valid"]:
                issues.extend(stamp_result["issues"])
                recommendations.extend(stamp_result["recommendations"])
        
        # Validate parents names
        if validation_rules.check_parents_names:
            parents_result = self._validate_parents_names(parents_info)
            validation_results["parents_names"] = parents_result
            if not parents_result["valid"]:
                issues.extend(parents_result["issues"])
                recommendations.extend(parents_result["recommendations"])
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(validation_results)
        
        return OCRResult(
            document_type=DocumentType.BIRTH_CERTIFICATE,
            confidence_score=confidence_score,
            extracted_text=text,
            validation_results=validation_results,
            issues=issues,
            recommendations=recommendations,
            metadata={
                "birth_info": birth_info,
                "stamp_info": stamp_info,
                "parents_info": parents_info,
                "config": config
            }
        )
    
    def _process_hotel_reservation(self, text: str, config: Dict[str, Any], metadata: Dict[str, Any] = None) -> OCRResult:
        """Process hotel reservation with specific validation rules"""
        validation_rules = config["ocrValidationRules"]
        issues = []
        recommendations = []
        validation_results = {}
        
        # Extract key information
        confirmation_info = self._extract_confirmation_info(text)
        dates_info = self._extract_reservation_dates(text)
        hotel_info = self._extract_hotel_info(text)
        payment_info = self._extract_payment_info(text)
        
        # Validate confirmation
        if validation_rules.check_confirmation:
            confirmation_result = self._validate_confirmation(confirmation_info)
            validation_results["confirmation"] = confirmation_result
            if not confirmation_result["valid"]:
                issues.extend(confirmation_result["issues"])
                recommendations.extend(confirmation_result["recommendations"])
        
        # Validate dates
        if validation_rules.check_dates:
            dates_result = self._validate_reservation_dates(dates_info)
            validation_results["dates"] = dates_result
            if not dates_result["valid"]:
                issues.extend(dates_result["issues"])
                recommendations.extend(dates_result["recommendations"])
        
        # Validate hotel reservation
        if validation_rules.check_hotel_reservation:
            hotel_result = self._validate_hotel_reservation(hotel_info)
            validation_results["hotel_reservation"] = hotel_result
            if not hotel_result["valid"]:
                issues.extend(hotel_result["issues"])
                recommendations.extend(hotel_result["recommendations"])
        
        # Validate payment proof
        if validation_rules.check_payment_proof:
            payment_result = self._validate_payment_proof(payment_info)
            validation_results["payment_proof"] = payment_result
            if not payment_result["valid"]:
                issues.extend(payment_result["issues"])
                recommendations.extend(payment_result["recommendations"])
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(validation_results)
        
        return OCRResult(
            document_type=DocumentType.HOTEL_RESERVATION,
            confidence_score=confidence_score,
            extracted_text=text,
            validation_results=validation_results,
            issues=issues,
            recommendations=recommendations,
            metadata={
                "confirmation_info": confirmation_info,
                "dates_info": dates_info,
                "hotel_info": hotel_info,
                "payment_info": payment_info,
                "config": config
            }
        )
    
    def _process_invitation_letter(self, text: str, config: Dict[str, Any], metadata: Dict[str, Any] = None) -> OCRResult:
        """Process invitation letter with specific validation rules"""
        validation_rules = config["ocrValidationRules"]
        issues = []
        recommendations = []
        validation_results = {}
        
        # Extract key information
        host_contact_info = self._extract_host_contact_info(text)
        host_info = self._extract_host_info(text)
        invitation_dates_info = self._extract_invitation_dates(text)
        signature_info = self._extract_signature_info(text)
        
        # Validate host contact
        if validation_rules.check_host_contact:
            host_contact_result = self._validate_host_contact(host_contact_info)
            validation_results["host_contact"] = host_contact_result
            if not host_contact_result["valid"]:
                issues.extend(host_contact_result["issues"])
                recommendations.extend(host_contact_result["recommendations"])
        
        # Validate host info
        if validation_rules.check_host_info:
            host_info_result = self._validate_host_info(host_info)
            validation_results["host_info"] = host_info_result
            if not host_info_result["valid"]:
                issues.extend(host_info_result["issues"])
                recommendations.extend(host_info_result["recommendations"])
        
        # Validate invitation dates
        if validation_rules.check_invitation_dates:
            invitation_dates_result = self._validate_invitation_dates(invitation_dates_info)
            validation_results["invitation_dates"] = invitation_dates_result
            if not invitation_dates_result["valid"]:
                issues.extend(invitation_dates_result["issues"])
                recommendations.extend(invitation_dates_result["recommendations"])
        
        # Validate signature
        if validation_rules.check_signature:
            signature_result = self._validate_signature(signature_info)
            validation_results["signature"] = signature_result
            if not signature_result["valid"]:
                issues.extend(signature_result["issues"])
                recommendations.extend(signature_result["recommendations"])
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(validation_results)
        
        return OCRResult(
            document_type=DocumentType.INVITATION_LETTER,
            confidence_score=confidence_score,
            extracted_text=text,
            validation_results=validation_results,
            issues=issues,
            recommendations=recommendations,
            metadata={
                "host_contact_info": host_contact_info,
                "host_info": host_info,
                "invitation_dates_info": invitation_dates_info,
                "signature_info": signature_info,
                "config": config
            }
        )
    
    def _process_previous_visas(self, text: str, config: Dict[str, Any], metadata: Dict[str, Any] = None) -> OCRResult:
        """Process previous visas with specific validation rules"""
        validation_rules = config["ocrValidationRules"]
        issues = []
        recommendations = []
        validation_results = {}
        
        # Extract key information
        visa_info = self._extract_visa_info(text)
        visa_country_info = self._extract_visa_country_info(text)
        visa_dates_info = self._extract_visa_dates(text)
        
        # Validate visa validity
        if validation_rules.check_validity:
            validity_result = self._validate_visa_validity(visa_info)
            validation_results["validity"] = validity_result
            if not validity_result["valid"]:
                issues.extend(validity_result["issues"])
                recommendations.extend(validity_result["recommendations"])
        
        # Validate visa country
        if validation_rules.check_visa_country:
            country_result = self._validate_visa_country(visa_country_info)
            validation_results["visa_country"] = country_result
            if not country_result["valid"]:
                issues.extend(country_result["issues"])
                recommendations.extend(country_result["recommendations"])
        
        # Validate visa dates
        if validation_rules.check_visa_dates:
            dates_result = self._validate_visa_dates(visa_dates_info)
            validation_results["visa_dates"] = dates_result
            if not dates_result["valid"]:
                issues.extend(dates_result["issues"])
                recommendations.extend(dates_result["recommendations"])
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(validation_results)
        
        return OCRResult(
            document_type=DocumentType.PREVIOUS_VISAS,
            confidence_score=confidence_score,
            extracted_text=text,
            validation_results=validation_results,
            issues=issues,
            recommendations=recommendations,
            metadata={
                "visa_info": visa_info,
                "visa_country_info": visa_country_info,
                "visa_dates_info": visa_dates_info,
                "config": config
            }
        )
    
    def _process_property_deed(self, text: str, config: Dict[str, Any], metadata: Dict[str, Any] = None) -> OCRResult:
        """Process property deed with specific validation rules"""
        validation_rules = config["ocrValidationRules"]
        issues = []
        recommendations = []
        validation_results = {}
        
        # Extract key information
        stamp_info = self._extract_property_deed_stamp(text)
        owner_info = self._extract_property_owner_info(text)
        value_info = self._extract_property_value_info(text)
        
        # Validate official stamp
        if validation_rules.check_official_stamp:
            stamp_result = self._validate_property_deed_stamp(stamp_info)
            validation_results["official_stamp"] = stamp_result
            if not stamp_result["valid"]:
                issues.extend(stamp_result["issues"])
                recommendations.extend(stamp_result["recommendations"])
        
        # Validate property owner
        if validation_rules.check_property_owner:
            owner_result = self._validate_property_owner(owner_info)
            validation_results["property_owner"] = owner_result
            if not owner_result["valid"]:
                issues.extend(owner_result["issues"])
                recommendations.extend(owner_result["recommendations"])
        
        # Validate property value
        if validation_rules.check_property_value:
            value_result = self._validate_property_value(value_info)
            validation_results["property_value"] = value_result
            if not value_result["valid"]:
                issues.extend(value_result["issues"])
                recommendations.extend(value_result["recommendations"])
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(validation_results)
        
        return OCRResult(
            document_type=DocumentType.PROPERTY_DEED,
            confidence_score=confidence_score,
            extracted_text=text,
            validation_results=validation_results,
            issues=issues,
            recommendations=recommendations,
            metadata={
                "stamp_info": stamp_info,
                "owner_info": owner_info,
                "value_info": value_info,
                "config": config
            }
        )
    
    def _process_social_security(self, text: str, config: Dict[str, Any], metadata: Dict[str, Any] = None) -> OCRResult:
        """Process social security document with specific validation rules"""
        validation_rules = config["ocrValidationRules"]
        issues = []
        recommendations = []
        validation_results = {}
        
        # Extract key information
        active_status_info = self._extract_active_status_info(text)
        registration_date_info = self._extract_registration_date_info(text)
        sgk_number_info = self._extract_sgk_number_info(text)
        
        # Validate active status
        if validation_rules.check_active_status:
            active_status_result = self._validate_active_status(active_status_info)
            validation_results["active_status"] = active_status_result
            if not active_status_result["valid"]:
                issues.extend(active_status_result["issues"])
                recommendations.extend(active_status_result["recommendations"])
        
        # Validate registration date
        if validation_rules.check_registration_date:
            registration_date_result = self._validate_registration_date(registration_date_info)
            validation_results["registration_date"] = registration_date_result
            if not registration_date_result["valid"]:
                issues.extend(registration_date_result["issues"])
                recommendations.extend(registration_date_result["recommendations"])
        
        # Validate SGK number
        if validation_rules.check_sgk_number:
            sgk_number_result = self._validate_sgk_number(sgk_number_info)
            validation_results["sgk_number"] = sgk_number_result
            if not sgk_number_result["valid"]:
                issues.extend(sgk_number_result["issues"])
                recommendations.extend(sgk_number_result["recommendations"])
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(validation_results)
        
        return OCRResult(
            document_type=DocumentType.SOCIAL_SECURITY,
            confidence_score=confidence_score,
            extracted_text=text,
            validation_results=validation_results,
            issues=issues,
            recommendations=recommendations,
            metadata={
                "active_status_info": active_status_info,
                "registration_date_info": registration_date_info,
                "sgk_number_info": sgk_number_info,
                "config": config
            }
        )
    
    def _process_student_certificate(self, text: str, config: Dict[str, Any], metadata: Dict[str, Any] = None) -> OCRResult:
        """Process student certificate with specific validation rules"""
        validation_rules = config["ocrValidationRules"]
        issues = []
        recommendations = []
        validation_results = {}
        
        # Extract key information
        issue_date_info = self._extract_student_certificate_issue_date(text)
        school_name_info = self._extract_school_name_info(text)
        school_stamp_info = self._extract_school_stamp_info(text)
        signature_info = self._extract_student_certificate_signature(text)
        
        # Validate issue date
        if validation_rules.check_issue_date:
            issue_date_result = self._validate_student_certificate_issue_date(issue_date_info, validation_rules.max_age_in_days)
            validation_results["issue_date"] = issue_date_result
            if not issue_date_result["valid"]:
                issues.extend(issue_date_result["issues"])
                recommendations.extend(issue_date_result["recommendations"])
        
        # Validate school name
        if validation_rules.check_school_name:
            school_name_result = self._validate_school_name(school_name_info)
            validation_results["school_name"] = school_name_result
            if not school_name_result["valid"]:
                issues.extend(school_name_result["issues"])
                recommendations.extend(school_name_result["recommendations"])
        
        # Validate school stamp
        if validation_rules.check_school_stamp:
            school_stamp_result = self._validate_school_stamp(school_stamp_info)
            validation_results["school_stamp"] = school_stamp_result
            if not school_stamp_result["valid"]:
                issues.extend(school_stamp_result["issues"])
                recommendations.extend(school_stamp_result["recommendations"])
        
        # Validate signature
        if validation_rules.check_signature:
            signature_result = self._validate_student_certificate_signature(signature_info)
            validation_results["signature"] = signature_result
            if not signature_result["valid"]:
                issues.extend(signature_result["issues"])
                recommendations.extend(signature_result["recommendations"])
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(validation_results)
        
        return OCRResult(
            document_type=DocumentType.STUDENT_CERTIFICATE,
            confidence_score=confidence_score,
            extracted_text=text,
            validation_results=validation_results,
            issues=issues,
            recommendations=recommendations,
            metadata={
                "issue_date_info": issue_date_info,
                "school_name_info": school_name_info,
                "school_stamp_info": school_stamp_info,
                "signature_info": signature_info,
                "config": config
            }
        )
    
    def _process_tax_return(self, text: str, config: Dict[str, Any], metadata: Dict[str, Any] = None) -> OCRResult:
        """Process tax return with specific validation rules"""
        validation_rules = config["ocrValidationRules"]
        issues = []
        recommendations = []
        validation_results = {}
        
        # Extract key information
        income_amount_info = self._extract_income_amount_info(text)
        tax_office_stamp_info = self._extract_tax_office_stamp_info(text)
        tax_year_info = self._extract_tax_year_info(text)
        
        # Validate income amount
        if validation_rules.check_income_amount:
            income_amount_result = self._validate_income_amount(income_amount_info)
            validation_results["income_amount"] = income_amount_result
            if not income_amount_result["valid"]:
                issues.extend(income_amount_result["issues"])
                recommendations.extend(income_amount_result["recommendations"])
        
        # Validate tax office stamp
        if validation_rules.check_tax_office_stamp:
            tax_office_stamp_result = self._validate_tax_office_stamp(tax_office_stamp_info)
            validation_results["tax_office_stamp"] = tax_office_stamp_result
            if not tax_office_stamp_result["valid"]:
                issues.extend(tax_office_stamp_result["issues"])
                recommendations.extend(tax_office_stamp_result["recommendations"])
        
        # Validate tax year
        if validation_rules.check_tax_year:
            tax_year_result = self._validate_tax_year(tax_year_info)
            validation_results["tax_year"] = tax_year_result
            if not tax_year_result["valid"]:
                issues.extend(tax_year_result["issues"])
                recommendations.extend(tax_year_result["recommendations"])
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(validation_results)
        
        return OCRResult(
            document_type=DocumentType.TAX_RETURN,
            confidence_score=confidence_score,
            extracted_text=text,
            validation_results=validation_results,
            issues=issues,
            recommendations=recommendations,
            metadata={
                "income_amount_info": income_amount_info,
                "tax_office_stamp_info": tax_office_stamp_info,
                "tax_year_info": tax_year_info,
                "config": config
            }
        )
    
    def _process_travel_insurance(self, text: str, config: Dict[str, Any], metadata: Dict[str, Any] = None) -> OCRResult:
        """Process travel insurance with specific validation rules"""
        validation_rules = config["ocrValidationRules"]
        issues = []
        recommendations = []
        validation_results = {}
        
        # Extract key information
        coverage_amount_info = self._extract_coverage_amount_info(text)
        coverage_area_info = self._extract_coverage_area_info(text)
        validity_period_info = self._extract_validity_period_info(text)
        
        # Validate coverage amount
        if validation_rules.check_coverage_amount:
            coverage_amount_result = self._validate_coverage_amount(coverage_amount_info)
            validation_results["coverage_amount"] = coverage_amount_result
            if not coverage_amount_result["valid"]:
                issues.extend(coverage_amount_result["issues"])
                recommendations.extend(coverage_amount_result["recommendations"])
        
        # Validate coverage area
        if validation_rules.check_coverage_area:
            coverage_area_result = self._validate_coverage_area(coverage_area_info)
            validation_results["coverage_area"] = coverage_area_result
            if not coverage_area_result["valid"]:
                issues.extend(coverage_area_result["issues"])
                recommendations.extend(coverage_area_result["recommendations"])
        
        # Validate validity period
        if validation_rules.check_validity_period:
            validity_period_result = self._validate_validity_period(validity_period_info)
            validation_results["validity_period"] = validity_period_result
            if not validity_period_result["valid"]:
                issues.extend(validity_period_result["issues"])
                recommendations.extend(validity_period_result["recommendations"])
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(validation_results)
        
        return OCRResult(
            document_type=DocumentType.TRAVEL_INSURANCE,
            confidence_score=confidence_score,
            extracted_text=text,
            validation_results=validation_results,
            issues=issues,
            recommendations=recommendations,
            metadata={
                "coverage_amount_info": coverage_amount_info,
                "coverage_area_info": coverage_area_info,
                "validity_period_info": validity_period_info,
                "config": config
            }
        )
    
    def _extract_account_info(self, text: str) -> Dict[str, Any]:
        """Extract account information from bank statement text"""
        account_info = {}
        
        # Account number patterns
        account_patterns = [
            r'hesap\s*no[:\s]*(\d+)',
            r'account\s*no[:\s]*(\d+)',
            r'hesap\s*numarası[:\s]*(\d+)',
            r'(\d{10,})',  # Generic 10+ digit number
        ]
        
        for pattern in account_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                account_info["account_number"] = match.group(1)
                break
        
        # Bank name patterns
        bank_patterns = [
            r'(ziraat|garanti|iş\s*bankası|akbank|yapı\s*kredi|halkbank|vakıfbank)',
            r'(türkiye\s*iş\s*bankası|türkiye\s*garanti\s*bankası)',
        ]
        
        for pattern in bank_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                account_info["bank_name"] = match.group(1).title()
                break
        
        return account_info
    
    def _extract_balance_info(self, text: str) -> Dict[str, Any]:
        """Extract balance information from bank statement text"""
        balance_info = {}
        
        # Balance patterns (Turkish and English)
        balance_patterns = [
            r'bakiye[:\s]*([\d.,]+)\s*(tl|try|₺|bb|ab)',
            r'balance[:\s]*([\d.,]+)\s*(tl|try|₺|bb|ab)',
            r'mevcut\s*bakiye[:\s]*([\d.,]+)\s*(tl|try|₺|bb|ab)',
            r'son\s*bakiye[:\s]*([\d.,]+)\s*(tl|try|₺|bb|ab)',
            r'([\d.,]+)\s*(tl|try|₺|bb|ab)',  # Generic amount with currency
            r'(\d{1,3}(?:\.\d{3})*,\d{2})\s*(bb|ab)',  # Turkish format: 53.989,75 BB
        ]
        
        balances = []
        for pattern in balance_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    amount_str = match[0]
                    # Handle Turkish number format (e.g., "53.989,75")
                    if '.' in amount_str and ',' in amount_str:
                        # Turkish format: thousands separator is dot, decimal is comma
                        amount_str = amount_str.replace('.', '').replace(',', '.')
                    else:
                        # English format: thousands separator is comma, decimal is dot
                        amount_str = amount_str.replace(',', '')
                    
                    amount = float(amount_str)
                    currency = match[1].upper()
                    balances.append({"amount": amount, "currency": currency})
                except ValueError:
                    continue
        
        if balances:
            # Get the highest balance (likely current balance)
            balance_info["balances"] = balances
            balance_info["current_balance"] = max(balances, key=lambda x: x["amount"])
        
        return balance_info
    
    def _extract_statement_period(self, text: str) -> Dict[str, Any]:
        """Extract statement period from bank statement text"""
        period_info = {}
        
        # Date patterns
        date_patterns = [
            r'(\d{1,2})[./](\d{1,2})[./](\d{4})',  # DD/MM/YYYY or DD.MM.YYYY
            r'(\d{4})[./](\d{1,2})[./](\d{1,2})',  # YYYY/MM/DD or YYYY.MM.DD
            r'(\d{1,2})\s+(ocak|şubat|mart|nisan|mayıs|haziran|temmuz|ağustos|eylül|ekim|kasım|aralık)\s+(\d{4})',
        ]
        
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    if len(match) == 3:
                        if match[1].isdigit():  # DD/MM/YYYY format
                            day, month, year = match
                        else:  # Month name format
                            day, month_name, year = match
                            month_names = {
                                'ocak': '01', 'şubat': '02', 'mart': '03', 'nisan': '04',
                                'mayıs': '05', 'haziran': '06', 'temmuz': '07', 'ağustos': '08',
                                'eylül': '09', 'ekim': '10', 'kasım': '11', 'aralık': '12'
                            }
                            month = month_names.get(month_name.lower(), '01')
                        
                        date_str = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                        dates.append(datetime.strptime(date_str, "%Y-%m-%d"))
                except ValueError:
                    continue
        
        if dates:
            period_info["dates"] = dates
            period_info["start_date"] = min(dates)
            period_info["end_date"] = max(dates)
            period_info["duration_days"] = (max(dates) - min(dates)).days
        
        return period_info
    
    def _extract_bank_stamp(self, text: str) -> Dict[str, Any]:
        """Extract bank stamp/seal information"""
        stamp_info = {}
        
        # Stamp patterns
        stamp_patterns = [
            r'(mühür|mühürlü|kaşeli)',
            r'(stamp|sealed)',
            r'(resmi\s*mühür|official\s*stamp)',
            r'(bank\s*stamp|banka\s*mühürü)',
        ]
        
        for pattern in stamp_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                stamp_info["has_stamp"] = True
                stamp_info["stamp_text"] = match.group(1)
                break
        
        if not stamp_info:
            stamp_info["has_stamp"] = False
        
        return stamp_info
    
    def _extract_passport_info(self, text: str) -> Dict[str, Any]:
        """Extract passport information from text"""
        passport_info = {}
        
        # Passport number patterns
        passport_patterns = [
            r'pasaport\s*no[:\s]*([A-Z0-9]+)',
            r'passport\s*no[:\s]*([A-Z0-9]+)',
            r'pasaport\s*numarası[:\s]*([A-Z0-9]+)',
            r'([A-Z]\d{8,})',  # Generic passport number pattern
        ]
        
        for pattern in passport_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                passport_info["passport_number"] = match.group(1)
                break
        
        # Country code patterns
        country_patterns = [
            r'ülke\s*kodu[:\s]*([A-Z]{3})',
            r'country\s*code[:\s]*([A-Z]{3})',
            r'([A-Z]{3})',  # Generic 3-letter country code
        ]
        
        for pattern in country_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                passport_info["country_code"] = match.group(1)
                break
        
        # Passport type
        type_patterns = [
            r'türü[:\s]*([A-Z])',
            r'type[:\s]*([A-Z])',
        ]
        
        for pattern in type_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                passport_info["passport_type"] = match.group(1)
                break
        
        return passport_info
    
    def _extract_passport_dates(self, text: str) -> Dict[str, Any]:
        """Extract passport dates from text"""
        date_info = {}
        
        # Date patterns for Turkish and English
        date_patterns = [
            r'(\d{1,2})[./](\d{1,2})[./](\d{4})',  # DD/MM/YYYY
            r'(\d{4})[./](\d{1,2})[./](\d{1,2})',  # YYYY/MM/DD
            r'(\d{1,2})\s+(ocak|şubat|mart|nisan|mayıs|haziran|temmuz|ağustos|eylül|ekim|kasım|aralık)\s+(\d{4})',
            r'(\d{1,2})\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+(\d{4})',
            r'(\d{1,2})\s+(oca|şub|mar|nis|may|haz|tem|ağu|eyl|eki|kas|ara)\s+(\d{4})',  # Turkish abbreviated months
            r'(\d{1,2})\s+(haz|jun)\s+(\d{4})',  # Special case for HAZ/JUN
            r'(\d{1,2})\s+(oca|jan)\s+(\d{4})',  # Special case for OCA/JAN
            r'(\d{1,2})\s+(haz|jun)\s+/\s+(jun)\s+(\d{4})',  # HAZ / JUN format
            r'(\d{1,2})\s+(oca|jan)\s+/\s+(jan)\s+(\d{4})',  # OCA / JAN format
        ]
        
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    if len(match) == 3:
                        if match[1].isdigit():  # DD/MM/YYYY format
                            day, month, year = match
                        else:  # Month name format
                            day, month_name, year = match
                            month_names = {
                                'ocak': '01', 'şubat': '02', 'mart': '03', 'nisan': '04',
                                'mayıs': '05', 'haziran': '06', 'temmuz': '07', 'ağustos': '08',
                                'eylül': '09', 'ekim': '10', 'kasım': '11', 'aralık': '12',
                                'oca': '01', 'şub': '02', 'mar': '03', 'nis': '04',
                                'may': '05', 'haz': '06', 'tem': '07', 'ağu': '08',
                                'eyl': '09', 'eki': '10', 'kas': '11', 'ara': '12',
                                'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
                                'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
                                'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
                            }
                            month = month_names.get(month_name.lower(), '01')
                        
                        date_str = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                        dates.append(datetime.strptime(date_str, "%Y-%m-%d"))
                    elif len(match) == 4:  # HAZ / JUN format
                        day, month_name1, month_name2, year = match
                        month_names = {
                            'ocak': '01', 'şubat': '02', 'mart': '03', 'nisan': '04',
                            'mayıs': '05', 'haziran': '06', 'temmuz': '07', 'ağustos': '08',
                            'eylül': '09', 'ekim': '10', 'kasım': '11', 'aralık': '12',
                            'oca': '01', 'şub': '02', 'mar': '03', 'nis': '04',
                            'may': '05', 'haz': '06', 'tem': '07', 'ağu': '08',
                            'eyl': '09', 'eki': '10', 'kas': '11', 'ara': '12',
                            'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
                            'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
                            'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
                        }
                        # Use the first month name (Turkish)
                        month = month_names.get(month_name1.lower(), '01')
                        date_str = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                        dates.append(datetime.strptime(date_str, "%Y-%m-%d"))
                except ValueError:
                    continue
        
        if dates:
            date_info["dates"] = dates
            
            # Try to identify issuance and expiry dates
            # Filter out birth dates (usually much older than issuance dates)
            current_year = datetime.now().year
            recent_dates = [d for d in dates if d.year >= current_year - 15]  # Last 15 years
            
            if recent_dates:
                sorted_dates = sorted(recent_dates)
                if len(sorted_dates) >= 2:
                    date_info["issuance_date"] = sorted_dates[0]
                    date_info["expiry_date"] = sorted_dates[-1]
                elif len(sorted_dates) == 1:
                    # If only one recent date, assume it's expiry date
                    date_info["expiry_date"] = sorted_dates[0]
            else:
                # Fallback to original logic if no recent dates found
                sorted_dates = sorted(dates)
                if len(sorted_dates) >= 2:
                    date_info["issuance_date"] = sorted_dates[0]
                    date_info["expiry_date"] = sorted_dates[-1]
                elif len(sorted_dates) == 1:
                    date_info["expiry_date"] = sorted_dates[0]
        
        return date_info
    
    def _extract_passport_pages(self, text: str) -> Dict[str, Any]:
        """Extract passport page information from text"""
        page_info = {}
        
        # Page patterns
        page_patterns = [
            r'sayfa[:\s]*(\d+)',
            r'page[:\s]*(\d+)',
            r'(\d+)\s*sayfa',
            r'(\d+)\s*page',
        ]
        
        pages = []
        for pattern in page_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    page_num = int(match)
                    if 1 <= page_num <= 50:  # Reasonable page range
                        pages.append(page_num)
                except ValueError:
                    continue
        
        if pages:
            page_info["pages"] = pages
            page_info["total_pages"] = max(pages)
            page_info["min_page"] = min(pages)
        
        return page_info
    
    def _validate_passport_expiry(self, expiry_info: Dict[str, Any], validity_months: int) -> Dict[str, Any]:
        """Validate passport expiry date"""
        result = {
            "valid": False,
            "issues": [],
            "recommendations": [],
            "details": expiry_info
        }
        
        if not expiry_info.get("expiry_date"):
            result["issues"].append("Passport expiry date not found")
            result["recommendations"].append("Ensure the document contains clear expiry date information")
            return result
        
        expiry_date = expiry_info["expiry_date"]
        current_date = datetime.now()
        
        # Calculate months until expiry
        months_until_expiry = (expiry_date.year - current_date.year) * 12 + (expiry_date.month - current_date.month)
        
        if expiry_date < current_date:
            result["issues"].append("Passport has expired")
            result["recommendations"].append("Obtain a new passport before applying for visa")
        elif months_until_expiry < validity_months:
            result["issues"].append(f"Passport expires in {months_until_expiry} months, less than required {validity_months} months")
            result["recommendations"].append(f"Ensure passport is valid for at least {validity_months} months from visa application date")
        else:
            result["valid"] = True
            result["recommendations"].append(f"Passport is valid for {months_until_expiry} months, meets requirements")
        
        return result
    
    def _validate_passport_issuance(self, expiry_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate passport issuance date"""
        result = {
            "valid": False,
            "issues": [],
            "recommendations": [],
            "details": expiry_info
        }
        
        if not expiry_info.get("issuance_date"):
            result["issues"].append("Passport issuance date not found")
            result["recommendations"].append("Ensure the document contains clear issuance date information")
            return result
        
        issuance_date = expiry_info["issuance_date"]
        current_date = datetime.now()
        
        # Check if passport was issued within last 10 years
        years_since_issuance = (current_date.year - issuance_date.year)
        
        if issuance_date > current_date:
            result["issues"].append("Passport issuance date is in the future")
            result["recommendations"].append("Check passport issuance date")
        elif years_since_issuance > 10:
            result["issues"].append(f"Passport was issued {years_since_issuance} years ago, exceeds 10-year limit")
            result["recommendations"].append("Obtain a new passport issued within the last 10 years")
        else:
            result["valid"] = True
            result["recommendations"].append(f"Passport was issued {years_since_issuance} years ago, meets requirements")
        
        return result
    
    def _validate_passport_number(self, passport_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate passport number format"""
        result = {
            "valid": False,
            "issues": [],
            "recommendations": [],
            "details": passport_info
        }
        
        if not passport_info.get("passport_number"):
            result["issues"].append("Passport number not found")
            result["recommendations"].append("Ensure the document contains clear passport number")
            return result
        
        passport_number = passport_info["passport_number"]
        
        # Basic validation - passport numbers are usually 8-10 characters
        if len(passport_number) < 6 or len(passport_number) > 12:
            result["issues"].append(f"Passport number '{passport_number}' has invalid length")
            result["recommendations"].append("Ensure passport number is clearly visible and readable")
        else:
            result["valid"] = True
            result["recommendations"].append("Passport number format appears valid")
        
        return result
    
    def _validate_passport_pages(self, page_info: Dict[str, Any], min_pages: int) -> Dict[str, Any]:
        """Validate passport has minimum required pages"""
        result = {
            "valid": False,
            "issues": [],
            "recommendations": [],
            "details": page_info
        }
        
        if not page_info.get("total_pages"):
            result["issues"].append("Passport page information not found")
            result["recommendations"].append("Ensure the document shows passport page information")
            return result
        
        total_pages = page_info["total_pages"]
        
        if total_pages < min_pages:
            result["issues"].append(f"Passport has {total_pages} pages, less than required {min_pages} pages")
            result["recommendations"].append(f"Ensure passport has at least {min_pages} blank pages")
        else:
            result["valid"] = True
            result["recommendations"].append(f"Passport has {total_pages} pages, meets requirements")
        
        return result
    
    def _validate_face_centering(self, face_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate face is centered in the photo"""
        result = {
            "valid": False,
            "issues": [],
            "recommendations": [],
            "details": face_info
        }
        
        face_position = face_info.get("face_position", {})
        face_centered = face_position.get("centered", True)  # Mock value
        
        if face_centered:
            result["valid"] = True
            result["recommendations"].append("Face is properly centered in the photo")
        else:
            result["issues"].append("Face is not centered in the photo")
            result["recommendations"].append("Ensure face is centered horizontally and vertically")
        
        return result
    
    def _validate_neutral_expression(self, face_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate neutral facial expression"""
        result = {
            "valid": False,
            "issues": [],
            "recommendations": [],
            "details": face_info
        }
        
        expression = face_info.get("expression", "neutral")  # Mock value
        
        if expression == "neutral":
            result["valid"] = True
            result["recommendations"].append("Facial expression is neutral, meets requirements")
        else:
            result["issues"].append(f"Facial expression is {expression}, should be neutral")
            result["recommendations"].append("Maintain a neutral expression with mouth closed")
        
        return result
    
    def _validate_eyes_open(self, face_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate eyes are open and looking at camera"""
        result = {
            "valid": False,
            "issues": [],
            "recommendations": [],
            "details": face_info
        }
        
        eyes_open = face_info.get("eyes_open", True)  # Mock value
        looking_at_camera = face_info.get("looking_at_camera", True)  # Mock value
        
        if eyes_open and looking_at_camera:
            result["valid"] = True
            result["recommendations"].append("Eyes are open and looking directly at camera")
        else:
            if not eyes_open:
                result["issues"].append("Eyes appear to be closed")
            if not looking_at_camera:
                result["issues"].append("Not looking directly at camera")
            result["recommendations"].append("Ensure eyes are open and looking directly at the camera")
        
        return result
    
    def _validate_no_glasses(self, face_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate no glasses are worn"""
        result = {
            "valid": False,
            "issues": [],
            "recommendations": [],
            "details": face_info
        }
        
        has_glasses = face_info.get("has_glasses", False)  # Mock value
        
        if not has_glasses:
            result["valid"] = True
            result["recommendations"].append("No glasses detected, meets requirements")
        else:
            result["issues"].append("Glasses detected in photo")
            result["recommendations"].append("Remove glasses for biometric photo")
        
        return result
    
    def _validate_no_headwear(self, face_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate no headwear is worn"""
        result = {
            "valid": False,
            "issues": [],
            "recommendations": [],
            "details": face_info
        }
        
        has_headwear = face_info.get("has_headwear", False)  # Mock value
        
        if not has_headwear:
            result["valid"] = True
            result["recommendations"].append("No headwear detected, meets requirements")
        else:
            result["issues"].append("Headwear detected in photo")
            result["recommendations"].append("Remove all headwear including hats, caps, and religious head coverings")
        
        return result
    
    def _validate_proper_lighting(self, photo_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate proper lighting conditions"""
        result = {
            "valid": False,
            "issues": [],
            "recommendations": [],
            "details": photo_info
        }
        
        lighting_quality = photo_info.get("lighting_quality", "good")  # Mock value
        has_shadows = photo_info.get("has_shadows", False)  # Mock value
        
        if lighting_quality == "good" and not has_shadows:
            result["valid"] = True
            result["recommendations"].append("Lighting is adequate with no shadows on face")
        else:
            if lighting_quality != "good":
                result["issues"].append("Poor lighting conditions detected")
            if has_shadows:
                result["issues"].append("Shadows detected on face")
            result["recommendations"].append("Ensure even lighting with no shadows on face")
        
        return result
    
    def _validate_high_resolution(self, size_info: Dict[str, Any], min_width: int, min_height: int) -> Dict[str, Any]:
        """Validate photo has sufficient resolution"""
        result = {
            "valid": False,
            "issues": [],
            "recommendations": [],
            "details": size_info
        }
        
        width_px = size_info.get("width_px", 0)
        height_px = size_info.get("height_px", 0)
        
        if width_px >= min_width and height_px >= min_height:
            result["valid"] = True
            result["recommendations"].append(f"Photo resolution ({width_px}x{height_px}) meets minimum requirements")
        else:
            result["issues"].append(f"Photo resolution ({width_px}x{height_px}) below minimum ({min_width}x{min_height})")
            result["recommendations"].append(f"Ensure photo resolution is at least {min_width}x{min_height} pixels")
        
        return result
    
    def _extract_photo_info(self, text: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Extract photo information"""
        photo_info = {}
        
        # Extract from metadata if available
        if metadata:
            photo_info["file_name"] = metadata.get("file_name")
            photo_info["image_dimensions"] = metadata.get("image_dimensions", {})
            photo_info["quality_score"] = metadata.get("image_quality_score", 0)
        
        return photo_info
    
    def _extract_background_info(self, text: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Extract background color information"""
        background_info = {}
        
        # Extract from metadata if available
        if metadata:
            background_info["background_color"] = metadata.get("background_color", "white")
            background_info["background_analysis"] = metadata.get("background_analysis", {})
        
        # Default to white background if not specified
        if not background_info.get("background_color"):
            background_info["background_color"] = "white"
        
        return background_info
    
    def _extract_face_info(self, text: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Extract face detection information"""
        face_info = {}
        
        # Extract from metadata if available
        if metadata:
            face_info["face_detected"] = metadata.get("face_detected", True)
            face_info["face_analysis"] = metadata.get("face_analysis", {})
        
        # Default to face detected if not specified
        if "face_detected" not in face_info:
            face_info["face_detected"] = True
        
        return face_info
    
    def _extract_photo_size_info(self, text: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Extract photo size information"""
        size_info = {}
        
        # Extract from metadata if available
        if metadata:
            size_info["width_px"] = metadata.get("image_dimensions", {}).get("width", 0)
            size_info["height_px"] = metadata.get("image_dimensions", {}).get("height", 0)
        
        return size_info
    
    def _validate_background_color(self, background_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate background color is white"""
        result = {
            "valid": False,
            "issues": [],
            "recommendations": [],
            "details": background_info
        }
        
        background_color = background_info.get("background_color", "").lower()
        
        if background_color in ["white", "beyaz"]:
            result["valid"] = True
            result["recommendations"].append("Background color is white, meets requirements")
        else:
            result["issues"].append(f"Background color is {background_color}, should be white")
            result["recommendations"].append("Ensure the background is white (plain white background)")
        
        return result
    
    def _validate_face_visibility(self, face_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate face is visible and clear"""
        result = {
            "valid": False,
            "issues": [],
            "recommendations": [],
            "details": face_info
        }
        
        face_detected = face_info.get("face_detected", False)
        
        if face_detected:
            result["valid"] = True
            result["recommendations"].append("Face is clearly visible and detected")
        else:
            result["issues"].append("Face not clearly visible or detected")
            result["recommendations"].append("Ensure face is clearly visible, eyes are open, and there are no shadows")
        
        return result
    
    def _validate_photo_size(self, size_info: Dict[str, Any], required_width_mm: int, required_height_mm: int) -> Dict[str, Any]:
        """Validate photo size meets requirements"""
        result = {
            "valid": False,
            "issues": [],
            "recommendations": [],
            "details": size_info
        }
        
        width_px = size_info.get("width_px", 0)
        height_px = size_info.get("height_px", 0)
        
        if width_px == 0 or height_px == 0:
            result["issues"].append("Photo dimensions not available")
            result["recommendations"].append("Ensure photo dimensions are clearly visible")
            return result
        
        # Convert mm to pixels (assuming 300 DPI for biometric photos)
        # 1 inch = 25.4 mm, 300 DPI = 300 pixels per inch
        # 35 mm = 35 / 25.4 * 300 = ~413 pixels
        # 45 mm = 45 / 25.4 * 300 = ~531 pixels
        required_width_px = int(required_width_mm / 25.4 * 300)
        required_height_px = int(required_height_mm / 25.4 * 300)
        
        # Allow 5% tolerance
        width_tolerance = required_width_px * 0.05
        height_tolerance = required_height_px * 0.05
        
        width_valid = abs(width_px - required_width_px) <= width_tolerance
        height_valid = abs(height_px - required_height_px) <= height_tolerance
        
        if width_valid and height_valid:
            result["valid"] = True
            result["recommendations"].append(f"Photo size ({width_px}x{height_px}px) meets requirements ({required_width_mm}x{required_height_mm}mm)")
        else:
            if not width_valid:
                result["issues"].append(f"Photo width ({width_px}px) does not meet requirement ({required_width_mm}mm)")
            if not height_valid:
                result["issues"].append(f"Photo height ({height_px}px) does not meet requirement ({required_height_mm}mm)")
            result["recommendations"].append(f"Ensure photo size is {required_width_mm}x{required_height_mm}mm (35x45mm)")
        
        return result
    
    def _validate_recent_photo(self, photo_info: Dict[str, Any], max_age_months: int) -> Dict[str, Any]:
        """Validate photo is recent (within last 6 months)"""
        result = {
            "valid": False,
            "issues": [],
            "recommendations": [],
            "details": photo_info
        }
        
        # For now, assume photo is recent if no date information is available
        # In production, this would check EXIF data or other metadata
        result["valid"] = True
        result["recommendations"].append(f"Photo appears to be recent (within last {max_age_months} months)")
        
        return result
    
    def _extract_birth_info(self, text: str) -> Dict[str, Any]:
        """Extract birth information from birth certificate text"""
        birth_info = {}
        
        # Birth date patterns
        date_patterns = [
            r'doğum\s*tarihi[:\s]*(\d{1,2})[./](\d{1,2})[./](\d{4})',
            r'doğum\s*tarihi[:\s]*(\d{1,2})\s+(ocak|şubat|mart|nisan|mayıs|haziran|temmuz|ağustos|eylül|ekim|kasım|aralık)\s+(\d{4})',
            r'birth\s*date[:\s]*(\d{1,2})[./](\d{1,2})[./](\d{4})',
            r'yıl[:\s]*(\d{4})',
            r'ay[:\s]*(ocak|şubat|mart|nisan|mayıs|haziran|temmuz|ağustos|eylül|ekim|kasım|aralık)',
            r'gün[:\s]*(\d{1,2})',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                birth_info["date_found"] = True
                birth_info["date_text"] = match.group(0)
                break
        
        # Birth place patterns
        place_patterns = [
            r'doğum\s*yeri[:\s]*([A-ZÇĞİÖŞÜ\s]+)',
            r'place\s*of\s*birth[:\s]*([A-Z\s]+)',
        ]
        
        for pattern in place_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                birth_info["place"] = match.group(1).strip()
                break
        
        return birth_info
    
    def _extract_birth_certificate_stamp(self, text: str) -> Dict[str, Any]:
        """Extract stamp information from birth certificate text"""
        stamp_info = {}
        
        # Stamp patterns
        stamp_patterns = [
            r'(mühür|mühürlü|kaşeli)',
            r'(stamp|sealed|official\s*stamp)',
            r'(yeminli\s*tercüme|certified\s*translation)',
            r'(resmi\s*mühür|official\s*seal)',
        ]
        
        for pattern in stamp_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                stamp_info["has_stamp"] = True
                stamp_info["stamp_text"] = match.group(1)
                break
        
        if not stamp_info:
            stamp_info["has_stamp"] = False
        
        return stamp_info
    
    def _extract_parents_info(self, text: str) -> Dict[str, Any]:
        """Extract parents information from birth certificate text"""
        parents_info = {}
        
        # Father patterns
        father_patterns = [
            r'baba[:\s]*soyadı[:\s]*([A-ZÇĞİÖŞÜ]+)',
            r'father[:\s]*surname[:\s]*([A-Z]+)',
            r'baba[:\s]*([A-ZÇĞİÖŞÜ]+)',
        ]
        
        for pattern in father_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                parents_info["father_surname"] = match.group(1)
                break
        
        # Mother patterns
        mother_patterns = [
            r'anne[:\s]*soyadı[:\s]*([A-ZÇĞİÖŞÜ]+)',
            r'mother[:\s]*surname[:\s]*([A-Z]+)',
            r'anne[:\s]*([A-ZÇĞİÖŞÜ]+)',
        ]
        
        for pattern in mother_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                parents_info["mother_surname"] = match.group(1)
                break
        
        return parents_info
    
    def _validate_birth_date(self, birth_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate birth date is present"""
        result = {
            "valid": False,
            "issues": [],
            "recommendations": [],
            "details": birth_info
        }
        
        if birth_info.get("date_found"):
            result["valid"] = True
            result["recommendations"].append("Birth date found and validated")
        else:
            result["issues"].append("Birth date not found in document")
            result["recommendations"].append("Ensure the document contains clear birth date information")
        
        return result
    
    def _validate_birth_certificate_stamp(self, stamp_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate official stamp presence"""
        result = {
            "valid": False,
            "issues": [],
            "recommendations": [],
            "details": stamp_info
        }
        
        if stamp_info.get("has_stamp"):
            result["valid"] = True
            result["recommendations"].append("Official stamp or seal detected")
        else:
            result["issues"].append("Official stamp or seal not detected")
            result["recommendations"].append("Ensure the document has an official stamp or seal")
        
        return result
    
    def _validate_parents_names(self, parents_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate parents names are present"""
        result = {
            "valid": False,
            "issues": [],
            "recommendations": [],
            "details": parents_info
        }
        
        has_father = bool(parents_info.get("father_surname"))
        has_mother = bool(parents_info.get("mother_surname"))
        
        if has_father and has_mother:
            result["valid"] = True
            result["recommendations"].append("Both parents' names found and validated")
        elif has_father or has_mother:
            result["issues"].append("Only one parent's name found")
            result["recommendations"].append("Ensure both parents' names are clearly visible")
        else:
            result["issues"].append("Parents' names not found in document")
            result["recommendations"].append("Ensure the document contains clear parents' names")
        
        return result
    
    def _extract_confirmation_info(self, text: str) -> Dict[str, Any]:
        """Extract confirmation information from hotel reservation text"""
        confirmation_info = {}
        
        # Confirmation patterns
        confirmation_patterns = [
            r'(onay|confirmation|confirmed|rezervasyon\s*onayı)',
            r'(booking\s*confirmed|reservation\s*confirmed)',
            r'(rezervasyon\s*numarası|booking\s*number)',
            r'(confirmation\s*number)',
        ]
        
        for pattern in confirmation_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                confirmation_info["has_confirmation"] = True
                confirmation_info["confirmation_text"] = match.group(1)
                break
        
        if not confirmation_info:
            confirmation_info["has_confirmation"] = False
        
        return confirmation_info
    
    def _extract_reservation_dates(self, text: str) -> Dict[str, Any]:
        """Extract reservation dates from hotel reservation text"""
        dates_info = {}
        
        # Date patterns
        date_patterns = [
            r'(\d{1,2})[./](\d{1,2})[./](\d{4})',  # DD/MM/YYYY
            r'(\d{4})[./](\d{1,2})[./](\d{1,2})',  # YYYY/MM/DD
            r'(check-in|check-out|giriş|çıkış)',
            r'(arrival|departure|varış|ayrılış)',
        ]
        
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match) == 3 and match[0].isdigit():
                    try:
                        day, month, year = match
                        date_str = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                        dates.append(datetime.strptime(date_str, "%Y-%m-%d"))
                    except ValueError:
                        continue
        
        if dates:
            dates_info["dates"] = dates
            dates_info["check_in"] = min(dates) if dates else None
            dates_info["check_out"] = max(dates) if dates else None
        
        return dates_info
    
    def _extract_hotel_info(self, text: str) -> Dict[str, Any]:
        """Extract hotel information from hotel reservation text"""
        hotel_info = {}
        
        # Hotel name patterns
        hotel_patterns = [
            r'(otel|hotel|konaklama|accommodation)',
            r'(resort|motel|hostel|pansiyon)',
        ]
        
        for pattern in hotel_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                hotel_info["has_hotel"] = True
                hotel_info["hotel_text"] = match.group(1)
                break
        
        if not hotel_info:
            hotel_info["has_hotel"] = False
        
        return hotel_info
    
    def _extract_payment_info(self, text: str) -> Dict[str, Any]:
        """Extract payment information from hotel reservation text"""
        payment_info = {}
        
        # Payment patterns
        payment_patterns = [
            r'(ödeme|payment|paid|ücret|fee)',
            r'(credit\s*card|debit\s*card|kredi\s*kartı)',
            r'(total|toplam|amount|miktar)',
        ]
        
        for pattern in payment_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                payment_info["has_payment"] = True
                payment_info["payment_text"] = match.group(1)
                break
        
        if not payment_info:
            payment_info["has_payment"] = False
        
        return payment_info
    
    def _validate_confirmation(self, confirmation_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate confirmation is present"""
        result = {
            "valid": False,
            "issues": [],
            "recommendations": [],
            "details": confirmation_info
        }
        
        if confirmation_info.get("has_confirmation"):
            result["valid"] = True
            result["recommendations"].append("Reservation confirmation found")
        else:
            result["issues"].append("Reservation confirmation not found")
            result["recommendations"].append("Ensure the document contains confirmation details")
        
        return result
    
    def _validate_reservation_dates(self, dates_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate reservation dates are present"""
        result = {
            "valid": False,
            "issues": [],
            "recommendations": [],
            "details": dates_info
        }
        
        if dates_info.get("dates"):
            result["valid"] = True
            result["recommendations"].append("Reservation dates found and validated")
        else:
            result["issues"].append("Reservation dates not found")
            result["recommendations"].append("Ensure the document contains check-in and check-out dates")
        
        return result
    
    def _validate_hotel_reservation(self, hotel_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate hotel reservation details are present"""
        result = {
            "valid": False,
            "issues": [],
            "recommendations": [],
            "details": hotel_info
        }
        
        if hotel_info.get("has_hotel"):
            result["valid"] = True
            result["recommendations"].append("Hotel reservation details found")
        else:
            result["issues"].append("Hotel reservation details not found")
            result["recommendations"].append("Ensure the document contains hotel or accommodation details")
        
        return result
    
    def _validate_payment_proof(self, payment_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate payment proof is present"""
        result = {
            "valid": False,
            "issues": [],
            "recommendations": [],
            "details": payment_info
        }
        
        if payment_info.get("has_payment"):
            result["valid"] = True
            result["recommendations"].append("Payment proof found")
        else:
            result["issues"].append("Payment proof not found")
            result["recommendations"].append("Ensure the document contains payment or fee information")
        
        return result
    
    def _extract_host_contact_info(self, text: str) -> Dict[str, Any]:
        """Extract host contact information from invitation letter text"""
        contact_info = {}
        
        # Contact patterns
        contact_patterns = [
            r'(phone|telefon|tel|mobile|cep)',
            r'(email|e-mail|mail)',
            r'(address|adres|adress)',
            r'(contact|iletişim)',
        ]
        
        for pattern in contact_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                contact_info["has_contact"] = True
                contact_info["contact_text"] = match.group(1)
                break
        
        if not contact_info:
            contact_info["has_contact"] = False
        
        return contact_info
    
    def _extract_host_info(self, text: str) -> Dict[str, Any]:
        """Extract host information from invitation letter text"""
        host_info = {}
        
        # Host patterns
        host_patterns = [
            r'(host|ev sahibi|davet eden)',
            r'(student|öğrenci|student at)',
            r'(university|üniversite|college|kolej)',
            r'(inviting|davet ediyorum)',
        ]
        
        for pattern in host_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                host_info["has_host"] = True
                host_info["host_text"] = match.group(1)
                break
        
        if not host_info:
            host_info["has_host"] = False
        
        return host_info
    
    def _extract_invitation_dates(self, text: str) -> Dict[str, Any]:
        """Extract invitation dates from invitation letter text"""
        dates_info = {}
        
        # Date patterns
        date_patterns = [
            r'(\d{1,2})[./](\d{1,2})[./](\d{4})',  # DD/MM/YYYY
            r'(\d{4})[./](\d{1,2})[./](\d{1,2})',  # YYYY/MM/DD
            r'(from|from|başlangıç|start)',
            r'(to|until|bitiş|end)',
        ]
        
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match) == 3 and match[0].isdigit():
                    try:
                        day, month, year = match
                        date_str = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                        dates.append(datetime.strptime(date_str, "%Y-%m-%d"))
                    except ValueError:
                        continue
        
        if dates:
            dates_info["dates"] = dates
            dates_info["start_date"] = min(dates) if dates else None
            dates_info["end_date"] = max(dates) if dates else None
        
        return dates_info
    
    def _extract_signature_info(self, text: str) -> Dict[str, Any]:
        """Extract signature information from invitation letter text"""
        signature_info = {}
        
        # Signature patterns
        signature_patterns = [
            r'(signature|imza|signed|imzalı)',
            r'(sincerely|saygılarımla|respectfully)',
            r'(yours truly|samimi saygılarımla)',
        ]
        
        for pattern in signature_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                signature_info["has_signature"] = True
                signature_info["signature_text"] = match.group(1)
                break
        
        if not signature_info:
            signature_info["has_signature"] = False
        
        return signature_info
    
    def _validate_host_contact(self, contact_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate host contact information is present"""
        result = {
            "valid": False,
            "issues": [],
            "recommendations": [],
            "details": contact_info
        }
        
        if contact_info.get("has_contact"):
            result["valid"] = True
            result["recommendations"].append("Host contact information found")
        else:
            result["issues"].append("Host contact information not found")
            result["recommendations"].append("Ensure the document contains host contact details (phone, email, address)")
        
        return result
    
    def _validate_host_info(self, host_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate host information is present"""
        result = {
            "valid": False,
            "issues": [],
            "recommendations": [],
            "details": host_info
        }
        
        if host_info.get("has_host"):
            result["valid"] = True
            result["recommendations"].append("Host information found")
        else:
            result["issues"].append("Host information not found")
            result["recommendations"].append("Ensure the document contains host details (name, status, affiliation)")
        
        return result
    
    def _validate_invitation_dates(self, dates_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate invitation dates are present"""
        result = {
            "valid": False,
            "issues": [],
            "recommendations": [],
            "details": dates_info
        }
        
        if dates_info.get("dates"):
            result["valid"] = True
            result["recommendations"].append("Invitation dates found and validated")
        else:
            result["issues"].append("Invitation dates not found")
            result["recommendations"].append("Ensure the document contains visit start and end dates")
        
        return result
    
    def _validate_signature(self, signature_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate signature is present"""
        result = {
            "valid": False,
            "issues": [],
            "recommendations": [],
            "details": signature_info
        }
        
        if signature_info.get("has_signature"):
            result["valid"] = True
            result["recommendations"].append("Signature found")
        else:
            result["issues"].append("Signature not found")
            result["recommendations"].append("Ensure the document contains a signature")
        
        return result
    
    def _extract_visa_info(self, text: str) -> Dict[str, Any]:
        """Extract visa information from previous visas text"""
        visa_info = {}
        
        # Visa patterns
        visa_patterns = [
            r'(visa|vize|vizum)',
            r'(schengen|schengen states)',
            r'(valid|geçerli|validity)',
            r'(expired|süresi dolmuş)',
        ]
        
        for pattern in visa_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                visa_info["has_visa"] = True
                visa_info["visa_text"] = match.group(1)
                break
        
        if not visa_info:
            visa_info["has_visa"] = False
        
        return visa_info
    
    def _extract_visa_country_info(self, text: str) -> Dict[str, Any]:
        """Extract visa country information from previous visas text"""
        country_info = {}
        
        # Country code patterns
        country_patterns = [
            r'\b([A-Z]{3})\b',  # 3-letter country codes
            r'(SVN|DEU|FRA|ITA|ESP|NLD|BEL|AUT|PRT|GRC|FIN|SWE|DNK|POL|CZE|HUN|SVK|SVN|LTU|LVA|EST|MLT|CYP|LUX|IRL)',
            r'(slovenia|germany|france|italy|spain|netherlands|belgium|austria|portugal|greece|finland|sweden|denmark|poland|czech|hungary|slovakia|lithuania|latvia|estonia|malta|cyprus|luxembourg|ireland)',
        ]
        
        countries = []
        for pattern in country_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    countries.extend(match)
                else:
                    countries.append(match)
        
        if countries:
            country_info["has_country"] = True
            country_info["countries"] = list(set(countries))
        else:
            country_info["has_country"] = False
        
        return country_info
    
    def _extract_visa_dates(self, text: str) -> Dict[str, Any]:
        """Extract visa dates from previous visas text"""
        dates_info = {}
        
        # Date patterns
        date_patterns = [
            r'(\d{1,2})[./-](\d{1,2})[./-](\d{2,4})',  # DD/MM/YYYY
            r'(\d{4})[./-](\d{1,2})[./-](\d{1,2})',  # YYYY/MM/DD
            r'(from|until|valid from|valid until)',
        ]
        
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match) == 3 and match[0].isdigit():
                    try:
                        if len(match[2]) == 2:
                            year = "20" + match[2]
                        else:
                            year = match[2]
                        
                        day, month = match[0], match[1]
                        date_str = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                        dates.append(datetime.strptime(date_str, "%Y-%m-%d"))
                    except ValueError:
                        continue
        
        if dates:
            dates_info["dates"] = dates
            dates_info["start_date"] = min(dates) if dates else None
            dates_info["end_date"] = max(dates) if dates else None
        
        return dates_info
    
    def _validate_visa_validity(self, visa_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate visa validity is present"""
        result = {
            "valid": False,
            "issues": [],
            "recommendations": [],
            "details": visa_info
        }
        
        if visa_info.get("has_visa"):
            result["valid"] = True
            result["recommendations"].append("Visa information found")
        else:
            result["issues"].append("Visa information not found")
            result["recommendations"].append("Ensure the document contains visa information")
        
        return result
    
    def _validate_visa_country(self, country_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate visa country is present"""
        result = {
            "valid": False,
            "issues": [],
            "recommendations": [],
            "details": country_info
        }
        
        if country_info.get("has_country"):
            result["valid"] = True
            result["recommendations"].append("Visa country information found")
        else:
            result["issues"].append("Visa country information not found")
            result["recommendations"].append("Ensure the document contains visa country information")
        
        return result
    
    def _validate_visa_dates(self, dates_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate visa dates are present"""
        result = {
            "valid": False,
            "issues": [],
            "recommendations": [],
            "details": dates_info
        }
        
        if dates_info.get("dates"):
            result["valid"] = True
            result["recommendations"].append("Visa dates found and validated")
        else:
            result["issues"].append("Visa dates not found")
            result["recommendations"].append("Ensure the document contains visa validity dates")
        
        return result
    
    def _extract_property_deed_stamp(self, text: str) -> Dict[str, Any]:
        """Extract official stamp information from property deed text"""
        stamp_info = {}
        
        # Stamp patterns
        stamp_patterns = [
            r'(mühür|kaşe|stamp|seal)',
            r'(siciline uygundur|conforms to the record)',
            r'(verily|verified)',
            r'(tapu|property deed)',
        ]
        
        for pattern in stamp_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                stamp_info["has_stamp"] = True
                stamp_info["stamp_text"] = match.group(1)
                break
        
        if not stamp_info:
            stamp_info["has_stamp"] = False
        
        return stamp_info
    
    def _extract_property_owner_info(self, text: str) -> Dict[str, Any]:
        """Extract property owner information from property deed text"""
        owner_info = {}
        
        # Owner patterns
        owner_patterns = [
            r'(malik|owner|sahip)',
            r'(adı soyadı|name|surname)',
            r'(baba adı|father\'s name)',
            r'(hissesi|share)',
        ]
        
        for pattern in owner_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                owner_info["has_owner"] = True
                owner_info["owner_text"] = match.group(1)
                break
        
        if not owner_info:
            owner_info["has_owner"] = False
        
        return owner_info
    
    def _extract_property_value_info(self, text: str) -> Dict[str, Any]:
        """Extract property value information from property deed text"""
        value_info = {}
        
        # Value patterns
        value_patterns = [
            r'(işlem bedeli|transaction price|purchase price)',
            r'(bedel|price|value)',
            r'(\d+\.?\d*\s*(tl|try|₺|euro|eur|usd|\$))',
            r'(\d+\.?\d*\s*(bin|million|milyon))',
        ]
        
        for pattern in value_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value_info["has_value"] = True
                value_info["value_text"] = match.group(1)
                break
        
        if not value_info:
            value_info["has_value"] = False
        
        return value_info
    
    def _validate_property_deed_stamp(self, stamp_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate official stamp is present"""
        result = {
            "valid": False,
            "issues": [],
            "recommendations": [],
            "details": stamp_info
        }
        
        if stamp_info.get("has_stamp"):
            result["valid"] = True
            result["recommendations"].append("Official stamp or seal detected")
        else:
            result["issues"].append("Official stamp or seal not detected")
            result["recommendations"].append("Ensure the document contains an official stamp or seal")
        
        return result
    
    def _validate_property_owner(self, owner_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate property owner information is present"""
        result = {
            "valid": False,
            "issues": [],
            "recommendations": [],
            "details": owner_info
        }
        
        if owner_info.get("has_owner"):
            result["valid"] = True
            result["recommendations"].append("Property owner information found")
        else:
            result["issues"].append("Property owner information not found")
            result["recommendations"].append("Ensure the document contains property owner details")
        
        return result
    
    def _validate_property_value(self, value_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate property value information is present"""
        result = {
            "valid": False,
            "issues": [],
            "recommendations": [],
            "details": value_info
        }
        
        if value_info.get("has_value"):
            result["valid"] = True
            result["recommendations"].append("Property value information found")
        else:
            result["issues"].append("Property value information not found")
            result["recommendations"].append("Ensure the document contains property value information")
        
        return result
    
    def _extract_active_status_info(self, text: str) -> Dict[str, Any]:
        """Extract active status information from social security text"""
        status_info = {}
        
        # Active status patterns
        status_patterns = [
            r'(çalışmaktadır|is working|active|aktif)',
            r'(faaliyet gösteren|operating)',
            r'(tescili bulunduğu|registration exists)',
            r'(işyerinde|at workplace)',
        ]
        
        for pattern in status_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                status_info["is_active"] = True
                status_info["status_text"] = match.group(1)
                break
        
        if not status_info:
            status_info["is_active"] = False
        
        return status_info
    
    def _extract_registration_date_info(self, text: str) -> Dict[str, Any]:
        """Extract registration date information from social security text"""
        date_info = {}
        
        # Date patterns
        date_patterns = [
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',  # DD/MM/YYYY
            r'(\d{1,2}/\d{1,2}/\d{4})',  # Date format
            r'(tarihinden itibaren|as of|from)',
        ]
        
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple) and len(match) == 3:
                    try:
                        day, month, year = match
                        date_str = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                        dates.append(datetime.strptime(date_str, "%Y-%m-%d"))
                    except ValueError:
                        continue
        
        if dates:
            date_info["dates"] = dates
            date_info["registration_date"] = min(dates) if dates else None
        
        return date_info
    
    def _extract_sgk_number_info(self, text: str) -> Dict[str, Any]:
        """Extract SGK number information from social security text"""
        number_info = {}
        
        # SGK number patterns
        number_patterns = [
            r'(sigorta sicil numarası|social security number|sgk number)',
            r'(\d{10,12})',  # 10-12 digit numbers
            r'(601\d{9})',  # SGK format
        ]
        
        for pattern in number_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                number_info["has_number"] = True
                if match.group(0).isdigit():
                    number_info["sgk_number"] = match.group(0)
                break
        
        if not number_info:
            number_info["has_number"] = False
        
        return number_info
    
    def _validate_active_status(self, status_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate active status is present"""
        result = {
            "valid": False,
            "issues": [],
            "recommendations": [],
            "details": status_info
        }
        
        if status_info.get("is_active"):
            result["valid"] = True
            result["recommendations"].append("Active employment status found")
        else:
            result["issues"].append("Active employment status not found")
            result["recommendations"].append("Ensure the document contains active employment status")
        
        return result
    
    def _validate_registration_date(self, date_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate registration date is present"""
        result = {
            "valid": False,
            "issues": [],
            "recommendations": [],
            "details": date_info
        }
        
        if date_info.get("dates"):
            result["valid"] = True
            result["recommendations"].append("Registration date found and validated")
        else:
            result["issues"].append("Registration date not found")
            result["recommendations"].append("Ensure the document contains registration date")
        
        return result
    
    def _validate_sgk_number(self, number_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate SGK number is present"""
        result = {
            "valid": False,
            "issues": [],
            "recommendations": [],
            "details": number_info
        }
        
        if number_info.get("has_number"):
            result["valid"] = True
            result["recommendations"].append("SGK number found")
        else:
            result["issues"].append("SGK number not found")
            result["recommendations"].append("Ensure the document contains SGK number")
        
        return result
    
    def _extract_student_certificate_issue_date(self, text: str) -> Dict[str, Any]:
        """Extract issue date from student certificate text"""
        date_info = {}
        
        # Date patterns
        date_patterns = [
            r'(\d{1,2})\.(\d{1,2})\.(\d{4})',  # DD.MM.YYYY
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',  # DD/MM/YYYY
        ]
        
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    day, month, year = match
                    date_str = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                    dates.append(datetime.strptime(date_str, "%Y-%m-%d"))
                except ValueError:
                    continue
        
        if dates:
            date_info["dates"] = dates
            date_info["issue_date"] = min(dates) if dates else None
        
        return date_info
    
    def _extract_school_name_info(self, text: str) -> Dict[str, Any]:
        """Extract school name information from student certificate text"""
        school_info = {}
        
        # School name patterns
        school_patterns = [
            r'(üniversite|university|universitesi)',
            r'(yükseköğretim|higher education)',
            r'(fakülte|faculty)',
            r'(bölüm|department)',
            r'(yök|yükseköğretim kurulu)',
        ]
        
        for pattern in school_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                school_info["has_school"] = True
                school_info["school_text"] = match.group(1)
                break
        
        if not school_info:
            school_info["has_school"] = False
        
        return school_info
    
    def _extract_school_stamp_info(self, text: str) -> Dict[str, Any]:
        """Extract school stamp information from student certificate text"""
        stamp_info = {}
        
        # Stamp patterns
        stamp_patterns = [
            r'(mühür|kaşe|stamp|seal)',
            r'(yök|yükseköğretim kurulu)',
            r'(üniversite|university|universitesi)',
            r'(logo|emblem)',
            r'(baskalik|presidency)',
            r'(ankara)',
        ]
        
        for pattern in stamp_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                stamp_info["has_stamp"] = True
                stamp_info["stamp_text"] = match.group(1)
                break
        
        if not stamp_info:
            stamp_info["has_stamp"] = False
        
        return stamp_info
    
    def _extract_student_certificate_signature(self, text: str) -> Dict[str, Any]:
        """Extract signature information from student certificate text"""
        signature_info = {}
        
        # Signature patterns
        signature_patterns = [
            r'(imza|signature)',
            r'(signed|imzalı)',
            r'(başkan|president|baskalik)',
            r'(müdür|director)',
            r'(ilgili makama|to whom it may concern)',
            r'(bildirilmiştir|certified)',
        ]
        
        for pattern in signature_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                signature_info["has_signature"] = True
                signature_info["signature_text"] = match.group(1)
                break
        
        if not signature_info:
            signature_info["has_signature"] = False
        
        return signature_info
    
    def _validate_student_certificate_issue_date(self, date_info: Dict[str, Any], max_age_in_days: int) -> Dict[str, Any]:
        """Validate student certificate issue date is recent"""
        result = {
            "valid": False,
            "issues": [],
            "recommendations": [],
            "details": date_info
        }
        
        if date_info.get("issue_date"):
            issue_date = date_info["issue_date"]
            today = datetime.now()
            age_in_days = (today - issue_date).days
            
            if age_in_days <= max_age_in_days:
                result["valid"] = True
                result["recommendations"].append(f"Certificate is recent (issued {age_in_days} days ago)")
            else:
                result["issues"].append(f"Certificate is too old (issued {age_in_days} days ago, max {max_age_in_days} days)")
                result["recommendations"].append(f"Ensure the certificate was issued within the last {max_age_in_days} days")
        else:
            result["issues"].append("Issue date not found")
            result["recommendations"].append("Ensure the document contains an issue date")
        
        return result
    
    def _validate_school_name(self, school_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate school name is present"""
        result = {
            "valid": False,
            "issues": [],
            "recommendations": [],
            "details": school_info
        }
        
        if school_info.get("has_school"):
            result["valid"] = True
            result["recommendations"].append("School name found")
        else:
            result["issues"].append("School name not found")
            result["recommendations"].append("Ensure the document contains school name")
        
        return result
    
    def _validate_school_stamp(self, stamp_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate school stamp is present"""
        result = {
            "valid": False,
            "issues": [],
            "recommendations": [],
            "details": stamp_info
        }
        
        if stamp_info.get("has_stamp"):
            result["valid"] = True
            result["recommendations"].append("School stamp or emblem detected")
        else:
            result["issues"].append("School stamp or emblem not detected")
            result["recommendations"].append("Ensure the document contains school stamp or emblem")
        
        return result
    
    def _validate_student_certificate_signature(self, signature_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate signature is present"""
        result = {
            "valid": False,
            "issues": [],
            "recommendations": [],
            "details": signature_info
        }
        
        if signature_info.get("has_signature"):
            result["valid"] = True
            result["recommendations"].append("Signature found")
        else:
            result["issues"].append("Signature not found")
            result["recommendations"].append("Ensure the document contains a signature")
        
        return result
    
    def _extract_income_amount_info(self, text: str) -> Dict[str, Any]:
        """Extract income amount information from tax return text"""
        amount_info = {}
        
        # Income amount patterns
        amount_patterns = [
            r'(gelir|income|kazanç)',
            r'(toplam|total|sum)',
            r'(\d+\.?\d*\.?\d*,\d{2})',  # Turkish number format
            r'(\d+,\d{3}\.\d{2})',  # Alternative format
        ]
        
        amounts = []
        for pattern in amount_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, str) and match.replace('.', '').replace(',', '').isdigit():
                    # Clean and parse Turkish number format
                    cleaned = match.replace('.', '').replace(',', '.')
                    try:
                        amounts.append(float(cleaned))
                    except ValueError:
                        continue
        
        if amounts:
            amount_info["has_amount"] = True
            amount_info["amounts"] = amounts
            amount_info["total_amount"] = sum(amounts)
        else:
            amount_info["has_amount"] = False
        
        return amount_info
    
    def _extract_tax_office_stamp_info(self, text: str) -> Dict[str, Any]:
        """Extract tax office stamp information from tax return text"""
        stamp_info = {}
        
        # Tax office stamp patterns
        stamp_patterns = [
            r'(vergi dairesi|tax office)',
            r'(müdürlük|directorate)',
            r'(onay|approval|approved)',
            r'(mühür|kaşe|stamp|seal)',
            r'(gelir idaresi|revenue administration)',
        ]
        
        for pattern in stamp_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                stamp_info["has_stamp"] = True
                stamp_info["stamp_text"] = match.group(1)
                break
        
        if not stamp_info:
            stamp_info["has_stamp"] = False
        
        return stamp_info
    
    def _extract_tax_year_info(self, text: str) -> Dict[str, Any]:
        """Extract tax year information from tax return text"""
        year_info = {}
        
        # Year patterns
        year_patterns = [
            r'(yıl|year)\s*:?\s*(\d{4})',
            r'(dönem|period)\s*:?\s*(\d{4})',
            r'(\d{4})\s*(yıl|year)',
        ]
        
        years = []
        for pattern in year_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    for item in match:
                        if item.isdigit() and len(item) == 4:
                            years.append(int(item))
                elif match.isdigit() and len(match) == 4:
                    years.append(int(match))
        
        if years:
            year_info["has_year"] = True
            year_info["years"] = list(set(years))
            year_info["tax_year"] = max(years) if years else None
        else:
            year_info["has_year"] = False
        
        return year_info
    
    def _validate_income_amount(self, amount_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate income amount is present"""
        result = {
            "valid": False,
            "issues": [],
            "recommendations": [],
            "details": amount_info
        }
        
        if amount_info.get("has_amount"):
            result["valid"] = True
            result["recommendations"].append("Income amount found")
        else:
            result["issues"].append("Income amount not found")
            result["recommendations"].append("Ensure the document contains income amount")
        
        return result
    
    def _validate_tax_office_stamp(self, stamp_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate tax office stamp is present"""
        result = {
            "valid": False,
            "issues": [],
            "recommendations": [],
            "details": stamp_info
        }
        
        if stamp_info.get("has_stamp"):
            result["valid"] = True
            result["recommendations"].append("Tax office stamp or approval found")
        else:
            result["issues"].append("Tax office stamp or approval not found")
            result["recommendations"].append("Ensure the document contains tax office stamp or approval")
        
        return result
    
    def _validate_tax_year(self, year_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate tax year is present"""
        result = {
            "valid": False,
            "issues": [],
            "recommendations": [],
            "details": year_info
        }
        
        if year_info.get("has_year"):
            result["valid"] = True
            result["recommendations"].append("Tax year found and validated")
        else:
            result["issues"].append("Tax year not found")
            result["recommendations"].append("Ensure the document contains tax year")
        
        return result
    
    def _extract_coverage_amount_info(self, text: str) -> Dict[str, Any]:
        """Extract coverage amount information from travel insurance text"""
        amount_info = {}
        
        # Coverage amount patterns
        amount_patterns = [
            r'(sum insured|coverage|teminat)',
            r'\$\s*(\d{1,3}(?:,\d{3})*)',  # Dollar amounts
            r'(\d{1,3}(?:,\d{3})*)\s*(usd|eur|tl|try)',  # Amount with currency
            r'(up to|maximum|max)\s*\$?\s*(\d{1,3}(?:,\d{3})*)',  # Up to amounts
        ]
        
        amounts = []
        for pattern in amount_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    for item in match:
                        if item and item.replace(',', '').isdigit():
                            amounts.append(item)
                elif isinstance(match, str) and match.replace(',', '').isdigit():
                    amounts.append(match)
        
        if amounts:
            amount_info["has_amount"] = True
            amount_info["amounts"] = amounts
        else:
            amount_info["has_amount"] = False
        
        return amount_info
    
    def _extract_coverage_area_info(self, text: str) -> Dict[str, Any]:
        """Extract coverage area information from travel insurance text"""
        area_info = {}
        
        # Coverage area patterns
        area_patterns = [
            r'(destination|hedef|varış)',
            r'(country|ülke|country of residence)',
            r'(schengen|europe|european union)',
            r'(jordan|turkey|germany|france|italy|spain|egypt|poland|netherlands|belgium|austria|switzerland|greece|croatia|czech|portugal|finland|sweden|denmark|norway)',
            r'(worldwide|world-wide|tüm dünya)',
        ]
        
        for pattern in area_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                area_info["has_area"] = True
                area_info["area_text"] = match.group(1)
                break
        
        if not area_info:
            area_info["has_area"] = False
        
        return area_info
    
    def _extract_validity_period_info(self, text: str) -> Dict[str, Any]:
        """Extract validity period information from travel insurance text"""
        period_info = {}
        
        # Date patterns
        date_patterns = [
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',  # DD/MM/YYYY
            r'(from|to|başlangıç|bitiş)',
        ]
        
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match) == 3 and match[0].isdigit():
                    try:
                        day, month, year = match
                        date_str = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                        dates.append(datetime.strptime(date_str, "%Y-%m-%d"))
                    except ValueError:
                        continue
        
        if dates:
            period_info["dates"] = dates
            period_info["start_date"] = min(dates) if dates else None
            period_info["end_date"] = max(dates) if dates else None
        
        return period_info
    
    def _validate_coverage_amount(self, amount_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate coverage amount is present"""
        result = {
            "valid": False,
            "issues": [],
            "recommendations": [],
            "details": amount_info
        }
        
        if amount_info.get("has_amount"):
            result["valid"] = True
            result["recommendations"].append("Coverage amount found")
        else:
            result["issues"].append("Coverage amount not found")
            result["recommendations"].append("Ensure the document contains coverage amount")
        
        return result
    
    def _validate_coverage_area(self, area_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate coverage area is present"""
        result = {
            "valid": False,
            "issues": [],
            "recommendations": [],
            "details": area_info
        }
        
        if area_info.get("has_area"):
            result["valid"] = True
            result["recommendations"].append("Coverage area found")
        else:
            result["issues"].append("Coverage area not found")
            result["recommendations"].append("Ensure the document contains coverage area")
        
        return result
    
    def _validate_validity_period(self, period_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate validity period is present"""
        result = {
            "valid": False,
            "issues": [],
            "recommendations": [],
            "details": period_info
        }
        
        if period_info.get("dates"):
            result["valid"] = True
            result["recommendations"].append("Validity period found and validated")
        else:
            result["issues"].append("Validity period not found")
            result["recommendations"].append("Ensure the document contains validity period")
        
        return result
    
    def _validate_account_balance(self, balance_info: Dict[str, Any], min_threshold: float) -> Dict[str, Any]:
        """Validate account balance meets minimum requirements"""
        result = {
            "valid": False,
            "issues": [],
            "recommendations": [],
            "details": balance_info
        }
        
        if not balance_info.get("current_balance"):
            result["issues"].append("Account balance not found in document")
            result["recommendations"].append("Ensure the document contains clear balance information")
            return result
        
        current_balance = balance_info["current_balance"]["amount"]
        
        if current_balance < min_threshold:
            result["issues"].append(f"Account balance ({current_balance}) is below minimum threshold ({min_threshold})")
            result["recommendations"].append(f"Ensure account balance is at least {min_threshold} {balance_info['current_balance']['currency']}")
        else:
            result["valid"] = True
            result["recommendations"].append("Account balance meets requirements")
        
        return result
    
    def _validate_bank_stamp(self, stamp_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate bank stamp presence"""
        result = {
            "valid": False,
            "issues": [],
            "recommendations": [],
            "details": stamp_info
        }
        
        if not stamp_info.get("has_stamp"):
            result["issues"].append("Bank stamp or seal not detected")
            result["recommendations"].append("Ensure the document has an official bank stamp or seal")
        else:
            result["valid"] = True
            result["recommendations"].append("Bank stamp detected successfully")
        
        return result
    
    def _validate_statement_period(self, period_info: Dict[str, Any], min_months: int) -> Dict[str, Any]:
        """Validate statement period covers minimum required months"""
        result = {
            "valid": False,
            "issues": [],
            "recommendations": [],
            "details": period_info
        }
        
        if not period_info.get("duration_days"):
            result["issues"].append("Statement period not clearly identifiable")
            result["recommendations"].append("Ensure the document contains clear date information")
            return result
        
        duration_days = period_info["duration_days"]
        duration_months = duration_days / 30  # Approximate months
        
        if duration_months < min_months:
            result["issues"].append(f"Statement period ({duration_months:.1f} months) is less than required ({min_months} months)")
            result["recommendations"].append(f"Provide bank statements covering at least {min_months} months")
        else:
            result["valid"] = True
            result["recommendations"].append(f"Statement period ({duration_months:.1f} months) meets requirements")
        
        return result
    
    def _calculate_confidence_score(self, validation_results: Dict[str, Any]) -> float:
        """Calculate overall confidence score based on validation results"""
        if not validation_results:
            return 0.0
        
        total_validations = len(validation_results)
        passed_validations = sum(1 for result in validation_results.values() if result.get("valid", False))
        
        return passed_validations / total_validations if total_validations > 0 else 0.0
    
    def _process_generic_document(self, text: str, config: Dict[str, Any], metadata: Dict[str, Any] = None) -> OCRResult:
        """Process generic document types"""
        return OCRResult(
            document_type=DocumentType(config["checkId"]),
            confidence_score=0.8,  # Default confidence for generic processing
            extracted_text=text,
            validation_results={"generic_processing": True},
            issues=[],
            recommendations=["Document processed successfully"],
            metadata={"config": config}
        )
    
    def get_document_type_config(self, document_type: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific document type"""
        try:
            doc_type = DocumentType(document_type)
            return self.document_type_configs.get(doc_type)
        except ValueError:
            return None
    
    def list_supported_document_types(self) -> List[Dict[str, Any]]:
        """List all supported document types and their configurations"""
        return [
            {
                "checkId": config["checkId"],
                "docDescription": config["docDescription"],
                "docName": config["docName"],
                "ocrValidationRules": config["ocrValidationRules"].__dict__,
                "requiredFor": config["requiredFor"]
            }
            for config in self.document_type_configs.values()
        ]
