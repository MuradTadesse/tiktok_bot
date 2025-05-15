#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import datetime
import os
import time
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import asyncio
import threading

class CampaignManager:
    """Advanced campaign management system for coordinating reporting efforts."""
    
    def __init__(self, database, bot=None):
        """Initialize the campaign manager with database access."""
        self.db = database
        self.bot = bot
        self.active_campaigns = {}
        self.lock = threading.RLock()
        self.load_campaigns()
    
    def load_campaigns(self):
        """Load all active campaigns from the database."""
        with self.lock:
            # In a real implementation, this would query the database
            # For this demo, we'll use a sample campaign
            self.active_campaigns = {
                1: {
                    'id': 1,
                    'name': 'Report Harmful TikTok Account',
                    'target_account': 'effoyyt',
                    'description': 'This account has been spreading hate speech and needs to be reported.',
                    'start_date': '2025-05-01',
                    'end_date': '2025-05-30',
                    'goal': 1000,
                    'current_count': 468,
                    'status': 'active',
                    'created_by': 12345,
                    'channels': ['main', 'private'],
                    'verification_required': True,
                    'reminder_frequency': 24,  # hours
                    'report_milestones': [100, 250, 500, 750, 1000],
                    'participating_users': set(),
                    'verified_reports': set()
                }
            }
    
    def get_active_campaign(self, campaign_id=None):
        """Get details of an active campaign or the most active one if no ID provided."""
        with self.lock:
            if campaign_id and campaign_id in self.active_campaigns:
                return self.active_campaigns[campaign_id].copy()
            elif self.active_campaigns:
                # Get the most active campaign (highest current_count/goal ratio)
                return max(
                    self.active_campaigns.values(),
                    key=lambda c: c['current_count'] / c['goal'] if c['goal'] > 0 else 0
                ).copy()
            return None
    
    def create_campaign(self, name, target_account, description, start_date, end_date, 
                      goal, created_by, channels=None, verification_required=True):
        """Create a new reporting campaign."""
        with self.lock:
            # In a real implementation, this would insert into the database
            campaign_id = len(self.active_campaigns) + 1
            
            if not channels:
                channels = ['main']
            
            campaign = {
                'id': campaign_id,
                'name': name,
                'target_account': target_account,
                'description': description,
                'start_date': start_date,
                'end_date': end_date,
                'goal': goal,
                'current_count': 0,
                'status': 'active',
                'created_by': created_by,
                'channels': channels,
                'verification_required': verification_required,
                'reminder_frequency': 24,  # hours
                'report_milestones': [int(goal * x/10) for x in range(1, 11)],
                'participating_users': set(),
                'verified_reports': set()
            }
            
            self.active_campaigns[campaign_id] = campaign
            return campaign_id
    
    def update_campaign(self, campaign_id, **kwargs):
        """Update an existing campaign with new values."""
        with self.lock:
            if campaign_id not in self.active_campaigns:
                return False
            
            # Update the provided fields
            for key, value in kwargs.items():
                if key in self.active_campaigns[campaign_id]:
                    self.active_campaigns[campaign_id][key] = value
            
            return True
    
    def log_report(self, campaign_id, user_id, verified=False):
        """Log a user's report for a campaign."""
        with self.lock:
            if campaign_id not in self.active_campaigns:
                return False
            
            campaign = self.active_campaigns[campaign_id]
            
            # Add user to participating users
            campaign['participating_users'].add(user_id)
            
            # If verification is not required or the report is verified,
            # increment the counter and check milestones
            if not campaign['verification_required'] or verified:
                campaign['current_count'] += 1
                
                if verified:
                    campaign['verified_reports'].add(user_id)
                
                # Check if we've hit a milestone
                for milestone in sorted(campaign['report_milestones']):
                    if campaign['current_count'] == milestone:
                        self._notify_milestone_reached(campaign_id, milestone)
                        break
            
            return True
    
    def verify_report(self, campaign_id, user_id):
        """Verify a user's report for a campaign."""
        with self.lock:
            if campaign_id not in self.active_campaigns:
                return False
            
            campaign = self.active_campaigns[campaign_id]
            
            # If user already submitted an unverified report
            if user_id in campaign['participating_users'] and user_id not in campaign['verified_reports']:
                campaign['verified_reports'].add(user_id)
                campaign['current_count'] += 1
                
                # Check for milestones
                for milestone in sorted(campaign['report_milestones']):
                    if campaign['current_count'] == milestone:
                        self._notify_milestone_reached(campaign_id, milestone)
                        break
                
                return True
            
            return False
    
    def _notify_milestone_reached(self, campaign_id, milestone):
        """Send notification when a campaign reaches a milestone."""
        campaign = self.active_campaigns.get(campaign_id)
        if not campaign or not self.bot:
            return
        
        # In a real implementation, this would send messages to all appropriate channels
        # For this demo, we'll just log it
        print(f"Milestone reached: Campaign {campaign['name']} reached {milestone} reports!")
    
    def get_campaign_progress(self, campaign_id):
        """Get the current progress of a campaign."""
        with self.lock:
            if campaign_id not in self.active_campaigns:
                return None
            
            campaign = self.active_campaigns[campaign_id]
            
            # Calculate percentage
            percentage = (campaign['current_count'] / campaign['goal']) * 100 if campaign['goal'] > 0 else 0
            percentage = min(100, percentage)  # Cap at 100%
            
            # Calculate estimated completion
            if percentage > 0:
                start_date = datetime.datetime.strptime(campaign['start_date'], '%Y-%m-%d')
                end_date = datetime.datetime.strptime(campaign['end_date'], '%Y-%m-%d')
                campaign_duration = (end_date - start_date).days
                
                days_elapsed = (datetime.datetime.now() - start_date).days
                
                if days_elapsed > 0 and percentage < 100:
                    rate = percentage / days_elapsed
                    days_to_complete = 100 / rate if rate > 0 else float('inf')
                    
                    estimated_completion = start_date + datetime.timedelta(days=days_to_complete)
                    
                    if estimated_completion > end_date:
                        on_track = False
                        days_behind = (estimated_completion - end_date).days
                    else:
                        on_track = True
                        days_ahead = (end_date - estimated_completion).days
                else:
                    estimated_completion = None
                    on_track = None
                    days_behind = None
                    days_ahead = None
            else:
                estimated_completion = None
                on_track = None
                days_behind = None
                days_ahead = None
            
            return {
                'campaign': campaign['name'],
                'target_account': campaign['target_account'],
                'current': campaign['current_count'],
                'goal': campaign['goal'],
                'percentage': percentage,
                'participants': len(campaign['participating_users']),
                'verified_count': len(campaign['verified_reports']),
                'estimated_completion': estimated_completion.strftime('%Y-%m-%d') if estimated_completion else None,
                'on_track': on_track,
                'days_behind': days_behind,
                'days_ahead': days_ahead
            }
    
    def get_campaign_keyboard(self, campaign_id, include_verify=False):
        """Get an inline keyboard for a campaign."""
        campaign = self.get_active_campaign(campaign_id)
        if not campaign:
            return None
        
        progress = self.get_campaign_progress(campaign_id)
        
        keyboard = [
            [InlineKeyboardButton(f"📊 Progress: {progress['percentage']:.1f}%", 
                                 callback_data=f"campaign_progress_{campaign_id}")],
            [InlineKeyboardButton("🚨 Report Now", 
                                 callback_data=f"report_{campaign_id}")]
        ]
        
        if include_verify:
            keyboard.append([
                InlineKeyboardButton("✅ Verify My Report", 
                                   callback_data=f"verify_report_{campaign_id}")
            ])
        
        keyboard.append([
            InlineKeyboardButton("📢 Share Campaign", 
                               callback_data=f"share_campaign_{campaign_id}")
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    def get_campaign_details_message(self, campaign_id, language='en'):
        """Get a detailed message about a campaign."""
        campaign = self.get_active_campaign(campaign_id)
        if not campaign:
            return "Campaign not found."
        
        progress = self.get_campaign_progress(campaign_id)
        
        # Different messages based on language
        if language == 'am':
            message = (
                f"*{campaign['name']}*\n\n"
                f"ዒላማ አካውንት: @{campaign['target_account']}\n"
                f"መግለጫ: {campaign['description']}\n\n"
                f"እድገት: {progress['current']}/{progress['goal']} "
                f"({progress['percentage']:.1f}%)\n"
                f"ተሳታፊዎች: {progress['participants']}\n"
                f"የተረጋገጡ ሪፖርቶች: {progress['verified_count']}\n\n"
            )
            
            if progress['on_track'] is not None:
                if progress['on_track']:
                    message += f"በጊዜ ገደቡ ውስጥ ነን! {progress['days_ahead']} ቀናት ቀድመናል።\n"
                else:
                    message += f"ከጊዜ ገደቡ {progress['days_behind']} ቀናት ወደኋላ ነን።\n"
            
            message += (
                f"\nከ {campaign['start_date']} እስከ {campaign['end_date']}\n\n"
                "ይህን ሪፖርት ለማድረግ ከታች ያለውን የሪፖርት አድርግ አዝራር ይጫኑ።"
            )
        else:  # English
            message = (
                f"*{campaign['name']}*\n\n"
                f"Target Account: @{campaign['target_account']}\n"
                f"Description: {campaign['description']}\n\n"
                f"Progress: {progress['current']}/{progress['goal']} "
                f"({progress['percentage']:.1f}%)\n"
                f"Participants: {progress['participants']}\n"
                f"Verified Reports: {progress['verified_count']}\n\n"
            )
            
            if progress['on_track'] is not None:
                if progress['on_track']:
                    message += f"We're on track! {progress['days_ahead']} days ahead of schedule.\n"
                else:
                    message += f"We're {progress['days_behind']} days behind schedule.\n"
            
            message += (
                f"\nCampaign Period: {campaign['start_date']} to {campaign['end_date']}\n\n"
                "Click the Report Now button below to participate."
            )
        
        return message
    
    def start_reminder_service(self):
        """Start a background service to send reminders to users."""
        if not self.bot:
            return False
        
        thread = threading.Thread(target=self._reminder_service_loop, daemon=True)
        thread.start()
        return True
    
    def _reminder_service_loop(self):
        """Background thread for sending periodic reminders."""
        while True:
            try:
                # Check each campaign for users who need reminders
                for campaign_id, campaign in self.active_campaigns.items():
                    if campaign['status'] != 'active':
                        continue
                    
                    # Get users who haven't completed their reports
                    incomplete_users = campaign['participating_users'] - campaign['verified_reports']
                    
                    # In a real implementation, check the last reminder time for each user
                    # and only send if enough time has passed
                    
                    # Send reminders (in a real bot, this would use the actual bot.send_message)
                    for user_id in incomplete_users:
                        print(f"Sending reminder to user {user_id} for campaign {campaign_id}")
                
                # Sleep for an hour before checking again
                time.sleep(3600)
            except Exception as e:
                print(f"Error in reminder service: {e}")
                time.sleep(3600)  # Sleep and try again
    
    def get_leaderboard(self, campaign_id=None, limit=10):
        """Get a leaderboard of top users who have made verified reports."""
        # In a real implementation, this would query the database
        # For this demo, we'll return sample data
        
        leaderboard = []
        for i in range(1, limit + 1):
            leaderboard.append({
                'rank': i,
                'user_id': 10000 + i,
                'username': f"user{i}",
                'reports': 20 - i,
                'last_report': datetime.datetime.now().strftime('%Y-%m-%d')
            })
        
        return leaderboard
    
    def format_leaderboard_message(self, campaign_id=None, limit=10, language='en'):
        """Format a leaderboard message for display."""
        leaderboard = self.get_leaderboard(campaign_id, limit)
        
        if language == 'am':
            message = "*🏆 የሪፖርት አድራጊዎች ደረጃ*\n\n"
            for entry in leaderboard:
                message += f"{entry['rank']}. {entry['username']}: {entry['reports']} ሪፖርቶች\n"
        else:
            message = "*🏆 Reporting Leaderboard*\n\n"
            for entry in leaderboard:
                message += f"{entry['rank']}. {entry['username']}: {entry['reports']} reports\n"
        
        return message
