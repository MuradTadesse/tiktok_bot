#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import re
from pathlib import Path

class Localization:
    """Handles multi-language support for the bot with dynamic string loading."""
    
    def __init__(self, default_language='en'):
        """Initialize the localization system with the default language."""
        self.default_language = default_language
        self.current_language = default_language
        self.translations = self._load_translations()
        self.fallback_translations = self._load_fallback_translations()
    
    def _load_translations(self):
        """Load translations from JSON files in the 'locales' directory."""
        translations = {}
        locale_dir = Path('locales')
        
        # Create locales directory if it doesn't exist
        if not locale_dir.exists():
            locale_dir.mkdir()
            
            # Create default translation files
            self._create_default_translations()
        
        # Load all locale files
        for locale_file in locale_dir.glob('*.json'):
            try:
                language_code = locale_file.stem
                with open(locale_file, 'r', encoding='utf-8') as f:
                    translations[language_code] = json.load(f)
            except Exception as e:
                print(f"Error loading translation file {locale_file}: {e}")
        
        return translations
    
    def _create_default_translations(self):
        """Create default translation files if they don't exist."""
        en_translations = {
            "welcome": "Welcome to the TikTok Report Bot! I'm here to help you report harmful content.",
            "main_menu": "Main Menu",
            "report_button": "🚨 Report Account",
            "steps_button": "📋 Reporting Steps",
            "about_button": "ℹ️ About",
            "help_button": "❓ Help",
            "back_button": "◀️ Back",
            "target_info": "Target Account: {username} ({display_name})",
            "report_reason": "Reason for reporting: {reason}",
            "step_1": "Step 1: Open the profile using this link: {url}",
            "step_2": "Step 2: Tap the share icon in the top right corner",
            "step_3": "Step 3: Select 'Report' from the menu",
            "step_4": "Step 4: Tap 'Report account'",
            "step_5": "Step 5: Select 'Posting Inappropriate Content'",
            "step_6": "Step 6: Choose 'Hate and harassment'",
            "step_7": "Step 7: Select 'Hate speech and hateful behaviors'",
            "step_8": "Step 8: Tap 'Submit' and toggle 'Block' before exiting",
            "confirm_report": "Did you complete the reporting process?",
            "yes_button": "✅ Yes, I reported",
            "no_button": "❌ No, not yet",
            "thanks_report": "Thank you for reporting! Together we can make a difference.",
            "report_stats": "Total reports so far: {count}",
            "users_stats": "Users participating: {count}",
            "about_text": "This bot helps coordinate reporting of accounts that violate TikTok's community guidelines by spreading hate speech and harmful content.",
            "help_text": "I can guide you through reporting a TikTok account. Just tap one of the buttons below to get started.",
            "language_changed": "Language changed to English",
            "choose_language": "Choose your preferred language:",
            "bot_version": "Bot Version: {version}",
            "campaign_info": "Current campaign: {name}",
            "campaign_progress": "Progress: {current}/{goal} reports ({percentage}%)",
            "verification_text": "To verify your report, please send a screenshot of the confirmation page",
            "verification_success": "Your report has been verified. Thank you for your contribution!",
            "verification_failed": "Verification failed. Please try again or contact an admin for help.",
            "admin_login": "Admin login successful. Welcome to the admin panel.",
            "admin_stats": "📊 Current Statistics:\n- Total Users: {users}\n- Total Reports: {reports}\n- Active Campaigns: {campaigns}",
            "share_button": "📤 Share This Bot",
            "reminder_text": "Don't forget to report the account! It only takes a minute to help make TikTok safer.",
            "tutorial_button": "🎓 Interactive Tutorial",
            "feedback_button": "📝 Give Feedback",
            "reminder_setup": "Would you like to receive reminders to report?",
            "notify_new_target": "We have a new target account to report. Tap for details."
        }
        
        am_translations = {
            "welcome": "ወደ ቲክቶክ ሪፖርት ቦት እንኳን ደህና መጡ! ጎጂ ይዘቶችን ሪፖርት እንዲያደርጉ ለመርዳት እዚህ አለሁ።",
            "main_menu": "ዋና ማውጫ",
            "report_button": "🚨 አካውንት ሪፖርት አድርግ",
            "steps_button": "📋 የሪፖርት አደራረግ ደረጃዎች",
            "about_button": "ℹ️ ስለ ቦቱ",
            "help_button": "❓ እገዛ",
            "back_button": "◀️ ተመለስ",
            "target_info": "ዒላማ አካውንት: {username} ({display_name})",
            "report_reason": "የሪፖርት ምክንያት: {reason}",
            "step_1": "ደረጃ 1: ይህን ሊንክ በመጠቀም ፕሮፋይሉን ይክፈቱ: {url}",
            "step_2": "ደረጃ 2: ከቀኝ በኩል ላይኛው ማዕዘን ላይ ያለውን የአጋራ ምልክት ይጫኑ",
            "step_3": "ደረጃ 3: ከመምረጫው ላይ 'Report' የሚለውን ይምረጡ",
            "step_4": "ደረጃ 4: 'Report account' የሚለውን ይጫኑ",
            "step_5": "ደረጃ 5: 'Posting Inappropriate Content' የሚለውን ይምረጡ",
            "step_6": "ደረጃ 6: 'Hate and harassment' የሚለውን ይምረጡ",
            "step_7": "ደረጃ 7: 'Hate speech and hateful behaviors' የሚለውን ይምረጡ",
            "step_8": "ደረጃ 8: 'Submit' የሚለውን ይጫኑ እና ከመውጣትዎ በፊት 'Block' የሚለውን ያብሩ",
            "confirm_report": "የሪፖርት ማድረጉን ሂደት ጨርሰዋል?",
            "yes_button": "✅ አዎ፣ ሪፖርት አድርጌያለሁ",
            "no_button": "❌ አይ፣ ገና አልጨረስኩም",
            "thanks_report": "ሪፖርት ስላደረጉ እናመሰግናለን! በአንድነት ልዩነት መፍጠር እንችላለን።",
            "report_stats": "እስካሁን ድረስ ጠቅላላ ሪፖርቶች: {count}",
            "users_stats": "ተሳታፊ ተጠቃሚዎች: {count}",
            "about_text": "ይህ ቦት የቲክቶክ የማህበረሰብ መመሪያዎችን በመጣስ የጥላቻ ንግግር እና ጎጂ ይዘቶችን የሚያሰራጩ አካውንቶችን ሪፖርት ለማድረግ ያስተባብራል።",
            "help_text": "የቲክቶክ አካውንትን ሪፖርት ለማድረግ እመራዎታለሁ። ለመጀመር ከታች ካሉት አዝራሮች አንዱን ይጫኑ።",
            "language_changed": "ቋንቋ ወደ አማርኛ ተቀይሯል",
            "choose_language": "የሚፈልጉትን ቋንቋ ይምረጡ:",
            "bot_version": "የቦት ስሪት: {version}",
            "campaign_info": "የአሁኑ ዘመቻ: {name}",
            "campaign_progress": "ሂደት: {current}/{goal} ሪፖርቶች ({percentage}%)",
            "verification_text": "ሪፖርትዎን ለማረጋገጥ እባክዎን የማረጋገጫ ገጹን ስክሪንሾት ይላኩ",
            "verification_success": "ሪፖርትዎ ተረጋግጧል። ለአስተዋጽኦዎ እናመሰግናለን!",
            "verification_failed": "ማረጋገጥ አልተሳካም። እባክዎ እንደገና ይሞክሩ ወይም ለእገዛ አስተዳዳሪን ያግኙ።",
            "admin_login": "የአስተዳዳሪ መግቢያ ተሳክቷል። ወደ አስተዳዳሪ ፓነል እንኳን በደህና መጡ።",
            "admin_stats": "📊 የአሁኑ ስታቲስቲክስ:\n- ጠቅላላ ተጠቃሚዎች: {users}\n- ጠቅላላ ሪፖርቶች: {reports}\n- ንቁ ዘመቻዎች: {campaigns}",
            "share_button": "📤 ይህን ቦት አጋራ",
            "reminder_text": "አካውንቱን ሪፖርት ማድረግ እንዳይረሱ! ቲክቶክን የበለጠ ደህንነቱ የተጠበቀ ለማድረግ አንድ ደቂቃ ብቻ ይወስዳል።",
            "tutorial_button": "🎓 ተግባራዊ ማጠናከሪያ",
            "feedback_button": "📝 አስተያየት ይስጡ",
            "reminder_setup": "ሪፖርት ለማድረግ አስታዋሽ መልዕክቶችን መቀበል ይፈልጋሉ?",
            "notify_new_target": "ሪፖርት የሚደረግ አዲስ ዒላማ አካውንት አለን። ለዝርዝሮች ይጫኑ።"
        }
        
        # Save the default translations
        with open('locales/en.json', 'w', encoding='utf-8') as f:
            json.dump(en_translations, f, ensure_ascii=False, indent=2)
        
        with open('locales/am.json', 'w', encoding='utf-8') as f:
            json.dump(am_translations, f, ensure_ascii=False, indent=2)
    
    def _load_fallback_translations(self):
        """Load built-in fallback translations for critical strings."""
        return {
            'en': {
                'error_loading': 'Error loading translations. Using fallback language.',
                'language_not_supported': 'This language is not supported yet. Using English instead.',
                'system_error': 'System error occurred. Please try again later.'
            },
            'am': {
                'error_loading': 'ትርጉሞችን መጫን አልተቻለም። ተተኪ ቋንቋን በመጠቀም ላይ።',
                'language_not_supported': 'ይህ ቋንቋ እስካሁን አልተደገፈም። በምትኩ እንግሊዘኛን እንጠቀማለን።',
                'system_error': 'የሲስተም ስህተት ተከስቷል። እባክዎ ቆየት ብለው እንደገና ይሞክሩ።'
            }
        }
    
    def set_language(self, language_code):
        """Set the current language for the bot."""
        if language_code in self.translations:
            self.current_language = language_code
            return True
        return False
    
    def get(self, key, **kwargs):
        """Get a localized string for the current language with optional formatting."""
        # Try to get from the current language
        if self.current_language in self.translations and key in self.translations[self.current_language]:
            text = self.translations[self.current_language][key]
        # Fall back to default language
        elif self.default_language in self.translations and key in self.translations[self.default_language]:
            text = self.translations[self.default_language][key]
        # Use a fallback message if available
        elif key in self.fallback_translations.get(self.current_language, {}):
            text = self.fallback_translations[self.current_language][key]
        elif key in self.fallback_translations.get(self.default_language, {}):
            text = self.fallback_translations[self.default_language][key]
        # Last resort fallback
        else:
            text = f"[{key}]"
        
        # Apply formatting if kwargs are provided
        if kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError as e:
                print(f"Missing formatting key in localization: {e}")
            except Exception as e:
                print(f"Error formatting localized string: {e}")
        
        return text
    
    def get_available_languages(self):
        """Get a list of all available languages."""
        return list(self.translations.keys())
    
    def add_translation(self, language_code, key, value):
        """Add or update a translation for a specific language."""
        if language_code not in self.translations:
            self.translations[language_code] = {}
        
        self.translations[language_code][key] = value
        
        # Save the updated translations
        self._save_translations(language_code)
        
        return True
    
    def _save_translations(self, language_code):
        """Save translations for a specific language to its JSON file."""
        if language_code in self.translations:
            try:
                locale_dir = Path('locales')
                if not locale_dir.exists():
                    locale_dir.mkdir()
                
                with open(f'locales/{language_code}.json', 'w', encoding='utf-8') as f:
                    json.dump(self.translations[language_code], f, ensure_ascii=False, indent=2)
                return True
            except Exception as e:
                print(f"Error saving translations for {language_code}: {e}")
        return False
    
    def import_translations(self, language_code, translations_dict):
        """Import a dictionary of translations for a language."""
        if not isinstance(translations_dict, dict):
            return False
        
        if language_code not in self.translations:
            self.translations[language_code] = {}
        
        # Update translations with the new dictionary
        self.translations[language_code].update(translations_dict)
        
        # Save the updated translations
        return self._save_translations(language_code)
    
    def detect_placeholders(self, text):
        """Detect formatting placeholders in a text string."""
        placeholder_pattern = r'\{([^{}]+)\}'
        return re.findall(placeholder_pattern, text)
