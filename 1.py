from telethon import TelegramClient, events, functions, types, utils
import asyncio
import pytz
from datetime import datetime, timedelta
import logging
import random
import os
import sys
import re
import json
import time
from PIL import Image, ImageDraw, ImageFont
import textwrap
from io import BytesIO
import requests
from gtts import gTTS
import jdatetime
import colorama
from colorama import Fore, Back, Style
import googletrans
from googletrans import Translator
import hashlib
import qrcode
import pyfiglet

# Initialize colorama for cross-platform colored terminal output
colorama.init(autoreset=True)

# ASCII Art Logo
LOGO = f"""
{Fore.CYAN}╔════════════════════════════════════════════╗
{Fore.CYAN}║ {Fore.BLUE}████████╗███████╗██╗     ███████╗██████╗  {Fore.CYAN}║
{Fore.CYAN}║ {Fore.BLUE}╚══██╔══╝██╔════╝██║     ██╔════╝██╔══██╗ {Fore.CYAN}║
{Fore.CYAN}║ {Fore.BLUE}   ██║   █████╗  ██║     █████╗  ██████╔╝ {Fore.CYAN}║
{Fore.CYAN}║ {Fore.BLUE}   ██║   ██╔══╝  ██║     ██╔══╝  ██╔══██╗ {Fore.CYAN}║
{Fore.CYAN}║ {Fore.BLUE}   ██║   ███████╗███████╗███████╗██████╔╝ {Fore.CYAN}║
{Fore.CYAN}║ {Fore.BLUE}   ╚═╝   ╚══════╝╚══════╝╚══════╝╚═════╝  {Fore.CYAN}║
{Fore.CYAN}║ {Fore.MAGENTA}███████╗███████╗██╗     ███████╗██████╗  {Fore.CYAN}║
{Fore.CYAN}║ {Fore.MAGENTA}██╔════╝██╔════╝██║     ██╔════╝██╔══██╗ {Fore.CYAN}║
{Fore.CYAN}║ {Fore.MAGENTA}███████╗█████╗  ██║     █████╗  ██████╔╝ {Fore.CYAN}║
{Fore.CYAN}║ {Fore.MAGENTA}╚════██║██╔══╝  ██║     ██╔══╝  ██╔══██╗ {Fore.CYAN}║
{Fore.CYAN}║ {Fore.MAGENTA}███████║███████╗███████╗███████╗██████╔╝ {Fore.CYAN}║
{Fore.CYAN}║ {Fore.MAGENTA}╚══════╝╚══════╝╚══════╝╚══════╝╚═════╝  {Fore.CYAN}║
{Fore.CYAN}║ {Fore.YELLOW}██████╗  ██████╗ ████████╗               {Fore.CYAN}║
{Fore.CYAN}║ {Fore.YELLOW}██╔══██╗██╔═══██╗╚══██╔══╝               {Fore.CYAN}║
{Fore.CYAN}║ {Fore.YELLOW}██████╔╝██║   ██║   ██║                  {Fore.CYAN}║
{Fore.CYAN}║ {Fore.YELLOW}██╔══██╗██║   ██║   ██║                  {Fore.CYAN}║
{Fore.CYAN}║ {Fore.YELLOW}██████╔╝╚██████╔╝   ██║                  {Fore.CYAN}║
{Fore.CYAN}║ {Fore.YELLOW}╚═════╝  ╚═════╝    ╚═╝                  {Fore.CYAN}║
{Fore.CYAN}╚════════════════════════════════════════════╝
{Fore.GREEN}        Enhanced Platinum Edition v3.0 (2025)
"""

# Configuration variables
CONFIG_FILE = "config.json"
LOG_FILE = "selfbot.log"

# Default configuration settings
default_config = {
    "api_id": 29042268,
    "api_hash": "54a7b377dd4a04a58108639febe2f443",
    "session_name": "anon",
    "log_level": "ERROR",
    "timezone": "Asia/Tehran",
    "auto_backup": True,
    "backup_interval": 60,  # minutes
    "enemy_reply_chance": 100,  # percentage
    "enemy_auto_reply": True,
    "auto_read_messages": False,
    "allowed_users": [],
    "cloud_backup": False,
    "auto_translate": False,
    "default_translate_lang": "fa",
    "weather_api_key": "",
    "auto_weather": False,
    "stats_tracking": True,
    "max_spam_count": 50
}

# Global variables
enemies = set()
current_font = 'normal'
actions = {
    'typing': False,
    'online': False,
    'reaction': False,
    'read': False,
    'auto_reply': False,
    'stats': False,
    'translate': False
}
spam_words = []
saved_messages = []
reminders = []
time_enabled = True
saved_pics = []
custom_replies = {}
blocked_words = []
last_backup_time = None
running = True
start_time = time.time()
status_rotation = []
status_rotation_active = False
periodic_messages = []
filters = {}
message_stats = {}
welcome_messages = {}
theme = "default"
chat_themes = {}

# Command history for undo functionality
command_history = []
MAX_HISTORY = 50

locked_chats = {
    'screenshot': set(),  # Screenshot protection
    'forward': set(),     # Forward protection
    'copy': set(),        # Copy protection
    'delete': set(),      # Auto-delete messages
    'edit': set(),        # Prevent editing
    'spam': set(),        # Anti-spam protection
    'link': set(),        # Block links
    'mention': set()      # Block mentions
}

# Font styles expanded
font_styles = {
    'normal': lambda text: text,
    'bold': lambda text: f"**{text}**",
    'italic': lambda text: f"__{text}__",
    'script': lambda text: f"`{text}`",
    'double': lambda text: f"```{text}```",
    'bubble': lambda text: f"||{text}||",
    'square': lambda text: f"```{text}```",
    'strikethrough': lambda text: f"~~{text}~~",
    'underline': lambda text: f"___{text}___",
    'caps': lambda text: text.upper(),
    'lowercase': lambda text: text.lower(),
    'title': lambda text: text.title(),
    'space': lambda text: " ".join(text),
    'reverse': lambda text: text[::-1],
    'rainbow': lambda text: "".join([f"<span style='color:#{color}'>{c}</span>" for c, color in zip(text, ['ff0000', 'ff7700', 'ffff00', '00ff00', '0000ff', '8a2be2', 'ff00ff'])]),
    'fancy': lambda text: "".join([c + "̲" for c in text]),
    'small_caps': lambda text: text.translate(str.maketrans("abcdefghijklmnopqrstuvwxyz", "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ")),
    'bubble_text': lambda text: text.translate(str.maketrans("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", "ⓐⓑⓒⓓⓔⓕⓖⓗⓘⓙⓚⓛⓜⓝⓞⓟⓠⓡⓢⓣⓤⓥⓦⓧⓨⓩⒶⒷⒸⒹⒺⒻⒼⒽⒾⒿⓀⓁⓂⓃⓄⓅⓆⓇⓈⓉⓊⓋⓌⓍⓎⓏ⓪①②③④⑤⑥⑦⑧⑨")),
    'medieval': lambda text: text.translate(str.maketrans("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ", "𝔞𝔟𝔠𝔡𝔢𝔣𝔤𝔥𝔦𝔧𝔨𝔩𝔪𝔫𝔬𝔭𝔮𝔯𝔰𝔱𝔲𝔳𝔴𝔵𝔶𝔷𝔄𝔅ℭ𝔇𝔈𝔉𝔊ℌℑ𝔍𝔎𝔏𝔐𝔑𝔒𝔓𝔔ℜ𝔖𝔗𝔘𝔙𝔚𝔛𝔜ℨ")),
    'cursive': lambda text: text.translate(str.maketrans("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ", "𝓪𝓫𝓬𝓭𝓮𝓯𝓰𝓱𝓲𝓳𝓴𝓵𝓶𝓷𝓸𝓹𝓺𝓻𝓼𝓽𝓾𝓿𝔀𝔁𝔂𝔃𝓐𝓑𝓒𝓓𝓔𝓕𝓖𝓗𝓘𝓙𝓚𝓛𝓜𝓝𝓞𝓟𝓠𝓡𝓢𝓣𝓤𝓥𝓦𝓧𝓨𝓩"))
}

# Insults list - unchanged for compatibility
insults = [
    "کیرم تو کص ننت", "مادرجنده", "کص ننت", "کونی", "جنده", "کیری", "بی ناموس", "حرومزاده", "مادر قحبه", "جاکش",
    "کص ننه", "ننه جنده", "مادر کصده", "خارکصه", "کون گشاد", "ننه کیردزد", "مادر به خطا", "توله سگ", "پدر سگ", "حروم لقمه",
    "ننه الکسیس", "کص ننت میجوشه", "کیرم تو کص مادرت", "مادر جنده ی حرومی", "زنا زاده", "مادر خراب", "کصکش", "ننه سگ پرست",
    "مادرتو گاییدم", "خواهرتو گاییدم", "کیر سگ تو کص ننت", "کص مادرت", "کیر خر تو کص ننت", "کص خواهرت", "کون گشاد",
    "سیکتیر کص ننه", "ننه کیر خور", "خارکصده", "مادر جنده", "ننه خیابونی", "کیرم تو دهنت", "کص لیس", "ساک زن",
    "کیرم تو قبر ننت", "بی غیرت", "کص ننه پولی", "کیرم تو کص زنده و مردت", "مادر به خطا", "لاشی", "عوضی", "آشغال",
    "ننه کص طلا", "کیرم تو کص ننت بالا پایین", "کیر قاطر تو کص ننت", "کص ننت خونه خالی", "کیرم تو کص ننت یه دور", 
    "مادر خراب گشاد", "کیرم تو نسل اولت", "کیرم تو کص ننت محکم", "کیر خر تو کص مادرت", "کیرم تو روح مادر جندت",
    "کص ننت سفید برفی", "کیرم تو کص خارت", "کیر سگ تو کص مادرت", "کص ننه کیر خور", "کیرم تو کص زیر خواب",
    "مادر جنده ولگرد", "کیرم تو دهن مادرت", "کص مادرت گشاد", "کیرم تو لای پای مادرت", "کص ننت خیس",
    "کیرم تو کص مادرت بگردش", "کص ننه پاره", "مادر جنده حرفه ای", "کیرم تو کص و کون ننت", "کص ننه تنگ",
    "کیرم تو حلق مادرت", "ننه جنده مفت خور", "کیرم از پهنا تو کص ننت", "کص مادرت بد بو", "کیرم تو همه کس و کارت",
    "مادر کصده سیاه", "کیرم تو کص گشاد مادرت", "کص ننه ساک زن", "کیرم تو کص خاندانت", "مادر جنده خیابونی",
    "کیرم تو کص ننت یه عمر", "ننه جنده کص خور", "کیرم تو نسل و نژادت", "کص مادرت پاره", "کیرم تو شرف مادرت",
    "مادر جنده فراری", "کیرم تو روح مادرت", "کص ننه جندت", "کیرم تو غیرتت", "کص مادر بدکاره",
    "کیرم تو ننه جندت", "مادر کصده لاشی", "کیرم تو وجود مادرت", "کص ننه بی آبرو", "کیرم تو شعور ننت"
]

# Color themes
themes = {
    "default": {
        "primary": Fore.BLUE,
        "secondary": Fore.CYAN,
        "accent": Fore.YELLOW,
        "success": Fore.GREEN,
        "error": Fore.RED,
        "warning": Fore.YELLOW,
        "info": Fore.WHITE
    },
    "dark": {
        "primary": Fore.BLUE,
        "secondary": Fore.MAGENTA,
        "accent": Fore.CYAN,
        "success": Fore.GREEN,
        "error": Fore.RED,
        "warning": Fore.YELLOW,
        "info": Fore.WHITE
    },
    "light": {
        "primary": Fore.BLUE,
        "secondary": Fore.CYAN,
        "accent": Fore.MAGENTA,
        "success": Fore.GREEN,
        "error": Fore.RED,
        "warning": Fore.YELLOW,
        "info": Fore.WHITE
    },
    "hacker": {
        "primary": Fore.GREEN,
        "secondary": Fore.GREEN,
        "accent": Fore.GREEN,
        "success": Fore.GREEN,
        "error": Fore.RED,
        "warning": Fore.YELLOW,
        "info": Fore.GREEN
    },
    "colorful": {
        "primary": Fore.BLUE,
        "secondary": Fore.MAGENTA,
        "accent": Fore.CYAN,
        "success": Fore.GREEN,
        "error": Fore.RED,
        "warning": Fore.YELLOW,
        "info": Fore.WHITE
    }
}

