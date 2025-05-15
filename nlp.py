#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import json
import string
from collections import Counter
import os
import requests

class NLPEngine:
    """Natural Language Processing engine for the bot to understand user messages."""
    
    def __init__(self, language='en'):
        """Initialize NLP engine with default language."""
        self.language = language
        self.intent_patterns = self._load_intent_patterns()
        self.translation_cache = {}
    
    def _load_intent_patterns(self):
        """Load intent recognition patterns from patterns.json or use defaults."""
        default_patterns = {
            'report': [
                r'(?i)report',
                r'(?i)how.*(report|flag)',
                r'(?i)want.*report',
                r'(?i)need.*report',
                r'(?i)ሪፖርት',
                r'(?i)አሪፖርት.*አድርግ'
            ],
            'help': [
                r'(?i)help',
                r'(?i)assist',
                r'(?i)how.*work',
                r'(?i)what.*(do|use)',
                r'(?i)እገዛ',
                r'(?i)እርዳታ'
            ],
            'stats': [
                r'(?i)stat',
                r'(?i)progress',
                r'(?i)how many',
                r'(?i)count',
                r'(?i)ስታቲስቲክስ',
                r'(?i)ስታቲክስ'
            ],
            'about': [
                r'(?i)about',
                r'(?i)who.*(you|bot)',
                r'(?i)info',
                r'(?i)ስለ',
                r'(?i)ማን ነህ'
            ],
            'greet': [
                r'(?i)^hi$',
                r'(?i)^hello$',
                r'(?i)^hey$',
                r'(?i)^ሰላም$',
                r'(?i)^ሀሎ$'
            ],
            'thanks': [
                r'(?i)thank',
                r'(?i)አመሰግናለሁ',
                r'(?i)እናመሰግናለን'
            ],
            'verify': [
                r'(?i)verify',
                r'(?i)confirm',
                r'(?i)done',
                r'(?i)complete',
                r'(?i)ተጠናቅቋል',
                r'(?i)አድርጌአለሁ'
            ]
        }
        
        try:
            if os.path.exists('patterns.json'):
                with open('patterns.json', 'r', encoding='utf-8') as f:
                    return json.load(f)
            return default_patterns
        except Exception as e:
            print(f"Error loading intent patterns: {e}")
            return default_patterns
    
    def detect_intent(self, text):
        """Detect the user's intent from their message text."""
        text = text.lower().strip()
        
        # Check against each intent pattern
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return intent
        
        # No clear intent detected
        return self._analyze_for_related_intent(text)
    
    def _analyze_for_related_intent(self, text):
        """Perform a deeper analysis when no direct intent pattern matches."""
        # Remove punctuation and tokenize
        text = text.translate(str.maketrans('', '', string.punctuation))
        words = text.lower().split()
        
        # Define keyword associations with intents
        intent_keywords = {
            'report': ['report', 'flag', 'submit', 'abuse', 'violation', 'tiktok', 'ሪፖርት'],
            'help': ['help', 'assist', 'guide', 'instruction', 'how', 'እገዛ'],
            'stats': ['statistics', 'numbers', 'how many', 'ስታቲስቲክስ'],
            'about': ['about', 'who', 'what', 'purpose', 'ስለ'],
            'greet': ['hi', 'hello', 'hey', 'ሰላም', 'ጤና'],
            'thanks': ['thanks', 'thank you', 'grateful', 'አመሰግናለሁ'],
            'verify': ['done', 'completed', 'finished', 'ጨርሻለሁ']
        }
        
        # Count matches for each intent
        intent_matches = Counter()
        for intent, keywords in intent_keywords.items():
            for word in words:
                if word in keywords:
                    intent_matches[intent] += 1
        
        # Return the most likely intent or 'unknown'
        if intent_matches:
            return intent_matches.most_common(1)[0][0]
        return 'unknown'
    
    def extract_entities(self, text):
        """Extract entities like account names, reasons, etc. from text."""
        entities = {}
        
        # Look for TikTok usernames (with @ symbol)
        username_match = re.search(r'@(\w+)', text)
        if username_match:
            entities['username'] = username_match.group(1)
        
        # Look for TikTok URLs
        url_match = re.search(r'(https?://(?:www\.)?tiktok\.com/@?[\w.-]+/?)', text)
        if url_match:
            entities['url'] = url_match.group(1)
        
        # Look for report reasons
        reason_patterns = [
            (r'(?i)hate', 'hate_speech'),
            (r'(?i)harassment', 'harassment'),
            (r'(?i)violence', 'violence'),
            (r'(?i)미스인포메이션|misinformation', 'misinformation'),
            (r'(?i)harm|harmful', 'harmful'),
            (r'(?i)inappropriate', 'inappropriate'),
            (r'(?i)ጥላቻ', 'hate_speech')
        ]
        
        for pattern, reason in reason_patterns:
            if re.search(pattern, text):
                entities['reason'] = reason
                break
        
        return entities
    
    def detect_language(self, text):
        """Detect the language of the input text (simplified implementation)."""
        # Very basic language detection based on character sets
        # For a production bot, you'd use a proper language detection library
        
        # Check for Amharic (Ethiopic script)
        amharic_chars = re.findall(r'[\u1200-\u137F]', text)
        if len(amharic_chars) > len(text) * 0.3:  # If more than 30% is Amharic
            return 'am'
        
        # Default to English
        return 'en'
    
    def translate_text(self, text, target_language):
        """Translate text to the target language.
        
        This is a mock implementation. In a real app, you'd use a translation API like:
        - Google Cloud Translation
        - DeepL API
        - Microsoft Translator
        """
        # Check cache first
        cache_key = f"{text}_{target_language}"
        if cache_key in self.translation_cache:
            return self.translation_cache[cache_key]
        
        # For this demo, we'll just simulate translation
        # In a real implementation, you would make an API call here
        
        # Simple mock translations for demo purposes
        translations = {
            'en_to_am': {
                'Welcome': 'እንኳን ደህና መጣህ',
                'How can I help you?': 'እንዴት ልረዳህ?',
                'Report': 'ሪፖርት አድርግ',
                'Help': 'እገዛ',
                'About': 'ስለ',
                'Reporting completed': 'ሪፖርት ማድረግ ተጠናቋል'
            },
            'am_to_en': {
                'ሰላም': 'Hello',
                'እገዛ': 'Help',
                'ሪፖርት አድርግ': 'Report',
                'ስለ': 'About',
                'ተጠናቋል': 'Completed'
            }
        }
        
        source_language = self.detect_language(text)
        
        if source_language == 'am' and target_language == 'en':
            for am, en in translations['am_to_en'].items():
                text = text.replace(am, en)
            
        elif source_language == 'en' and target_language == 'am':
            for en, am in translations['en_to_am'].items():
                text = text.replace(en, am)
        
        # Cache the result
        self.translation_cache[cache_key] = text
        return text
    
    def get_smart_response(self, intent, entities=None, language='en'):
        """Generate a smart response based on intent and entities."""
        if not entities:
            entities = {}
        
        responses = {
            'en': {
                'greet': [
                    "Hello! I'm the TikTok Report Bot. How can I help you today?",
                    "Hi there! Need help with reporting a TikTok account?"
                ],
                'report': [
                    "I can help you report the account. Would you like to see the step-by-step process?",
                    "Ready to report a TikTok account? I'll guide you through each step."
                ],
                'help': [
                    "I'm here to assist you with reporting harmful TikTok accounts. What would you like to know?",
                    "Need help? I can show you how to report, check stats, or learn about our campaigns."
                ],
                'thanks': [
                    "You're welcome! Together we can make social media safer.",
                    "Happy to help! Your reports make a difference."
                ],
                'verify': [
                    "Great! Thanks for confirming that you've reported the account.",
                    "Thank you for taking action! Your report has been logged."
                ],
                'unknown': [
                    "I'm not sure I understand. Would you like to report an account, check stats, or get help?",
                    "Could you please rephrase that? I'm here to help with reporting TikTok accounts."
                ]
            },
            'am': {
                'greet': [
                    "ሰላም! የቲክቶክ ሪፖርት ቦት ነኝ። እንዴት ልረዳህ?",
                    "ሰላም! የቲክቶክ አካውንት ሪፖርት ለማድረግ እገዛ ያስፈልግዎታል?"
                ],
                'report': [
                    "አካውንቱን ሪፖርት እንዲያደርጉ ልረዳዎት እችላለሁ። የሪፖርት ሂደቱን እርምጃ በእርምጃ ማየት ይፈልጋሉ?",
                    "የቲክቶክ አካውንት ሪፖርት ለማድረግ ዝግጁ ነዎት? በእያንዳንዱ ደረጃ አመራዎታለሁ።"
                ],
                'help': [
                    "ጎጂ የሆኑ የቲክቶክ አካውንቶችን ሪፖርት ለማድረግ እረዳዎታለሁ። ምን እንድነግርዎት ይፈልጋሉ?",
                    "እገዛ ይፈልጋሉ? እንዴት ሪፖርት እንደሚደረግ፣ ስታቲስቲክስ እንዴት እንደሚታይ ወይም ስለ ዘመቻዎቻችን መረጃ ልሰጥዎት እችላለሁ።"
                ],
                'thanks': [
                    "እንኳን ደስ አለዎት! በአንድነት ማህበራዊ ሚዲያን ደህንነቱ የተጠበቀ ማድረግ እንችላለን።",
                    "ስለ እገዛዎ አመሰግናለሁ! ሪፖርቶችዎ ልዩነት ይፈጥራሉ።"
                ],
                'verify': [
                    "እሰየው! አካውንቱን ሪፖርት ለማድረግዎ አመሰግናለሁ።",
                    "እርምጃ ስለወሰዱ እናመሰግናለን! ሪፖርትዎ ተመዝግቧል።"
                ],
                'unknown': [
                    "ምን ማለት እንደፈለጉ አልገባኝም። አካውንት ሪፖርት ማድረግ፣ ስታቲስቲክስ ማየት ወይም እገዛ ማግኘት ይፈልጋሉ?",
                    "እባክዎን እንደገና ይሞክሩ። የቲክቶክ አካውንቶችን ሪፖርት ማድረግ ለመርዳት እዚህ አለሁ።"
                ]
            }
        }
        
        # Get responses for the requested language or fall back to English
        lang_responses = responses.get(language, responses['en'])
        
        # Get responses for the detected intent or fall back to unknown
        intent_responses = lang_responses.get(intent, lang_responses['unknown'])
        
        # Get a response (in a real bot, you'd use a more sophisticated selection)
        import random
        response = random.choice(intent_responses)
        
        # Personalize with entities if available
        if 'username' in entities:
            if language == 'en':
                response += f" I see you're interested in reporting @{entities['username']}."
            elif language == 'am':
                response += f" @{entities['username']} ሪፖርት ለማድረግ እንደሚፈልጉ ተረድቻለሁ።"
        
        return response
