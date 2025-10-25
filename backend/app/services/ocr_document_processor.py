"""
OCR Document Processor
Handles actual OCR processing using Tesseract and OpenCV
"""

import cv2
import numpy as np
import pytesseract
from PIL import Image
import io
import logging
from typing import Dict, List, Any, Optional, Tuple
import re
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class OCRDocumentProcessor:
    """Handles actual OCR processing of documents"""
    
    def __init__(self):
        # Configure Tesseract (adjust path based on your system)
        # For Windows: pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        # For Linux/Mac: usually works with default installation
        import platform
        if platform.system() == 'Windows':
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        self.tesseract_config = '--oem 3 --psm 6 -l eng+tur'  # English + Turkish
        
    def extract_text_from_image(self, image_data: bytes, file_type: str = "image") -> str:
        """
        Extract text from image using OCR
        
        Args:
            image_data: Raw image bytes
            file_type: Type of file (image, pdf, etc.)
            
        Returns:
            Extracted text string
        """
        try:
            if file_type.lower() == "pdf":
                return self._extract_text_from_pdf(image_data)
            else:
                return self._extract_text_from_image_bytes(image_data)
                
        except Exception as e:
            logger.error(f"Error extracting text from {file_type}: {str(e)}")
            return ""
    
    def _extract_text_from_image_bytes(self, image_data: bytes) -> str:
        """Extract text from image bytes using OpenCV and Tesseract"""
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                raise ValueError("Could not decode image")
            
            # Preprocess image for better OCR
            processed_image = self._preprocess_image(image)
            
            # Extract text using Tesseract
            text = pytesseract.image_to_string(processed_image, config=self.tesseract_config)
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error in OCR processing: {str(e)}")
            return ""
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR results"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply denoising for better quality
            denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(denoised, (3, 3), 0)
            
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            # Morphological operations to clean up the image
            kernel = np.ones((1, 1), np.uint8)
            processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            return processed
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {str(e)}")
            return image
    
    def _extract_text_from_pdf(self, pdf_data: bytes) -> str:
        """Extract text from PDF (placeholder - would need pdf2image or similar)"""
        # For now, return empty string
        # In production, you would use pdf2image to convert PDF pages to images
        # then process each image with OCR
        logger.warning("PDF processing not implemented yet")
        return ""
    
    def enhance_text_extraction(self, text: str, document_type: str) -> str:
        """
        Enhance extracted text based on document type
        
        Args:
            text: Raw extracted text
            document_type: Type of document
            
        Returns:
            Enhanced text
        """
        try:
            if document_type == "bank_statement":
                return self._enhance_bank_statement_text(text)
            else:
                return self._enhance_generic_text(text)
                
        except Exception as e:
            logger.error(f"Error enhancing text: {str(e)}")
            return text
    
    def _enhance_bank_statement_text(self, text: str) -> str:
        """Enhance bank statement text extraction"""
        # Clean up common OCR errors
        enhanced_text = text
        
        # Fix common OCR mistakes
        replacements = {
            'O': '0',  # Letter O to number 0 in amounts
            'I': '1',  # Letter I to number 1
            'S': '5',  # Letter S to number 5 in amounts
            'B': '8',  # Letter B to number 8
        }
        
        # Apply replacements only in numeric contexts
        for old, new in replacements.items():
            # Replace in contexts that look like amounts
            pattern = r'(\d+)' + old + r'(\d*)'
            enhanced_text = re.sub(pattern, r'\1' + new + r'\2', enhanced_text)
        
        return enhanced_text
    
    def _enhance_generic_text(self, text: str) -> str:
        """Enhance generic text extraction"""
        # Basic cleanup
        enhanced_text = text
        
        # Remove excessive whitespace
        enhanced_text = re.sub(r'\s+', ' ', enhanced_text)
        
        # Fix common OCR errors
        enhanced_text = enhanced_text.replace('|', 'I')
        enhanced_text = enhanced_text.replace('@', 'a')
        
        return enhanced_text.strip()
    
    def extract_document_metadata(self, image_data: bytes, file_name: str = None) -> Dict[str, Any]:
        """
        Extract metadata from document
        
        Args:
            image_data: Raw image bytes
            file_name: Original file name
            
        Returns:
            Document metadata
        """
        metadata = {
            "file_name": file_name,
            "file_size": len(image_data),
            "processing_timestamp": datetime.utcnow().isoformat(),
            "ocr_engine": "tesseract",
            "language": "eng+tur"
        }
        
        try:
            # Get image dimensions
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is not None:
                height, width = image.shape[:2]
                metadata["image_dimensions"] = {
                    "width": width,
                    "height": height
                }
                
                # Estimate image quality
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
                metadata["image_quality_score"] = float(laplacian_var)
                
        except Exception as e:
            logger.error(f"Error extracting metadata: {str(e)}")
            metadata["error"] = str(e)
        
        return metadata
    
    def validate_image_quality(self, image_data: bytes) -> Dict[str, Any]:
        """
        Validate image quality for OCR processing
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Quality validation results
        """
        validation_result = {
            "is_valid": True,
            "issues": [],
            "recommendations": [],
            "quality_score": 0.0
        }
        
        try:
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                validation_result["is_valid"] = False
                validation_result["issues"].append("Could not decode image")
                return validation_result
            
            height, width = image.shape[:2]
            
            # Check image dimensions
            if width < 200 or height < 200:
                validation_result["issues"].append("Image too small for reliable OCR")
                validation_result["recommendations"].append("Use higher resolution image")
            
            # Check aspect ratio
            aspect_ratio = width / height
            if aspect_ratio < 0.5 or aspect_ratio > 2.0:
                validation_result["issues"].append("Unusual aspect ratio")
                validation_result["recommendations"].append("Ensure document is properly oriented")
            
            # Check image quality
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            validation_result["quality_score"] = float(laplacian_var)
            
            if laplacian_var < 100:
                validation_result["issues"].append("Image appears blurry")
                validation_result["recommendations"].append("Use a sharper image")
            elif laplacian_var > 1000:
                validation_result["issues"].append("Image may be too noisy")
                validation_result["recommendations"].append("Use a cleaner image")
            
            # Check brightness
            mean_brightness = np.mean(gray)
            if mean_brightness < 50:
                validation_result["issues"].append("Image too dark")
                validation_result["recommendations"].append("Improve lighting")
            elif mean_brightness > 200:
                validation_result["issues"].append("Image too bright")
                validation_result["recommendations"].append("Reduce brightness")
            
            # Overall validation
            if len(validation_result["issues"]) > 2:
                validation_result["is_valid"] = False
            
        except Exception as e:
            logger.error(f"Error validating image quality: {str(e)}")
            validation_result["is_valid"] = False
            validation_result["issues"].append(f"Validation error: {str(e)}")
        
        return validation_result
