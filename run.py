#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple launcher for the TikTok Report Bot
"""

import os
import sys
import logging
import asyncio
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("TikTokReportBot")

def main():
    # Load environment variables
    load_dotenv()
    
    # Check for token
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("No TELEGRAM_BOT_TOKEN found in .env file")
        return 1
    
    logger.info(f"Starting bot with token: {token[:5]}...{token[-5:]}")
    
    try:
        # Create necessary directories
        for directory in ["analytics", "images", "locales", "verification_images"]:
            if not os.path.exists(directory):
                os.makedirs(directory)
                logger.info(f"Created directory: {directory}")
        
        # Import and run the main function
        logger.info("Starting main.py...")
        from main import main as run_bot
        asyncio.run(run_bot())
        return 0
    except Exception as e:
        logger.error(f"Error running bot: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main())
