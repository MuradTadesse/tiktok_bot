#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import datetime
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import CallbackContext
import io
from PIL import Image, ImageDraw, ImageFont

class AdminPanel:
    """Advanced admin panel for bot management and campaign coordination."""
    
    def __init__(self, database, campaign_manager, analytics_dashboard):
        """Initialize the admin panel with necessary components."""
        self.db = database
        self.campaign_manager = campaign_manager
        self.analytics = analytics_dashboard
        self.admin_commands = self._get_admin_commands()
    
    def _get_admin_commands(self):
        """Get dictionary of admin commands and their handlers."""
        return {
            'stats': self.show_stats,
            'dashboard': self.show_dashboard,
            'campaign': self.manage_campaign,
            'broadcast': self.send_broadcast,
            'users': self.manage_users,
            'settings': self.bot_settings,
            'verification': self.verification_settings,
            'languages': self.language_settings,
            'export': self.export_data,
            'help': self.admin_help
        }
    
    async def handle_admin_command(self, update: Update, context: CallbackContext):
        """Handle commands from admin users."""
        # Check if user is admin
        user_id = update.effective_user.id
        if not self.db.is_admin(user_id):
            await update.message.reply_text("You don't have permission to use admin commands.")
            return
        
        # Get the specific admin command
        command = context.args[0] if context.args else 'help'
        
        # Execute the appropriate handler
        if command in self.admin_commands:
            await self.admin_commands[command](update, context)
        else:
            await self.admin_help(update, context)
    
    async def admin_help(self, update: Update, context: CallbackContext):
        """Show admin help menu."""
        message = (
            "🔐 *TikTok Report Bot Admin Panel*\n\n"
            "Available commands:\n\n"
            "/admin stats - View current statistics\n"
            "/admin dashboard - Get analytics dashboard\n"
            "/admin campaign - Manage reporting campaigns\n"
            "/admin broadcast - Send message to all users\n"
            "/admin users - Manage users\n"
            "/admin settings - Bot configuration\n"
            "/admin verification - Report verification settings\n"
            "/admin languages - Manage supported languages\n"
            "/admin export - Export data\n"
            "/admin help - Show this help message"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("📊 Stats", callback_data="admin_stats"),
                InlineKeyboardButton("🖼️ Dashboard", callback_data="admin_dashboard")
            ],
            [
                InlineKeyboardButton("📢 Campaign", callback_data="admin_campaign"),
                InlineKeyboardButton("📣 Broadcast", callback_data="admin_broadcast")
            ],
            [
                InlineKeyboardButton("👥 Users", callback_data="admin_users"),
                InlineKeyboardButton("⚙️ Settings", callback_data="admin_settings")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    async def show_stats(self, update: Update, context: CallbackContext):
        """Show key statistics about the bot and campaigns."""
        # Get statistics from database
        # In a real implementation, these would come from actual database queries
        user_count = 152
        report_count = 468
        active_campaigns = 1
        verification_rate = 78
        
        # Get campaign statistics
        campaign = self.campaign_manager.get_active_campaign()
        progress = self.campaign_manager.get_campaign_progress(campaign['id']) if campaign else None
        
        message = (
            "📊 *Bot Statistics*\n\n"
            f"Total Users: *{user_count}*\n"
            f"Total Reports: *{report_count}*\n"
            f"Active Campaigns: *{active_campaigns}*\n"
            f"Verification Rate: *{verification_rate}%*\n\n"
        )
        
        if progress:
            message += (
                "🚨 *Current Campaign*\n\n"
                f"Name: *{campaign['name']}*\n"
                f"Target: *@{campaign['target_account']}*\n"
                f"Progress: *{progress['current']}/{progress['goal']}* (*{progress['percentage']:.1f}%*)\n"
                f"Participants: *{progress['participants']}*\n\n"
            )
            
            if progress['on_track'] is not None:
                if progress['on_track']:
                    message += f"Status: *On track* (_{progress['days_ahead']} days ahead_)\n"
                else:
                    message += f"Status: *Behind schedule* (_{progress['days_behind']} days behind_)\n"
        
        # Add recent activity
        recent_reports = 42  # Placeholder for actual data
        active_today = 37    # Placeholder for actual data
        
        message += (
            "📈 *Recent Activity (24h)*\n\n"
            f"New Reports: *{recent_reports}*\n"
            f"Active Users: *{active_today}*\n"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("🔄 Refresh", callback_data="admin_stats_refresh"),
                InlineKeyboardButton("📊 Full Dashboard", callback_data="admin_dashboard")
            ],
            [
                InlineKeyboardButton("🚨 Campaign Details", callback_data="admin_campaign"),
                InlineKeyboardButton("◀️ Back to Admin", callback_data="admin_menu")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    async def show_dashboard(self, update: Update, context: CallbackContext):
        """Generate and send the analytics dashboard."""
        await update.message.reply_text("Generating analytics dashboard... Please wait.")
        
        try:
            # Generate the dashboard image
            dashboard_buffer, dashboard_path = self.analytics.generate_dashboard_image()
            
            # Send the dashboard image
            await update.message.reply_photo(
                photo=dashboard_buffer,
                caption="📊 *TikTok Report Bot Analytics Dashboard*\n\nGenerated: " + 
                       datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Send follow-up message with options
            keyboard = [
                [
                    InlineKeyboardButton("📈 Report Trends", callback_data="admin_chart_reports"),
                    InlineKeyboardButton("👥 User Activity", callback_data="admin_chart_users")
                ],
                [
                    InlineKeyboardButton("🎯 Campaign Progress", callback_data="admin_chart_campaign"),
                    InlineKeyboardButton("🔄 Refresh Data", callback_data="admin_dashboard_refresh")
                ],
                [
                    InlineKeyboardButton("◀️ Back to Admin", callback_data="admin_menu")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "Select a specific chart to view or other options:",
                reply_markup=reply_markup
            )
            
        except Exception as e:
            await update.message.reply_text(f"Error generating dashboard: {e}")
    
    async def manage_campaign(self, update: Update, context: CallbackContext):
        """Campaign management interface."""
        # Get current active campaign
        campaign = self.campaign_manager.get_active_campaign()
        
        if not campaign:
            # No campaign exists, offer to create one
            message = (
                "🚨 *Campaign Management*\n\n"
                "No active campaigns found. Would you like to create a new campaign?"
            )
            
            keyboard = [
                [InlineKeyboardButton("➕ Create New Campaign", callback_data="admin_campaign_create")],
                [InlineKeyboardButton("◀️ Back to Admin", callback_data="admin_menu")]
            ]
            
        else:
            # Show existing campaign details
            progress = self.campaign_manager.get_campaign_progress(campaign['id'])
            
            message = (
                "🚨 *Campaign Management*\n\n"
                f"Current Campaign: *{campaign['name']}*\n"
                f"Target Account: *@{campaign['target_account']}*\n"
                f"Description: _{campaign['description']}_\n\n"
                f"Progress: *{progress['current']}/{progress['goal']}* (*{progress['percentage']:.1f}%*)\n"
                f"Participants: *{progress['participants']}*\n"
                f"Verified Reports: *{progress['verified_count']}*\n\n"
                f"Start Date: *{campaign['start_date']}*\n"
                f"End Date: *{campaign['end_date']}*\n"
            )
            
            keyboard = [
                [
                    InlineKeyboardButton("✏️ Edit Campaign", callback_data=f"admin_campaign_edit_{campaign['id']}"),
                    InlineKeyboardButton("❌ End Campaign", callback_data=f"admin_campaign_end_{campaign['id']}")
                ],
                [
                    InlineKeyboardButton("📊 Campaign Stats", callback_data=f"admin_campaign_stats_{campaign['id']}"),
                    InlineKeyboardButton("🏆 Leaderboard", callback_data=f"admin_campaign_leaderboard_{campaign['id']}")
                ],
                [
                    InlineKeyboardButton("📢 Send Reminder", callback_data=f"admin_campaign_remind_{campaign['id']}"),
                    InlineKeyboardButton("➕ New Campaign", callback_data="admin_campaign_create")
                ],
                [
                    InlineKeyboardButton("◀️ Back to Admin", callback_data="admin_menu")
                ]
            ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    async def send_broadcast(self, update: Update, context: CallbackContext):
        """Interface for sending broadcast messages to all users."""
        message = (
            "📣 *Broadcast Message*\n\n"
            "This will send a message to all bot users. Choose an option below:"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("📝 New Text Message", callback_data="admin_broadcast_text"),
                InlineKeyboardButton("🖼️ New Image Message", callback_data="admin_broadcast_image")
            ],
            [
                InlineKeyboardButton("📊 Campaign Update", callback_data="admin_broadcast_campaign"),
                InlineKeyboardButton("🏆 Leaderboard Update", callback_data="admin_broadcast_leaderboard")
            ],
            [
                InlineKeyboardButton("⚠️ Urgent Alert", callback_data="admin_broadcast_alert"),
                InlineKeyboardButton("🔔 Reminder", callback_data="admin_broadcast_reminder")
            ],
            [
                InlineKeyboardButton("◀️ Back to Admin", callback_data="admin_menu")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    async def manage_users(self, update: Update, context: CallbackContext):
        """User management interface."""
        message = (
            "👥 *User Management*\n\n"
            "What would you like to do?"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("👥 View All Users", callback_data="admin_users_view"),
                InlineKeyboardButton("🔍 Find User", callback_data="admin_users_find")
            ],
            [
                InlineKeyboardButton("➕ Add Admin", callback_data="admin_users_add_admin"),
                InlineKeyboardButton("🚫 Ban User", callback_data="admin_users_ban")
            ],
            [
                InlineKeyboardButton("📊 User Stats", callback_data="admin_users_stats"),
                InlineKeyboardButton("📧 Export Users", callback_data="admin_users_export")
            ],
            [
                InlineKeyboardButton("◀️ Back to Admin", callback_data="admin_menu")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    async def bot_settings(self, update: Update, context: CallbackContext):
        """Bot configuration settings interface."""
        message = (
            "⚙️ *Bot Settings*\n\n"
            "Configure bot behavior and features:"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("🌐 Language Settings", callback_data="admin_settings_language"),
                InlineKeyboardButton("🔔 Notification Settings", callback_data="admin_settings_notifications")
            ],
            [
                InlineKeyboardButton("🔐 Verification Settings", callback_data="admin_settings_verification"),
                InlineKeyboardButton("📊 Analytics Settings", callback_data="admin_settings_analytics")
            ],
            [
                InlineKeyboardButton("⚠️ Mode Settings", callback_data="admin_settings_mode"),
                InlineKeyboardButton("🛠️ Advanced Settings", callback_data="admin_settings_advanced")
            ],
            [
                InlineKeyboardButton("◀️ Back to Admin", callback_data="admin_menu")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    async def verification_settings(self, update: Update, context: CallbackContext):
        """Report verification settings interface."""
        # Get current verification settings
        # In a real implementation, this would come from the database
        require_verification = True
        verification_methods = ["Screenshot", "Confirmation Message"]
        auto_verify = False
        
        message = (
            "🔐 *Verification Settings*\n\n"
            f"Require Verification: *{'Yes' if require_verification else 'No'}*\n"
            f"Verification Methods: *{', '.join(verification_methods)}*\n"
            f"Auto-verify Reports: *{'Yes' if auto_verify else 'No'}*\n\n"
            "Configure how users verify their reports:"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("✅ Toggle Verification", callback_data="admin_verification_toggle"),
                InlineKeyboardButton("🔄 Change Methods", callback_data="admin_verification_methods")
            ],
            [
                InlineKeyboardButton("🤖 Toggle Auto-verify", callback_data="admin_verification_auto"),
                InlineKeyboardButton("🧪 Test Verification", callback_data="admin_verification_test")
            ],
            [
                InlineKeyboardButton("◀️ Back to Settings", callback_data="admin_settings")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    async def language_settings(self, update: Update, context: CallbackContext):
        """Language settings interface."""
        # Get current language settings
        # In a real implementation, this would come from the database
        default_language = "en"
        available_languages = ["en", "am"]
        
        message = (
            "🌐 *Language Settings*\n\n"
            f"Default Language: *{default_language}*\n"
            f"Available Languages: *{', '.join(available_languages)}*\n\n"
            "Manage language settings:"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("🔄 Change Default", callback_data="admin_language_default"),
                InlineKeyboardButton("➕ Add Language", callback_data="admin_language_add")
            ],
            [
                InlineKeyboardButton("📝 Edit Translations", callback_data="admin_language_edit"),
                InlineKeyboardButton("📤 Export Translations", callback_data="admin_language_export")
            ],
            [
                InlineKeyboardButton("◀️ Back to Settings", callback_data="admin_settings")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    async def export_data(self, update: Update, context: CallbackContext):
        """Data export interface."""
        message = (
            "📤 *Export Data*\n\n"
            "What data would you like to export?"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("👥 Users Data", callback_data="admin_export_users"),
                InlineKeyboardButton("📊 Reports Data", callback_data="admin_export_reports")
            ],
            [
                InlineKeyboardButton("🚨 Campaign Data", callback_data="admin_export_campaigns"),
                InlineKeyboardButton("📈 Analytics Data", callback_data="admin_export_analytics")
            ],
            [
                InlineKeyboardButton("🌐 Translations", callback_data="admin_export_translations"),
                InlineKeyboardButton("📑 All Data", callback_data="admin_export_all")
            ],
            [
                InlineKeyboardButton("◀️ Back to Admin", callback_data="admin_menu")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    async def handle_admin_callback(self, update: Update, context: CallbackContext):
        """Handle callback queries from admin panel buttons."""
        query = update.callback_query
        user_id = query.from_user.id
        
        # Verify the user is an admin
        if not self.db.is_admin(user_id):
            await query.answer("You don't have permission to access the admin panel.")
            return
        
        await query.answer()
        
        # Extract the callback data
        callback_data = query.data
        
        # Main admin menu
        if callback_data == "admin_menu":
            await self.admin_help(update, context)
            return
        
        # Handle other admin callbacks
        if callback_data.startswith("admin_stats"):
            await self.handle_stats_callback(update, context, callback_data)
        elif callback_data.startswith("admin_dashboard"):
            await self.handle_dashboard_callback(update, context, callback_data)
        elif callback_data.startswith("admin_campaign"):
            await self.handle_campaign_callback(update, context, callback_data)
        elif callback_data.startswith("admin_broadcast"):
            await self.handle_broadcast_callback(update, context, callback_data)
        elif callback_data.startswith("admin_users"):
            await self.handle_users_callback(update, context, callback_data)
        elif callback_data.startswith("admin_settings"):
            await self.handle_settings_callback(update, context, callback_data)
        elif callback_data.startswith("admin_verification"):
            await self.handle_verification_callback(update, context, callback_data)
        elif callback_data.startswith("admin_language"):
            await self.handle_language_callback(update, context, callback_data)
        elif callback_data.startswith("admin_export"):
            await self.handle_export_callback(update, context, callback_data)
        elif callback_data.startswith("admin_chart"):
            await self.handle_chart_callback(update, context, callback_data)
    
    # These handler methods would be implemented for each callback type
    async def handle_stats_callback(self, update, context, callback_data):
        """Handle stats-related callbacks."""
        if callback_data == "admin_stats_refresh":
            await self.show_stats(update, context)
    
    async def handle_dashboard_callback(self, update, context, callback_data):
        """Handle dashboard-related callbacks."""
        if callback_data == "admin_dashboard_refresh":
            await self.show_dashboard(update, context)
    
    async def handle_campaign_callback(self, update, context, callback_data):
        """Handle campaign-related callbacks."""
        pass  # Implementation would be added here
    
    async def handle_broadcast_callback(self, update, context, callback_data):
        """Handle broadcast-related callbacks."""
        pass  # Implementation would be added here
    
    async def handle_users_callback(self, update, context, callback_data):
        """Handle user management callbacks."""
        pass  # Implementation would be added here
    
    async def handle_settings_callback(self, update, context, callback_data):
        """Handle settings callbacks."""
        pass  # Implementation would be added here
    
    async def handle_verification_callback(self, update, context, callback_data):
        """Handle verification settings callbacks."""
        pass  # Implementation would be added here
    
    async def handle_language_callback(self, update, context, callback_data):
        """Handle language settings callbacks."""
        pass  # Implementation would be added here
    
    async def handle_export_callback(self, update, context, callback_data):
        """Handle data export callbacks."""
        pass  # Implementation would be added here
    
    async def handle_chart_callback(self, update, context, callback_data):
        """Handle chart display callbacks."""
        pass  # Implementation would be added here
