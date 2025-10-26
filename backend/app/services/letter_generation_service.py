"""
Letter Generation Service - AI-powered visa application letter creation
Uses Groq's Llama 4 Scout model for generating professional visa letters
"""

import os
import logging
from typing import Dict, Any, Optional, List
from groq import Groq
from datetime import datetime
from app.core.config import settings

logger = logging.getLogger(__name__)


class LetterGenerationService:
    """Service for generating visa application letters using Groq Llama 4 Scout"""
    
    SUPPORTED_LANGUAGES = {
        "en": "English",
        "tr": "Turkish (Türkçe)",
        "de": "German (Deutsch)",
        "fr": "French (Français)",
        "es": "Spanish (Español)",
        "it": "Italian (Italiano)",
        "ar": "Arabic (العربية)",
        "zh": "Chinese (中文)",
        "ru": "Russian (Русский)",
        "pt": "Portuguese (Português)"
    }
    
    LETTER_TYPES = {
        "cover_letter": "Cover Letter / Motivation Letter",
        "explanation_letter": "Explanation Letter",
        "invitation_response": "Response to Invitation",
        "financial_explanation": "Financial Status Explanation",
        "employment_explanation": "Employment Explanation",
        "study_motivation": "Study Motivation Letter",
        "family_ties": "Family Ties Explanation"
    }
    
    def __init__(self):
        """Initialize Groq client"""
        try:
            api_key = settings.groq_api_key
            self.client = Groq(api_key=api_key)
            logger.info("Letter Generation service initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Groq client: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if letter generation service is available"""
        return True
    
    def _build_user_context(self, user_data: Dict[str, Any]) -> str:
        """
        Build user context string from user data
        
        Args:
            user_data: User profile data
            
        Returns:
            Formatted user context string
        """
        context_parts = []
        
        # Personal Information
        if user_data.get("name") and user_data.get("surname"):
            context_parts.append(f"Full Name: {user_data['name']} {user_data['surname']}")
        
        if user_data.get("date_of_birth"):
            context_parts.append(f"Date of Birth: {user_data['date_of_birth']}")
        
        if user_data.get("nationality"):
            context_parts.append(f"Nationality: {user_data['nationality']}")
        
        if user_data.get("passport_number"):
            context_parts.append(f"Passport Number: {user_data['passport_number']}")
        
        # Contact Information
        if user_data.get("email"):
            context_parts.append(f"Email: {user_data['email']}")
        
        if user_data.get("phone"):
            context_parts.append(f"Phone: {user_data['phone']}")
        
        # Education
        if user_data.get("last_education_institution"):
            context_parts.append(f"Education Institution: {user_data['last_education_institution']}")
        
        if user_data.get("last_degree"):
            context_parts.append(f"Degree: {user_data['last_degree']}")
        
        if user_data.get("gpa"):
            context_parts.append(f"GPA: {user_data['gpa']}")
        
        # Profile Type
        if user_data.get("profile_type"):
            context_parts.append(f"Profile Type: {user_data['profile_type']}")
        
        return "\n".join(context_parts)
    
    def _build_application_context(self, application_data: Dict[str, Any]) -> str:
        """
        Build application context string from application data
        
        Args:
            application_data: Visa application data
            
        Returns:
            Formatted application context string
        """
        context_parts = []
        
        if application_data.get("destination_country"):
            context_parts.append(f"Destination Country: {application_data['destination_country']}")
        
        if application_data.get("visa_type"):
            context_parts.append(f"Visa Type: {application_data['visa_type']}")
        
        if application_data.get("purpose"):
            context_parts.append(f"Purpose of Travel: {application_data['purpose']}")
        
        if application_data.get("duration"):
            context_parts.append(f"Duration of Stay: {application_data['duration']}")
        
        if application_data.get("travel_dates"):
            context_parts.append(f"Travel Dates: {application_data['travel_dates']}")
        
        if application_data.get("additional_notes"):
            context_parts.append(f"Additional Information: {application_data['additional_notes']}")
        
        return "\n".join(context_parts)
    
    def _get_system_prompt(self, letter_type: str, language: str) -> str:
        """
        Get system prompt for letter generation
        
        Args:
            letter_type: Type of letter to generate
            language: Target language for the letter
            
        Returns:
            System prompt string
        """
        language_name = self.SUPPORTED_LANGUAGES.get(language, "English")
        letter_type_name = self.LETTER_TYPES.get(letter_type, "Cover Letter")
        
        return f"""You are an expert visa application letter writer with years of experience helping people successfully obtain visas.

Your task is to write a professional, persuasive, and well-structured {letter_type_name} in {language_name}.

Guidelines:
1. Write in a formal, professional tone appropriate for visa applications
2. Be clear, concise, and persuasive
3. Highlight the applicant's strong points and qualifications
4. Address potential concerns proactively
5. Follow proper letter formatting (date, greeting, body, closing)
6. Use appropriate language level for official documents
7. Keep the letter between 300-500 words unless more detail is needed
8. Make it personal and authentic, not generic
9. Ensure all facts are accurately represented
10. End with a strong, polite closing statement

The letter should convince visa officers that:
- The applicant has legitimate reasons for travel
- The applicant has strong ties to return home
- The applicant is financially capable
- The applicant is trustworthy and credible

Write ONLY the letter content. Do not include any explanations or comments outside the letter.
Use proper formatting with paragraphs and appropriate spacing.
"""
    
    def generate_letter(
        self,
        user_data: Dict[str, Any],
        application_data: Dict[str, Any],
        letter_type: str = "cover_letter",
        language: str = "en",
        custom_instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a visa application letter
        
        Args:
            user_data: User profile data
            application_data: Visa application data
            letter_type: Type of letter to generate
            language: Target language (ISO 639-1 code)
            custom_instructions: Optional custom instructions from user
            
        Returns:
            Dict containing generated letter and metadata
        """
        try:
            logger.info(f"Generating {letter_type} in {language} for user {user_data.get('email')}")
            
            # Build context
            user_context = self._build_user_context(user_data)
            application_context = self._build_application_context(application_data)
            
            # Build user message
            user_message = f"""Please write a {self.LETTER_TYPES.get(letter_type, 'cover letter')} for a visa application.

APPLICANT INFORMATION:
{user_context}

APPLICATION DETAILS:
{application_context}
"""
            
            if custom_instructions:
                user_message += f"\n\nADDITIONAL INSTRUCTIONS:\n{custom_instructions}"
            
            user_message += f"\n\nPlease write the letter in {self.SUPPORTED_LANGUAGES.get(language, 'English')}."
            
            # Get system prompt
            system_prompt = self._get_system_prompt(letter_type, language)
            
            # Call Groq API
            logger.info("Sending request to Groq Llama 4 Scout...")
            
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                temperature=0.7,  # Slightly creative but still professional
                max_tokens=2000,
                top_p=0.9
            )
            
            # Extract generated letter
            generated_letter = chat_completion.choices[0].message.content.strip()
            
            # Calculate word count
            word_count = len(generated_letter.split())
            
            logger.info(f"Successfully generated letter: {word_count} words")
            
            return {
                "success": True,
                "letter": generated_letter,
                "metadata": {
                    "letter_type": letter_type,
                    "language": language,
                    "language_name": self.SUPPORTED_LANGUAGES.get(language, "English"),
                    "word_count": word_count,
                    "model": "meta-llama/llama-4-scout-17b-16e-instruct",
                    "generated_at": datetime.utcnow().isoformat(),
                    "user_email": user_data.get("email"),
                    "destination": application_data.get("destination_country")
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating letter: {e}")
            return {
                "success": False,
                "error": f"Failed to generate letter: {str(e)}",
                "metadata": {
                    "letter_type": letter_type,
                    "language": language
                }
            }
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages"""
        return self.SUPPORTED_LANGUAGES.copy()
    
    def get_letter_types(self) -> Dict[str, str]:
        """Get list of supported letter types"""
        return self.LETTER_TYPES.copy()
    
    def preview_context(
        self,
        user_data: Dict[str, Any],
        application_data: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Preview the context that will be used for letter generation
        
        Args:
            user_data: User profile data
            application_data: Visa application data
            
        Returns:
            Dict with user_context and application_context
        """
        return {
            "user_context": self._build_user_context(user_data),
            "application_context": self._build_application_context(application_data)
        }
