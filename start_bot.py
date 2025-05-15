#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TikTok Report Bot Launcher
--------------------------
Simple script to start the TikTok reporting bot and handle any initialization errors.
"""

import os
import sys
import logging
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot_log.txt"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("TikTokReportBot")

def check_dependencies():
    """Check if all required dependencies are installed."""
    import importlib
    
    # Package name mapping to actual import names
    packages = {
        "python-telegram-bot": "telegram",
        "requests": "requests",
        "python-dotenv": "dotenv.main",
        "pillow": "PIL",
        "matplotlib": "matplotlib",
        "numpy": "numpy",
        "opencv-python": "cv2",
        "pytesseract": "pytesseract"
    }
    
    missing = []
    
    for package_name, import_name in packages.items():
        try:
            importlib.import_module(import_name)
            logger.info(f"✓ {package_name} is installed")
        except ImportError:
            missing.append(package_name)
            logger.error(f"✗ {package_name} is missing")
    
    return missing

def check_environment():
    """Check if the environment is properly configured."""
    from dotenv import load_dotenv
    load_dotenv()
    
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        return False
    return True

def create_directories():
    """Create necessary directories if they don't exist."""
    directories = [
        "analytics",
        "images",
        "locales",
        "verification_images"
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"Created directory: {directory}")

def main():
    """Main entry point for starting the bot."""
    try:
        logger.info("Starting TikTok Report Bot...")
        
        # Check dependencies
        missing = check_dependencies()
        if missing:
            logger.error(f"Missing dependencies: {', '.join(missing)}")
            logger.error("Please install them using: pip install -r requirements.txt")
            return 1
        
        # Check environment
        if not check_environment():
            logger.error("Environment not configured correctly. Check your .env file.")
            return 1
        
        # Create necessary directories
        create_directories()
        
        # Import and run the bot
        logger.info("Initializing bot...")
        from main import main as run_bot
        import asyncio
        
        # Run the bot
        asyncio.run(run_bot())
        
        return 0
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main())
