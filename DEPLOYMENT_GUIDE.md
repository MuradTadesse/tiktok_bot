# TikTok Report Bot Deployment Guide

This guide will help you deploy and announce your TikTok Report Bot to your Telegram channel with 100,000+ members.

## Deployment Options

### Option 1: Local Deployment (Short-Term Testing)

This approach is useful for testing the bot before announcing it, but not recommended for long-term deployment.

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Tesseract OCR** (required for screenshot verification):
   - **Windows**: Download and install from [here](https://github.com/UB-Mannheim/tesseract/wiki)
   - **Linux**: `sudo apt install tesseract-ocr`
   - **macOS**: `brew install tesseract`

3. **Run the bot**:
   ```bash
   python start_bot.py
   ```

### Option 2: Cloud Deployment (Recommended)

For a reliable service to your 100,000+ channel members, deploy the bot to a cloud server:

1. **Rent a VPS** (Virtual Private Server):
   - Recommended providers: DigitalOcean, Linode, AWS Lightsail, or Google Cloud
   - Minimum specs: 1GB RAM, 1 CPU, 25GB SSD

2. **Set up the server**:
   ```bash
   # Update the system
   sudo apt update && sudo apt upgrade -y
   
   # Install Python and required tools
   sudo apt install python3 python3-pip python3-venv git tesseract-ocr -y
   
   # Clone your repository (if using git) or upload files via SFTP
   git clone [your-repository-url]
   # OR
   # Upload files via SFTP
   
   # Enter project directory
   cd "Report Telegram Bot"
   
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Set up environment**:
   ```bash
   # Create .env file
   echo "TELEGRAM_BOT_TOKEN=7805756791:AAFnK2wnpuhtZLsJtOk4jndBLFkLxIuCj7k" > .env
   ```

4. **Create a systemd service** for 24/7 operation:
   ```bash
   sudo nano /etc/systemd/system/tiktok-report-bot.service
   ```
   
   Add this content:
   ```
   [Unit]
   Description=TikTok Report Telegram Bot
   After=network.target
   
   [Service]
   User=your-username
   WorkingDirectory=/path/to/Report Telegram Bot
   ExecStart=/path/to/Report Telegram Bot/venv/bin/python start_bot.py
   Restart=always
   RestartSec=10
   StandardOutput=journal
   StandardError=journal
   
   [Install]
   WantedBy=multi-user.target
   ```
   
   Enable and start the service:
   ```bash
   sudo systemctl enable tiktok-report-bot
   sudo systemctl start tiktok-report-bot
   ```

5. **Monitor the bot**:
   ```bash
   sudo systemctl status tiktok-report-bot
   sudo journalctl -u tiktok-report-bot -f
   ```

## Announcing to Your 100,000+ Channel Members

### Preparation

1. **Test thoroughly** before announcing to your large audience
2. **Prepare server capacity** - with 100,000+ members, many might try the bot simultaneously
3. **Create clear instructions** in both English and Amharic

### Announcement Message Template

```
🚨 IMPORTANT ANNOUNCEMENT 🚨

We've launched a new Telegram bot to help report the TikTok account that has been spreading hate speech:

@YourBotUsername

✅ This bot will:
- Guide you through the reporting process step-by-step
- Verify your reports to track our progress
- Show real-time statistics of our campaign

💪 Together, we can make a difference! The more people report, the more likely TikTok will take action.

📱 How to use:
1. Tap the bot username above
2. Click "Start" in Telegram
3. Follow the instructions

አካውንቱን የማዘጋት ዘመቻ‼
====================
ቦቱን ይጠቀሙ፦ @YourBotUsername
```

### Post-Announcement Support

1. **Monitor bot load** during the first few hours to ensure server stability
2. **Be prepared to answer questions** from users
3. **Update your channel** with progress statistics to keep momentum

## Maintenance

1. **Regular Backups**:
   ```bash
   # Backup the database (runs daily at 2 AM)
   0 2 * * * sqlite3 /path/to/Report\ Telegram\ Bot/bot_data.db .dump > /path/to/backups/bot_backup_$(date +\%Y\%m\%d).sql
   ```

2. **Check Logs Regularly**:
   ```bash
   sudo journalctl -u tiktok-report-bot -f
   ```

3. **Update the Bot** when needed:
   ```bash
   # Stop the service
   sudo systemctl stop tiktok-report-bot
   
   # Pull changes or upload new files
   git pull
   # OR
   # Upload via SFTP
   
   # Start the service
   sudo systemctl start tiktok-report-bot
   ```

By following this guide, your TikTok Report Bot will be available 24/7 to your 100,000+ channel members, helping maximize the reporting impact.
