#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple Test Bot for Telegram using python-telegram-bot v20.7
"""

import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ParseMode  # Note: ParseMode moved to constants in v20+
from telegram.ext import Application, CommandHandler, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        "✅ Bot is working correctly! This is a test for the TikTok Report Bot.\n\n"
        "Your bot token is valid and the bot is active."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        "This is a test bot for verifying your Telegram Bot Token.\n\n"
        "Commands:\n"
        "/start - Test if the bot is working\n"
        "/help - Show this help message"
    )

def main():
    """Start the bot."""
    # Load environment variables
    load_dotenv()
    
    # Get token from environment variable
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("No token provided in .env file!")
        return
    
    # Create the Application and pass it your bot's token
    application = Application.builder().token(token).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))

    # Start the Bot
    logger.info("Starting test bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
