#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
import asyncio
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from telegram.constants import ParseMode

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get the webapp URL from environment
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://muradtadesse.com/tiktok_bot/webapp")
logger.info(f"Using WebApp URL: {WEBAPP_URL}")

# Database setup
def setup_database():
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    
    # Create users table if not exists
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        last_name TEXT,
        join_date DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create reports table if not exists
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        target_account TEXT,
        reason TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        verified BOOLEAN DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )
    ''')
    
    # Create campaigns table if not exists
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS campaigns (
        id INTEGER PRIMARY KEY,
        target_account TEXT,
        reason TEXT,
        description TEXT,
        start_date DATETIME,
        end_date DATETIME,
        goal INTEGER DEFAULT 100,
        active BOOLEAN DEFAULT 1
    )
    ''')
    
    # Create errors table if not exists
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS errors (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        error_message TEXT,
        traceback TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Database setup complete")

# User registration
def register_user(user_id, username, first_name, last_name):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT OR IGNORE INTO users (user_id, username, first_name, last_name)
    VALUES (?, ?, ?, ?)
    ''', (user_id, username, first_name, last_name))
    
    conn.commit()
    conn.close()

# Log a report
def log_report(user_id, target_account, reason):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO reports (user_id, target_account, reason)
    VALUES (?, ?, ?)
    ''', (user_id, target_account, reason))
    
    report_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    
    return report_id

# Verify a report
def verify_report(report_id):
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    UPDATE reports SET verified = 1 WHERE id = ?
    ''', (report_id,))
    
    conn.commit()
    conn.close()

# Get reporting statistics
def get_stats():
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    
    # Get total number of reports
    cursor.execute('SELECT COUNT(*) FROM reports')
    total_reports = cursor.fetchone()[0]
    
    # Get number of verified reports
    cursor.execute('SELECT COUNT(*) FROM reports WHERE verified = 1')
    verified_reports = cursor.fetchone()[0]
    
    # Get number of unique reporters
    cursor.execute('SELECT COUNT(DISTINCT user_id) FROM reports')
    unique_reporters = cursor.fetchone()[0]
    
    # Get active campaign info
    cursor.execute('SELECT goal FROM campaigns WHERE active = 1 ORDER BY start_date DESC LIMIT 1')
    result = cursor.fetchone()
    campaign_goal = result[0] if result else 500
    
    conn.close()
    
    return {
        'total': total_reports,
        'verified': verified_reports,
        'reporters': unique_reporters,
        'goal': campaign_goal
    }

# Get active campaigns
def get_active_campaigns():
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT id, target_account, reason, description
    FROM campaigns 
    WHERE active = 1 AND start_date <= datetime('now') AND end_date >= datetime('now')
    ORDER BY start_date DESC
    ''')
    
    campaigns = cursor.fetchall()
    conn.close()
    
    return campaigns

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    register_user(user.id, user.username, user.first_name, user.last_name)
    
    # Create keyboard with new Modern WebApp button
    keyboard = [
        [InlineKeyboardButton("📱 Use Modern Report Helper", web_app=WebAppInfo(url=WEBAPP_URL))],
        [InlineKeyboardButton("⚠️ Report Account", callback_data="report")],
        [InlineKeyboardButton("📊 View Statistics", callback_data="stats")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_html(
        f"Hi {user.mention_html()}!\n\n"
        f"Welcome to the <b>TikTok Report Bot</b>. This bot helps coordinate reporting "
        f"campaigns against accounts that violate TikTok's community guidelines.\n\n"
        f"<b>NEW!</b> Try our modern report helper for a guided experience.\n\n"
        f"Please select an option below:",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("📱 Use Modern Report Helper", web_app=WebAppInfo(url=WEBAPP_URL))],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    help_text = (
        "<b>TikTok Report Bot - Help</b>\n\n"
        "This bot helps coordinate mass reporting campaigns against TikTok accounts "
        "that violate community guidelines such as hate speech, harassment, or harmful misinformation.\n\n"
        "<b>Commands:</b>\n"
        "/start - Start the bot and show the main menu\n"
        "/report - Start the reporting process\n"
        "/stats - View current campaign statistics\n"
        "/help - Show this help message\n\n"
        "<b>How to report:</b>\n"
        "1. Use our modern report helper for a guided experience\n"
        "2. Or select 'Report Account' from the menu\n"
        "3. Follow the on-screen instructions to report the account on TikTok\n"
        "4. Verify your report to help us track campaign progress\n\n"
        "Thank you for helping make TikTok safer!"
    )
    
    await update.message.reply_html(help_text, reply_markup=reply_markup)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_stats(update, context)

async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await start_report_process(update, context)

# Add a webapp command handler
async def webapp_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for the /webapp command"""
    keyboard = [[InlineKeyboardButton("📱 Open Modern Report Helper", web_app=WebAppInfo(url=WEBAPP_URL))]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Click the button below to open our modern reporting interface.\n"
        "It provides a step-by-step guide to help you report harmful accounts easily.",
        reply_markup=reply_markup
    )

# Handle WebApp data received from the webapp
async def webapp_data_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process data received from the WebApp"""
    try:
        # Get the data sent from the WebApp
        data = update.effective_message.web_app_data.data
        logger.info(f"Received WebApp data: {data}")
        
        # Parse the data (assuming JSON format)
        import json
        report_data = json.loads(data)
        
        # Process the report data
        user_id = update.effective_user.id
        target_account = report_data.get('target', '@effoyyt')
        reason = report_data.get('reason', 'Hate speech and hateful behaviors')
        
        # Log the report
        report_id = log_report(user_id, target_account, reason)
        
        # Verify the report automatically (since it was done through the WebApp)
        verify_report(report_id)
        
        # Acknowledge the report
        await update.message.reply_html(
            f"✅ <b>Report Submitted Successfully!</b>\n\n"
            f"Thank you for reporting {target_account} for {reason}.\n"
            f"Your contribution helps make TikTok a safer platform for everyone.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📊 View Statistics", callback_data="stats")],
                [InlineKeyboardButton("🔙 Back to Menu", callback_data="start")]
            ])
        )
    except Exception as e:
        logger.error(f"Error processing WebApp data: {e}")
        await update.message.reply_text(
            "Sorry, there was an error processing your report. Please try again."
        )

