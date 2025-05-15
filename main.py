#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Advanced TikTok Report Telegram Bot
-----------------------------------
A comprehensive bot for coordinating reporting of harmful TikTok accounts.
This main file integrates all the specialized modules to create a feature-rich bot.
"""

import os
import logging
import asyncio
from datetime import datetime
from dotenv import load_dotenv
import json
import traceback

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, 
    ReplyKeyboardMarkup, KeyboardButton, BotCommand
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler,
    filters, ConversationHandler, ContextTypes
)

# Import all our custom modules
from database import Database
from nlp import NLPEngine
from localization import Localization
from analytics import AnalyticsDashboard
from campaign_manager import CampaignManager
from verification import VerificationSystem
from admin_panel import AdminPanel

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Conversation states
(START, MAIN_MENU, REPORT_FLOW, VERIFICATION_FLOW, SETTINGS_FLOW, 
 HELP_FLOW, ADMIN_FLOW, CAMPAIGN_FLOW, LANGUAGE_FLOW) = range(9)

# Create a class to manage the bot functionality
class TikTokReportBot:
    """Main class for the TikTok reporting bot."""
    
    def __init__(self):
        """Initialize the bot with all its components."""
        self.version = "1.0.0"
        
        # Initialize database
        self.db = Database()
        
        # Initialize NLP engine
        self.nlp = NLPEngine()
        
        # Initialize localization
        self.localization = Localization()
        
        # Initialize campaign manager
        self.campaign_manager = CampaignManager(self.db)
        
        # Initialize analytics
        self.analytics = AnalyticsDashboard(self.db)
        
        # Initialize verification system
        self.verification = VerificationSystem(self.db)
        
        # Initialize admin panel (needs to be after other components)
        self.admin_panel = AdminPanel(self.db, self.campaign_manager, self.analytics)
        
        # Target account info (could be moved to database/config in a real implementation)
        self.target_account = {
            "username": "effoyyt",
            "display_name": "አፎይ",
            "url": "https://www.tiktok.com/@effoyyt",
            "reason": "Hate speech and hateful behaviors",
            "description": "This account has been identified as spreading hate speech related to religion and race."
        }
    
    async def init_application(self):
        """Initialize and configure the application."""
        # Get token from environment variable
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            logger.error("No token provided. Set the TELEGRAM_BOT_TOKEN environment variable.")
            raise ValueError("Telegram bot token not found")
        
        # Create the Application with defaults for PTB v20+
        application = Application.builder().token(token).build()
        
        # Register command handlers
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("report", self.report_command))
        application.add_handler(CommandHandler("steps", self.steps_command))
        application.add_handler(CommandHandler("verify", self.verify_command))
        application.add_handler(CommandHandler("stats", self.stats_command))
        application.add_handler(CommandHandler("settings", self.settings_command))
        application.add_handler(CommandHandler("language", self.language_command))
        application.add_handler(CommandHandler("campaign", self.campaign_command))
        application.add_handler(CommandHandler("admin", self.admin_command))
        
        # Register general message handlers
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        application.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))
        
        # Register callback query handler
        application.add_handler(CallbackQueryHandler(self.handle_callback))
        
        # Register error handler
        application.add_error_handler(self.error_handler)
        
        # Set bot commands
        await self.set_commands(application)
        
        # Set the bot instance in the campaign manager
        self.campaign_manager.bot = application.bot
        
        return application
    
    async def set_commands(self, application):
        """Set the bot's command list."""
        commands = [
            BotCommand("start", "Start the bot and see the main menu"),
            BotCommand("report", "Report the target TikTok account"),
            BotCommand("steps", "See step-by-step reporting instructions"),
            BotCommand("verify", "Verify that you've completed reporting"),
            BotCommand("stats", "View reporting statistics"),
            BotCommand("settings", "Change your personal settings"),
            BotCommand("language", "Change the bot language"),
            BotCommand("help", "Get help with using the bot"),
        ]
        
        await application.bot.set_my_commands(commands)
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /start command."""
        user = update.effective_user
        
        # Add or update user in database
        self.db.add_user(
            user.id, 
            user.username, 
            user.first_name, 
            user.last_name,
            self._detect_user_language(update, context)
        )
        
        # Log this event
        self.db.log_analytics(user.id, 'command', '/start command')
        
        # Get user's language preference
        language = self._get_user_language(user.id)
        
        # Create custom welcome message
        welcome_text = self.localization.get('welcome', user_name=user.first_name, 
                                            target_name=self.target_account['display_name'])
        
        # Create keyboard with main options
        keyboard = [
            [InlineKeyboardButton(self.localization.get('report_button'), callback_data="report")],
            [InlineKeyboardButton(self.localization.get('steps_button'), callback_data="steps")],
            [InlineKeyboardButton(self.localization.get('about_button'), callback_data="about")],
            [InlineKeyboardButton(self.localization.get('help_button'), callback_data="help")],
            [InlineKeyboardButton("🌐 Language / ቋንቋ", callback_data="language")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send welcome message with the inline keyboard
        await update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        
        return MAIN_MENU
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /help command."""
        user_id = update.effective_user.id
        language = self._get_user_language(user_id)
        
        # Log this event
        self.db.log_analytics(user_id, 'command', '/help command')
        
        help_text = self.localization.get('help_text')
        
        keyboard = [
            [InlineKeyboardButton(self.localization.get('report_button'), callback_data="report")],
            [InlineKeyboardButton(self.localization.get('steps_button'), callback_data="steps")],
            [InlineKeyboardButton("🏠 " + self.localization.get('main_menu'), callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            help_text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        
        return HELP_FLOW
    
    async def report_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /report command."""
        user_id = update.effective_user.id
        language = self._get_user_language(user_id)
        
        # Log this event
        self.db.log_analytics(user_id, 'command', '/report command')
        
        # Show information about the account to report
        return await self._show_report_info(update, context)
    
    async def steps_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /steps command."""
        user_id = update.effective_user.id
        language = self._get_user_language(user_id)
        
        # Log this event
        self.db.log_analytics(user_id, 'command', '/steps command')
        
        # Show reporting steps
        return await self._show_report_steps(update, context)
    
    async def verify_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /verify command."""
        user_id = update.effective_user.id
        language = self._get_user_language(user_id)
        
        # Log this event
        self.db.log_analytics(user_id, 'command', '/verify command')
        
        # Start the verification flow
        return await self._start_verification_flow(update, context)
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /stats command."""
        user_id = update.effective_user.id
        language = self._get_user_language(user_id)
        
        # Log this event
        self.db.log_analytics(user_id, 'command', '/stats command')
        
        # Show campaign statistics
        active_campaign = self.campaign_manager.get_active_campaign()
        if active_campaign:
            campaign_id = active_campaign['id']
            progress = self.campaign_manager.get_campaign_progress(campaign_id)
            
            # Format stats message
            stats_message = (
                f"📊 *{self.localization.get('campaign_info', name=active_campaign['name'])}*\n\n"
                f"🎯 {self.localization.get('target_info', username=active_campaign['target_account'], display_name=self.target_account['display_name'])}\n\n"
                f"📈 {self.localization.get('campaign_progress', current=progress['current'], goal=progress['goal'], percentage=progress['percentage'])}\n\n"
                f"👥 {self.localization.get('users_stats', count=progress['participants'])}\n\n"
            )
            
            # Create keyboard with options
            keyboard = [
                [InlineKeyboardButton("📊 " + self.localization.get('report_button'), callback_data="report")],
                [InlineKeyboardButton("🔄 " + self.localization.get('refresh_button'), callback_data="refresh_stats")],
                [InlineKeyboardButton("🏠 " + self.localization.get('main_menu'), callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                stats_message,
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            # No active campaign
            await update.message.reply_text(
                self.localization.get('no_active_campaign'),
                parse_mode=ParseMode.MARKDOWN
            )
        
        return MAIN_MENU
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /settings command."""
        user_id = update.effective_user.id
        language = self._get_user_language(user_id)
        
        # Log this event
        self.db.log_analytics(user_id, 'command', '/settings command')
        
        # Get user preferences
        user = self.db.get_user(user_id)
        preferences = user.get('preferences', {}) if user else {}
        
        # Create settings message
        settings_message = (
            f"⚙️ *{self.localization.get('settings_title')}*\n\n"
            f"🌐 {self.localization.get('language_setting')}: `{language}`\n"
            f"🔔 {self.localization.get('notifications_setting')}: `{'On' if preferences.get('notifications', True) else 'Off'}`\n"
            f"📱 {self.localization.get('verification_setting')}: `{'Required' if preferences.get('verification', True) else 'Optional'}`\n"
        )
        
        # Create keyboard with settings options
        keyboard = [
            [InlineKeyboardButton("🌐 " + self.localization.get('change_language'), callback_data="change_language")],
            [InlineKeyboardButton("🔔 " + self.localization.get('toggle_notifications'), callback_data="toggle_notifications")],
            [InlineKeyboardButton("📱 " + self.localization.get('toggle_verification'), callback_data="toggle_verification")],
            [InlineKeyboardButton("🏠 " + self.localization.get('main_menu'), callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            settings_message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        
        return SETTINGS_FLOW
    
    async def language_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /language command."""
        user_id = update.effective_user.id
        
        # Log this event
        self.db.log_analytics(user_id, 'command', '/language command')
        
        # Show language selection
        return await self._show_language_selection(update, context)
    
    async def campaign_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /campaign command."""
        user_id = update.effective_user.id
        language = self._get_user_language(user_id)
        
        # Log this event
        self.db.log_analytics(user_id, 'command', '/campaign command')
        
        # Show active campaign details
        active_campaign = self.campaign_manager.get_active_campaign()
        if active_campaign:
            message = self.campaign_manager.get_campaign_details_message(active_campaign['id'], language)
            keyboard = self.campaign_manager.get_campaign_keyboard(active_campaign['id'], include_verify=True)
            
            await update.message.reply_text(
                message,
                reply_markup=keyboard,
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            # No active campaign
            await update.message.reply_text(
                self.localization.get('no_active_campaign'),
                parse_mode=ParseMode.MARKDOWN
            )
        
        return CAMPAIGN_FLOW
    
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /admin command."""
        user_id = update.effective_user.id
        
        # Check if user is admin
        if not self.db.is_admin(user_id):
            await update.message.reply_text(
                self.localization.get('admin_access_denied'),
                parse_mode=ParseMode.MARKDOWN
            )
            return MAIN_MENU
        
        # Log this event
        self.db.log_analytics(user_id, 'command', '/admin command')
        
        # Delegate to admin panel
        await self.admin_panel.handle_admin_command(update, context)
        
        return ADMIN_FLOW
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages."""
        user_id = update.effective_user.id
        language = self._get_user_language(user_id)
        message_text = update.message.text
        
        # Log this event
        self.db.log_analytics(user_id, 'message', 'Text message received')
        
        # Use NLP to detect intent and entities
        intent = self.nlp.detect_intent(message_text)
        entities = self.nlp.extract_entities(message_text)
        
        # Generate a smart response based on intent
        response = self.nlp.get_smart_response(intent, entities, language)
        
        # Handle verification messages
        if intent == 'verify':
            result = self.verification.validate_text_confirmation(message_text, self.target_account['username'])
            if result['verified']:
                # Log the report
                active_campaign = self.campaign_manager.get_active_campaign()
                if active_campaign:
                    self.campaign_manager.log_report(active_campaign['id'], user_id, verified=True)
                
                report_id = self.db.log_report(user_id, self.target_account['username'], 'hate_speech')
                self.db.verify_report(report_id)
                
                # Send confirmation
                await update.message.reply_text(
                    self.localization.get('thanks_report'),
                    parse_mode=ParseMode.MARKDOWN
                )
                
                # Show updated stats
                total_reports = self.db.get_report_count(self.target_account['username'])
                await update.message.reply_text(
                    self.localization.get('report_stats', count=total_reports),
                    parse_mode=ParseMode.MARKDOWN
                )
                
                return MAIN_MENU
        
        # Send the response
        keyboard = [
            [InlineKeyboardButton(self.localization.get('report_button'), callback_data="report")],
            [InlineKeyboardButton(self.localization.get('steps_button'), callback_data="steps")],
            [InlineKeyboardButton(self.localization.get('help_button'), callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            response,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        
        return MAIN_MENU
    
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle photo messages (for verification)."""
        user_id = update.effective_user.id
        language = self._get_user_language(user_id)
        
        # Log this event
        self.db.log_analytics(user_id, 'message', 'Photo received')
        
        # Get the photo file
        photo_file = await update.message.photo[-1].get_file()
        photo_bytes = await photo_file.download_as_bytearray()
        
        # Verify the screenshot
        verification_result = self.verification.verify_screenshot(photo_bytes, self.target_account['username'])
        
        if verification_result['verified']:
            # Log the verified report
            active_campaign = self.campaign_manager.get_active_campaign()
            if active_campaign:
                self.campaign_manager.log_report(active_campaign['id'], user_id, verified=True)
            
            report_id = self.db.log_report(user_id, self.target_account['username'], 'hate_speech')
            self.db.verify_report(report_id)
            
            # Send success message
            await update.message.reply_text(
                self.localization.get('verification_success'),
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Show updated stats
            total_reports = self.db.get_report_count(self.target_account['username'])
            await update.message.reply_text(
                self.localization.get('report_stats', count=total_reports),
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            # Verification failed
            await update.message.reply_text(
                self.localization.get('verification_failed') + f"\n\nConfidence: {verification_result['confidence']:.2f}",
                parse_mode=ParseMode.MARKDOWN
            )
        
        return MAIN_MENU
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from inline buttons."""
        query = update.callback_query
        user_id = query.from_user.id
        callback_data = query.data
        
        # Log this event
        self.db.log_analytics(user_id, 'callback', f'Callback: {callback_data}')
        
        # Always answer the callback query first
        await query.answer()
        
        # Admin panel callbacks
        if callback_data.startswith('admin_'):
            return await self.admin_panel.handle_admin_callback(update, context)
        
        # Campaign-related callbacks
        elif callback_data.startswith('campaign_'):
            return await self._handle_campaign_callback(update, context, callback_data)
        
        # Main menu callbacks
        elif callback_data == 'main_menu':
            return await self._show_main_menu(update, context)
        elif callback_data == 'report':
            return await self._show_report_info(update, context)
        elif callback_data == 'steps':
            return await self._show_report_steps(update, context)
        elif callback_data == 'about':
            return await self._show_about(update, context)
        elif callback_data == 'help':
            return await self._show_help(update, context)
        
        # Language selection
        elif callback_data == 'language' or callback_data.startswith('lang_'):
            return await self._handle_language_callback(update, context, callback_data)
        
        # Settings callbacks
        elif callback_data.startswith('toggle_') or callback_data == 'change_language':
            return await self._handle_settings_callback(update, context, callback_data)
        
        # Verification callbacks
        elif callback_data.startswith('verify_'):
            return await self._handle_verification_callback(update, context, callback_data)
        
        # Stats callbacks
        elif callback_data == 'refresh_stats':
            return await self.stats_command(update, context)
        
        # Default: return to main menu
        return await self._show_main_menu(update, context)
    
    async def _show_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show the main menu."""
        query = update.callback_query
        user_id = query.from_user.id
        language = self._get_user_language(user_id)
        
        # Create main menu message
        menu_text = (
            f"🏠 *{self.localization.get('main_menu')}*\n\n"
            f"_{self.localization.get('target_info', username=self.target_account['username'], display_name=self.target_account['display_name'])}_"
        )
        
        # Create keyboard with main options
        keyboard = [
            [InlineKeyboardButton(self.localization.get('report_button'), callback_data="report")],
            [InlineKeyboardButton(self.localization.get('steps_button'), callback_data="steps")],
            [InlineKeyboardButton(self.localization.get('about_button'), callback_data="about")],
            [InlineKeyboardButton(self.localization.get('help_button'), callback_data="help")],
            [InlineKeyboardButton("🌐 Language / ቋንቋ", callback_data="language")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Edit the message with the main menu
        await query.edit_message_text(
            menu_text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        
        return MAIN_MENU
    
    async def _show_report_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show information about the account to report."""
        # Handle both callback queries and direct commands
        if update.callback_query:
            query = update.callback_query
            message_obj = query
            edit_message = query.edit_message_text
        else:
            message_obj = update.message
            edit_message = message_obj.reply_text
        
        user_id = message_obj.from_user.id
        language = self._get_user_language(user_id)
        
        # Create report info message
        report_info = self.localization.get(
            'report_info',
            username=self.target_account['username'],
            display_name=self.target_account['display_name'],
            reason=self.target_account['reason'],
            url=self.target_account['url']
        )
        
        # Create keyboard with options
        keyboard = [
            [InlineKeyboardButton(self.localization.get('steps_button'), callback_data="steps")],
            [InlineKeyboardButton(self.localization.get('back_button'), callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send or edit the message
        await edit_message(
            report_info,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=False
        )
        
        return REPORT_FLOW
    
    async def _show_report_steps(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show step-by-step instructions for reporting."""
        # Handle both callback queries and direct commands
        if update.callback_query:
            query = update.callback_query
            message_obj = query
            edit_message = query.edit_message_text
        else:
            message_obj = update.message
            edit_message = message_obj.reply_text
        
        user_id = message_obj.from_user.id
        language = self._get_user_language(user_id)
        
        # Create steps message
        steps_message = (
            f"<b>📋 {self.localization.get('steps_title')}</b>\n\n"
            f"1️⃣ {self.localization.get('step_1', url=self.target_account['url'])}\n\n"
            f"2️⃣ {self.localization.get('step_2')}\n\n"
            f"3️⃣ {self.localization.get('step_3')}\n\n"
            f"4️⃣ {self.localization.get('step_4')}\n\n"
            f"5️⃣ {self.localization.get('step_5')}\n\n"
            f"6️⃣ {self.localization.get('step_6')}\n\n"
            f"7️⃣ {self.localization.get('step_7')}\n\n"
            f"8️⃣ {self.localization.get('step_8')}\n\n"
            f"⚠️ <b>{self.localization.get('steps_warning')}</b>"
        )
        
        # Create keyboard with options
        keyboard = [
            [InlineKeyboardButton(self.localization.get('show_images_button'), callback_data="show_images")],
            [
                InlineKeyboardButton(self.localization.get('verify_button'), callback_data="verify_report"),
                InlineKeyboardButton(self.localization.get('back_button'), callback_data="main_menu")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send or edit the message
        await edit_message(
            steps_message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True
        )
        
        return REPORT_FLOW
    async def _show_about(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show information about the bot."""
        query = update.callback_query
        user_id = query.from_user.id
        language = self._get_user_language(user_id)
        
        # Create about message
        about_message = (
            f"<b>ℹ️ {self.localization.get('about_title')}</b>\n\n"
            f"{self.localization.get('about_text')}\n\n"
            f"<b>{self.localization.get('bot_version', version=self.version)}</b>\n\n"
            f"<i>{self.localization.get('about_footer')}</i>"
        )
        
        # Create keyboard with options
        keyboard = [
            [InlineKeyboardButton(self.localization.get('back_button'), callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Edit the message
        await query.edit_message_text(
            about_message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        
        return MAIN_MENU
    
    async def _show_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help information."""
        query = update.callback_query
        user_id = query.from_user.id
        language = self._get_user_language(user_id)
        
        # Create help message
        help_message = (
            f"<b>❓ {self.localization.get('help_title')}</b>\n\n"
            f"{self.localization.get('help_text')}\n\n"
            f"<b>{self.localization.get('available_commands')}</b>\n"
            f"🔹 <b>/start</b> - {self.localization.get('start_command_desc')}\n"
            f"🔹 <b>/help</b> - {self.localization.get('help_command_desc')}\n"
            f"🔹 <b>/report</b> - {self.localization.get('report_command_desc')}\n"
            f"🔹 <b>/steps</b> - {self.localization.get('steps_command_desc')}\n"
            f"🔹 <b>/verify</b> - {self.localization.get('verify_command_desc')}\n"
            f"🔹 <b>/stats</b> - {self.localization.get('stats_command_desc')}\n"
            f"🔹 <b>/settings</b> - {self.localization.get('settings_command_desc')}\n"
            f"🔹 <b>/language</b> - {self.localization.get('language_command_desc')}\n\n"
            f"<b>{self.localization.get('contact_info')}</b>"
        )
        
        # Create keyboard with options
        keyboard = [
            [InlineKeyboardButton(self.localization.get('back_button'), callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Edit the message
        await query.edit_message_text(
            help_message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        
        return HELP_FLOW
    
    async def _start_verification_flow(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start the verification flow."""
        user_id = update.effective_user.id
        language = self._get_user_language(user_id)
        
        # Create verification message
        verification_message = (
            f"*{self.localization.get('verification_title')}*\n\n"
            f"{self.localization.get('verification_text')}\n\n"
            f"*{self.localization.get('verification_options')}*"
        )
        
        # Create keyboard with verification options
        keyboard = [
            [InlineKeyboardButton(self.localization.get('verify_photo_button'), callback_data="verify_photo")],
            [InlineKeyboardButton(self.localization.get('verify_text_button'), callback_data="verify_text")],
            [InlineKeyboardButton(self.localization.get('back_button'), callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send the message
        await update.message.reply_text(
            verification_message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        
        return VERIFICATION_FLOW
    
    async def _handle_verification_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle verification-related callbacks."""
        query = update.callback_query
        user_id = query.from_user.id
        language = self._get_user_language(user_id)
        callback_data = query.data
        
        if callback_data == "verify_report":
            # Start verification process
            verification_message = (
                f"*{self.localization.get('verification_title')}*\n\n"
                f"{self.localization.get('verification_text')}\n\n"
                f"*{self.localization.get('verification_options')}*"
            )
            
            keyboard = [
                [InlineKeyboardButton(self.localization.get('verify_photo_button'), callback_data="verify_photo")],
                [InlineKeyboardButton(self.localization.get('verify_text_button'), callback_data="verify_text")],
                [InlineKeyboardButton(self.localization.get('back_button'), callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                verification_message,
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
            
            return VERIFICATION_FLOW
            
        elif callback_data == "verify_photo":
            # Ask for screenshot
            await query.edit_message_text(
                self.localization.get('send_screenshot'),
                parse_mode=ParseMode.MARKDOWN
            )
            
            return VERIFICATION_FLOW
            
        elif callback_data == "verify_text":
            # Ask for text confirmation
            await query.edit_message_text(
                self.localization.get('send_text_confirmation'),
                parse_mode=ParseMode.MARKDOWN
            )
            
            return VERIFICATION_FLOW
        
        return MAIN_MENU
    
    async def _show_language_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show language selection options."""
        # Handle both callback queries and direct commands
        if update.callback_query:
            query = update.callback_query
            message_obj = query
            edit_message = query.edit_message_text
        else:
            message_obj = update.message
            edit_message = message_obj.reply_text
        
        user_id = message_obj.from_user.id
        
        # Get available languages
        languages = self.localization.get_available_languages()
        
        # Create language selection message
        language_message = (
            f"🌐 *{self.localization.get('choose_language')}*"
        )
        
        # Create keyboard with language options
        keyboard = []
        for lang_code in languages:
            lang_name = "English" if lang_code == "en" else "አማርኛ"
            keyboard.append([InlineKeyboardButton(lang_name, callback_data=f"lang_{lang_code}")])
        
        keyboard.append([InlineKeyboardButton(self.localization.get('back_button'), callback_data="main_menu")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send or edit the message
        await edit_message(
            language_message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        
        return LANGUAGE_FLOW
    
    async def _handle_language_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle language selection callbacks."""
        query = update.callback_query
        user_id = query.from_user.id
        callback_data = query.data
        
        if callback_data == "language":
            # Show language selection
            return await self._show_language_selection(update, context)
        
        elif callback_data.startswith("lang_"):
            # Set the selected language
            lang_code = callback_data.split("_")[1]
            
            # Update user preference in database
            self.db.set_user_preference(user_id, 'language', lang_code)
            
            # Log this event
            self.db.log_analytics(user_id, 'language_change', f'Language changed to {lang_code}')
            
            # Confirm language change
            await query.edit_message_text(
                self.localization.get('language_changed', language_code=lang_code),
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Return to main menu after a short delay
            await asyncio.sleep(2)
            return await self._show_main_menu(update, context)
        
        return MAIN_MENU
    
    async def _handle_settings_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle settings-related callbacks."""
        query = update.callback_query
        user_id = query.from_user.id
        callback_data = query.data
        
        if callback_data == "change_language":
            # Show language selection
            return await self._show_language_selection(update, context)
        
        elif callback_data == "toggle_notifications":
            # Toggle notifications setting
            user = self.db.get_user(user_id)
            preferences = user.get('preferences', {}) if user else {}
            current_setting = preferences.get('notifications', True)
            
            # Update setting to opposite of current
            self.db.set_user_preference(user_id, 'notifications', not current_setting)
            
            # Log this event
            self.db.log_analytics(user_id, 'settings_change', f'Notifications toggled to {not current_setting}')
            
            # Return to settings menu
            return await self.settings_command(update, context)
        
        elif callback_data == "toggle_verification":
            # Toggle verification setting
            user = self.db.get_user(user_id)
            preferences = user.get('preferences', {}) if user else {}
            current_setting = preferences.get('verification', True)
            
            # Update setting to opposite of current
            self.db.set_user_preference(user_id, 'verification', not current_setting)
            
            # Log this event
            self.db.log_analytics(user_id, 'settings_change', f'Verification toggled to {not current_setting}')
            
            # Return to settings menu
            return await self.settings_command(update, context)
        
        return SETTINGS_FLOW
    
    async def _handle_campaign_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Handle campaign-related callbacks."""
        query = update.callback_query
        user_id = query.from_user.id
        
        # Extract campaign ID if present
        campaign_id = None
        if '_' in callback_data:
            parts = callback_data.split('_')
            if len(parts) > 1 and parts[1].isdigit():
                campaign_id = int(parts[1])
        
        if callback_data.startswith("campaign_progress"):
            # Show campaign progress
            active_campaign = self.campaign_manager.get_active_campaign(campaign_id)
            if active_campaign:
                progress = self.campaign_manager.get_campaign_progress(active_campaign['id'])
                
                # Generate and send a progress chart
                chart_buffer = self.analytics.generate_campaign_progress_chart(active_campaign['id'])
                
                await query.message.reply_photo(
                    photo=chart_buffer,
                    caption=f"📊 *{self.localization.get('campaign_progress', current=progress['current'], goal=progress['goal'], percentage=progress['percentage'])}*",
                    parse_mode=ParseMode.MARKDOWN
                )
            
            return CAMPAIGN_FLOW
        
        elif callback_data.startswith("report_"):
            # Start the reporting process
            return await self._show_report_steps(update, context)
        
        elif callback_data.startswith("verify_report_"):
            # Start the verification process
            return await self._handle_verification_callback(update, context)
        
        elif callback_data.startswith("share_campaign_"):
            # Generate a shareable message
            active_campaign = self.campaign_manager.get_active_campaign(campaign_id)
            if active_campaign:
                share_text = (
                    f"🚨 *{self.localization.get('share_campaign_title')}*\n\n"
                    f"{self.localization.get('share_campaign_text', name=active_campaign['name'], username=active_campaign['target_account'])}\n\n"
                    f"[{self.localization.get('share_campaign_button')}](https://t.me/{context.bot.username}?start=campaign_{active_campaign['id']})"
                )
                
                await query.edit_message_text(
                    share_text,
                    parse_mode=ParseMode.MARKDOWN
                )
            
            return CAMPAIGN_FLOW
        
        return MAIN_MENU
    
    def _get_user_language(self, user_id: int) -> str:
        """Get the user's preferred language."""
        user = self.db.get_user(user_id)
        if user and 'preferences' in user and 'language' in user['preferences']:
            return user['preferences']['language']
        return "en"  # Default to English
    
    def _detect_user_language(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        """Detect the user's language from their Telegram client."""
        user_language_code = update.effective_user.language_code
        
        # Map Telegram language codes to our supported languages
        if user_language_code and user_language_code.startswith('am'):
            return 'am'
        return 'en'  # Default to English
    
    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle errors that occur in the dispatcher.
        This is a more robust implementation for PTB v20.7.
        """
        # Log the error before we do anything else
        logger.error(f"Exception while handling an update: {context.error}")
        
        # Format the traceback details
        error_traceback = ''.join(traceback.format_exception(None, context.error, context.error.__traceback__))
        logger.error(f"Error details: {error_traceback}")
        
        # Extract the update and if possible notify the user of the error
        if update and isinstance(update, Update) and update.effective_message:
            error_message = self.localization.get('system_error')
            
            # First try to notify the user
            try:
                await update.effective_message.reply_text(
                    error_message,
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception as e:
                logger.error(f"Failed to send error message: {e}")
        
        # Log the error to the database for admin review later
        try:
            if update and isinstance(update, Update) and update.effective_user:
                user_id = update.effective_user.id
                self.db.log_error(user_id, str(context.error), error_traceback[:500])
            else:
                self.db.log_error(0, str(context.error), error_traceback[:500])  # System error with no user
        except Exception as e:
            logger.error(f"Failed to log error to database: {e}")


async def main() -> None:
    """Start the bot."""
    try:
        # Initialize the bot
        tiktok_report_bot = TikTokReportBot()
        
        # Set up the application
        application = await tiktok_report_bot.init_application()
        
        # Start the campaign reminder service
        tiktok_report_bot.campaign_manager.start_reminder_service()
        
        # Run the bot until the user presses Ctrl-C
        await application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"Critical error: {e}")
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(main())