# Setup logging
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=LOG_FILE
)
logger = logging.getLogger("TelegramSelfBot")

# Translator instance for auto translation
translator = Translator()

# Convert numbers to superscript
def to_superscript(num):
    """Convert numbers to superscript notation"""
    superscripts = {
        '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
        '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹'
    }
    return ''.join(superscripts.get(n, n) for n in str(num))

# Pretty print functions
def print_header(text):
    """Print a header with decoration"""
    width = len(text) + 4
    print(f"\n{themes[theme]['secondary']}{'═' * width}")
    print(f"{themes[theme]['secondary']}║ {themes[theme]['info']}{text} {themes[theme]['secondary']}║")
    print(f"{themes[theme]['secondary']}{'═' * width}\n")

def print_success(text):
    """Print success message"""
    print(f"{themes[theme]['success']}✅ {text}")

def print_error(text):
    """Print error message"""
    print(f"{themes[theme]['error']}❌ {text}")

def print_warning(text):
    """Print warning message"""
    print(f"{themes[theme]['warning']}⚠️ {text}")

def print_info(text):
    """Print info message"""
    print(f"{themes[theme]['info']}ℹ️ {text}")

def print_status(label, status, active=True):
    """Print a status item with colored indicator"""
    status_color = themes[theme]['success'] if active else themes[theme]['error']
    status_icon = "✅" if active else "❌"
    print(f"{themes[theme]['info']}{label}: {status_color}{status_icon} {status}")

def print_loading(text="Loading", cycles=3):
    """Display a loading animation"""
    animations = [".  ", ".. ", "..."]
    for _ in range(cycles):
        for animation in animations:
            sys.stdout.write(f"\r{themes[theme]['warning']}{text} {animation}")
            sys.stdout.flush()
            time.sleep(0.3)
    sys.stdout.write("\r" + " " * (len(text) + 5) + "\r")
    sys.stdout.flush()

def print_progress_bar(iteration, total, prefix='', suffix='', length=30, fill='█'):
    """Call in a loop to create terminal progress bar"""
    percent = "{0:.1f}".format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '░' * (length - filled_length)
    sys.stdout.write(f'\r{themes[theme]["primary"]}{prefix} |{themes[theme]["secondary"]}{bar}{themes[theme]["primary"]}| {percent}% {suffix}')
    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()

def print_figlet(text, font="slant"):
    """Print stylized ASCII text using figlet"""
    try:
        fig_text = pyfiglet.figlet_format(text, font=font)
        print(f"{themes[theme]['accent']}{fig_text}")
    except Exception as e:
        logger.error(f"Error in figlet: {e}")
        print(text)

# Config management functions
def load_config():
    """Load configuration from file or create default"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                # Update with any missing keys from default config
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        except Exception as e:
            print_error(f"Failed to load config: {e}")
            return default_config
    else:
        save_config(default_config)
        return default_config

def save_config(config):
    """Save configuration to file"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        print_error(f"Failed to save config: {e}")
        return False

# Data backup functions
def backup_data():
    """Backup all user data to file"""
    global last_backup_time
    backup_data = {
        "enemies": list(enemies),
        "current_font": current_font,
        "actions": actions,
        "spam_words": spam_words,
        "saved_messages": saved_messages,
        "reminders": reminders,
        "time_enabled": time_enabled,
        "saved_pics": saved_pics,
        "custom_replies": custom_replies,
        "blocked_words": blocked_words,
        "locked_chats": {k: list(v) for k, v in locked_chats.items()},
        "status_rotation": status_rotation,
        "status_rotation_active": status_rotation_active,
        "periodic_messages": periodic_messages,
        "filters": filters,
        "message_stats": message_stats,
        "welcome_messages": welcome_messages,
        "theme": theme,
        "chat_themes": chat_themes
    }
    
    try:
        with open("selfbot_backup.json", 'w') as f:
            json.dump(backup_data, f, indent=4)
        last_backup_time = datetime.now()
        return True
    except Exception as e:
        logger.error(f"Backup failed: {e}")
        return False

def restore_data():
    """Restore user data from backup file"""
    global enemies, current_font, actions, spam_words, saved_messages, reminders
    global time_enabled, saved_pics, custom_replies, blocked_words, locked_chats
    global status_rotation, status_rotation_active, periodic_messages, filters 
    global message_stats, welcome_messages, theme, chat_themes
    
    if not os.path.exists("selfbot_backup.json"):
        return False
    
    try:
        with open("selfbot_backup.json", 'r') as f:
            data = json.load(f)
            
        enemies = set(data.get("enemies", []))
        current_font = data.get("current_font", "normal")
        actions.update(data.get("actions", {}))
        spam_words = data.get("spam_words", [])
        saved_messages = data.get("saved_messages", [])
        reminders = data.get("reminders", [])
        time_enabled = data.get("time_enabled", True)
        saved_pics = data.get("saved_pics", [])
        custom_replies = data.get("custom_replies", {})
        blocked_words = data.get("blocked_words", [])
        status_rotation = data.get("status_rotation", [])
        status_rotation_active = data.get("status_rotation_active", False)
        periodic_messages = data.get("periodic_messages", [])
        filters = data.get("filters", {})
        message_stats = data.get("message_stats", {})
        welcome_messages = data.get("welcome_messages", {})
        theme = data.get("theme", "default")
        chat_themes = data.get("chat_themes", {})
        
        # Restore locked_chats as sets
        locked_chats_data = data.get("locked_chats", {})
        for key, value in locked_chats_data.items():
            if key in locked_chats:
                locked_chats[key] = set(value)
                
        return True
    except Exception as e:
        logger.error(f"Restore failed: {e}")
        return False

