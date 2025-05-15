#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import time
import datetime
import matplotlib.pyplot as plt
import io
import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np

class AnalyticsDashboard:
    """Generates visual analytics and reports for the bot administration."""
    
    def __init__(self, database, output_dir="analytics"):
        """Initialize with database connection."""
        self.db = database
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def generate_report_chart(self, days=7, target_account=None):
        """Generate a chart showing reporting activity over time."""
        # Get reporting data from database
        today = datetime.datetime.now()
        start_date = today - datetime.timedelta(days=days)
        
        # In a real implementation, we would query the database here
        # For this demo, we'll generate sample data
        dates = [(today - datetime.timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days)]
        dates.reverse()  # Oldest to newest
        
        # Generate sample data (in a real bot, this comes from the database)
        if target_account:
            counts = self._get_report_counts_for_account(dates, target_account)
        else:
            counts = self._get_total_report_counts(dates)
        
        # Create the chart
        plt.figure(figsize=(10, 6))
        plt.bar(dates, counts, color='#1DA1F2')
        plt.xlabel('Date')
        plt.ylabel('Reports')
        plt.title(f'Report Activity Over the Last {days} Days')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save to a buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()
        
        # Also save to file
        chart_path = os.path.join(self.output_dir, f'report_chart_{int(time.time())}.png')
        with open(chart_path, 'wb') as f:
            f.write(buf.getvalue())
        
        return buf
    
    def _get_report_counts_for_account(self, dates, target_account):
        """Get report counts for a specific account (sample data for demo)."""
        # In a real implementation, this would query the database
        # For this demo, we'll generate realistic-looking data
        base_counts = [15, 22, 35, 42, 30, 25, 18]
        
        # Add some randomness
        import random
        counts = [max(0, count + random.randint(-5, 5)) for count in base_counts]
        
        # Ensure we have the right number of data points
        while len(counts) < len(dates):
            counts.append(random.randint(10, 40))
        
        return counts[:len(dates)]
    
    def _get_total_report_counts(self, dates):
        """Get total report counts across all accounts (sample data for demo)."""
        # In a real implementation, this would query the database
        # For this demo, we'll generate realistic-looking data
        base_counts = [25, 40, 65, 80, 55, 45, 30]
        
        # Add some randomness
        import random
        counts = [max(0, count + random.randint(-10, 10)) for count in base_counts]
        
        # Ensure we have the right number of data points
        while len(counts) < len(dates):
            counts.append(random.randint(20, 70))
        
        return counts[:len(dates)]
    
    def generate_campaign_progress_chart(self, campaign_id=None):
        """Generate a chart showing campaign progress toward goal."""
        # In a real implementation, we would get real campaign data
        # For this demo, we'll use sample data
        
        if campaign_id:
            # Get specific campaign data
            campaign = {
                'name': 'Report Harmful Account Campaign',
                'goal': 1000,
                'current_count': 468,
                'start_date': '2025-05-01',
                'end_date': '2025-05-30'
            }
        else:
            # Get the most recent active campaign
            campaign = {
                'name': 'Report Harmful Account Campaign',
                'goal': 1000,
                'current_count': 468,
                'start_date': '2025-05-01',
                'end_date': '2025-05-30'
            }
        
        # Calculate progress percentage
        progress = min(100, (campaign['current_count'] / campaign['goal']) * 100)
        
        # Create progress chart
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Draw progress bar
        ax.barh('Progress', progress, color='#1DA1F2')
        ax.barh('Progress', 100, color='lightgray', alpha=0.3)
        
        # Add labels
        ax.text(progress/2, 'Progress', f"{progress:.1f}%", va='center', ha='center', color='white', fontweight='bold')
        
        # Set title and labels
        ax.set_title(f"Campaign Progress: {campaign['name']}")
        ax.set_xlim(0, 100)
        ax.set_xlabel('Percentage Complete')
        ax.set_yticks([])
        
        # Add campaign details as text
        plt.figtext(0.1, 0.02, 
                   f"Goal: {campaign['goal']} reports | Current: {campaign['current_count']} reports | " + 
                   f"Campaign Period: {campaign['start_date']} to {campaign['end_date']}", 
                   wrap=True, fontsize=10)
        
        plt.tight_layout()
        
        # Save to a buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()
        
        # Also save to file
        chart_path = os.path.join(self.output_dir, f'campaign_progress_{int(time.time())}.png')
        with open(chart_path, 'wb') as f:
            f.write(buf.getvalue())
        
        return buf
    
    def generate_user_activity_chart(self, days=7):
        """Generate a chart showing user activity over time."""
        # Get dates for the chart
        today = datetime.datetime.now()
        dates = [(today - datetime.timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days)]
        dates.reverse()  # Oldest to newest
        
        # Sample data for active users and new users
        active_users = [45, 52, 58, 65, 60, 72, 80]
        new_users = [12, 15, 10, 18, 14, 20, 25]
        
        while len(active_users) < len(dates):
            import random
            active_users.append(random.randint(40, 80))
            new_users.append(random.randint(10, 25))
        
        active_users = active_users[:len(dates)]
        new_users = new_users[:len(dates)]
        
        # Create chart with two lines
        plt.figure(figsize=(10, 6))
        plt.plot(dates, active_users, 'b-', label='Active Users', linewidth=2)
        plt.plot(dates, new_users, 'g-', label='New Users', linewidth=2)
        plt.fill_between(dates, active_users, alpha=0.2, color='blue')
        plt.fill_between(dates, new_users, alpha=0.2, color='green')
        
        plt.xlabel('Date')
        plt.ylabel('Number of Users')
        plt.title(f'User Activity Over the Last {days} Days')
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save to a buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()
        
        # Also save to file
        chart_path = os.path.join(self.output_dir, f'user_activity_{int(time.time())}.png')
        with open(chart_path, 'wb') as f:
            f.write(buf.getvalue())
        
        return buf
    
    def generate_report_types_chart(self):
        """Generate a pie chart showing the distribution of report types."""
        # Sample data for report types
        report_types = ['Hate Speech', 'Harassment', 'Violence', 'Misinformation', 'Other']
        counts = [65, 15, 10, 5, 5]  # Percentages
        colors = ['#FF9999', '#66B2FF', '#99FF99', '#FFCC99', '#CCCCCC']
        
        # Create pie chart
        plt.figure(figsize=(8, 8))
        plt.pie(counts, labels=report_types, colors=colors, autopct='%1.1f%%', startangle=90, shadow=True)
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        plt.title('Distribution of Report Types')
        
        # Save to a buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()
        
        # Also save to file
        chart_path = os.path.join(self.output_dir, f'report_types_{int(time.time())}.png')
        with open(chart_path, 'wb') as f:
            f.write(buf.getvalue())
        
        return buf
    
    def generate_dashboard_image(self, user_id=None):
        """Generate a complete dashboard image with multiple charts."""
        # Create a blank white image
        width, height = 1200, 1600
        dashboard = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(dashboard)
        
        # Try to load a font, fall back to default if not available
        try:
            title_font = ImageFont.truetype("arial.ttf", 36)
            subtitle_font = ImageFont.truetype("arial.ttf", 24)
            stats_font = ImageFont.truetype("arial.ttf", 20)
        except IOError:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            stats_font = ImageFont.load_default()
        
        # Add title
        current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        draw.text((50, 30), f"TikTok Report Bot - Analytics Dashboard", fill='black', font=title_font)
        draw.text((50, 80), f"Generated: {current_date}", fill='gray', font=subtitle_font)
        
        # Add key statistics
        total_reports = 468  # In a real implementation, get this from database
        total_users = 152     # In a real implementation, get this from database
        completion_rate = 78  # In a real implementation, calculate this
        
        stats_y = 150
        draw.text((50, stats_y), f"Total Reports: {total_reports}", fill='black', font=stats_font)
        draw.text((400, stats_y), f"Total Users: {total_users}", fill='black', font=stats_font)
        draw.text((700, stats_y), f"Completion Rate: {completion_rate}%", fill='black', font=stats_font)
        
        # Generate charts and add them to the dashboard
        try:
            # Report activity chart
            report_chart = self.generate_report_chart(days=7)
            report_img = Image.open(report_chart)
            report_img = report_img.resize((1100, 400))
            dashboard.paste(report_img, (50, 200))
            
            # Campaign progress chart
            campaign_chart = self.generate_campaign_progress_chart()
            campaign_img = Image.open(campaign_chart)
            campaign_img = campaign_img.resize((1100, 400))
            dashboard.paste(campaign_img, (50, 620))
            
            # User activity chart
            user_chart = self.generate_user_activity_chart()
            user_img = Image.open(user_chart)
            user_img = user_img.resize((540, 400))
            dashboard.paste(user_img, (50, 1040))
            
            # Report types chart
            types_chart = self.generate_report_types_chart()
            types_img = Image.open(types_chart)
            types_img = types_img.resize((540, 400))
            dashboard.paste(types_img, (610, 1040))
            
        except Exception as e:
            print(f"Error generating dashboard charts: {e}")
            # Add error message to the dashboard
            draw.text((50, 200), f"Error generating charts: {e}", fill='red', font=subtitle_font)
        
        # Save the dashboard
        dashboard_path = os.path.join(self.output_dir, f'dashboard_{int(time.time())}.png')
        dashboard.save(dashboard_path)
        
        # Save to buffer for telegram sending
        buf = io.BytesIO()
        dashboard.save(buf, format='PNG')
        buf.seek(0)
        
        return buf, dashboard_path
    
    def get_summary_text(self):
        """Get a text summary of current analytics."""
        # In a real implementation, get these values from the database
        total_reports = 468
        total_users = 152
        completion_rate = 78
        recent_activity = 42  # reports in last 24 hours
        
        summary = (
            "📊 *Analytics Summary*\n\n"
            f"Total Reports: *{total_reports}*\n"
            f"Active Users: *{total_users}*\n"
            f"Completion Rate: *{completion_rate}%*\n"
            f"Recent Activity: *{recent_activity}* reports in last 24h\n\n"
            "Current Campaign Progress: *46.8%*"
        )
        
        return summary
