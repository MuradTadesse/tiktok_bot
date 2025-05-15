#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
from PIL import Image, ImageDraw, ImageFont
import os

class ReportingImageGenerator:
    """Utility class to generate reporting guide images with annotations."""
    
    def __init__(self, img_folder="images"):
        """Initialize with path to image folder."""
        self.img_folder = img_folder
        self.font_size = 36
        
        # Create images directory if it doesn't exist
        if not os.path.exists(img_folder):
            os.makedirs(img_folder)
    
    def annotate_image(self, image_path, text, position, circle_area=None):
        """
        Add text and optional circle annotation to an image.
        
        Args:
            image_path: Path to the image file
            text: Text to add to the image
            position: Tuple (x, y) for text position
            circle_area: Optional tuple (x, y, radius) for circling an area
            
        Returns:
            PIL Image object with annotations
        """
        try:
            # Open image
            img = Image.open(image_path)
            
            # Create draw object
            draw = ImageDraw.Draw(img)
            
            # Try to load a font, fall back to default if not available
            try:
                font = ImageFont.truetype("arial.ttf", self.font_size)
            except IOError:
                font = ImageFont.load_default()
            
            # Add text
            draw.text(position, text, fill=(255, 0, 0), font=font)
            
            # Add circle if specified
            if circle_area:
                x, y, radius = circle_area
                draw.ellipse(
                    (x - radius, y - radius, x + radius, y + radius),
                    outline=(255, 0, 0),
                    width=3
                )
            
            return img
            
        except Exception as e:
            print(f"Error annotating image: {e}")
            return None
    
    def generate_step_image(self, step_num, image_path, instruction, circle_coords=None):
        """
        Generate an instructional image for a specific reporting step.
        
        Args:
            step_num: The step number (1-8)
            image_path: Path to the screenshot
            instruction: Text instruction for this step
            circle_coords: Optional tuple (x, y, radius) to highlight an area
            
        Returns:
            Path to the generated image
        """
        # Position for step number text
        position = (20, 20)
        
        # Create annotation text
        text = f"Step {step_num}: {instruction}"
        
        # Annotate the image
        annotated_img = self.annotate_image(image_path, text, position, circle_coords)
        
        if annotated_img:
            # Save the annotated image
            output_path = os.path.join(self.img_folder, f"step_{step_num}.jpg")
            annotated_img.save(output_path)
            return output_path
        
        return None
    
    def create_blank_instruction_image(self, step_num, instruction):
        """
        Create a blank image with text instructions when screenshots aren't available.
        
        Args:
            step_num: The step number (1-8)
            instruction: Text instruction for this step
            
        Returns:
            PIL Image object with instructions
        """
        # Create a blank white image
        img = Image.new('RGB', (800, 400), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        # Try to load a font, fall back to default if not available
        try:
            title_font = ImageFont.truetype("arial.ttf", 40)
            body_font = ImageFont.truetype("arial.ttf", 30)
        except IOError:
            title_font = ImageFont.load_default()
            body_font = ImageFont.load_default()
        
        # Add step number as title
        draw.text((50, 50), f"Step {step_num}", fill=(0, 0, 0), font=title_font)
        
        # Add instruction text with word wrapping
        lines = self._wrap_text(instruction, body_font, 700)
        y_position = 120
        for line in lines:
            draw.text((50, y_position), line, fill=(0, 0, 0), font=body_font)
            y_position += 40
        
        # Save the image
        output_path = os.path.join(self.img_folder, f"step_{step_num}.jpg")
        img.save(output_path)
        return output_path
    
    def _wrap_text(self, text, font, max_width):
        """Helper function to wrap text."""
        lines = []
        words = text.split()
        current_line = words[0]
        
        for word in words[1:]:
            # Check if adding this word exceeds the width
            test_line = current_line + " " + word
            width = font.getbbox(test_line)[2] if hasattr(font, 'getbbox') else font.getsize(test_line)[0]
            
            if width <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        
        lines.append(current_line)
        return lines
    
    def generate_all_instruction_images(self):
        """
        Generate all instructional images for the reporting process.
        If actual screenshots aren't available, create text-based instructions.
        
        Returns:
            List of paths to all generated images
        """
        instructions = [
            "Open the profile and tap the share icon in the top right",
            "Select 'Report' from the share menu",
            "Tap 'Report account' option",
            "Select 'Posting Inappropriate Content' as the reason",
            "Choose 'Hate and harassment' from the options",
            "Select 'Hate speech and hateful behaviors'",
            "Tap the 'Submit' button to send your report",
            "Toggle on 'Block effoyyt' and tap 'Done'"
        ]
        
        # Check if we have actual screenshots to annotate
        has_screenshots = False
        
        image_paths = []
        
        for i, instruction in enumerate(instructions, 1):
            if has_screenshots:
                # If we have screenshots, annotate them
                screenshot_path = f"screenshots/step_{i}.jpg"
                # Example circle coordinates - these would need to be adjusted for real screenshots
                circle_coords = (200, 200, 50)  # x, y, radius
                path = self.generate_step_image(i, screenshot_path, instruction, circle_coords)
            else:
                # Otherwise create text-based instruction images
                path = self.create_blank_instruction_image(i, instruction)
            
            if path:
                image_paths.append(path)
        
        return image_paths

# Utility for tracking reporting statistics
class ReportingStats:
    """Simple class to track reporting statistics."""
    
    def __init__(self, stats_file="report_stats.txt"):
        """Initialize with path to stats file."""
        self.stats_file = stats_file
        self.users_count = 0
        self.load_stats()
    
    def load_stats(self):
        """Load statistics from file if it exists."""
        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r') as f:
                    self.users_count = int(f.read().strip())
        except Exception as e:
            print(f"Error loading stats: {e}")
    
    def save_stats(self):
        """Save statistics to file."""
        try:
            with open(self.stats_file, 'w') as f:
                f.write(str(self.users_count))
        except Exception as e:
            print(f"Error saving stats: {e}")
    
    def increment_user_count(self):
        """Increment the count of users who have used the reporting function."""
        self.users_count += 1
        self.save_stats()
        return self.users_count
    
    def get_user_count(self):
        """Get the current count of users."""
        return self.users_count

# TikTok policy information
class TikTokPolicies:
    """Class containing information about TikTok's community guidelines."""
    
    @staticmethod
    def get_hate_speech_policy():
        """Return TikTok's hate speech policy information."""
        return {
            'title': 'TikTok Hate Speech Policy',
            'description': (
                "TikTok doesn't permit content that contains hate speech or involves hateful behavior, "
                "and we remove it from our platform."
            ),
            'examples': [
                "Attacks or promotes hatred against protected groups based on race, ethnicity, national origin, religion, etc.",
                "Denies well-documented and violent events",
                "Promotes or supports hateful ideologies",
                "Uses slurs or dehumanizing references",
                "Incites fear or promotes violence against protected groups"
            ],
            'why_report': (
                "Reporting hate speech helps keep TikTok a safe place for everyone. "
                "Multiple reports on the same content increase the likelihood of it being reviewed quickly."
            )
        }
