# TikTok Report Telegram Bot

A powerful, user-friendly Telegram bot designed to facilitate reporting TikTok accounts that violate community guidelines, specifically accounts spreading hate speech and harmful content.

## Features

- 🚀 **User-Friendly Interface**: Beautiful, intuitive design with inline buttons
- 📚 **Comprehensive Instructions**: Detailed step-by-step guides on how to report accounts
- 🌐 **Multilingual Support**: Primary support for Amharic and English 
- 📊 **Educational Content**: Information about TikTok's community guidelines and why reporting harmful content matters
- 🛠️ **Robust Design**: Error handling and conversation management for smooth user experience

## Setup Instructions

### Prerequisites

- Python 3.7 or higher
- A Telegram Bot Token (obtained from [@BotFather](https://t.me/BotFather))
- Basic knowledge of running Python scripts

### Installation

1. **Clone or download this repository**

2. **Install required packages**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**

   Create a `.env` file in the root directory with the following content:
   ```
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   ```
   Replace `your_telegram_bot_token_here` with the token provided by BotFather.

4. **Run the bot**

   ```bash
   python bot.py
   ```

## Usage

Once the bot is running, users can interact with it on Telegram by:

1. Starting a conversation with `/start`
2. Following the menu options to:
   - Learn about the account that needs reporting
   - View step-by-step reporting instructions with images
   - Get help and additional information

## Customization

To target a different account for reporting, modify the `TARGET_ACCOUNT` dictionary in the `bot.py` file.

## Legal and Ethical Considerations

This bot is designed to facilitate legitimate reporting of content that violates TikTok's community guidelines. It should only be used to report accounts that truly engage in harmful behaviors such as hate speech, harassment, or other prohibited activities.

## Disclaimer

This tool is not affiliated with, authorized, maintained, sponsored or endorsed by TikTok or any of its affiliates or subsidiaries. This is an independent and unofficial project. Use at your own discretion.

---

Created by: Murad Tadesse - 2025
