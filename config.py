#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Configuration for the TikTok reporting Telegram bot."""

# Bot configuration
BOT_CONFIG = {
    "name": "TikTok Report Bot",
    "description": "A bot to facilitate reporting harmful TikTok accounts",
    "version": "1.0.0"
}

# Target account information
TARGET_ACCOUNT = {
    "username": "effoyyt",
    "display_name": "አፎይ",
    "url": "https://www.tiktok.com/@effoyyt",
    "reason": "Hate speech and hateful behaviors",
    "description": "This account has been identified as spreading hate speech related to religion and race."
}

# Reporting steps in Amharic
REPORTING_STEPS_AM = [
    "የግለሰቡን አካውንት የሚገኝበትን ሊንክ ተጫኑት።",
    "ከቀኝ በኩል top ላይ የምትታየዋን የሼር ምልክት ንኳት።",
    "Report የሚል ይመጣላችኋል።",
    "Report account የሚለውን ተጫኑ።",
    "Posting Inappropriate Content የሚለውን ምክንያት ምረጡ።",
    "Hate and Harassment የሚለውን ምረጡ።",
    "Hate speech and hateful behaviors የሚለውን ምረጡ።",
    "Submit የሚለውን በተን ተጫኑ እና ብሎክ የሚለውን On አድርጉትና ውጡ።"
]

# Reporting steps in English
REPORTING_STEPS_EN = [
    "Open the link to the user's profile.",
    "Tap the share icon in the top right corner.",
    "Select 'Report' from the menu.",
    "Tap 'Report account'.",
    "Select 'Posting Inappropriate Content' as the reason.",
    "Choose 'Hate and Harassment'.",
    "Select 'Hate speech and hateful behaviors'.",
    "Tap 'Submit' and toggle on 'Block' before exiting."
]

# Message templates
MESSAGES = {
    "welcome": (
        "👋 <b>ሰላም {user_name}!</b>\n\n"
        "ይህ ቦት ሕገ-ወጥ የሆኑ የ TikTok አካውንቶችን ለማስወገድ ሪፖርት ለማድረግ የሚረዳ ነው።\n\n"
        "<i>አሁን እያነጣጠርነው በጥላቻ ንግግር እና በኃይማኖት ጥላቻ የሚታወቀውን '{target_name}' ነው።</i>"
    ),
    "report_info": (
        "<b>🚨 የሚከተለውን አካውንት ሪፖርት ለማድረግ:</b>\n\n"
        "<b>የአካውንት ስም:</b> {display_name} (@{username})\n"
        "<b>ምክንያት:</b> {reason}\n\n"
        "<i>ሪፖርት ማድረግ አስፈላጊ የሆነበት ምክንያት: ይህ ግለሰብ በጥላቻ ንግግር እና በኃይማኖት ግጭት ተጠርጥሮ የሚፈለግ ነው።</i>\n\n"
        "አካውንቱን ለማየት እና ሪፖርት ለማድረግ የሚከተለውን ሊንክ ይጠቀሙ:\n"
        "<a href='{url}'>TikTok አካውንት ማስፋፊያ</a>"
    ),
    "about": (
        "<b>ℹ️ ስለ ቦቱ</b>\n\n"
        "ይህ ቦት የ TikTok ላይ የጥላቻ ንግግር እና ኃይማኖታዊ ጥላቻን የሚያስፋፉ አካውንቶችን "
        "ሪፖርት የማድረግ ሂደቱን ለማቅለል የተሰራ ነው።\n\n"
        "<b>ይህ ቦት የሚያግዝ:</b>\n"
        "✅ የሪፖርት ማድረጊያ ደረጃዎችን በምስል ማሳየት\n"
        "✅ የተጠቃሚዎችን ተሞክሮ ማሻሻል\n"
        "✅ ተመሳሳይ የሪፖርት ምክንያቶችን ለመጠቀም ማስቻል\n\n"
        "<i>በአንድነት በመሆን ያልተገቡ ይዘቶችን ከማህበረሰባችን ማጥፋት እንችላለን።</i>\n\n"
        "የተሰራው በ: AI ፕሮግራመር"
    ),
    "help": (
        "<b>❓ እገዛ</b>\n\n"
        "<b>የመጠቀሚያ መመሪያ:</b>\n"
        "🔹 <b>/start</b> - ቦቱን ለማስጀመር\n"
        "🔹 <b>/help</b> - የእገዛ መረጃን ለመመልከት\n"
        "🔹 <b>/report</b> - ስለሪፖርት ሂደት መረጃ ለማግኘት\n"
        "🔹 <b>/steps</b> - የሪፖርት ቅደም ተከተልን ለማየት\n\n"
        "<b>ለተጨማሪ ጥያቄዎች:</b>\n"
        "ማንኛውንም ጥያቄ ወይም ችግር ካለዎት በቀጥታ መልእክት ይላኩ።\n\n"
        "<b>ስለ TikTok ሪፖርት:</b>\n"
        "የ TikTok ሪፖርት ሲደረግ፣ ብዙ ሰዎች ተመሳሳይ ምክንያት ሲጠቀሙ ውጤታማ ይሆናል።"
    ),
    "success": (
        "✅ <b>ስኬታማ ሪፖርት!</b>\n\n"
        "የ TikTok አካውንት ሪፖርት ማድረግዎን አመሰግናለሁ። ሪፖርት የተደረገው አካውንት በቲክቶክ ባለስልጣናት ይገመገማል። "
        "በጋራ በመሆን ይህን አይነት ጥላቻን በአካውንቶቻችን ላይ ማስወገድ እንችላለን።\n\n"
        "ይህንን ቦት ለምን ያክል ተጠቃሚዎች እንደላኩ ያሳውቁን።"
    )
}

# Admin configuration
ADMIN_CONFIG = {
    "admin_chat_ids": []  # Add admin Telegram chat IDs here
}

# Logging configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "bot_logs.log"
}