# Callback query handlers
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    if query.data == "start":
        keyboard = [
            [InlineKeyboardButton("📱 Use Modern Report Helper", web_app=WebAppInfo(url=WEBAPP_URL))],
            [InlineKeyboardButton("⚠️ Report Account", callback_data="report")],
            [InlineKeyboardButton("📊 View Statistics", callback_data="stats")],
            [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text="<b>TikTok Report Bot - Main Menu</b>\n\n"
                 "Please select an option:",
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    
    elif query.data == "help":
        keyboard = [
            [InlineKeyboardButton("📱 Use Modern Report Helper", web_app=WebAppInfo(url=WEBAPP_URL))],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        help_text = (
            "<b>TikTok Report Bot - Help</b>\n\n"
            "This bot helps coordinate mass reporting campaigns against TikTok accounts "
            "that violate community guidelines such as hate speech, harassment, or harmful misinformation.\n\n"
            "<b>Commands:</b>\n"
            "/start - Start the bot and show the main menu\n"
            "/report - Start the reporting process\n"
            "/stats - View current campaign statistics\n"
            "/help - Show this help message\n\n"
            "<b>How to report:</b>\n"
            "1. Use our modern report helper for a guided experience\n"
            "2. Or select 'Report Account' from the menu\n"
            "3. Follow the on-screen instructions to report the account on TikTok\n"
            "4. Verify your report to help us track campaign progress\n\n"
            "Thank you for helping make TikTok safer!"
        )
        
        await query.edit_message_text(
            text=help_text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    
    elif query.data == "stats":
        await send_stats(update, context, is_callback=True)
    
    elif query.data == "report":
        await start_report_process(update, context, is_callback=True)
    
    elif query.data.startswith("verify_"):
        report_id = int(query.data.split("_")[1])
        verify_report(report_id)
        
        keyboard = [
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text="✅ <b>Report Verified!</b>\n\n"
                 "Thank you for your contribution to making TikTok safer.\n"
                 "Your report has been verified and added to our campaign statistics.",
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    
    elif query.data.startswith("campaign_"):
        campaign_id = int(query.data.split("_")[1])
        await show_campaign_details(update, context, campaign_id, is_callback=True)

# Helper functions
async def send_stats(update: Update, context: ContextTypes.DEFAULT_TYPE, is_callback=False) -> None:
    stats = get_stats()
    
    stats_text = (
        "📊 <b>Reporting Statistics</b>\n\n"
        f"Current reporting campaign statistics:\n\n"
        f"• Reports submitted: {stats['total']}\n"
        f"• Verified reports: {stats['verified']}\n"
        f"• Unique reporters: {stats['reporters']}\n"
        f"• Campaign goal: {stats['goal']} reports\n"
    )
    
    keyboard = [
        [InlineKeyboardButton("📱 Use Modern Report Helper", web_app=WebAppInfo(url=WEBAPP_URL))],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if is_callback:
        await update.callback_query.edit_message_text(
            text=stats_text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    else:
        await update.message.reply_html(stats_text, reply_markup=reply_markup)

async def start_report_process(update: Update, context: ContextTypes.DEFAULT_TYPE, is_callback=False) -> None:
    campaigns = get_active_campaigns()
    
    if not campaigns:
        # Use a default campaign if none are active
        report_text = (
            "⚠️ <b>Report Account</b>\n\n"
            "Report <b>@effoyyt</b> (@effoyyt)\n\n"
            "Reason: <i>Hate speech and hateful behaviors</i>\n\n"
            "URL: https://www.tiktok.com/@effoyyt\n\n"
            "Follow the steps below and then verify your report."
        )
        
        # Log the report
        user_id = update.effective_user.id
        report_id = log_report(user_id, "@effoyyt", "Hate speech and hateful behaviors")
        
        # Create instruction steps
        instruction_text = (
            "<b>How to Report a TikTok Account:</b>\n\n"
            "1. Open TikTok and go to the account profile\n"
            "2. Tap the three dots (⋯) in the top right corner\n"
            "3. Select 'Report'\n"
            "4. Choose the reason: <b>Hate Speech</b>\n"
            "5. Follow the on-screen prompts to complete\n"
            "6. Return here and verify you completed the report"
        )
        
        keyboard = [
            [InlineKeyboardButton("📱 Use Modern Report Helper", web_app=WebAppInfo(url=f"{WEBAPP_URL}?account=@effoyyt&reason=Hate speech"))],
            [InlineKeyboardButton("📱 Open TikTok", url="https://www.tiktok.com/@effoyyt")],
            [InlineKeyboardButton("✅ I've Reported", callback_data=f"verify_{report_id}")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if is_callback:
            await update.callback_query.edit_message_text(
                text=report_text + "\n\n" + instruction_text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML
            )
        else:
            await update.message.reply_html(
                report_text + "\n\n" + instruction_text,
                reply_markup=reply_markup
            )
    else:
        # If we have active campaigns, show a list to choose from
        text = "<b>Active Reporting Campaigns</b>\n\nPlease select a campaign to participate in:"
        
        keyboard = []
        # Add WebApp button at the top
        keyboard.append([InlineKeyboardButton(
            "📱 Use Modern Report Helper",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )])
        
        for campaign in campaigns:
            campaign_id, target, reason, _ = campaign
            keyboard.append([InlineKeyboardButton(
                f"Report {target} - {reason[:20]}...",
                callback_data=f"campaign_{campaign_id}"
            )])
        
        keyboard.append([InlineKeyboardButton("🔙 Back to Menu", callback_data="start")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if is_callback:
            await update.callback_query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML
            )
        else:
            await update.message.reply_html(text, reply_markup=reply_markup)

async def show_campaign_details(update: Update, context: ContextTypes.DEFAULT_TYPE, campaign_id, is_callback=False) -> None:
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT target_account, reason, description
    FROM campaigns 
    WHERE id = ?
    ''', (campaign_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        text = "Error: Campaign not found."
        keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="start")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if is_callback:
            await update.callback_query.edit_message_text(
                text=text,
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(text, reply_markup=reply_markup)
        return
    
    target_account, reason, description = result
    
    # Log the report
    user_id = update.effective_user.id
    report_id = log_report(user_id, target_account, reason)
    
    report_text = (
        f"⚠️ <b>Report {target_account}</b>\n\n"
        f"Reason: <i>{reason}</i>\n\n"
        f"URL: https://www.tiktok.com/{target_account.replace('@', '')}\n\n"
        f"{description}\n\n"
        f"Follow the steps below and then verify your report."
    )
    
    instruction_text = (
        "<b>How to Report a TikTok Account:</b>\n\n"
        "1. Open TikTok and go to the account profile\n"
        "2. Tap the three dots (⋯) in the top right corner\n"
        "3. Select 'Report'\n"
        f"4. Choose the reason: <b>{reason}</b>\n"
        "5. Follow the on-screen prompts to complete\n"
        "6. Return here and verify you completed the report"
    )
    
    # Create WebApp URL with parameters
    webapp_params = f"?account={target_account}&reason={reason}&campaign={campaign_id}"
    
    keyboard = [
        [InlineKeyboardButton("📱 Use Modern Report Helper", web_app=WebAppInfo(url=f"{WEBAPP_URL}{webapp_params}"))],
        [InlineKeyboardButton("📱 Open TikTok", url=f"https://www.tiktok.com/{target_account.replace('@', '')}")],
        [InlineKeyboardButton("✅ I've Reported", callback_data=f"verify_{report_id}")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if is_callback:
        await update.callback_query.edit_message_text(
            text=report_text + "\n\n" + instruction_text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    else:
        await update.message.reply_html(
            report_text + "\n\n" + instruction_text,
            reply_markup=reply_markup
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a message to the user."""
    logger.error("Exception while handling an update:", exc_info=context.error)
    
    # Log to database if possible
    try:
        user_id = update.effective_user.id if update and update.effective_user else 0
        error_message = str(context.error)
        error_traceback = ''.join(context.error.__traceback__.format())
        
        conn = sqlite3.connect('bot_database.db')
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO errors (user_id, error_message, traceback)
        VALUES (?, ?, ?)
        ''', (user_id, error_message, error_traceback[:500]))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to log error to database: {e}")
    
    # Notify user
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "Sorry, something went wrong. The error has been logged and will be addressed."
            )
    except Exception:
        pass

def main() -> None:
    """Start the bot."""
    # Set up the database
    setup_database()
    
    # Create a default campaign if none exists
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM campaigns')
    if cursor.fetchone()[0] == 0:
        # Insert a default campaign
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        end_date = datetime.now().replace(year=datetime.now().year + 1).strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
        INSERT INTO campaigns (target_account, reason, description, start_date, end_date, goal, active)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ('@effoyyt', 'Hate speech and hateful behaviors', 
              'This account consistently posts content containing hate speech targeting ethnic groups.', 
              now, end_date, 500, 1))
        conn.commit()
    conn.close()
    
    # Create the Application
    application = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("report", report_command))
    application.add_handler(CommandHandler("webapp", webapp_command))  # New command for webapp
    
    # WebApp data handler
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, webapp_data_handler))
    
    # Add callback query handler
    application.add_handler(CallbackQueryHandler(button))
    
    # Add error handler
    application.add_error_handler(error_handler)

    # Run the bot
    logger.info("Starting bot...")
    application.run_polling()

if __name__ == "__main__":
    main()
