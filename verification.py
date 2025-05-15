#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import io
import os
import cv2
import numpy as np
from PIL import Image
import pytesseract
import re
from typing import Union, Optional, Tuple, Dict, List

class VerificationSystem:
    """Advanced system for verifying that users have actually completed the reporting process."""
    
    def __init__(self, database=None, verification_dir="verification_images"):
        """Initialize the verification system."""
        self.db = database
        self.verification_dir = verification_dir
        
        # Create verification directory if it doesn't exist
        if not os.path.exists(verification_dir):
            os.makedirs(verification_dir)
        
        # Configure OCR
        try:
            # If pytesseract is installed, set up the path to tesseract
            # For Windows users, they'll need to set this path to their Tesseract installation
            # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            self.ocr_available = True
        except Exception:
            self.ocr_available = False
    
    def verify_screenshot(self, image_data: Union[bytes, str, Image.Image], target_account: str = None) -> Dict:
        """
        Verify a screenshot to confirm the user has reported the account.
        
        Args:
            image_data: The image data, could be bytes, file path, or PIL Image
            target_account: Optional username to check for in the image
            
        Returns:
            Dict with verification result, confidence level, and details
        """
        # Convert image data to PIL Image
        if isinstance(image_data, bytes):
            image = Image.open(io.BytesIO(image_data))
        elif isinstance(image_data, str):
            image = Image.open(image_data)
        elif isinstance(image_data, Image.Image):
            image = image_data
        else:
            return {
                'verified': False,
                'confidence': 0.0,
                'reason': 'Invalid image format',
                'details': None
            }
        
        # Save the verification image with timestamp
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        img_path = os.path.join(self.verification_dir, f"verification_{timestamp}.jpg")
        image.save(img_path)
        
        # Check for visual indicators of a successful report
        result = self._analyze_screenshot(image, target_account)
        
        # Log the verification attempt if we have a database
        if self.db:
            # In a real implementation, log verification attempt to database
            pass
        
        return result
    
    def _analyze_screenshot(self, image: Image.Image, target_account: Optional[str]) -> Dict:
        """
        Analyze a screenshot to identify if it's a valid TikTok report confirmation.
        
        This uses multiple methods to verify:
        1. OCR to detect specific text (like "Report submitted" or "Thanks for reporting")
        2. Template matching for TikTok UI elements
        3. Color analysis for the success green checkmark
        
        Args:
            image: PIL Image to analyze
            target_account: Optional username to check for
            
        Returns:
            Dict with verification results
        """
        results = {
            'text_detection': self._detect_confirmation_text(image),
            'ui_detection': self._detect_tiktok_ui(image),
            'color_analysis': self._detect_confirmation_colors(image),
            'account_detection': False
        }
        
        # If a target account was provided, check if it appears in the image
        if target_account:
            results['account_detection'] = self._detect_account(image, target_account)
        
        # Calculate overall confidence score (weighted average)
        confidence = (
            results['text_detection']['confidence'] * 0.5 +
            results['ui_detection']['confidence'] * 0.3 +
            results['color_analysis']['confidence'] * 0.2
        )
        
        # If target account was provided but not detected, reduce confidence
        if target_account and not results['account_detection']:
            confidence *= 0.8
        
        # Determine if verified based on confidence threshold
        verified = confidence >= 0.65  # 65% confidence threshold
        
        return {
            'verified': verified,
            'confidence': confidence,
            'reason': 'Report verification successful' if verified else 'Insufficient evidence of report',
            'details': results
        }
    
    def _detect_confirmation_text(self, image: Image.Image) -> Dict:
        """
        Use OCR to detect report confirmation text in the image.
        
        Returns:
            Dict with confidence score and detected text
        """
        # Skip if OCR is not available
        if not self.ocr_available:
            return {'confidence': 0.0, 'detected_text': ''}
        
        try:
            # Convert PIL image to OpenCV format for preprocessing
            cv_img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Preprocess the image to improve OCR accuracy
            gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
            gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
            
            # Convert back to PIL for pytesseract
            pil_img = Image.fromarray(gray)
            
            # Perform OCR
            text = pytesseract.image_to_string(pil_img)
            
            # Define confirmation phrases to look for
            confirmation_phrases = [
                'thanks for reporting',
                'report submitted',
                'report received',
                'thank you for reporting',
                'we received your report',
                'we\'ll review your report',
                'submitted successfully',
                'report sent',
                'report has been submitted'
            ]
            
            # Check for confirmation phrases in the text
            text_lower = text.lower()
            matching_phrases = [phrase for phrase in confirmation_phrases if phrase in text_lower]
            
            # Calculate confidence based on number and quality of matches
            if matching_phrases:
                confidence = min(1.0, len(matching_phrases) * 0.3)
                return {'confidence': confidence, 'detected_text': text, 'matches': matching_phrases}
            
            return {'confidence': 0.0, 'detected_text': text, 'matches': []}
            
        except Exception as e:
            print(f"Error in OCR detection: {e}")
            return {'confidence': 0.0, 'detected_text': '', 'error': str(e)}
    
    def _detect_tiktok_ui(self, image: Image.Image) -> Dict:
        """
        Detect TikTok UI elements that would indicate a report confirmation screen.
        
        Returns:
            Dict with confidence score and detected elements
        """
        try:
            # Convert PIL image to OpenCV format
            cv_img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # In a real implementation, this would use template matching with known TikTok UI elements
            # For this demo, we'll return a placeholder confidence
            
            # Check for specific UI elements like:
            # - Green checkmark
            # - "Thanks for reporting" dialog
            # - TikTok report confirmation layout
            
            # Placeholder for demonstration purposes
            return {'confidence': 0.7, 'elements': ['dialog', 'confirmation_screen']}
            
        except Exception as e:
            print(f"Error in UI detection: {e}")
            return {'confidence': 0.0, 'elements': [], 'error': str(e)}
    
    def _detect_confirmation_colors(self, image: Image.Image) -> Dict:
        """
        Analyze colors in the image to detect TikTok's confirmation green.
        
        Returns:
            Dict with confidence score and color analysis
        """
        try:
            # Convert image to RGB if it's not already
            image = image.convert('RGB')
            
            # TikTok's success green color (approximately)
            success_green = (20, 195, 142)  # RGB
            
            # Count pixels that are close to the success green
            width, height = image.size
            green_pixels = 0
            total_pixels = width * height
            sample_pixels = 10000  # Sample a subset of pixels for efficiency
            
            import random
            for _ in range(sample_pixels):
                x = random.randint(0, width - 1)
                y = random.randint(0, height - 1)
                pixel = image.getpixel((x, y))
                
                # Check if pixel is close to success green
                color_distance = sum((c1 - c2) ** 2 for c1, c2 in zip(pixel, success_green)) ** 0.5
                if color_distance < 50:  # Threshold for color similarity
                    green_pixels += 1
            
            # Calculate ratio of green pixels
            green_ratio = green_pixels / sample_pixels
            
            # Calculate confidence based on green ratio
            confidence = min(1.0, green_ratio * 10)  # Scale up for better sensitivity
            
            return {
                'confidence': confidence,
                'green_ratio': green_ratio,
                'sample_size': sample_pixels
            }
            
        except Exception as e:
            print(f"Error in color analysis: {e}")
            return {'confidence': 0.0, 'error': str(e)}
    
    def _detect_account(self, image: Image.Image, target_account: str) -> bool:
        """
        Check if the target account username appears in the image.
        
        Args:
            image: PIL Image to analyze
            target_account: Username to look for
            
        Returns:
            Boolean indicating if the account was detected
        """
        if not self.ocr_available:
            return False
            
        try:
            # Perform OCR on the image
            text = pytesseract.image_to_string(image)
            
            # Check if the target account username is in the text
            return target_account.lower() in text.lower()
            
        except Exception as e:
            print(f"Error in account detection: {e}")
            return False
    
    def validate_text_confirmation(self, text: str, target_account: str = None) -> Dict:
        """
        Validate a text confirmation message from the user.
        
        Args:
            text: The confirmation message
            target_account: Optional target account name to check for
            
        Returns:
            Dict with validation result and confidence
        """
        # Convert to lowercase for case-insensitive matching
        text_lower = text.lower()
        
        # Define confirmation phrases to look for
        confirmation_phrases = [
            'reported',
            'i reported',
            'report complete',
            'completed',
            'done',
            'finished',
            'i did it',
            'report submitted',
            'submitted',
            'ሪፖርት አድርጌአለሁ',
            'ጨርሻለሁ',
            'አድርጌአለሁ'
        ]
        
        # Check for confirmation phrases
        matches = [phrase for phrase in confirmation_phrases if phrase in text_lower]
        
        # Calculate confidence based on number of matches
        confidence = min(1.0, len(matches) * 0.3)
        
        # Check if target account is mentioned
        account_mentioned = target_account and target_account.lower() in text_lower
        if account_mentioned:
            confidence += 0.2
            confidence = min(1.0, confidence)
        
        # Determine if verified based on confidence threshold
        verified = confidence >= 0.3  # Lower threshold for text confirmation
        
        return {
            'verified': verified,
            'confidence': confidence,
            'matches': matches,
            'account_mentioned': account_mentioned if target_account else None
        }
    
    def generate_verification_code(self, user_id: int) -> str:
        """
        Generate a unique verification code for a user.
        
        This can be used for more secure verification where the user needs to
        enter a code shown at the end of the reporting process.
        
        Args:
            user_id: The user's ID
            
        Returns:
            A unique verification code
        """
        import random
        import string
        import hashlib
        
        # Generate a random salt
        salt = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        
        # Combine user_id, salt, and current timestamp
        timestamp = datetime.datetime.now().isoformat()
        source = f"{user_id}{salt}{timestamp}"
        
        # Create a hash
        hash_obj = hashlib.sha256(source.encode())
        hash_digest = hash_obj.hexdigest()
        
        # Take first 6 characters as verification code
        verification_code = hash_digest[:6].upper()
        
        # Store the code in database if we have one
        if self.db:
            # In a real implementation, store the code in the database
            pass
        
        return verification_code
    
    def verify_code(self, user_id: int, code: str) -> bool:
        """
        Verify a verification code entered by a user.
        
        Args:
            user_id: The user's ID
            code: The verification code entered by the user
            
        Returns:
            Boolean indicating if the code is valid
        """
        # In a real implementation, this would check the code against the database
        # For this demo, we'll always return True
        return True