# Cloud backup to Telegram saved messages
async def cloud_backup(client):
    """Backup data to Telegram saved messages"""
    try:
        if os.path.exists("selfbot_backup.json"):
            me = await client.get_me()
            await client.send_file(
                me.id, 
                "selfbot_backup.json",
                caption=f"📂 Automatic cloud backup\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            return True
        return False
    except Exception as e:
        logger.error(f"Cloud backup failed: {e}")
        return False

# Enhanced utility functions
async def text_to_voice(text, lang='fa'):
    """Convert text to voice file with progress indicators"""
    print_info("Converting text to voice...")
    try:
        tts = gTTS(text=text, lang=lang)
        filename = f"voice_{int(time.time())}.mp3"
        tts.save(filename)
        print_success("Voice file created successfully")
        return filename
    except Exception as e:
        logger.error(f"Error in text to voice: {e}")
        print_error(f"Failed to convert text to voice: {e}")
        return None

async def text_to_image(text, bg_color='white', text_color='black', font_name=None, font_size=40):
    """Convert text to image with enhanced customization"""
    print_info("Creating image from text...")
    try:
        width = 800
        height = max(400, len(text) // 20 * 50)  # Dynamic height based on text length
        img = Image.new('RGB', (width, height), color=bg_color)
        draw = ImageDraw.Draw(img)
        
        try:
            if font_name:
                font = ImageFont.truetype(font_name, font_size)
            else:
                font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            # Fallback to default
            font = ImageFont.load_default()
        
        lines = textwrap.wrap(text, width=30)
        y = 50
        for i, line in enumerate(lines):
            print_progress_bar(i + 1, len(lines), 'Progress:', 'Complete', 20)
            draw.text((50, y), line, font=font, fill=text_color)
            y += font_size + 10
            
        filename = f"text_{int(time.time())}.png"
        img.save(filename)
        print_success("Image created successfully")
        return filename
    except Exception as e:
        logger.error(f"Error in text to image: {e}")
        print_error(f"Failed to convert text to image: {e}")
        return None

async def text_to_gif(text, duration=500, bg_color='white', effects='color'):
    """Convert text to animated GIF with customization"""
    print_info("Creating GIF from text...")
    try:
        width = 800
        height = 400
        frames = []
        colors = ['red', 'blue', 'green', 'purple', 'orange']
        
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except IOError:
            font = ImageFont.load_default()
        
        if effects == 'color':
            # Color changing effect
            for i, color in enumerate(colors):
                print_progress_bar(i + 1, len(colors), 'Creating frames:', 'Complete', 20)
                img = Image.new('RGB', (width, height), color=bg_color)
                draw = ImageDraw.Draw(img)
                draw.text((50, 150), text, font=font, fill=color)
                frames.append(img)
        elif effects == 'zoom':
            # Zoom effect
            for i in range(5):
                print_progress_bar(i + 1, 5, 'Creating frames:', 'Complete', 20)
                img = Image.new('RGB', (width, height), color=bg_color)
                draw = ImageDraw.Draw(img)
                size = 30 + i * 10
                try:
                    font = ImageFont.truetype("arial.ttf", size)
                except:
                    font = ImageFont.load_default()
                draw.text((width//2 - len(text)*size//4, height//2 - size//2), text, font=font, fill='black')
                frames.append(img)
        elif effects == 'fade':
            # Fade effect
            for i in range(5):
                print_progress_bar(i + 1, 5, 'Creating frames:', 'Complete', 20)
                img = Image.new('RGB', (width, height), color=bg_color)
                draw = ImageDraw.Draw(img)
                opacity = int(255 * (i+1) / 5)
                draw.text((50, 150), text, font=font, fill=(0, 0, 0, opacity))
                frames.append(img)
        else:
            # Default animation
            for i, color in enumerate(colors):
                print_progress_bar(i + 1, len(colors), 'Creating frames:', 'Complete', 20)
                img = Image.new('RGB', (width, height), color=bg_color)
                draw = ImageDraw.Draw(img)
                draw.text((50, 150), text, font=font, fill=color)
                frames.append(img)
        
        filename = f"text_{int(time.time())}.gif"
        frames[0].save(
            filename,
            save_all=True,
            append_images=frames[1:],
            duration=duration,
            loop=0
        )
        print_success("GIF created successfully")
        return filename
    except Exception as e:
        logger.error(f"Error in text to gif: {e}")
        print_error(f"Failed to convert text to GIF: {e}")
        return None

async def create_qr_code(text, file_path=None):
    """Create a QR code from text"""
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        if not file_path:
            file_path = f"qrcode_{int(time.time())}.png"
            
        img.save(file_path)
        return file_path
    except Exception as e:
        logger.error(f"Error creating QR code: {e}")
        return None

async def translate_text(text, dest='fa', src='auto'):
    """Translate text to specified language"""
    try:
        result = translator.translate(text, dest=dest, src=src)
        return result.text
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return text

async def get_weather(city, api_key):
    """Get weather information for a city"""
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url)
        data = response.json()
        
        if data["cod"] != 200:
            return f"Error: {data['message']}"
            
        weather = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        wind = data["wind"]["speed"]
        
        return f"🌡️ Weather in {city}:\n" \
               f"🌤️ Condition: {weather}\n" \
               f"🌡️ Temperature: {temp}°C\n" \
               f"💧 Humidity: {humidity}%\n" \
               f"💨 Wind: {wind} m/s"
    except Exception as e:
        logger.error(f"Weather API error: {e}")
        return f"Error getting weather data: {e}"

async def update_time(client):
    """Update the last name with current time"""
    while running:
        try:
            if time_enabled:
                config = load_config()
                now = datetime.now(pytz.timezone(config['timezone']))
                hours = to_superscript(now.strftime('%H'))
                minutes = to_superscript(now.strftime('%M'))
                time_string = f"{hours}:{minutes}"
                await client(functions.account.UpdateProfileRequest(last_name=time_string))
        except Exception as e:
            logger.error(f'Error updating time: {e}')
        await asyncio.sleep(60)

async def update_status_rotation(client):
    """Rotate through status messages in bio"""
    global status_rotation, status_rotation_active
    
    current_index = 0
    
    while running and status_rotation_active and status_rotation:
        try:
            status = status_rotation[current_index]
            await client(functions.account.UpdateProfileRequest(about=status))
            
            # Move to next status
            current_index = (current_index + 1) % len(status_rotation)
            
            # Wait for next rotation
            await asyncio.sleep(300)  # Change every 5 minutes
        except Exception as e:
            logger.error(f'Error updating status rotation: {e}')
            await asyncio.sleep(60)

async def auto_online(client):
    """Keep user online automatically"""
    while running and actions['online']:
        try:
            await client(functions.account.UpdateStatusRequest(offline=False))
        except Exception as e:
            logger.error(f'Error updating online status: {e}')
        await asyncio.sleep(30)

async def auto_typing(client, chat):
    """Maintain typing status in chat"""
    while running and actions['typing']:
        try:
            async with client.action(chat, 'typing'):
                await asyncio.sleep(3)
        except Exception as e:
            logger.error(f'Error in typing action: {e}')
            break

async def auto_reaction(event):
    """Add automatic reaction to messages"""
    if actions['reaction']:
        try:
            await event.message.react('👍')
        except Exception as e:
            logger.error(f'Error adding reaction: {e}')

async def auto_read_messages(event, client):
    """Mark messages as read automatically"""
    if actions['read']:
        try:
            await client.send_read_acknowledge(event.chat_id, event.message)
        except Exception as e:
            logger.error(f'Error marking message as read: {e}')

async def auto_translate_message(event, client):
    """Automatically translate incoming messages"""
    if actions['translate'] and event.text:
        try:
            config = load_config()
            translated = await translate_text(event.text, dest=config['default_translate_lang'])
            
            if translated != event.text:
                sender = await event.get_sender()
                sender_name = utils.get_display_name(sender) if sender else "Unknown"
                
                translation_text = f"🔄 {sender_name}: {translated}"
                await client.send_message(event.chat_id, translation_text, reply_to=event.id)
        except Exception as e:
            logger.error(f'Error in auto translation: {e}')

async def schedule_message(client, chat_id, delay, message, recurring=False, interval=0):
    """Schedule message sending with countdown"""
    print_info(f"Message scheduled to send in {delay} minutes")
    
    # For one-time messages
    if not recurring:
        for i in range(delay):
            remaining = delay - i
            if remaining % 5 == 0 or remaining <= 5:  # Show updates every 5 minutes or in final countdown
                logger.info(f"Scheduled message will send in {remaining} minutes")
            await asyncio.sleep(60)
        
        try:
            await client.send_message(chat_id, message)
            print_success(f"Scheduled message sent: {message[:30]}...")
            return True
        except Exception as e:
            logger.error(f"Failed to send scheduled message: {e}")
            print_error(f"Failed to send scheduled message: {e}")
            return False
    
    # For recurring messages
    else:
        while running:
            # Wait for the interval
            for i in range(interval):
                if not running:
                    return
                await asyncio.sleep(60)
            
            try:
                await client.send_message(chat_id, message)
                logger.info(f"Recurring message sent: {message[:30]}...")
            except Exception as e:
                logger.error(f"Failed to send recurring message: {e}")

async def spam_messages(client, chat_id, count, message):
    """Send multiple messages in sequence with progress indicators"""
    print_info(f"Sending {count} messages...")
    success_count = 0
    
    for i in range(count):
        try:
            await client.send_message(chat_id, message)
            success_count += 1
            print_progress_bar(i + 1, count, 'Sending:', 'Complete', 20)
            await asyncio.sleep(0.5)
        except Exception as e:
            logger.error(f"Error in spam message {i+1}: {e}")
    
    print_success(f"Successfully sent {success_count}/{count} messages")
    return success_count

async def check_reminders(client):
    """Check and send reminders"""
    while running:
        current_time = datetime.now().strftime('%H:%M')
        to_remove = []
        
        for i, (reminder_time, message, chat_id) in enumerate(reminders):
            if reminder_time == current_time:
                try:
                    await client.send_message(chat_id, f"🔔 یادآوری: {message}")
                    to_remove.append(i)
                except Exception as e:
                    logger.error(f"Failed to send reminder: {e}")
        
        # Remove sent reminders
        for i in sorted(to_remove, reverse=True):
            del reminders[i]
            
        await asyncio.sleep(30)  # Check every 30 seconds

async def auto_backup(client):
    """Automatically backup data at intervals"""
    config = load_config()
    if not config['auto_backup']:
        return
        
    interval = config['backup_interval'] * 60  # Convert to seconds
    
    while running:
        await asyncio.sleep(interval)
        if backup_data():
            logger.info("Auto-backup completed successfully")
            
            # If cloud backup is enabled
            if config['cloud_backup']:
                if await cloud_backup(client):
                    logger.info("Cloud backup completed successfully")
                else:
                    logger.error("Cloud backup failed")
        else:
            logger.error("Auto-backup failed")

async def handle_anti_delete(event):
    """Save deleted messages for anti-delete feature"""
    chat_id = str(event.chat_id)
    if chat_id in locked_chats['delete'] and event.message:
        try:
            # Save message info before it's deleted
            msg = event.message
            sender = await event.get_sender()
            sender_name = utils.get_display_name(sender) if sender else "Unknown"
            
            saved_text = f"🔴 Deleted message from {sender_name}:\n{msg.text}"
            await event.reply(saved_text)
            return True
        except Exception as e:
            logger.error(f"Error in anti-delete: {e}")
    return False

async def track_message_stats(event):
    """Track message statistics for analytics"""
    if actions['stats']:
        try:
            chat_id = str(event.chat_id)
            sender_id = str(event.sender_id) if event.sender_id else "unknown"
            
            # Initialize chat stats if not exist
            if chat_id not in message_stats:
                message_stats[chat_id] = {
                    "total_messages": 0,
                    "users": {},
                    "hourly": [0] * 24,
                    "daily": [0] * 7,
                    "keywords": {}
                }
            
            # Update total messages
            message_stats[chat_id]["total_messages"] += 1
            
            # Update user stats
            if sender_id not in message_stats[chat_id]["users"]:
                message_stats[chat_id]["users"][sender_id] = 0
            message_stats[chat_id]["users"][sender_id] += 1
            
            # Update hourly stats
            hour = datetime.now().hour
            message_stats[chat_id]["hourly"][hour] += 1
            
            # Update daily stats
            day = datetime.now().weekday()
            message_stats[chat_id]["daily"][day] += 1
            
            # Track keywords
            if event.text:
                words = event.text.lower().split()
                for word in words:
                    if len(word) > 3:  # Only track words longer than 3 chars
                        if word not in message_stats[chat_id]["keywords"]:
                            message_stats[chat_id]["keywords"][word] = 0
                        message_stats[chat_id]["keywords"][word] += 1
            
            # Save stats periodically
            if message_stats[chat_id]["total_messages"] % 100 == 0:
                backup_data()
                
        except Exception as e:
            logger.error(f"Error tracking message stats: {e}")

async def show_help_menu(client, event):
    """Show enhanced help menu with categories"""
    help_text = """
📱 **راهنمای ربات سلف بات پلاتینیوم نسخه 3.0**

🔰 **بخش‌های اصلی**:

🔹 **تنظیمات اولیه**:
• `پنل` - نمایش منوی راهنما
• `وضعیت` - نمایش وضعیت کلی ربات
• `theme [نام تم]` - تغییر تم ربات (default, dark, light, hacker, colorful)
• `exit` - خروج از برنامه
• `backup` - پشتیبان‌گیری دستی از داده‌ها
• `restore` - بازیابی داده‌ها از پشتیبان
• `cloud backup on/off` - پشتیبان‌گیری خودکار در پیام‌های ذخیره شده
• `undo` - برگرداندن آخرین عملیات

🔹 **مدیریت دشمن**:
• `تنظیم دشمن` (ریپلای) - اضافه کردن به لیست دشمن
• `حذف دشمن` (ریپلای) - حذف از لیست دشمن  
• `لیست دشمن` - نمایش لیست دشمنان
• `insult [on/off]` - فعال/غیرفعال کردن پاسخ خودکار به دشمن

🔹 **سبک متن**:
• `bold on/off` - فونت ضخیم
• `italic on/off` - فونت کج
• `script on/off` - فونت دست‌نویس 
• `double on/off` - فونت دوتایی
• `bubble on/off` - فونت حبابی
• `square on/off` - فونت مربعی
• `strikethrough on/off` - فونت خط خورده
• `underline on/off` - فونت زیر خط دار
• `caps on/off` - فونت بزرگ
• `lowercase on/off` - فونت کوچک
• `title on/off` - فونت عنوان
• `space on/off` - فونت فاصله‌دار
• `reverse on/off` - فونت معکوس
• `rainbow on/off` - فونت رنگین‌کمانی
• `fancy on/off` - فونت فانتزی
• `small_caps on/off` - فونت کوچک کپس
• `bubble_text on/off` - فونت حبابی متن
• `medieval on/off` - فونت قرون وسطایی
• `cursive on/off` - فونت دست‌خط

🔹 **اکشن‌های خودکار**:
• `typing on/off` - تایپینگ دائم
• `online on/off` - آنلاین دائم 
• `reaction on/off` - ری‌اکشن خودکار
• `time on/off` - نمایش ساعت در نام
• `read on/off` - خواندن خودکار پیام‌ها
• `reply on/off` - پاسخ خودکار به پیام‌ها
• `stats on/off` - ثبت آمار پیام‌ها
• `translate on/off` - ترجمه خودکار پیام‌ها
• `set translate [زبان]` - تنظیم زبان پیش‌فرض ترجمه

🔹 **قفل‌های امنیتی**:
• `screenshot on/off` - قفل اسکرین‌شات
• `forward on/off` - قفل فوروارد
• `copy on/off` - قفل کپی
• `delete on/off` - ضد حذف پیام
• `edit on/off` - ضد ویرایش پیام
• `spam on/off` - ضد اسپم
• `link on/off` - فیلتر لینک
• `mention on/off` - فیلتر منشن

🔹 **تبدیل فرمت**:
• `متن به ویس بگو [متن]` - تبدیل متن به ویس
• `متن به عکس [متن]` - تبدیل متن به عکس
• `متن به گیف [متن]` - تبدیل متن به گیف
• `متن به گیف [متن] [افکت]` - تبدیل متن به گیف با افکت (color/zoom/fade)
• `متن به عکس [متن] [رنگ‌پس‌زمینه] [رنگ‌متن]` - تبدیل متن به عکس با رنگ سفارشی
• `qrcode [متن]` - ساخت کیو‌آر‌کد از متن
• `ترجمه [متن] [زبان مقصد]` - ترجمه متن به زبان مورد نظر

🔹 **ذخیره و مدیریت**:
• `save pic` - ذخیره عکس (ریپلای)
• `show pics` - نمایش عکس‌های ذخیره شده
• `save` - ذخیره پیام (ریپلای)
• `saved` - نمایش پیام های ذخیره شده
• `block word [کلمه]` - مسدود کردن کلمه
• `unblock word [کلمه]` - رفع مسدودیت کلمه
• `block list` - نمایش لیست کلمات مسدود شده

🔹 **پیام‌رسانی پیشرفته**:
• `schedule [زمان به دقیقه] [متن پیام]` - ارسال پیام زمان‌دار
• `schedule recurring [فاصله به دقیقه] [متن پیام]` - ارسال پیام تکراری
• `remind [ساعت:دقیقه] [متن پیام]` - تنظیم یادآور
• `spam [تعداد] [متن پیام]` - ارسال پیام تکراری
• `auto reply [کلمه کلیدی] [پاسخ]` - تنظیم پاسخ خودکار
• `delete reply [کلمه کلیدی]` - حذف پاسخ خودکار
• `replies` - نمایش لیست پاسخ‌های خودکار
• `welcome [متن]` - تنظیم پیام خوش‌آمدگویی
• `show welcome` - نمایش پیام خوش‌آمدگویی

🔹 **ابزار کاربردی**:
• `status [متن]` - تنظیم متن وضعیت (بیو)
• `add status [متن]` - اضافه کردن به وضعیت‌های چرخشی
• `status rotation on/off` - فعال/غیرفعال کردن چرخش خودکار وضعیت
• `show status` - نمایش وضعیت‌های چرخشی
• `clear status` - پاک کردن وضعیت‌های چرخشی
• `search [متن]` - جستجو در پیام ها
• `weather [شهر]` - نمایش آب و هوا
• `set weather [کلید API]` - تنظیم کلید API آب و هوا
• `stats [نام چت/آیدی]` - نمایش آمار پیام‌ها

---
📝 دستورات جدید به مرور اضافه می‌شوند. برای اطلاع از آخرین قابلیت‌ها، دستور `پنل` را اجرا کنید.
"""
    try:
        await event.edit(help_text)
    except:
        print("Error displaying help menu")
        print(help_text.replace("**", "").replace("`", ""))

async def show_status(client, event):
    """Show enhanced bot status with detailed information"""
    global start_time

    try:
        # Measure ping
        start_time = time.time()
        await client(functions.PingRequest(ping_id=0))
        end_time = time.time()
        ping = round((end_time - start_time) * 1000, 2)

        # Get time information
        config = load_config()
        tz = pytz.timezone(config['timezone'])
        now = datetime.now(tz)
        
        # Jalali date for Iran
        j_date = jdatetime.datetime.fromgregorian(datetime=now)
        jalali_date = j_date.strftime('%Y/%m/%d')
        local_time = now.strftime('%H:%M:%S')

        # Calculate uptime
        uptime_seconds = int(time.time() - start_time)
        global start_time
        uptime = str(timedelta(seconds=uptime_seconds))

        # Memory usage
        try:
            import psutil
            process = psutil.Process(os.getpid())
            memory_usage = f"{process.memory_info().rss / 1024 / 1024:.2f} MB"
        except ImportError:
            memory_usage = "N/A"

        # Count active chats with protections
        active_protections = sum(1 for v in locked_chats.values() if v)
        
        # Count recurring messages
        recurring_count = len([m for m in periodic_messages if m.get('recurring', False)])

        status_text = f"""
⚡️ **وضعیت ربات سلف بات پلاتینیوم**

📊 **اطلاعات سیستم**:
• پینگ: `{ping} ms`
• زمان کارکرد: `{uptime}`
• مصرف حافظه: `{memory_usage}`
• نسخه ربات: `پلاتینیوم 3.0`
• آخرین پشتیبان‌گیری: `{last_backup_time.strftime('%Y/%m/%d %H:%M') if last_backup_time else 'هیچوقت'}`

📅 **اطلاعات زمانی**:
• تاریخ شمسی: `{jalali_date}`
• ساعت: `{local_time}`
• منطقه زمانی: `{config['timezone']}`

💡 **وضعیت قابلیت‌ها**:
• تایپینگ: {'✅' if actions['typing'] else '❌'}
• آنلاین: {'✅' if actions['online'] else '❌'} 
• ری‌اکشن: {'✅' if actions['reaction'] else '❌'}
• ساعت: {'✅' if time_enabled else '❌'}
• خواندن خودکار: {'✅' if actions['read'] else '❌'}
• پاسخ خودکار: {'✅' if actions['auto_reply'] else '❌'}
• جمع‌آوری آمار: {'✅' if actions['stats'] else '❌'}
• ترجمه خودکار: {'✅' if actions['translate'] else '❌'}
• چرخش وضعیت: {'✅' if status_rotation_active else '❌'}

📌 **آمار**:
• تعداد دشمنان: `{len(enemies)}`
• پیام‌های ذخیره شده: `{len(saved_messages)}`
• یادآوری‌ها: `{len(reminders)}`
• کلمات مسدود شده: `{len(blocked_words)}`
• پاسخ‌های خودکار: `{len(custom_replies)}`
• وضعیت‌های چرخشی: `{len(status_rotation)}`
• پیام‌های زمان‌بندی شده: `{len(periodic_messages)}`
• پیام‌های تکراری فعال: `{recurring_count}`

🔒 **قفل‌های فعال**:
• اسکرین‌شات: `{len(locked_chats['screenshot'])}`
• فوروارد: `{len(locked_chats['forward'])}`
• کپی: `{len(locked_chats['copy'])}`
• ضد حذف: `{len(locked_chats['delete'])}`
• ضد ویرایش: `{len(locked_chats['edit'])}`
• ضد اسپم: `{len(locked_chats['spam'])}`
• فیلتر لینک: `{len(locked_chats['link'])}`
• فیلتر منشن: `{len(locked_chats['mention'])}`

🎨 **تنظیمات ظاهری**:
• فونت فعال: `{current_font}`
• تم فعال: `{theme}`
• تم‌های اختصاصی چت: `{len(chat_themes)}`

🔧 **پیکربندی**:
• حداکثر تعداد اسپم: `{config['max_spam_count']}`
• زبان پیش‌فرض ترجمه: `{config['default_translate_lang']}`
• پشتیبان‌گیری خودکار: {'✅' if config['auto_backup'] else '❌'}
• پشتیبان‌گیری ابری: {'✅' if config['cloud_backup'] else '❌'}
• فاصله پشتیبان‌گیری: `{config['backup_interval']} دقیقه`
"""
        await event.edit(status_text)
    except Exception as e:
        logger.error(f"Error in status handler: {e}")
        print_error(f"Error showing status: {e}")

async def show_chat_stats(client, event, chat_id=None):
    """Display chat statistics"""
    try:
        if not chat_id:
            chat_id = str(event.chat_id)
            
        if chat_id not in message_stats:
            await event.edit("❌ آماری برای این چت ثبت نشده است")
            return
            
        stats = message_stats[chat_id]
        
        # Get chat info
        try:
            chat = await client.get_entity(int(chat_id))
            chat_name = chat.title if hasattr(chat, 'title') else f"چت خصوصی {chat_id}"
        except:
            chat_name = f"چت {chat_id}"
            
        # Get top 5 users
        top_users = sorted(stats["users"].items(), key=lambda x: x[1], reverse=True)[:5]
        top_users_text = ""
        for i, (user_id, count) in enumerate(top_users, 1):
            try:
                user = await client.get_entity(int(user_id))
                user_name = utils.get_display_name(user)
            except:
                user_name = f"کاربر {user_id}"
            top_users_text += f"{i}. {user_name}: {count} پیام\n"
            
        # Get top 5 keywords
        top_keywords = sorted(stats["keywords"].items(), key=lambda x: x[1], reverse=True)[:5]
        keywords_text = "\n".join([f"{i+1}. {word}: {count} بار" for i, (word, count) in enumerate(top_keywords)])
        
        # Most active hours
        max_hour = stats["hourly"].index(max(stats["hourly"]))
        
        # Most active day
        days = ["دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه", "شنبه", "یکشنبه"]
        max_day = days[stats["daily"].index(max(stats["daily"]))]
        
        stats_text = f"""
📊 **آمار چت: {chat_name}**

📈 **آمار کلی**:
• تعداد کل پیام‌ها: `{stats['total_messages']}`
• تعداد کاربران فعال: `{len(stats['users'])}`
• ساعت فعالیت بیشتر: `{max_hour}:00`
• روز فعالیت بیشتر: `{max_day}`

👥 **کاربران فعال**:
{top_users_text}

🔤 **کلمات پرتکرار**:
{keywords_text}
"""
        await event.edit(stats_text)
    except Exception as e:
        logger.error(f"Error in show_chat_stats: {e}")
        await event.edit(f"❌ خطا در نمایش آمار: {str(e)}")

async def main():
    """Main function with enhanced UI and error handling"""
    # Print logo and initialize
    print(LOGO)
    print_header("Initializing Telegram Self-Bot")
    
    # Load configuration
    config = load_config()
    print_info(f"Configuration loaded from {CONFIG_FILE}")
    
    # Setup logging
    log_level = getattr(logging, config['log_level'])
    logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename=LOG_FILE)
    
    # Restore data if available
    if os.path.exists("selfbot_backup.json"):
        if restore_data():
            print_success("Data restored from backup")
        else:
            print_warning("Failed to restore data from backup")
    
    # Initialize client with animated progress
    print_loading("Connecting to Telegram")
    client = TelegramClient(config['session_name'], config['api_id'], config['api_hash'])
    
    try:
        # Connect to Telegram
        await client.connect()
        print_success("Connected to Telegram")
        
        # Check authorization
        if not await client.is_user_authorized():
            print_header("Authentication Required")
            print("Please enter your phone number (e.g., +989123456789):")
            phone = input(f"{Fore.GREEN}> ")
            
            try:
                print_loading("Sending verification code")
                await client.send_code_request(phone)
                print_success("Verification code sent")
                
                print("\nPlease enter the verification code:")
                code = input(f"{Fore.GREEN}> ")
                
                print_loading("Verifying code")
                await client.sign_in(phone, code)
                print_success("Verification successful")
                
            except Exception as e:
                if "two-steps verification" in str(e).lower():
                    print_warning("Two-step verification is enabled")
                    print("Please enter your password:")
                    password = input(f"{Fore.GREEN}> ")
                    
                    print_loading("Verifying password")
                    await client.sign_in(password=password)
                    print_success("Password verification successful")
                else:
                    print_error(f"Login error: {str(e)}")
                    return
        
        # Successfully logged in
        me = await client.get_me()
        print_success(f"Logged in as: {me.first_name} {me.last_name or ''} (@{me.username or 'No username'})")
        print_info("Self-bot is now active! Type 'پنل' in any chat to see commands.")
        
        # Start background tasks
        asyncio.create_task(update_time(client))
        asyncio.create_task(check_reminders(client))
        asyncio.create_task(auto_backup(client))
        
        if status_rotation_active and status_rotation:
            asyncio.create_task(update_status_rotation(client))
        
        # Event handlers for time-related commands
        @client.on(events.NewMessage(pattern=r'^time (on|off)$'))
        async def time_handler(event):
            global time_enabled
            try:
                if not event.from_id or event.from_id.user_id != (await client.get_me()).id:
                    return
                    
                status = event.pattern_match.group(1)
                time_enabled = (status == 'on')
                if not time_enabled:
                    await client(functions.account.UpdateProfileRequest(last_name=''))
                
                # Add to command history
                command_history.append(('time', not time_enabled))
                if len(command_history) > MAX_HISTORY:
                    command_history.pop(0)
                    
                await event.edit(f"✅ نمایش ساعت {'فعال' if time_enabled else 'غیرفعال'} شد")
            except Exception as e:
                logger.error(f"Error in time handler: {e}")
                await event.edit(f"❌ خطا: {str(e)}")

        # Event handlers for enemy-related commands
        @client.on(events.NewMessage(pattern=r'^insult (on|off)$'))
        async def insult_toggle_handler(event):
            try:
                if not event.from_id or event.from_id.user_id != (await client.get_me()).id:
                    return
                    
                status = event.pattern_match.group(1)
                config = load_config()
                config['enemy_auto_reply'] = (status == 'on')
                save_config(config)
                
                await event.edit(f"✅ پاسخ خودکار به دشمن {'فعال' if config['enemy_auto_reply'] else 'غیرفعال'} شد")
            except Exception as e:
                logger.error(f"Error in insult toggle handler: {e}")
                await event.edit(f"❌ خطا: {str(e)}")

        # Event handlers for text-to-media conversion
        @client.on(events.NewMessage(pattern='^متن به ویس بگو (.+)$'))
        async def voice_handler(event):
            try:
                if not event.from_id or event.from_id.user_id != (await client.get_me()).id:
                    return
                    
                text = event.pattern_match.group(1)
                await event.edit("⏳ در حال تبدیل متن به ویس...")
                
                voice_file = await text_to_voice(text)
                if voice_file:
                    await event.delete()
                    await client.send_file(event.chat_id, voice_file)
                    os.remove(voice_file)
                else:
                    await event.edit("❌ خطا در تبدیل متن به ویس")
            except Exception as e:
                logger.error(f"Error in voice handler: {e}")
                await event.edit(f"❌ خطا: {str(e)}")

        @client.on(events.NewMessage(pattern='^save pic$'))
        async def save_pic_handler(event):
            try:
                if not event.from_id or event.from_id.user_id != (await client.get_me()).id:
                    return
                    
                if not event.is_reply:
                    await event.edit("❌ لطفا روی یک عکس ریپلای کنید")
                    return
                    
                replied = await event.get_reply_message()
                if not replied.photo:
                    await event.edit("❌ پیام ریپلای شده عکس نیست")
                    return
                    
                await event.edit("⏳ در حال ذخیره عکس...")
                path = await client.download_media(replied.photo)
                saved_pics.append(path)
                
                # Add to command history
                command_history.append(('save_pic', path))
                if len(command_history) > MAX_HISTORY:
                    command_history.pop(0)
                
                # Backup after significant change
                backup_data()
                
                await event.edit("✅ عکس ذخیره شد")
            except Exception as e:
                logger.error(f"Error in save pic handler: {e}")
                await event.edit(f"❌ خطا: {str(e)}")

        @client.on(events.NewMessage(pattern='^show pics$'))
        async def show_pics_handler(event):
            try:
                if not event.from_id or event.from_id.user_id != (await client.get_me()).id:
                    return
                    
                if not saved_pics:
                    await event.edit("❌ هیچ عکسی ذخیره نشده است")
                    return
                
                await event.edit(f"⏳ در حال بارگذاری {len(saved_pics)} عکس...")
                
                # Send saved pictures one by one
                for i, pic_path in enumerate(saved_pics):
                    if os.path.exists(pic_path):
                        await client.send_file(event.chat_id, pic_path, caption=f"عکس {i+1}/{len(saved_pics)}")
                    else:
                        await client.send_message(event.chat_id, f"❌ عکس {i+1} یافت نشد")
                
                await event.edit(f"✅ {len(saved_pics)} عکس نمایش داده شد")
            except Exception as e:
                logger.error(f"Error in show pics handler: {e}")
                await event.edit(f"❌ خطا: {str(e)}")

        @client.on(events.NewMessage(pattern='^متن به عکس (.+)$'))
        async def img_handler(event):
            try:
                if not event.from_id or event.from_id.user_id != (await client.get_me()).id:
                    return
                
                parts = event.raw_text.split(maxsplit=3)
                text = parts[3] if len(parts) > 3 else event.pattern_match.group(1)
                bg_color = parts[3] if len(parts) > 3 else 'white'
                text_color = parts[4] if len(parts) > 4 else 'black'
                
                await event.edit("⏳ در حال تبدیل متن به عکس...")
                
                img_file = await text_to_image(text, bg_color, text_color)
                if img_file:
                    await event.delete()
                    await client.send_file(event.chat_id, img_file)
                    os.remove(img_file)
                else:
                    await event.edit("❌ خطا در تبدیل متن به عکس")
            except Exception as e:
                logger.error(f"Error in image handler: {e}")
                await event.edit(f"❌ خطا: {str(e)}")

        @client.on(events.NewMessage(pattern='^متن به گیف (.+)$'))
        async def gif_handler(event):
            try:
                if not event.from_id or event.from_id.user_id != (await client.get_me()).id:
                    return
                
                parts = event.raw_text.split(maxsplit=4)
                text = parts[3] if len(parts) > 3 else event.pattern_match.group(1)
                effect = parts[4] if len(parts) > 4 else 'color'
                
                await event.edit("⏳ در حال تبدیل متن به گیف...")
                
                gif_file = await text_to_gif(text, effects=effect)
                if gif_file:
                    await event.delete()
                    await client.send_file(event.chat_id, gif_file)
                    os.remove(gif_file)
                else:
                    await event.edit("❌ خطا در تبدیل متن به گیف")
            except Exception as e:
                logger.error(f"Error in gif handler: {e}")
                await event.edit(f"❌ خطا: {str(e)}")

        @client.on(events.NewMessage(pattern='^qrcode (.+)$'))
        async def qrcode_handler(event):
            try:
                if not event.from_id or event.from_id.user_id != (await client.get_me()).id:
                    return
                    
                text = event.pattern_match.group(1)
                await event.edit("⏳ در حال ساخت کیو آر کد...")
                
                qr_file = await create_qr_code(text)
                if qr_file:
                    await event.delete()
                    await client.send_file(event.chat_id, qr_file, caption=f"QR Code for: {text[:30]}...")
                    os.remove(qr_file)
                else:
                    await event.edit("❌ خطا در ساخت کیو آر کد")
            except Exception as e:
                logger.error(f"Error in qrcode handler: {e}")
                await event.edit(f"❌ خطا: {str(e)}")

        @client.on(events.NewMessage(pattern='^ترجمه (.+?) (.+?)$'))
        async def translate_handler(event):
            try:
                if not event.from_id or event.from_id.user_id != (await client.get_me()).id:
                    return
                    
                parts = event.raw_text.split(maxsplit=2)
                text = parts[1]
                dest = parts[2] if len(parts) > 2 else 'fa'
                
                await event.edit("⏳ در حال ترجمه متن...")
                
                translated = await translate_text(text, dest)
                await event.edit(f"🔄 **متن اصلی**: \n{text}\n\n📝 **ترجمه شده** ({dest}): \n{translated}")
            except Exception as e:
                logger.error(f"Error in translate handler: {e}")
                await event.edit(f"❌ خطا در ترجمه: {str(e)}")

        @client.on(events.NewMessage(pattern='^weather (.+)$'))
        async def weather_handler(event):
            try:
                if not event.from_id or event.from_id.user_id != (await client.get_me()).id:
                    return
                    
                city = event.pattern_match.group(1)
                config = load_config()
                
                if not config.get('weather_api_key'):
                    await event.edit("❌ کلید API آب و هوا تنظیم نشده است. با دستور `set weather [کلید API]` آن را تنظیم کنید")
                    return
                    
                await event.edit(f"⏳ در حال دریافت اطلاعات آب و هوای {city}...")
                
                weather_info = await get_weather(city, config['weather_api_key'])
                await event.edit(weather_info)
            except Exception as e:
                logger.error(f"Error in weather handler: {e}")
                await event.edit(f"❌ خطا در دریافت آب و هوا: {str(e)}")

        @client.on(events.NewMessage(pattern='^set weather (.+)$'))
        async def set_weather_api_handler(event):
            try:
                if not event.from_id or event.from_id.user_id != (await client.get_me()).id:
                    return
                    
                api_key = event.pattern_match.group(1)
                config = load_config()
                config['weather_api_key'] = api_key
                save_config(config)
                
                await event.edit("✅ کلید API آب و هوا با موفقیت تنظیم شد")
            except Exception as e:
                logger.error(f"Error in set weather api handler: {e}")
                await event.edit(f"❌ خطا: {str(e)}")

        @client.on(events.NewMessage(pattern=r'^(screenshot|forward|copy|delete|edit|spam|link|mention) (on|off)$'))
        async def lock_handler(event):
            try:
                if not event.from_id or event.from_id.user_id != (await client.get_me()).id:
                    return
                    
                command, status = event.raw_text.lower().split()
                chat_id = str(event.chat_id)
                
                # Previous state for undo
                prev_state = chat_id in locked_chats[command]
                
                if status == 'on':
                    locked_chats[command].add(chat_id)
                    await event.edit(f"✅ قفل {command} فعال شد")
                else:
                    locked_chats[command].discard(chat_id)
                    await event.edit(f"✅ قفل {command} غیرفعال شد")
                
                # Add to command history
                command_history.append(('lock', (command, chat_id, prev_state)))
                if len(command_history) > MAX_HISTORY:
                    command_history.pop(0)
                    
                # Backup after significant change
                backup_data()
                    
            except Exception as e:
                logger.error(f"Error in lock handler: {e}")
                await event.edit(f"❌ خطا: {str(e)}")

        @client.on(events.NewMessage(pattern='^theme (.+)$'))
        async def theme_handler(event):
            try:
                if not event.from_id or event.from_id.user_id != (await client.get_me()).id:
                    return
                    
                global theme
                new_theme = event.pattern_match.group(1).lower()
                
                if new_theme not in themes:
                    await event.edit(f"❌ تم '{new_theme}' یافت نشد. تم‌های موجود: {', '.join(themes.keys())}")
                    return
                    
                # Store previous state for undo
                prev_theme = theme
                
                # Update theme
                theme = new_theme
                
                # Add to command history
                command_history.append(('theme', prev_theme))
                if len(command_history) > MAX_HISTORY:
                    command_history.pop(0)
                    
                # Backup after change
                backup_data()
                
                await event.edit(f"✅ تم به '{new_theme}' تغییر یافت")
            except Exception as e:
                logger.error(f"Error in theme handler: {e}")
                await event.edit(f"❌ خطا: {str(e)}")

        @client.on(events.NewMessage(pattern='^status (.+)$'))
        async def status_set_handler(event):
            try:
                if not event.from_id or event.from_id.user_id != (await client.get_me()).id:
                    return
                    
                status = event.pattern_match.group(1)
                await client(functions.account.UpdateProfileRequest(about=status))
                await event.edit("✅ وضعیت (بیو) با موفقیت تنظیم شد")
            except Exception as e:
                logger.error(f"Error in status set handler: {e}")
                await event.edit(f"❌ خطا: {str(e)}")

        @client.on(events.NewMessage(pattern='^add status (.+)$'))
        async def add_status_handler(event):
            try:
                if not event.from_id or event.from_id.user_id != (await client.get_me()).id:
                    return
                    
                global status_rotation
                status = event.pattern_match.group(1)
                
                if status in status_rotation:
                    await event.edit("❌ این وضعیت قبلاً در لیست چرخشی وجود دارد")
                    return
                    
                status_rotation.append(status)
                
                # Backup after change
                backup_data()
                
                await event.edit(f"✅ وضعیت به لیست چرخشی اضافه شد (تعداد: {len(status_rotation)})")
            except Exception as e:
                logger.error(f"Error in add status handler: {e}")
                await event.edit(f"❌ خطا: {str(e)}")

        @client.on(events.NewMessage(pattern='^status rotation (on|off)$'))
        async def status_rotation_handler(event):
            try:
                if not event.from_id or event.from_id.user_id != (await client.get_me()).id:
                    return
                    
                global status_rotation_active
                status = event.pattern_match.group(1)
                
                if status == 'on' and not status_rotation:
                    await event.edit("❌ لیست وضعیت‌های چرخشی خالی است. ابتدا با دستور `add status` وضعیت اضافه کنید")
                    return
                    
                # Previous state for undo
                prev_state = status_rotation_active
                
                status_rotation_active = (status == 'on')
                
                # Add to command history
                command_history.append(('status_rotation', prev_state))
                if len(command_history) > MAX_HISTORY:
                    command_history.pop(0)
                    
                # Start or stop the rotation task
                if status_rotation_active:
                    asyncio.create_task(update_status_rotation(client))
                    
                # Backup after change
                backup_data()
                
                await event.edit(f"✅ چرخش خودکار وضعیت {'فعال' if status_rotation_active else 'غیرفعال'} شد")
            except Exception as e:
                logger.error(f"Error in status rotation handler: {e}")
                await event.edit(f"❌ خطا: {str(e)}")

        @client.on(events.NewMessage(pattern='^show status$'))
        async def show_status_handler(event):
            try:
                if not event.from_id or event.from_id.user_id != (await client.get_me()).id:
                    return
                    
                if not status_rotation:
                    await event.edit("❌ لیست وضعیت‌های چرخشی خالی است")
                    return
                    
                statuses = "\n".join([f"{i+1}. {status}" for i, status in enumerate(status_rotation)])
                await event.edit(f"📋 **لیست وضعیت‌های چرخشی**:\n\n{statuses}\n\n🔄 وضعیت چرخش: {'✅ فعال' if status_rotation_active else '❌ غیرفعال'}")
            except Exception as e:
                logger.error(f"Error in show status handler: {e}")
                await event.edit(f"❌ خطا: {str(e)}")

        @client.on(events.NewMessage(pattern='^clear status$'))
        async def clear_status_handler(event):
            try:
                if not event.from_id or event.from_id.user_id != (await client.get_me()).id:
                    return
                    
                global status_rotation, status_rotation_active
                
                # Store for undo
                prev_statuses = status_rotation.copy()
                prev_active = status_rotation_active
                
                # Clear the statuses
                status_rotation = []
                status_rotation_active = False
                
                # Add to command history
                command_history.append(('clear_status', (prev_statuses, prev_active)))
                if len(command_history) > MAX_HISTORY:
                    command_history.pop(0)
                    
                # Backup after change
                backup_data()
                
                await event.edit("✅ لیست وضعیت‌های چرخشی پاک شد")
            except Exception as e:
                logger.error(f"Error in clear status handler: {e}")
                await event.edit(f"❌ خطا: {str(e)}")

        @client.on(events.NewMessage(pattern='^cloud backup (on|off)$'))
        async def cloud_backup_handler(event):
            try:
                if not event.from_id or event.from_id.user_id != (await client.get_me()).id:
                    return
                    
                status = event.pattern_match.group(1)
                config = load_config()
                
                # Previous state for undo
                prev_state = config['cloud_backup']
                
                config['cloud_backup'] = (status == 'on')
                save_config(config)
                
                # Add to command history
                command_history.append(('cloud_backup', prev_state))
                if len(command_history) > MAX_HISTORY:
                    command_history.pop(0)
                
                if status == 'on':
                    # Perform an immediate backup to test
                    await event.edit("⏳ در حال آزمایش پشتیبان‌گیری ابری...")
                    if await cloud_backup(client):
                        await event.edit("✅ پشتیبان‌گیری ابری فعال شد و با موفقیت آزمایش شد")
                    else:
                        config['cloud_backup'] = False
                        save_config(config)
                        await event.edit("❌ خطا در پشتیبان‌گیری ابری. این قابلیت غیرفعال شد")
                else:
                    await event.edit("✅ پشتیبان‌گیری ابری غیرفعال شد")
            except Exception as e:
                logger.error(f"Error in cloud backup handler: {e}")
                await event.edit(f"❌ خطا: {str(e)}")

        @client.on(events.NewMessage(pattern='^translate (on|off)$'))
        async def translate_toggle_handler(event):
            try:
                if not event.from_id or event.from_id.user_id != (await client.get_me()).id:
                    return
                    
                status = event.pattern_match.group(1)
                
                # Store previous state for undo
                prev_state = actions['translate']
                
                # Update state
                actions['translate'] = (status == 'on')
                
                # Add to command history
                command_history.append(('action', ('translate', prev_state)))
                if len(command_history) > MAX_HISTORY:
                    command_history.pop(0)
                    
                # Backup after change
                backup_data()
                
                await event.edit(f"✅ ترجمه خودکار {'فعال' if actions['translate'] else 'غیرفعال'} شد")
            except Exception as e:
                logger.error(f"Error in translate toggle handler: {e}")
                await event.edit(f"❌ خطا: {str(e)}")

        @client.on(events.NewMessage(pattern='^set translate (.+)$'))
        async def set_translate_lang_handler(event):
            try:
                if not event.from_id or event.from_id.user_id != (await client.get_me()).id:
                    return
                    
                lang = event.pattern_match.group(1)
                config = load_config()
                
                # Store previous state for undo
                prev_lang = config['default_translate_lang']
                
                # Update config
                config['default_translate_lang'] = lang
                save_config(config)
                
                # Add to command history
                command_history.append(('translate_lang', prev_lang))
                if len(command_history) > MAX_HISTORY:
                    command_history.pop(0)
                
                await event.edit(f"✅ زبان پیش‌فرض ترجمه به '{lang}' تغییر یافت")
            except Exception as e:
                logger.error(f"Error in set translate language handler: {e}")
                await event.edit(f"❌ خطا: {str(e)}")

        @client.on(events.NewMessage(pattern='^stats (on|off)$'))
        async def stats_toggle_handler(event):
            try:
                if not event.from_id or event.from_id.user_id != (await client.get_me()).id:
                    return
                    
                status = event.pattern_match.group(1)
                
                # Store previous state for undo
                prev_state = actions['stats']
                
                # Update state
                actions['stats'] = (status == 'on')
                
                # Add to command history
                command_history.append(('action', ('stats', prev_state)))
                if len(command_history) > MAX_HISTORY:
                    command_history.pop(0)
                    
                # Backup after change
                backup_data()
                
                await event.edit(f"✅ ثبت آمار پیام‌ها {'فعال' if actions['stats'] else 'غیرفعال'} شد")
            except Exception as e:
                logger.error(f"Error in stats toggle handler: {e}")
                await event.edit(f"❌ خطا: {str(e)}")

        @client.on(events.NewMessage(pattern='^stats$'))
        async def show_chat_stats_handler(event):
            try:
                if not event.from_id or event.from_id.user_id != (await client.get_me()).id:
                    return
                    
                await show_chat_stats(client, event)
            except Exception as e:
                logger.error(f"Error in show chat stats handler: {e}")
                await event.edit(f"❌ خطا: {str(e)}")

        @client.on(events.NewMessage(pattern='^stats (.+)$'))
        async def show_specific_chat_stats_handler(event):
            try:
                if not event.from_id or event.from_id.user_id != (await client.get_me()).id:
                    return
                    
                chat_id = event.pattern_match.group(1)
                try:
                    # Try to convert to integer ID
                    chat_id = str(int(chat_id))
                except:
                    # It might be a username or chat name
                    try:
                        chat = await client.get_entity(chat_id)
                        chat_id = str(chat.id)
                    except:
                        await event.edit(f"❌ چت '{chat_id}' یافت نشد")
                        return
                
                await show_chat_stats(client, event, chat_id)
            except Exception as e:
                logger.error(f"Error in show specific chat stats handler: {e}")
                await event.edit(f"❌ خطا: {str(e)}")

        @client.on(events.NewMessage(pattern='^welcome (.+)$'))
        async def set_welcome_handler(event):
            try:
                if not event.from_id or event.from_id.user_id != (await client.get_me()).id:
                    return
                    
                message = event.pattern_match.group(1)
                chat_id = str(event.chat_id)
                
                # Store previous welcome message for undo
                prev_welcome = welcome_messages.get(chat_id, None)
                
                # Update welcome message
                welcome_messages[chat_id] = message
                
                # Add to command history
                command_history.append(('welcome', (chat_id, prev_welcome)))
                if len(command_history) > MAX_HISTORY:
                    command_history.pop(0)
                    
                # Backup after change
                backup_data()
                
                await event.edit("✅ پیام خوش‌آمدگویی با موفقیت تنظیم شد")
            except Exception as e:
                logger.error(f"Error in set welcome handler: {e}")
                await event.edit(f"❌ خطا: {str(e)}")

        @client.on(events.NewMessage(pattern='^show welcome$'))
        async def show_welcome_handler(event):
            try:
                if not event.from_id or event.from_id.user_id != (await client.get_me()).id:
                    return
                    
                chat_id = str(event.chat_id)
                
                if chat_id not in welcome_messages:
                    await event.edit("❌ پیام خوش‌آمدگویی برای این چت تنظیم نشده است")
                    return
                    
                welcome = welcome_messages[chat_id]
                await event.edit(f"📝 **پیام خوش‌آمدگویی چت فعلی**:\n\n{welcome}")
            except Exception as e:
                logger.error(f"Error in show welcome handler: {e}")
                await event.edit(f"❌ خطا: {str(e)}")

        @client.on(events.NewMessage(pattern='پنل'))
        async def panel_handler(event):
            try:
                if not event.from_id:
                    return
                    
                if event.from_id.user_id == (await client.get_me()).id:
                    await show_help_menu(client, event)
            except Exception as e:
                logger.error(f"Error in panel handler: {e}")
                pass

        @client.on(events.NewMessage(pattern='undo'))
        async def undo_handler(event):
            try:
                if not event.from_id or event.from_id.user_id != (await client.get_me()).id:
                    return
                    
                if not command_history:
                    await event.edit("❌ تاریخچه دستورات خالی است")
                    return
                
                last_command = command_history.pop()
                command_type, data = last_command
                
                if command_type == 'time':
                    global time_enabled
                    time_enabled = data
                    if not time_enabled:
                        await client(functions.account.UpdateProfileRequest(last_name=''))
                    await event.edit(f"✅ وضعیت نمایش ساعت به {'فعال' if time_enabled else 'غیرفعال'} برگردانده شد")
                
                elif command_type == 'lock':
                    lock_type, chat_id, prev_state = data
                    if prev_state:
                        locked_chats[lock_type].add(chat_id)
                    else:
                        locked_chats[lock_type].discard(chat_id)
                    await event.edit(f"✅ وضعیت قفل {lock_type} به {'فعال' if prev_state else 'غیرفعال'} برگردانده شد")
                
                elif command_type == 'font':
                    global current_font
                    current_font = data
                    await event.edit(f"✅ فونت به {current_font} برگردانده شد")
                
                elif command_type == 'enemy_add':
                    enemies.discard(data)
                    await event.edit("✅ کاربر از لیست دشمن حذف شد")
                
                elif command_type == 'enemy_remove':
                    enemies.add(data)
                    await event.edit("✅ کاربر به لیست دشمن اضافه شد")
                
                elif command_type == 'action':
                    action_type, prev_state = data
                    actions[action_type] = prev_state
                    await event.edit(f"✅ وضعیت {action_type} به {'فعال' if prev_state else 'غیرفعال'} برگردانده شد")
                
                elif command_type == 'save_msg':
                    saved_messages.pop()
                    await event.edit("✅ آخرین پیام ذخیره شده حذف شد")
                
                elif command_type == 'save_pic':
                    path = data
                    if path in saved_pics:
                        saved_pics.remove(path)
                    if os.path.exists(path):
                        os.remove(path)
                    await event.edit("✅ آخرین عکس ذخیره شده حذف شد")
                
                elif command_type == 'block_word':
                    blocked_words.remove(data)
                    await event.edit(f"✅ کلمه '{data}' از لیست کلمات مسدود شده حذف شد")
                
                elif command_type == 'unblock_word':
                    blocked_words.append(data)
                    await event.edit(f"✅ کلمه '{data}' به لیست کلمات مسدود شده اضافه شد")
                
                elif command_type == 'add_reply':
                    trigger = data
                    if trigger in custom_replies:
                        del custom_replies[trigger]
                    await event.edit(f"✅ پاسخ خودکار برای '{trigger}' حذف شد")
                
                elif command_type == 'del_reply':
                    trigger, response = data
                    custom_replies[trigger] = response
                    await event.edit(f"✅ پاسخ خودکار برای '{trigger}' بازگردانده شد")
                
                elif command_type == 'theme':
                    global theme
                    theme = data
                    await event.edit(f"✅ تم به '{theme}' برگردانده شد")
                
                elif command_type == 'translate_lang':
                    config = load_config()
                    config['default_translate_lang'] = data
                    save_config(config)
                    await event.edit(f"✅ زبان پیش‌فرض ترجمه به '{data}' برگردانده شد")
                
                elif command_type == 'cloud_backup':
                    config = load_config()
                    config['cloud_backup'] = data
                    save_config(config)
                    await event.edit(f"✅ وضعیت پشتیبان‌گیری ابری به {'فعال' if data else 'غیرفعال'} برگردانده شد")
                
                elif command_type == 'status_rotation':
                    global status_rotation_active
                    status_rotation_active = data
                    if status_rotation_active and status_rotation:
                        asyncio.create_task(update_status_rotation(client))
                    await event.edit(f"✅ وضعیت چرخش خودکار وضعیت به {'فعال' if data else 'غیرفعال'} برگردانده شد")
                
                elif command_type == 'clear_status':
                    global status_rotation
                    statuses, active = data
                    status_rotation = statuses
                    status_rotation_active = active
                    if active:
                        asyncio.create_task(update_status_rotation(client))
                    await event.edit("✅ لیست وضعیت‌های چرخشی بازگردانده شد")
                
                elif command_type == 'welcome':
                    chat_id, prev_welcome = data
                    if prev_welcome:
                        welcome_messages[chat_id] = prev_welcome
                    else:
                        if chat_id in welcome_messages:
                            del welcome_messages[chat_id]
                    await event.edit("✅ پیام خوش‌آمدگویی به وضعیت قبلی برگردانده شد")
                
                # Backup after undo
                backup_data()
                
            except Exception as e:
                logger.error(f"Error in undo handler: {e}")
                await event.edit(f"❌ خطا در برگرداندن عملیات: {str(e)}")

        @client.on(events.NewMessage)
        async def enemy_handler(event):
            try:
                if not event.from_id:
                    return
                
                config = load_config()
                if event.from_id.user_id == (await client.get_me()).id:
                    if event.raw_text == 'تنظیم دشمن' and event.is_reply:
                        # Fix for enemy reply bug
                        replied = await event.get_reply_message()
                        if replied and replied.from_id and hasattr(replied.from_id, 'user_id'):
                            user_id = str(replied.from_id.user_id)
                            # Previous state for undo
                            prev_state = user_id in enemies
                            
                            # Add to enemies set
                            enemies.add(user_id)
                            
                            # Add to command history
                            command_history.append(('enemy_add', user_id))
                            if len(command_history) > MAX_HISTORY:
                                command_history.pop(0)
                                
                            # Backup after significant change
                            backup_data()
                            
                            await event.reply('✅ کاربر به لیست دشمن اضافه شد')
                        else:
                            await event.reply('❌ نمی‌توان این کاربر را به لیست دشمن اضافه کرد')

                    elif event.raw_text == 'حذف دشمن' and event.is_reply:
                        replied = await event.get_reply_message()
                        if replied and replied.from_id and hasattr(replied.from_id, 'user_id'):
                            user_id = str(replied.from_id.user_id)
                            # Previous state for undo
                            prev_state = user_id in enemies
                            
                            # Remove from enemies set
                            enemies.discard(user_id)
                            
                            # Add to command history
                            command_history.append(('enemy_remove', user_id))
                            if len(command_history) > MAX_HISTORY:
                                command_history.pop(0)
                                
                            # Backup after significant change
                            backup_data()
                            
                            await event.reply('✅ کاربر از لیست دشمن حذف شد')
                        else:
                            await event.reply('❌ نمی‌توان این کاربر را از لیست دشمن حذف کرد')

                    elif event.raw_text == 'لیست دشمن':
                        enemy_list = ''
                        for i, enemy in enumerate(enemies, 1):
                            try:
                                user = await client.get_entity(int(enemy))
                                enemy_list += f'{i}. {user.first_name} {user.last_name or ""} (@{user.username or "بدون یوزرنیم"})\n'
                            except:
                                enemy_list += f'{i}. ID: {enemy}\n'
                        await event.reply(enemy_list or '❌ لیست دشمن خالی است')

                # Auto-reply to enemy messages
                elif config['enemy_auto_reply'] and str(event.from_id.user_id) in enemies:
                    # Fix: Only reply to enemies if auto-reply is enabled
                    insult1 = random.choice(insults)
                    insult2 = random.choice(insults)
                    while insult2 == insult1:
                        insult2 = random.choice(insults)
                    
                    # Send insults with a slight delay
                    await event.reply(insult1)
                    await asyncio.sleep(0.5)  # Increased delay for better visibility
                    await event.reply(insult2)
            except Exception as e:
                logger.error(f"Error in enemy handler: {e}")
                pass

        @client.on(events.NewMessage)
        async def font_handler(event):
            global current_font
            
            try:
                if not event.from_id or not event.raw_text:
                    return
                            
                if event.from_id.user_id != (await client.get_me()).id:
                    return

                text = event.raw_text.lower().split()
                
                # Font style settings
                if len(text) == 2 and text[1] in ['on', 'off'] and text[0] in font_styles:
                    font, status = text
                    
                    # Previous state for undo
                    prev_font = current_font
                    
                    if status == 'on':
                        current_font = font
                        await event.edit(f'✅ حالت {font} فعال شد')
                    else:
                        current_font = 'normal'
                        await event.edit(f'✅ حالت {font} غیرفعال شد')
                    
                    # Add to command history
                    command_history.append(('font', prev_font))
                    if len(command_history) > MAX_HISTORY:
                        command_history.pop(0)
                
                # Apply font formatting to message
                elif current_font != 'normal' and current_font in font_styles:
                    await event.edit(font_styles[current_font](event.raw_text))
            except Exception as e:
                logger.error(f"Error in font handler: {e}")
                pass

        @client.on(events.NewMessage)
        async def check_locks(event):
            try:
                chat_id = str(event.chat_id)
                
                # Check if message forwarding is locked in this chat
                if chat_id in locked_chats['forward'] and event.forward:
                    await event.delete()
                    logger.info(f"Deleted forwarded message in chat {chat_id}")
                    
                # Check if message copying is locked in this chat
                if chat_id in locked_chats['copy'] and event.forward_from:
                    await event.delete()
                    logger.info(f"Deleted copied message in chat {chat_id}")
                    
                # Check if links are blocked in this chat
                if chat_id in locked_chats['link'] and event.text:
                    # Simple regex for URL matching
                    url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
                    if url_pattern.search(event.text):
                        await event.delete()
                        logger.info(f"Deleted message with link in chat {chat_id}")
                        
                # Check if mentions are blocked in this chat
                if chat_id in locked_chats['mention'] and event.text:
                    if '@' in event.text:
                        await event.delete()
                        logger.info(f"Deleted message with mention in chat {chat_id}")
                    
            except Exception as e:
                logger.error(f"Error in check locks: {e}")

        @client.on(events.NewMessage)
        async def message_handler(event):
            try:
                # Track message stats if enabled
                if actions['stats']:
                    await track_message_stats(event)
                
                # Auto-read messages if enabled
                if actions['read']:
                    await auto_read_messages(event, client)
                
                # Auto-translate if enabled
                if actions['translate'] and event.text:
                    await auto_translate_message(event, client)
                
                # Do not process further if message is not from the user
                if not event.from_id or event.from_id.user_id != (await client.get_me()).id:
                    # Check for custom replies if auto_reply is enabled
                    if actions['auto_reply'] and event.raw_text and event.raw_text in custom_replies:
                        await event.reply(custom_replies[event.raw_text])
                    return

                # Check for blocked words
                if any(word in event.raw_text.lower() for word in blocked_words):
                    await event.delete()
                    return

                # Auto actions
                if actions['typing']:
                    asyncio.create_task(auto_typing(client, event.chat_id))
                
                if actions['reaction']:
                    await auto_reaction(event)

                # Schedule message
                if event.raw_text.startswith('schedule '):
                    if event.raw_text.startswith('schedule recurring '):
                        parts = event.raw_text.split(maxsplit=3)
                        if len(parts) >= 4:
                            try:
                                interval = int(parts[2])
                                message = parts[3]
                                
                                # Add to periodic messages list
                                periodic_messages.append({
                                    'chat_id': event.chat_id,
                                    'message': message,
                                    'interval': interval,
                                    'recurring': True,
                                    'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                })
                                
                                # Start task
                                asyncio.create_task(schedule_message(client, event.chat_id, 0, message, True, interval))
                                
                                # Backup after significant change
                                backup_data()
                                
                                await event.reply(f'✅ پیام تکراری هر {interval} دقیقه ارسال خواهد شد')
                            except ValueError:
                                await event.reply('❌ فرمت صحیح: schedule recurring [فاصله به دقیقه] [پیام]')
                    else:
                        parts = event.raw_text.split(maxsplit=2)
                        if len(parts) == 3:
                            try:
                                delay = int(parts[1])
                                message = parts[2]
                                
                                # Add to periodic messages list
                                periodic_messages.append({
                                    'chat_id': event.chat_id,
                                    'message': message,
                                    'delay': delay,
                                    'recurring': False,
                                    'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                })
                                
                                asyncio.create_task(schedule_message(client, event.chat_id, delay, message))
                                
                                # Backup after significant change
                                backup_data()
                                
                                await event.reply(f'✅ پیام بعد از {delay} دقیقه ارسال خواهد شد')
                            except ValueError:
                                await event.reply('❌ فرمت صحیح: schedule [زمان به دقیقه] [پیام]')

                # Spam messages
                elif event.raw_text.startswith('spam '):
                    parts = event.raw_text.split(maxsplit=2)
                    if len(parts) == 3:
                        try:
                            count = int(parts[1])
                            config = load_config()
                            max_spam = config.get('max_spam_count', 50)
                            
                            if count > max_spam:  # Limit to prevent abuse
                                await event.reply(f'❌ حداکثر تعداد پیام برای اسپم {max_spam} است')
                                return
                                
                            message = parts[2]
                            asyncio.create_task(spam_messages(client, event.chat_id, count, message))
                        except ValueError:
                            await event.reply('❌ فرمت صحیح: spam [تعداد] [پیام]')

                # Save message
                elif event.raw_text == 'save' and event.is_reply:
                    replied = await event.get_reply_message()
                    if replied and replied.text:
                        # Previous state for undo
                        prev_len = len(saved_messages)
                        
                        saved_messages.append(replied.text)
                        
                        # Add to command history
                        command_history.append(('save_msg', None))
                        if len(command_history) > MAX_HISTORY:
                            command_history.pop(0)
                            
                        # Backup after significant change
                        backup_data()
                        
                        await event.reply('✅ پیام ذخیره شد')
                    else:
                        await event.reply('❌ پیام ریپلای شده متن ندارد')

                # Show saved messages
                elif event.raw_text == 'saved':
                    if not saved_messages:
                        await event.reply('❌ پیامی ذخیره نشده است')
                        return
                        
                    saved_text = '\n\n'.join(f'{i+1}. {msg}' for i, msg in enumerate(saved_messages))
                    
                    # Split long messages if needed
                    if len(saved_text) > 4000:
                        chunks = [saved_text[i:i+4000] for i in range(0, len(saved_text), 4000)]
                        for i, chunk in enumerate(chunks):
                            await event.reply(f"بخش {i+1}/{len(chunks)}:\n\n{chunk}")
                    else:
                        await event.reply(saved_text)

                # Set reminder
                elif event.raw_text.startswith('remind '):
                    parts = event.raw_text.split(maxsplit=2)
                    if len(parts) == 3:
                        time_str = parts[1]
                        message = parts[2]
                        
                        # Validate time format (HH:MM)
                        if re.match(r'^([01]?[0-9]|2[0-3]):([0-5][0-9])$', time_str):
                            reminders.append((time_str, message, event.chat_id))
                            
                            # Backup after significant change
                            backup_data()
                            
                            await event.reply(f'✅ یادآور برای ساعت {time_str} تنظیم شد')
                        else:
                            await event.reply('❌ فرمت زمان اشتباه است. از فرمت HH:MM استفاده کنید')
                    else:
                        await event.reply('❌ فرمت صحیح: remind [زمان] [پیام]')

                # Search in messages
                elif event.raw_text.startswith('search '):
                    query = event.raw_text.split(maxsplit=1)[1]
                    await event.edit(f"🔍 در حال جستجوی '{query}'...")
                    
                    messages = await client.get_messages(event.chat_id, search=query, limit=10)
                    if not messages:
                        await event.edit("❌ پیامی یافت نشد")
                        return
                        
                    result = f"🔍 نتایج جستجو برای '{query}':\n\n"
                    for i, msg in enumerate(messages, 1):
                        sender = await msg.get_sender()
                        sender_name = utils.get_display_name(sender) if sender else "Unknown"
                        result += f"{i}. از {sender_name}: {msg.text[:100]}{'...' if len(msg.text) > 100 else ''}\n\n"
                    
                    await event.edit(result)

                # Block word
                elif event.raw_text.startswith('block word '):
                    word = event.raw_text.split(maxsplit=2)[2].lower()
                    if word in blocked_words:
                        await event.reply(f"❌ کلمه '{word}' قبلاً مسدود شده است")
                    else:
                        # Previous state for undo
                        blocked_words.append(word)
                        
                        # Add to command history
                        command_history.append(('block_word', word))
                        if len(command_history) > MAX_HISTORY:
                            command_history.pop(0)
                            
                        # Backup after significant change
                        backup_data()
                        
                        await event.reply(f"✅ کلمه '{word}' مسدود شد")

                # Unblock word
                elif event.raw_text.startswith('unblock word '):
                    word = event.raw_text.split(maxsplit=2)[2].lower()
                    if word not in blocked_words:
                        await event.reply(f"❌ کلمه '{word}' در لیست مسدود شده‌ها نیست")
                    else:
                        # Previous state for undo
                        blocked_words.remove(word)
                        
                        # Add to command history
                        command_history.append(('unblock_word', word))
                        if len(command_history) > MAX_HISTORY:
                            command_history.pop(0)
                            
                        # Backup after significant change
                        backup_data()
                        
                        await event.reply(f"✅ کلمه '{word}' از لیست مسدود شده‌ها حذف شد")

                # Show blocked words
                elif event.raw_text == 'block list':
                    if not blocked_words:
                        await event.reply("❌ لیست کلمات مسدود شده خالی است")
                    else:
                        block_list = '\n'.join(f"{i+1}. {word}" for i, word in enumerate(blocked_words))
                        await event.reply(f"📋 لیست کلمات مسدود شده:\n\n{block_list}")

                # Set auto reply
                elif event.raw_text.startswith('auto reply '):
                    parts = event.raw_text.split(maxsplit=3)
                    if len(parts) == 4:
                        trigger = parts[2]
                        response = parts[3]
                        
                        # Previous state for undo
                        prev_response = custom_replies.get(trigger, None)
                        
                        custom_replies[trigger] = response
                        
                        # Add to command history
                        command_history.append(('add_reply', trigger))
                        if len(command_history) > MAX_HISTORY:
                            command_history.pop(0)
                            
                        # Backup after significant change
                        backup_data()
                        
                        await event.reply(f"✅ پاسخ خودکار برای '{trigger}' تنظیم شد")
                    else:
                        await event.reply("❌ فرمت صحیح: auto reply [کلمه کلیدی] [پاسخ]")

                # Delete auto reply
                elif event.raw_text.startswith('delete reply '):
                    trigger = event.raw_text.split(maxsplit=2)[2]
                    if trigger not in custom_replies:
                        await event.reply(f"❌ هیچ پاسخ خودکاری برای '{trigger}' وجود ندارد")
                    else:
                        # Previous state for undo
                        prev_response = custom_replies[trigger]
                        
                        del custom_replies[trigger]
                        
                        # Add to command history
                        command_history.append(('del_reply', (trigger, prev_response)))
                        if len(command_history) > MAX_HISTORY:
                            command_history.pop(0)
                            
                        # Backup after significant change
                        backup_data()
                        
                        await event.reply(f"✅ پاسخ خودکار برای '{trigger}' حذف شد")

                # Show auto replies
                elif event.raw_text == 'replies':
                    if not custom_replies:
                        await event.reply("❌ هیچ پاسخ خودکاری تنظیم نشده است")
                    else:
                        reply_list = '\n\n'.join(f"🔹 {trigger}:\n{response}" for trigger, response in custom_replies.items())
                        await event.reply(f"📋 لیست پاسخ‌های خودکار:\n\n{reply_list}")

                # Backup data manually
                elif event.raw_text == 'backup':
                    if backup_data():
                        await event.reply("✅ پشتیبان‌گیری با موفقیت انجام شد")
                    else:
                        await event.reply("❌ خطا در پشتیبان‌گیری")

                # Restore data manually
                elif event.raw_text == 'restore':
                    if restore_data():
                        await event.reply("✅ بازیابی داده‌ها با موفقیت انجام شد")
                    else:
                        await event.reply("❌ فایل پشتیبان یافت نشد یا مشکلی در بازیابی وجود دارد")

                # Toggle typing status
                elif event.raw_text in ['typing on', 'typing off']:
                    # Previous state for undo
                    prev_state = actions['typing']
                    
                    actions['typing'] = event.raw_text.endswith('on')
                    
                    # Add to command history
                    command_history.append(('action', ('typing', prev_state)))
                    if len(command_history) > MAX_HISTORY:
                        command_history.pop(0)
                    
                    await event.reply(f"✅ تایپینگ {'فعال' if actions['typing'] else 'غیرفعال'} شد")

                # Toggle online status
                elif event.raw_text in ['online on', 'online off']:
                    # Previous state for undo
                    prev_state = actions['online']
                    
                    actions['online'] = event.raw_text.endswith('on')
                    
                    # Add to command history
                    command_history.append(('action', ('online', prev_state)))
                    if len(command_history) > MAX_HISTORY:
                        command_history.pop(0)
                    
                    if actions['online']:
                        asyncio.create_task(auto_online(client))
                    await event.reply(f"✅ آنلاین {'فعال' if actions['online'] else 'غیرفعال'} شد")

                # Toggle reaction status
                elif event.raw_text in ['reaction on', 'reaction off']:
                    # Previous state for undo
                    prev_state = actions['reaction']
                    
                    actions['reaction'] = event.raw_text.endswith('on')
                    
                    # Add to command history
                    command_history.append(('action', ('reaction', prev_state)))
                    if len(command_history) > MAX_HISTORY:
                        command_history.pop(0)
                    
                    await event.reply(f"✅ ری‌اکشن {'فعال' if actions['reaction'] else 'غیرفعال'} شد")

                # Toggle read status
                elif event.raw_text in ['read on', 'read off']:
                    # Previous state for undo
                    prev_state = actions['read']
                    
                    actions['read'] = event.raw_text.endswith('on')
                    
                    # Add to command history
                    command_history.append(('action', ('read', prev_state)))
                    if len(command_history) > MAX_HISTORY:
                        command_history.pop(0)
                    
                    await event.reply(f"✅ خواندن خودکار {'فعال' if actions['read'] else 'غیرفعال'} شد")

                # Toggle auto reply status
                elif event.raw_text in ['reply on', 'reply off']:
                    # Previous state for undo
                    prev_state = actions['auto_reply']
                    
                    actions['auto_reply'] = event.raw_text.endswith('on')
                    
                    # Add to command history
                    command_history.append(('action', ('auto_reply', prev_state)))
                    if len(command_history) > MAX_HISTORY:
                        command_history.pop(0)
                    
                    await event.reply(f"✅ پاسخ خودکار {'فعال' if actions['auto_reply'] else 'غیرفعال'} شد")

                # Exit command
                elif event.raw_text == 'exit':
                    await event.reply("✅ در حال خروج از برنامه...")
                    global running
                    running = False
                    await client.disconnect()
                    return
            except Exception as e:
                logger.error(f"Error in message handler: {e}")
                pass

        @client.on(events.NewMessage(pattern='وضعیت'))
        async def status_handler(event):
            try:
                if not event.from_id:
                    return
                    
                if event.from_id.user_id == (await client.get_me()).id:
                    await show_status(client, event)
            except Exception as e:
                logger.error(f"Error in status handler: {e}")
                print_error(f"Error showing status: {e}")

        @client.on(events.MessageDeleted)
        async def delete_handler(event):
            """Handle deleted messages for anti-delete feature"""
            try:
                for deleted_id in event.deleted_ids:
                    chat_id = str(event.chat_id)
                    if chat_id in locked_chats['delete']:
                        # Try to find the message in our cache
                        msg = await client.get_messages(event.chat_id, ids=deleted_id)
                        if msg and msg.text:
                            sender = await msg.get_sender()
                            sender_name = utils.get_display_name(sender) if sender else "Unknown"
                            
                            saved_text = f"🔴 پیام حذف شده از {sender_name}:\n{msg.text}"
                            await client.send_message(event.chat_id, saved_text)
            except Exception as e:
                logger.error(f"Error in delete handler: {e}")

        @client.on(events.MessageEdited)
        async def edit_handler(event):
            """Handle edited messages for anti-edit feature"""
            try:
                chat_id = str(event.chat_id)
                if chat_id in locked_chats['edit'] and event.message:
                    # We need to find the original message
                    msg_id = event.message.id
                    
                    # Get edit history
                    edit_history = await client(functions.channels.GetMessageEditHistoryRequest(
                        channel=event.chat_id,
                        id=msg_id
                    ))
                    
                    if edit_history and edit_history.messages:
                        # Get the original message (first in history)
                        original = edit_history.messages[-1]
                        current = event.message
                        
                        if original.message != current.message:
                            sender = await event.get_sender()
                            sender_name = utils.get_display_name(sender) if sender else "Unknown"
                            
                            edit_text = f"🔄 پیام ویرایش شده از {sender_name}:\n\nقبل:\n{original.message}\n\nبعد:\n{current.message}"
                            await client.send_message(event.chat_id, edit_text)
            except Exception as e:
                logger.error(f"Error in edit handler: {e}")

        @client.on(events.ChatAction)
        async def chat_action_handler(event):
            """Handle chat actions like user joining"""
            try:
                # Handle welcome messages
                if event.user_joined or event.user_added:
                    chat_id = str(event.chat_id)
                    if chat_id in welcome_messages:
                        user = await event.get_user()
                        user_name = user.first_name if user else "Unknown"
                        welcome_text = welcome_messages[chat_id].replace("{user}", user_name)
                        await client.send_message(event.chat_id, welcome_text)
            except Exception as e:
                logger.error(f"Error in chat action handler: {e}")

        # Run the client until disconnected
        print_success("Self-bot is running")
        await client.run_until_disconnected()

    except KeyboardInterrupt:
        print_warning("\nKilling the self-bot by keyboard interrupt...")
        return
    except Exception as e:
        print_error(f"\nUnexpected error: {e}")
        logger.error(f"Unexpected error: {e}")
        return
    finally:
        
        running = False
        if client and client.is_connected():
            await client.disconnect()
        print_info("Self-bot has been shut down")

def init():
    """Initialize and run the self-bot"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print_warning("\nExiting self-bot...")
    except Exception as e:
        print_error(f"\nUnexpected error: {e}")
        logging.error(f"Unexpected init error: {e}")

if __name__ == '__main__':
    init()
