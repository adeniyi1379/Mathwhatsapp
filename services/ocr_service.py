import os
import httpx
import pytesseract
from PIL import Image
import logging
from io import BytesIO

logger = logging.getLogger(__name__)

class OCRService:
    def __init__(self):
        # Configure Tesseract path if needed
        # pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
        pass
    
    async def extract_text_from_image(self, image_url: str) -> str:
        """Extract text from image using Tesseract OCR"""
        try:
            # Download image
            async with httpx.AsyncClient() as client:
                response = await client.get(image_url)
                response.raise_for_status()
                
                # Open image
                image = Image.open(BytesIO(response.content))
                
                # Preprocess image for better OCR
                image = self._preprocess_image(image)
                
                # Extract text using Tesseract
                text = pytesseract.image_to_string(image, lang='eng')
                
                # Clean extracted text
                cleaned_text = self._clean_extracted_text(text)
                
                logger.info(f"Extracted text from image: {cleaned_text[:100]}...")
                return cleaned_text
        
        except Exception as e:
            logger.error(f"Error extracting text from image: {str(e)}")
            return ""
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """Preprocess image for better OCR accuracy"""
        try:
            # Convert to grayscale
            if image.mode != 'L':
                image = image.convert('L')
            
            # Resize if too small
            width, height = image.size
            if width < 300 or height < 300:
                scale_factor = max(300/width, 300/height)
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            return image
        
        except Exception as e:
            logger.error(f"Error preprocessing image: {str(e)}")
            return image
    
    def _clean_extracted_text(self, text: str) -> str:
        """Clean and format extracted text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove common OCR artifacts
        text = text.replace('|', 'I')
        text = text.replace('0', 'O')  # Only in specific contexts
        
        # Basic math symbol corrections
        text = text.replace(' + ', ' + ')
        text = text.replace(' - ', ' - ')
        text = text.replace(' = ', ' = ')
        text = text.replace(' x ', ' × ')
        
        return text.strip()
