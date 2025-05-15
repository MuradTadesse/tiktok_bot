#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TikTok Report Bot Demo
----------------------
A simplified demo of the TikTok report bot to verify functionality with python-telegram-bot v20.7
"""

import logging
import os
import asyncio
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Target account info
TARGET_ACCOUNT = {
    "username": "effoyyt",
    "display_name": "አፎይ",
    "url": "https://www.tiktok.com/@effoyyt",
    "reason": "Hate speech and hateful behaviors",
    "description": "This account has been identified as spreading hate speech related to religion and race."
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    welcome_text = (
        f"👋 Welcome <b>{user.first_name}</b>!\n\n"
        f"This bot helps coordinate reporting of the TikTok account <b>{TARGET_ACCOUNT['display_name']}</b> "
        f"(@{TARGET_ACCOUNT['username']}) for {TARGET_ACCOUNT['reason']}.\n\n"
        f"What would you like to do?"
    )
    
    keyboard = [
        [InlineKeyboardButton("📝 Report Account", callback_data="report")],
        [InlineKeyboardButton("📋 Reporting Steps", callback_data="steps")],
        [InlineKeyboardButton("📊 View Statistics", callback_data="stats")],
        [InlineKeyboardButton("ℹ️ About", callback_data="about")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button callbacks."""
    query = update.callback_query
    await query.answer()  # Answer the callback query
    
    if query.data == "report":
        text = (
            f"<b>Report {TARGET_ACCOUNT['display_name']} (@{TARGET_ACCOUNT['username']})</b>\n\n"
            f"<b>Reason:</b> {TARGET_ACCOUNT['reason']}\n\n"
            f"<b>URL:</b> {TARGET_ACCOUNT['url']}\n\n"
            f"Follow the steps below and then verify your report."
        )
        
        keyboard = [
            [InlineKeyboardButton("📱 Open TikTok", url=TARGET_ACCOUNT['url'])],
            [InlineKeyboardButton("✅ I've Reported", callback_data="verify")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    
    elif query.data == "steps":
        text = (
            "<b>How to Report a TikTok Account:</b>\n\n"
            "1. Open TikTok and go to the account profile\n"
            "2. Tap the three dots (⋯) in the top right corner\n"
            "3. Select 'Report'\n"
            "4. Choose the reason: <i>Hate Speech</i>\n"
            "5. Follow the on-screen prompts to complete\n"
            "6. Return here and verify you completed the report"
        )
        
        keyboard = [
            [InlineKeyboardButton("📱 Open TikTok", url=TARGET_ACCOUNT['url'])],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    
    elif query.data == "stats":
        text = (
            "<b>📊 Reporting Statistics</b>\n\n"
            "Current reporting campaign statistics:\n\n"
            "• Reports submitted: <b>127</b>\n"
            "• Verified reports: <b>98</b>\n"
            "• Unique reporters: <b>84</b>\n"
            "• Campaign goal: <b>500 reports</b>\n\n"
            "<i>These are demo numbers for testing purposes</i>"
        )
        
        keyboard = [
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    
    elif query.data == "about":
        text = (
            "<b>About This Bot</b>\n\n"
            "This TikTok Report Bot helps coordinate mass reporting of accounts that violate TikTok's community guidelines.\n\n"
            "<b>Features:</b>\n"
            "• Multi-language support (English & Amharic)\n"
            "• Report verification system\n"
            "• Campaign management\n"
            "• Analytics dashboard\n"
            "• Natural language processing\n\n"
            "<b>Version:</b> 1.0.0"
        )
        
        keyboard = [
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    
    elif query.data == "verify":
        text = (
            "<b>Verification Options</b>\n\n"
            "Please verify that you've completed the reporting process by:\n\n"
            "1️⃣ Uploading a screenshot of your report confirmation\n\n"
            "2️⃣ Or confirming you've reported the account by clicking the button below"
        )
        
        keyboard = [
            [InlineKeyboardButton("✅ I've Reported This Account", callback_data="confirm_report")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    
    elif query.data == "confirm_report":
        text = (
            "✅ <b>Thank you for reporting!</b>\n\n"
            "Your report has been verified and added to our campaign statistics.\n\n"
            "Together we can make TikTok a safer platform for everyone."
        )
        
        keyboard = [
            [InlineKeyboardButton("📊 View Statistics", callback_data="stats")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    
    elif query.data == "back":
        # Go back to the main menu
        await start(update, context)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = (
        "<b>TikTok Report Bot Help</b>\n\n"
        "This bot helps coordinate reporting of harmful TikTok accounts.\n\n"
        "<b>Available commands:</b>\n"
        "/start - Start the bot and see main menu\n"
        "/report - Report the target account\n"
        "/steps - See step-by-step reporting instructions\n"
        "/stats - View reporting statistics\n"
        "/help - Show this help message"
    )
    
    await update.message.reply_text(
        help_text,
        parse_mode=ParseMode.HTML
    )

async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /report command."""
    text = (
        f"<b>Report {TARGET_ACCOUNT['display_name']} (@{TARGET_ACCOUNT['username']})</b>\n\n"
        f"<b>Reason:</b> {TARGET_ACCOUNT['reason']}\n\n"
        f"<b>URL:</b> {TARGET_ACCOUNT['url']}\n\n"
        f"Follow the steps below and then verify your report."
    )
    
    keyboard = [
        [InlineKeyboardButton("📱 Open TikTok", url=TARGET_ACCOUNT['url'])],
        [InlineKeyboardButton("✅ I've Reported", callback_data="verify")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        text,
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /stats command."""
    text = (
        "<b>📊 Reporting Statistics</b>\n\n"
        "Current reporting campaign statistics:\n\n"
        "• Reports submitted: <b>127</b>\n"
        "• Verified reports: <b>98</b>\n"
        "• Unique reporters: <b>84</b>\n"
        "• Campaign goal: <b>500 reports</b>\n\n"
        "<i>These are demo numbers for testing purposes</i>"
    )
    
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        text,
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors."""
    logger.error(f"Exception while handling an update: {context.error}")

def main() -> None:
    """Start the bot."""
    # Load environment variables
    load_dotenv()
    
    # Get the bot token
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("No token provided in .env file!")
        return
    
    # Create the Application
    application = Application.builder().token(token).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("report", report_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Add error handler
    application.add_error_handler(error_handler)

    # Run the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
