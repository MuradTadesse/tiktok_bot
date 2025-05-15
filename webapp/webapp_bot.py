#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TikTok Report Helper - Web App Integration
Created by Murad Tadesse

This module handles the integration between the Telegram bot and the web application.
It provides in-app browser functionality for guiding users through the TikTok reporting process.
"""

import os
import json
import logging
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL", "http://localhost:8000")

# Database setup
DB_PATH = Path("reports.db")

def init_db():
    """Initialize the SQLite database for storing report information."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create tables if they don't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        last_name TEXT,
        registration_date TEXT,
        last_active TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS campaigns (
        campaign_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        target_account TEXT NOT NULL,
        reason TEXT NOT NULL,
        created_at TEXT,
        created_by INTEGER,
        status TEXT DEFAULT 'active',
        FOREIGN KEY (created_by) REFERENCES users(user_id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reports (
        report_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        campaign_id INTEGER,
        target_account TEXT NOT NULL,
        reason TEXT NOT NULL,
        timestamp TEXT,
        status TEXT DEFAULT 'completed',
        platform TEXT DEFAULT 'tiktok',
        FOREIGN KEY (user_id) REFERENCES users(user_id),
        FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id)
    )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Database initialized")

def record_user(user_id, username, first_name, last_name):
    """Record or update user information in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    
    # Check if user already exists
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    
    if result:
        # Update existing user
        cursor.execute(
            "UPDATE users SET username = ?, first_name = ?, last_name = ?, last_active = ? WHERE user_id = ?",
            (username, first_name, last_name, now, user_id)
        )
    else:
        # Insert new user
        cursor.execute(
            "INSERT INTO users (user_id, username, first_name, last_name, registration_date, last_active) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, username, first_name, last_name, now, now)
        )
    
    conn.commit()
    conn.close()

def record_report(user_id, target_account, reason, campaign_id=None):
    """Record a completed report in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    
    cursor.execute(
        "INSERT INTO reports (user_id, campaign_id, target_account, reason, timestamp) VALUES (?, ?, ?, ?, ?)",
        (user_id, campaign_id, target_account, reason, now)
    )
    
    report_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    
    return report_id

class TikTokReportWebApp:
    """TikTok Report Web App integration class."""
    
    def __init__(self, token):
        """Initialize the web app bot with the given token."""
        self.application = Application.builder().token(token).build()
        
        # Initialize database
        init_db()
        
        # Register handlers
        self.register_handlers()
        
        logger.info("TikTok Report Web App initialized")
    
    def register_handlers(self):
        """Register command and callback handlers."""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("report", self.report_command))
        self.application.add_handler(CommandHandler("campaigns", self.campaigns_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        
        # Callback query handlers
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Message handlers
        self.application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, self.web_app_data))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /start command."""
        user = update.effective_user
        record_user(user.id, user.username, user.first_name, user.last_name)
        
        welcome_text = (
            f"👋 Hello, {user.first_name}!\n\n"
            f"Welcome to the TikTok Report Helper Bot. This bot helps you report harmful TikTok accounts "
            f"that violate community guidelines.\n\n"
            f"Use /report to start the reporting process or /help to see all available commands."
        )
        
        report_button = InlineKeyboardButton(
            "Start Reporting",
            callback_data="start_reporting"
        )
        
        keyboard = InlineKeyboardMarkup([[report_button]])
        
        await update.message.reply_text(welcome_text, reply_markup=keyboard)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /help command."""
        help_text = (
            "🛡️ *TikTok Report Helper Bot Commands*\n\n"
            "/start - Start the bot and see welcome message\n"
            "/help - Show this help message\n"
            "/report - Start the reporting process\n"
            "/campaigns - View active reporting campaigns\n"
            "/stats - View your reporting statistics\n\n"
            "To report a TikTok account, simply use the /report command and follow the guided process."
        )
        
        await update.message.reply_text(help_text, parse_mode="Markdown")
    
    async def report_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /report command."""
        user = update.effective_user
        record_user(user.id, user.username, user.first_name, user.last_name)
        
        # Create web app button for reporting
        webapp_button = InlineKeyboardButton(
            "Open Report Helper",
            web_app=WebAppInfo(url=f"{WEBAPP_URL}/index.html")
        )
        
        keyboard = InlineKeyboardMarkup([[webapp_button]])
        
        await update.message.reply_text(
            "Click the button below to open our Report Helper web app. "
            "You'll be guided through the process step by step.",
            reply_markup=keyboard
        )
    
    async def campaigns_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /campaigns command."""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM campaigns WHERE status = 'active' ORDER BY created_at DESC LIMIT 5"
        )
        
        campaigns = cursor.fetchall()
        conn.close()
        
        if not campaigns:
            await update.message.reply_text(
                "No active campaigns at the moment. Check back later or start your own report using /report."
            )
            return
        
        response = "🚨 *Active Reporting Campaigns*\n\n"
        
        for campaign in campaigns:
            target = campaign['target_account']
            reason = campaign['reason']
            name = campaign['name']
            
            # Create a webapp URL with campaign parameters
            campaign_params = f"account={target}&reason={reason}&campaign={campaign['campaign_id']}"
            webapp_url = f"{WEBAPP_URL}/index.html?{campaign_params}"
            
            button = InlineKeyboardButton(
                f"Report {target}",
                web_app=WebAppInfo(url=webapp_url)
            )
            
            keyboard = InlineKeyboardMarkup([[button]])
            
            campaign_text = (
                f"📣 *Campaign: {name}*\n"
                f"Target: {target}\n"
                f"Reason: {reason}\n\n"
            )
            
            await update.message.reply_text(campaign_text, parse_mode="Markdown", reply_markup=keyboard)
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /stats command."""
        user = update.effective_user
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get user's report count
        cursor.execute(
            "SELECT COUNT(*) FROM reports WHERE user_id = ?",
            (user.id,)
        )
        report_count = cursor.fetchone()[0]
        
        # Get count of unique accounts reported by the user
        cursor.execute(
            "SELECT COUNT(DISTINCT target_account) FROM reports WHERE user_id = ?",
            (user.id,)
        )
        unique_accounts = cursor.fetchone()[0]
        
        # Get user's first report date
        cursor.execute(
            "SELECT MIN(timestamp) FROM reports WHERE user_id = ?",
            (user.id,)
        )
        first_report = cursor.fetchone()[0]
        
        # Get latest report
        cursor.execute(
            "SELECT target_account, timestamp FROM reports WHERE user_id = ? ORDER BY timestamp DESC LIMIT 1",
            (user.id,)
        )
        latest_report = cursor.fetchone()
        
        conn.close()
        
        if report_count == 0:
            await update.message.reply_text(
                "You haven't submitted any reports yet. Use /report to get started!"
            )
            return
        
        stats_text = (
            f"📊 *Your Reporting Statistics*\n\n"
            f"Total reports submitted: {report_count}\n"
            f"Unique accounts reported: {unique_accounts}\n"
        )
        
        if first_report:
            first_date = datetime.fromisoformat(first_report).strftime("%Y-%m-%d")
            stats_text += f"First report submitted: {first_date}\n"
        
        if latest_report:
            latest_account, latest_timestamp = latest_report
            latest_date = datetime.fromisoformat(latest_timestamp).strftime("%Y-%m-%d")
            stats_text += f"Latest report: {latest_account} on {latest_date}\n"
        
        report_button = InlineKeyboardButton(
            "Submit New Report",
            callback_data="start_reporting"
        )
        
        keyboard = InlineKeyboardMarkup([[report_button]])
        
        await update.message.reply_text(stats_text, parse_mode="Markdown", reply_markup=keyboard)
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callback queries."""
        query = update.callback_query
        await query.answer()
        
        if query.data == "start_reporting":
            # Create web app button for reporting
            webapp_button = InlineKeyboardButton(
                "Open Report Helper",
                web_app=WebAppInfo(url=f"{WEBAPP_URL}/index.html")
            )
            
            keyboard = InlineKeyboardMarkup([[webapp_button]])
            
            await query.edit_message_text(
                "Click the button below to open our Report Helper web app. "
                "You'll be guided through the process step by step.",
                reply_markup=keyboard
            )
    
    async def web_app_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle data sent from the web app."""
        user = update.effective_user
        data = json.loads(update.effective_message.web_app_data.data)
        
        if data.get('action') == 'report_completed':
            target_account = data.get('target', '')
            reason = data.get('reason', '')
            campaign_id = data.get('campaign')
            
            if campaign_id and campaign_id.isdigit():
                campaign_id = int(campaign_id)
            else:
                campaign_id = None
            
            # Record the report in the database
            report_id = record_report(user.id, target_account, reason, campaign_id)
            
            # Send confirmation message
            await update.message.reply_text(
                f"✅ Thank you for your report!\n\n"
                f"Your report against {target_account} has been recorded.\n"
                f"Report ID: #{report_id}\n\n"
                f"Together we're making TikTok a safer platform."
            )
    
    async def run(self):
        """Run the bot."""
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        
        logger.info("Bot started, press Ctrl+C to stop")
        
        # Run the bot until the user presses Ctrl+C
        await self.application.updater.stop()
        await self.application.stop()
        await self.application.shutdown()

async def main():
    """Run the bot as a standalone application."""
    bot = TikTokReportWebApp(TOKEN)
    await bot.run()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
