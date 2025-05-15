#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import json
import time
import threading
import os
from datetime import datetime

class Database:
    """SQLite database manager for the Telegram bot with advanced features."""
    
    def __init__(self, db_file="bot_data.db"):
        """Initialize the database connection and create tables if they don't exist."""
        self.db_file = db_file
        self.lock = threading.RLock()  # Thread-safe operations
        self._create_tables()
    
    def _get_connection(self):
        """Get a database connection with row factory for dictionary results."""
        conn = sqlite3.connect(self.db_file, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _create_tables(self):
        """Create all necessary database tables if they don't exist."""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Users table - stores user information and preferences
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    language TEXT DEFAULT 'en',
                    join_date TEXT,
                    last_active TEXT,
                    is_admin INTEGER DEFAULT 0,
                    is_banned INTEGER DEFAULT 0,
                    preferences TEXT
                )
            ''')
            
            # Errors table - logs system errors for admin review
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS errors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    user_id INTEGER,
                    error_message TEXT,
                    traceback TEXT,
                    resolved INTEGER DEFAULT 0
                )
            ''')
            
            # Reports table - tracks reporting activities
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    target_account TEXT,
                    report_type TEXT,
                    report_date TEXT,
                    status TEXT,
                    verified INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Campaigns table - for organizing reporting campaigns
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS campaigns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    target_account TEXT,
                    description TEXT,
                    start_date TEXT,
                    end_date TEXT,
                    goal INTEGER,
                    current_count INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'active',
                    created_by INTEGER,
                    FOREIGN KEY (created_by) REFERENCES users (user_id)
                )
            ''')
            
            # Analytics table - for tracking user interactions
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action_type TEXT,
                    action_data TEXT,
                    timestamp TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Languages table - for multi-language support
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS languages (
                    code TEXT PRIMARY KEY,
                    name TEXT,
                    native_name TEXT,
                    is_active INTEGER DEFAULT 1
                )
            ''')
            
            # Add default languages
            cursor.execute('''
                INSERT OR IGNORE INTO languages (code, name, native_name)
                VALUES 
                    ('en', 'English', 'English'),
                    ('am', 'Amharic', 'አማርኛ')
            ''')
            
            conn.commit()
            conn.close()
    
    def add_user(self, user_id, username, first_name, last_name=None, language='en'):
        """Add a new user to the database or update if already exists."""
        current_time = datetime.now().isoformat()
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Check if user exists
            cursor.execute('''
                SELECT user_id FROM users WHERE user_id = ?
            ''', (user_id,))
            result = cursor.fetchone()
            
            if result:
                # Update existing user's last active time
                cursor.execute('''
                    UPDATE users
                    SET username = ?, first_name = ?, last_name = ?, 
                        language = ?, last_active = ?
                    WHERE user_id = ?
                ''', (username, first_name, last_name, language, current_time, user_id))
            else:
                # Insert new user
                cursor.execute('''
                    INSERT INTO users 
                    (user_id, username, first_name, last_name, language, join_date, last_active, preferences)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, username, first_name, last_name, language, 
                      current_time, current_time, json.dumps({})))
            
            conn.commit()
            conn.close()
            
            # Log this event
            self.log_analytics(user_id, 'user_activity', 'User active')
            
            return True
    
    def get_user(self, user_id):
        """Get user data by user_id."""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            user = cursor.fetchone()
            
            conn.close()
            
            if user:
                # Convert to dict and parse preferences
                user_dict = dict(user)
                if 'preferences' in user_dict and user_dict['preferences']:
                    user_dict['preferences'] = json.loads(user_dict['preferences'])
                return user_dict
            return None
    
    def log_report(self, user_id, target_account, report_type):
        """Log a report made by a user."""
        current_time = datetime.now().isoformat()
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO reports 
                (user_id, target_account, report_type, report_date, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, target_account, report_type, current_time, 'submitted'))
            
            report_id = cursor.lastrowid
            
            # Update campaign counts if the target account is part of a campaign
            cursor.execute('''
                UPDATE campaigns
                SET current_count = current_count + 1
                WHERE target_account = ? AND status = 'active'
            ''', (target_account,))
            
            conn.commit()
            conn.close()
            
            # Log this event
            self.log_analytics(user_id, 'report', f'Report submitted for {target_account}')
            
            return report_id
    
    def verify_report(self, report_id):
        """Mark a report as verified (user confirms they completed the reporting process)."""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE reports
                SET verified = 1, status = 'verified'
                WHERE id = ?
            ''', (report_id,))
            
            conn.commit()
            conn.close()
            return True
    
    def get_campaign_stats(self, campaign_id=None):
        """Get statistics for a specific campaign or all campaigns."""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if campaign_id:
                cursor.execute('''
                    SELECT * FROM campaigns WHERE id = ?
                ''', (campaign_id,))
                campaign = cursor.fetchone()
                
                if campaign:
                    # Get detailed report counts by date
                    cursor.execute('''
                        SELECT DATE(report_date) as date, COUNT(*) as count
                        FROM reports
                        WHERE target_account = ?
                        GROUP BY DATE(report_date)
                        ORDER BY date
                    ''', (campaign['target_account'],))
                    daily_stats = cursor.fetchall()
                    
                    result = dict(campaign)
                    result['daily_stats'] = [dict(row) for row in daily_stats]
                    
                    conn.close()
                    return result
            else:
                cursor.execute('SELECT * FROM campaigns ORDER BY start_date DESC')
                campaigns = cursor.fetchall()
                
                result = [dict(campaign) for campaign in campaigns]
                
                conn.close()
                return result
            
            conn.close()
            return None
    
    def create_campaign(self, name, target_account, description, start_date, 
                        end_date, goal, created_by):
        """Create a new reporting campaign."""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO campaigns
                (name, target_account, description, start_date, end_date, goal, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, target_account, description, start_date, end_date, goal, created_by))
            
            campaign_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            # Log this event
            self.log_analytics(created_by, 'campaign_created', 
                               f'Campaign created: {name} for {target_account}')
            
            return campaign_id
    
    def log_analytics(self, user_id, action_type, action_data):
        """Log user actions for analytics."""
        current_time = datetime.now().isoformat()
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO analytics
                (user_id, action_type, action_data, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (user_id, action_type, action_data, current_time))
            
            conn.commit()
            conn.close()
            return True
    
    def get_analytics(self, start_date=None, end_date=None, user_id=None, action_type=None):
        """Get analytics data with various filters."""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = "SELECT * FROM analytics WHERE 1=1"
            params = []
            
            if start_date:
                query += " AND timestamp >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND timestamp <= ?"
                params.append(end_date)
            
            if user_id:
                query += " AND user_id = ?"
                params.append(user_id)
            
            if action_type:
                query += " AND action_type = ?"
                params.append(action_type)
            
            query += " ORDER BY timestamp DESC"
            
            cursor.execute(query, params)
            analytics = cursor.fetchall()
            
            result = [dict(entry) for entry in analytics]
            
            conn.close()
            return result
    
    def get_report_count(self, target_account=None):
        """Get the count of reports, optionally filtered by target account."""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if target_account:
                cursor.execute('''
                    SELECT COUNT(*) as count FROM reports
                    WHERE target_account = ?
                ''', (target_account,))
            else:
                cursor.execute('SELECT COUNT(*) as count FROM reports')
            
            result = cursor.fetchone()
            count = result['count'] if result else 0
            
            conn.close()
            return count
    
    def get_user_count(self):
        """Get the count of registered users."""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) AS count FROM users')
            result = cursor.fetchone()
            
            conn.close()
            return result['count']
    
    def log_error(self, user_id, error_message, traceback):
        """Log an error to the database for admin review.
        
        Args:
            user_id (int): The user ID associated with the error, or 0 for system errors
            error_message (str): A brief description of the error
            traceback (str): The detailed error traceback
        """
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            timestamp = datetime.now().isoformat()
            
            cursor.execute(
                'INSERT INTO errors (timestamp, user_id, error_message, traceback) VALUES (?, ?, ?, ?)',
                (timestamp, user_id, error_message, traceback)
            )
            
            conn.commit()
            conn.close()
            
            return cursor.lastrowid
    
    def add_admin(self, user_id):
        """Make a user an admin."""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE users
                SET is_admin = 1
                WHERE user_id = ?
            ''', (user_id,))
            
            conn.commit()
            conn.close()
            return True
    
    def is_admin(self, user_id):
        """Check if a user is an admin."""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT is_admin FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            
            conn.close()
            
            return result and result['is_admin'] == 1
    
    def set_user_preference(self, user_id, key, value):
        """Set a user preference."""
        with self.lock:
            user = self.get_user(user_id)
            if not user:
                return False
            
            preferences = user.get('preferences', {})
            preferences[key] = value
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE users
                SET preferences = ?
                WHERE user_id = ?
            ''', (json.dumps(preferences), user_id))
            
            conn.commit()
            conn.close()
            return True
    
    def add_language(self, code, name, native_name):
        """Add a new supported language."""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO languages
                (code, name, native_name, is_active)
                VALUES (?, ?, ?, 1)
            ''', (code, name, native_name))
            
            conn.commit()
            conn.close()
            return True
    
    def get_languages(self, active_only=True):
        """Get all supported languages."""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if active_only:
                cursor.execute('SELECT * FROM languages WHERE is_active = 1')
            else:
                cursor.execute('SELECT * FROM languages')
            
            languages = cursor.fetchall()
            result = [dict(lang) for lang in languages]
            
            conn.close()
            return result
