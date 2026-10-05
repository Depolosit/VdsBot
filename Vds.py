import telebot
import subprocess
import os
import zipfile
import tempfile
import shutil
from telebot import types
import time
from datetime import datetime, timedelta
import sqlite3
import json
import logging
import signal
import threading
import re
import sys
import atexit
import requests
import hashlib
import mimetypes
import struct
import base64
import csv
import io
from collections import defaultdict
import gzip
import urllib.parse

                          
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "🤖 @RolexsWhat Bot - Operational"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
                                                                                   
    host = os.environ.get("FLASK_BIND_HOST", "127.0.0.1")
    app.run(host=host, port=port, threaded=True)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    print("Flask Canlı Tutma sunucusu başlatıldı.")
                              
                                                                                
TOKEN = "8918219884:AAG2j5F3C4CHYqAT_kBUaXgIQMH1NdAuqFk"
try:
    OWNER_ID = int(os.environ.get("OWNER_ID", "8501534985"))
except ValueError:
    print("HATA: OWNER_ID ortam değişkeni geçerli bir tamsayı olmalıdır.", file=sys.stderr)
    sys.exit(1)
_admin_raw = os.environ.get("ADMIN_ID", "").strip()
try:
    ADMIN_ID = int(_admin_raw) if _admin_raw else OWNER_ID
except ValueError:
    print("HATA: ADMIN_ID geçerli bir tamsayı olmalıdır.", file=sys.stderr)
    sys.exit(1)
YOUR_USERNAME = os.environ.get("BOT_PUBLIC_USERNAME", "@RolexsWhat")
UPDATE_CHANNEL = "https://t.me/YokGençler"

                                                        
def get_ban_message(reason="Belirtilmemiş", ban_until_dt=None, banner_name=None):
    if ban_until_dt:
        sure_str = f"⏰ *Ban Bitiş:* {ban_until_dt.strftime('%Y-%m-%d %H:%M')}\n🔴 *Ban Türü:* Süreli"
    else:
        sure_str = "🔴 *Ban Türü:* Sınırsız (Kalıcı)"
    banner_str = f"\n👮 *Banlayan:* {banner_name}" if banner_name else ""
    return (
        "🚫 *YÖNETİCİ TARAFINDAN BANLANDINIZ!*\n\n"
        "━━━━━━━━━━━━━━━━\n"
        f"📝 *Sebep:* _{reason}_\n"
        f"{sure_str}"
        f"{banner_str}\n"
        "━━━━━━━━━━━━━━━━\n\n"
        "Bu bot üzerindeki tüm özellikler kullanıma kapatılmıştır.\n\n"
        f"İtiraz için: {os.environ.get('BOT_PUBLIC_USERNAME', '@RolexsWhat')}"
    )

                                                           
BAN_MESSAGE = (
    "🚫 *BANLANDINIZ!*\n\n"
    "Bot yöneticisi/sahibi tarafından engellendiniz.\n"
    "Bu bot üzerindeki tüm özellikler kullanıma kapatılmıştır.\n\n"
    f"İtiraz için: {os.environ.get('BOT_PUBLIC_USERNAME', '@RolexsWhat')}"
)

                                                                                  
def get_lock_message():
    reason = lock_info.get('reason', 'Bakım çalışması')
    locker = lock_info.get('locker_name', 'Yönetici')
    until = lock_info.get('until')
    if until:
        remaining_secs = max(0, int((until - datetime.now()).total_seconds()))
        remaining_str = f"{remaining_secs//3600}s {(remaining_secs%3600)//60}dk {remaining_secs%60}sn" if remaining_secs > 3600 else f"{remaining_secs//60}dk {remaining_secs%60}sn"
        until_str = f"\n⏰ Açılış: {until.strftime('%Y-%m-%d %H:%M')} (Kalan: {remaining_str})"
        tur_str = "Süreli Kilit"
    else:
        until_str = "\n🔴 Süresiz Kilit"
        tur_str = "Süresiz Kilit"
    return (
        f"🔒 *BOT KİLİTLİ — {tur_str.upper()}*\n\n"
        f"Bu bot şu an yönetici tarafından kilitlenmiştir.\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"📝 *Sebep:* _{reason}_\n"
        f"👤 *Kilitleyen:* {locker}"
        f"{until_str}\n"
        f"━━━━━━━━━━━━━━━━\n\n"
        f"Lütfen daha sonra tekrar deneyin veya yöneticiyle iletişime geçin:\n"
        f"{os.environ.get('BOT_PUBLIC_USERNAME', '@RolexsWhat')}"
    )

                                              
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_BOTS_DIR = os.path.join(BASE_DIR, 'upload_bots')
IROTECH_DIR = os.path.join(BASE_DIR, 'inf')
DATABASE_PATH = os.path.join(IROTECH_DIR, 'bot_data.db')

                    
FREE_USER_LIMIT = 5
SUBSCRIBED_USER_LIMIT = 15
STARS_PREMIUM_LIMIT = 35                                                  
ADMIN_LIMIT = 999
OWNER_LIMIT = float('inf')
STARS_PRICE = 15                                        

                           
os.makedirs(UPLOAD_BOTS_DIR, exist_ok=True)
os.makedirs(IROTECH_DIR, exist_ok=True)

             
bot = telebot.TeleBot(TOKEN)

                                                    
from telebot import BaseMiddleware, CancelUpdate

class ZorunluKanalMiddleware(BaseMiddleware):
    """Her mesaj/callback'ten önce kanal üyeliğini kontrol et."""
    def __init__(self):
        self.update_sensitive = True
        self.update_types = ['message', 'callback_query']

    def pre_process(self, message, data):
                                                
        if hasattr(message, 'from_user') and message.from_user:
            user_id = message.from_user.id
        else:
            return                       

                            
        if user_id in admin_ids or user_id == OWNER_ID:
            return

                                                                         
        if user_id in banned_users:
            return

                                                                              
        if hasattr(message, 'text') and message.text:
            if message.text.strip().startswith('/start'):
                return
        if hasattr(message, 'data') and message.data == 'check_membership':
            return

                        
        if not check_channel_membership(user_id):
            chat_id = message.chat.id if hasattr(message, 'chat') else message.message.chat.id
            send_join_channel_message(chat_id)
            return CancelUpdate()

    def post_process(self, message, data, exception):
        pass

bot.setup_middleware(ZorunluKanalMiddleware())
                            

                       
bot_scripts = {}
user_subscriptions = {}
referral_data = {}                                     
user_files = {}
active_users = set()
admin_ids = {ADMIN_ID, OWNER_ID}
banned_users = set()                   
banned_users_until = {}                                                 
malware_whitelist = set()                                            
stars_premium_users = set()                                                
pending_stars_payments = {}                                                                
bot_locked = False
lock_info = {                             
    'reason': '',
    'locker_id': None,
    'locker_name': 'Yönetici',
    'until': None,                                   
}

KNOWN_COMMANDS = {
    'start', 'help', 'status', 'encode', 'decode', 'encrypt', 'decrypt',
    'shorten', 'myinfo', 'randpass', 'hash_password', 'file_size', 'file_hash',
    'cleanup_files', 'compress_file',
    'updateschannel', 'uploadfile', 'checkfiles', 'botspeed', 'sendcommand',
    'contactowner', 'subscriptions', 'statistics', 'broadcast', 'lockbot',
    'adminpanel', 'runningallcode', 'ping',
    'ai', 'chat', 'ai_reset', 'debugai', 'loganaliz', 'analyzelogs',
    'monitor', 'satin_al', 'premium', 'buy',
    'lang', 'language', 'dil',
    'profil', 'profile', 'kart',
    'webhook', 'webhook_history',
    'schedule', 'zamanla', 'takvim', 'schedule_list', 'schedule_cancel',
    '2fa_enable', 'guvenligi_ac', '2fa_disable', '2fa_verify', 'dogrula',
    '2fa_send', 'kod_gonder', '2fa_unlock', '2fa_status',
    'yenikomutlar', 'newcmds',
    'backup', 'sysinfo', 'userlist', 'ban', 'unban', 'search', 'announce',
    'convert_csv_to_json', 'convert_json_to_csv',
    'support', 'destek', 'msg', 'reply', 'yanit', 'broadcast_msg', 'toplu',
    'referral', 'davet', 'leaderboard', 'siralama',
    'stopuser', 'kullanicidurdur', 'startuser', 'kullanicibaslat',
    'deleteuser', 'kullanicisil', 'userbots', 'kullanicibotlari',
    'tickets', 'talepler', 'botstatus', 'tumdurum',
    'subreduce', 'abonelikkis', 'uptime', 'myid',
    'allsubs', 'tumabonenlik', 'ai_ask', 'ai_code', 'ai_fix', 'ai_daily',
    'adminlist', 'userinfo', 'kickuser', 'lockstatus',
    'ip', 'sunucuip', 'disk', 'diskusage',
}

def _notify_all_users(text: str, exclude_id=None, parse_mode='Markdown'):
    """Tüm aktif kullanıcılara sessizce mesaj gönder."""
    def _send():
        for uid in list(active_users):
            if uid == exclude_id or uid in admin_ids:
                continue
            try:
                bot.send_message(uid, text, parse_mode=parse_mode)
                time.sleep(0.05)
            except Exception:
                pass
    threading.Thread(target=_send, daemon=True).start()

                                                                  
                                                                      

                                              

                                          
class FileManager:
    """Dosya yönetimi, analiz ve temizleme araçları"""
    
    @staticmethod
    def get_file_size(file_path):
        """Dosya boyutunu MB cinsinden döndür"""
        try:
            return os.path.getsize(file_path) / (1024 * 1024)
        except:
            return 0
    
    @staticmethod
    def get_directory_size(directory):
        """Dizin boyutunu MB cinsinden hesapla"""
        total = 0
        try:
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    total += os.path.getsize(filepath)
        except:
            pass
        return total / (1024 * 1024)
    
    @staticmethod
    def get_file_hash(file_path):
        """Dosyasının SHA256 hash'ini hesapla"""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except:
            return None
    
    @staticmethod
    def compress_file(file_path):
        """Dosyayı gzip ile sıkıştır"""
        try:
            compressed_path = file_path + ".gz"
            with open(file_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            return compressed_path
        except:
            return None
    
    @staticmethod
    def cleanup_old_files(directory, days=7):
        """Belirtilen günden eski dosyaları sil"""
        cutoff_time = time.time() - (days * 86400)
        deleted = 0
        try:
            for filename in os.listdir(directory):
                filepath = os.path.join(directory, filename)
                if os.path.isfile(filepath):
                    if os.path.getmtime(filepath) < cutoff_time:
                        os.remove(filepath)
                        deleted += 1
        except:
            pass
        return deleted

                            
class EncryptionTools:
    """Base64 ve hash tabanlı şifreleme/şifre çözme"""
    
    @staticmethod
    def encrypt_text(text):
        """Metni Base64 ile şifrele"""
        try:
            return base64.b64encode(text.encode()).decode()
        except:
            return None
    
    @staticmethod
    def decrypt_text(encrypted_text):
        """Base64 şifreli metni çöz"""
        try:
            return base64.b64decode(encrypted_text.encode()).decode()
        except:
            return None
    
    @staticmethod
    def hash_password(password):
        """Şifreyi hash'le (SHA256)"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def verify_password(password, hash_value):
        """Şifreyi hash'le ve karşılaştır"""
        return hashlib.sha256(password.encode()).hexdigest() == hash_value

                                      
    @staticmethod
    def encode_hex(text):
        try: return text.encode().hex()
        except: return None

    @staticmethod
    def decode_hex(hex_text):
        try: return bytes.fromhex(hex_text).decode()
        except: return None

    @staticmethod
    def encode_url(text):
        try: return urllib.parse.quote(text)
        except: return None

    @staticmethod
    def decode_url(text):
        try: return urllib.parse.unquote(text)
        except: return None

    @staticmethod
    def encode_binary(text):
        try: return ' '.join(format(ord(c), '08b') for c in text)
        except: return None

    @staticmethod
    def decode_binary(binary_text):
        try:
            parts = binary_text.strip().split()
            return ''.join(chr(int(b, 2)) for b in parts)
        except: return None

    @staticmethod
    def encode_rot13(text):
        try:
            result = []
            for c in text:
                if 'a' <= c <= 'z': result.append(chr((ord(c) - ord('a') + 13) % 26 + ord('a')))
                elif 'A' <= c <= 'Z': result.append(chr((ord(c) - ord('A') + 13) % 26 + ord('A')))
                else: result.append(c)
            return ''.join(result)
        except: return None

    @staticmethod
    def encode_morse(text):
        MORSE = {'A':'.-','B':'-...','C':'-.-.','D':'-..','E':'.','F':'..-.','G':'--.','H':'....','I':'..','J':'.---','K':'-.-','L':'.-..','M':'--','N':'-.','O':'---','P':'.--.','Q':'--.-','R':'.-.','S':'...','T':'-','U':'..-','V':'...-','W':'.--','X':'-..-','Y':'-.--','Z':'--..',
                  '0':'-----','1':'.----','2':'..---','3':'...--','4':'....-','5':'.....','6':'-....','7':'--...','8':'---..','9':'----.','.':'.-.-.-',',':'--..--','?':'..--..','!':'-.-.--',' ': '/'}
        try: return ' '.join(MORSE.get(c.upper(), '?') for c in text)
        except: return None

    @staticmethod
    def decode_morse(morse_text):
        MORSE_REV = {v: k for k, v in {'A':'.-','B':'-...','C':'-.-.','D':'-..','E':'.','F':'..-.','G':'--.','H':'....','I':'..','J':'.---','K':'-.-','L':'.-..','M':'--','N':'-.','O':'---','P':'.--.','Q':'--.-','R':'.-.','S':'...','T':'-','U':'..-','V':'...-','W':'.--','X':'-..-','Y':'-.--','Z':'--..',
                  '0':'-----','1':'.----','2':'..---','3':'...--','4':'....-','5':'.....','6':'-....','7':'--...','8':'---..','9':'----.','.':'.-.-.-',',':'--..--','?':'..--..','!':'-.-.--'}.items()}
        MORSE_REV['/'] = ' '
        try: return ''.join(MORSE_REV.get(word, '?') for word in morse_text.strip().split(' '))
        except: return None

    @staticmethod
    def encode_ascii(text):
        try: return ' '.join(str(ord(c)) for c in text)
        except: return None

    @staticmethod
    def decode_ascii(ascii_text):
        try: return ''.join(chr(int(x)) for x in ascii_text.strip().split())
        except: return None

                                   
class ActivityLogger:
    """Tüm kullanıcı aktivitelerini takip et ve analiz et"""
    
    def __init__(self):
        self.activities = defaultdict(list)
        self.activity_db_path = os.path.join(IROTECH_DIR, 'activities.json')
        self._dirty = False
        self._save_lock = threading.Lock()
                                                                       
        t = threading.Thread(target=self._periodic_save, daemon=True)
        t.start()
    
    def log_activity(self, user_id, action, details=""):
        """Aktiviteyi kaydet (dosyaya yazmadan, sadece belleğe)"""
        activity = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'action': action,
            'details': details
        }
        self.activities[user_id].append(activity)
                                                          
        if len(self.activities[user_id]) > 500:
            self.activities[user_id] = self.activities[user_id][-500:]
        self._dirty = True

    def _periodic_save(self):
        """Her 60 saniyede bir, değişiklik varsa dosyaya yaz"""
        while True:
            time.sleep(60)
            if self._dirty:
                self._save_to_file()

    def _save_to_file(self):
        """Aktiviteleri dosyaya kaydet"""
        with self._save_lock:
            try:
                with open(self.activity_db_path, 'w') as f:
                    json.dump(dict(self.activities), f, indent=2)
                self._dirty = False
            except:
                pass
    
    def get_user_activities(self, user_id, limit=10):
        """Kullanıcı aktivitelerini getir"""
        return self.activities.get(user_id, [])[-limit:]
    
    def get_activity_summary(self, user_id):
        """Kullanıcı aktivitelerinin özetini ver"""
        activities = self.activities.get(user_id, [])
        summary = defaultdict(int)
        for activity in activities:
            summary[activity['action']] += 1
        return dict(summary)

                           
class PerformanceTracker:
    """Bot ve sistem performansını takip et"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.command_count = 0
        self.error_count = 0
        self.request_times = []
        self._MAX_SAMPLES = 200                             
    
    def record_request(self, duration):
        """İstek süresini kaydet"""
        self.request_times.append(duration)
                                                       
        if len(self.request_times) > self._MAX_SAMPLES:
            self.request_times = self.request_times[-self._MAX_SAMPLES:]
    
    def get_average_response_time(self):
        """Ortalama yanıt süresini hesapla"""
        if not self.request_times:
            return 0
        return sum(self.request_times) / len(self.request_times)
    
    def get_uptime(self):
        """Bot çalışma süresini hesapla (saat)"""
        return (datetime.now() - self.start_time).total_seconds() / 3600
    
    def get_stats(self):
        """Tüm performans istatistiklerini döndür"""
        return {
            'uptime_hours': round(self.get_uptime(), 2),
            'total_commands': self.command_count,
            'total_errors': self.error_count,
            'avg_response_time': round(self.get_average_response_time(), 3),
            'total_requests': len(self.request_times)
        }

                              
class BatchProcessor:
    """Toplu dosya işleme ve dönüştürme"""
    
    @staticmethod
    def convert_to_json(csv_data):
        """CSV'yi JSON'a dönüştür"""
        try:
            reader = csv.DictReader(io.StringIO(csv_data))
            return json.dumps(list(reader), indent=2, ensure_ascii=False)
        except:
            return None
    
    @staticmethod
    def convert_to_csv(json_data):
        """JSON'u CSV'ye dönüştür"""
        try:
            data = json.loads(json_data)
            if not data:
                return None
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
            return output.getvalue()
        except:
            return None

                       
class RateLimiter:
    """Spam koruması için rate limiting"""
    
    def __init__(self, max_requests=10, time_window=60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.user_requests = defaultdict(list)
    
    def is_allowed(self, user_id):
        """Kullanıcının istek yapmasına izin ver"""
        now = time.time()
                                
        self.user_requests[user_id] = [
            t for t in self.user_requests[user_id] 
            if now - t < self.time_window
        ]
        
        if len(self.user_requests[user_id]) < self.max_requests:
            self.user_requests[user_id].append(now)
            return True
        return False
    
    def get_remaining_requests(self, user_id):
        """Kalan istekleri döndür"""
        now = time.time()
        self.user_requests[user_id] = [
            t for t in self.user_requests[user_id] 
            if now - t < self.time_window
        ]
        return self.max_requests - len(self.user_requests[user_id])

                          
class ReportGenerator:
    """Otomatik raporlama sistemi"""
    
    @staticmethod
    def generate_bot_report(perf_tracker):
        """Bot durum raporunu oluştur"""
        stats = perf_tracker.get_stats()
        report = f"""
📊 BOT DURUM RAPORU
==================
⏱️ Çalışma Süresi: {stats['uptime_hours']} saat
📈 Toplam Komut: {stats['total_commands']}
❌ Toplam Hata: {stats['total_errors']}
⚡ Ort. Yanıt Süresi: {stats['avg_response_time']}ms
🔄 Toplam İstek: {stats['total_requests']}
        """
        return report
    
    @staticmethod
    def generate_user_report(user_id, activity_logger, file_manager):
        """Kullanıcı raporu oluştur"""
        _user_files_list = user_files.get(user_id, [])
        total_files = len(_user_files_list)
        activities = activity_logger.get_activity_summary(user_id)
        
        report = f"""
👤 KULLANICI RAPORU: {user_id}
========================
📁 Toplam Dosya: {total_files}
📊 Aktivite Özeti:
"""
        for action, count in activities.items():
            report += f"  • {action}: {count}\n"
        
        return report

                                          
file_manager = FileManager()
encryption_tools = EncryptionTools()
activity_logger = ActivityLogger()
performance_tracker = PerformanceTracker()
batch_processor = BatchProcessor()
rate_limiter = RateLimiter(max_requests=20, time_window=60)
report_generator = ReportGenerator()

                               
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

                                                       
COMMAND_BUTTONS_LAYOUT_USER_SPEC = [
    ["𝐆𝐔𝐍𝐂𝐄𝐋𝐋𝐄𝐌𝐄 𝐊𝐀𝐍𝐀𝐋𝐈"],
    ["📤 Dosya Yükle", "📂 Dosyalarım"],
    ["⚡ Bot Hızı", "📊 İstatistikler"],
    ["🌍 Dil Seç", "🔔 Webhook"],
    ["⏱️ Uptime", "🤖 Bot Durumları"],
    ["📤 Komut Gönder", "📞 Sahiple İletişim"]
]
ADMIN_COMMAND_BUTTONS_LAYOUT_USER_SPEC = [
    ["𝐆𝐔𝐍𝐂𝐄𝐋𝐋𝐄𝐌𝐄 𝐊𝐀𝐍𝐀𝐋𝐈"],
    ["📤 Dosya Yükle", "📂 Dosyalarım"],
    ["⚡ Bot Hızı", "📊 İstatistikler"],
    ["🌍 Dil Seç", "🔔 Webhook"],
    ["⏱️ Uptime", "🤖 Bot Durumları"],
    ["💳 Abonelikler", "📢 Duyuru"],
    ["📢 Resmi Duyuru"],
    ["🔒 Botu Kilitle", "🟢 Tüm Kodları Çalıştır"],
    ["🖥️ Sistem Bilgisi", "👥 Kullanıcı Listesi"],
    ["💾 Yedek Al", "🚫 Kullanıcı Banla", "🔓 Ban Kaldır"],
    ["📤 Komut Gönder", "👑 Yönetici Paneli"],
    ["📞 Sahiple İletişim"]
]


def format_remaining_time(expiry_dt):
    """Kalan süreyi okunabilir formatta döndür"""
    try:
        remaining = expiry_dt - datetime.now()
        if remaining.total_seconds() <= 0:
            return "Süre doldu"
        days = remaining.days
        hours, rem = divmod(remaining.seconds, 3600)
        minutes = rem // 60
        if days > 0:
            return f"{days}g {hours}s"
        elif hours > 0:
            return f"{hours}s {minutes}dk"
        else:
            return f"{minutes}dk"
    except Exception:
        return "?"

def reduce_subscription_db(user_id: int, days: int):
    """Kullanıcının aboneliğini belirtilen gün kadar azalt"""
    try:
        sub = user_subscriptions.get(user_id)
        if not sub:
            return False, "Bu kullanıcının aktif aboneliği yok."
        current_expiry = sub.get('expiry')
        if not current_expiry or current_expiry <= datetime.now():
            remove_subscription_db(user_id)
            return True, "removed"
        new_expiry = current_expiry - timedelta(days=days)
        if new_expiry <= datetime.now():
            remove_subscription_db(user_id)
            return True, "removed"
        save_subscription(user_id, new_expiry)
        return True, new_expiry
    except Exception as e:
        logger.error(f"reduce_subscription_db hatası: {e}")
        return False, str(e)


                        
def init_db():
    """Initialize the database with required tables"""
    logger.info(f"Veritabanı başlatılıyor: {DATABASE_PATH}")
    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS subscriptions
                     (user_id INTEGER PRIMARY KEY, expiry TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS user_files
                     (user_id INTEGER, file_name TEXT, file_type TEXT,
                      PRIMARY KEY (user_id, file_name))''')
        c.execute('''CREATE TABLE IF NOT EXISTS active_users
                     (user_id INTEGER PRIMARY KEY)''')
        c.execute('''CREATE TABLE IF NOT EXISTS admins
                     (user_id INTEGER PRIMARY KEY)''')
        c.execute('''CREATE TABLE IF NOT EXISTS banned_users
                     (user_id INTEGER PRIMARY KEY, ban_reason TEXT, ban_until TEXT)''')
                                                      
        existing_cols = [row[1] for row in c.execute('PRAGMA table_info(banned_users)').fetchall()]
        if 'ban_reason' not in existing_cols:
            try:
                c.execute('ALTER TABLE banned_users ADD COLUMN ban_reason TEXT')
            except Exception:
                pass
        if 'ban_until' not in existing_cols:
            try:
                c.execute('ALTER TABLE banned_users ADD COLUMN ban_until TEXT')
            except Exception:
                pass
        c.execute('''CREATE TABLE IF NOT EXISTS malware_whitelist
                     (user_id INTEGER PRIMARY KEY, added_by INTEGER, added_at TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS referrals
                     (referrer_id INTEGER, referred_id INTEGER,
                      bonus_days INTEGER DEFAULT 3, created_at TEXT,
                      PRIMARY KEY (referrer_id, referred_id))''')
        c.execute('''CREATE TABLE IF NOT EXISTS stars_premium
                     (user_id INTEGER PRIMARY KEY, bought_at TEXT, stars_paid INTEGER)''')
        c.execute('INSERT OR IGNORE INTO admins (user_id) VALUES (?)', (OWNER_ID,))
        if ADMIN_ID != OWNER_ID:
            c.execute('INSERT OR IGNORE INTO admins (user_id) VALUES (?)', (ADMIN_ID,))
        conn.commit()
        conn.close()
        logger.info("Veritabanı başarıyla başlatıldı (BAN tablosu dahil).")
    except Exception as e:
        logger.error(f"❌ Veritabanı başlatma hatası: {e}", exc_info=True)

def load_data():
    """Load data from database into memory"""
    logger.info("Veritabanından veriler yükleniyor...")
    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()

                            
        c.execute('SELECT user_id, expiry FROM subscriptions')
        for user_id, expiry in c.fetchall():
            try:
                user_subscriptions[user_id] = {'expiry': datetime.fromisoformat(expiry)}
            except ValueError:
                logger.warning(f"⚠️ Kullanıcı {user_id} için geçersiz bitiş tarihi formatı: {expiry}. Atlanıyor.")

                         
        c.execute('SELECT user_id, file_name, file_type FROM user_files')
        for user_id, file_name, file_type in c.fetchall():
            if user_id not in user_files:
                user_files[user_id] = []
            user_files[user_id].append((file_name, file_type))

                           
        c.execute('SELECT user_id FROM active_users')
        active_users.update(user_id for (user_id,) in c.fetchall())

                     
        c.execute('SELECT user_id FROM admins')
        admin_ids.update(user_id for (user_id,) in c.fetchall())
        
                                                     
        c.execute('SELECT user_id, ban_until FROM banned_users')
        for row in c.fetchall():
            uid = row[0]
            ban_until_str = row[1] if len(row) > 1 else None
            if ban_until_str:
                try:
                    ban_until_dt = datetime.fromisoformat(ban_until_str)
                    if datetime.now() >= ban_until_dt:
                                                   
                        try:
                            conn.execute('DELETE FROM banned_users WHERE user_id=?', (uid,))
                        except Exception:
                            pass
                        continue
                    banned_users_until[uid] = ban_until_dt
                except Exception:
                    pass
            banned_users.add(uid)

                                 
        c.execute('SELECT user_id FROM malware_whitelist')
        malware_whitelist.update(row[0] for row in c.fetchall())

                                             
        c.execute('SELECT user_id FROM stars_premium')
        stars_premium_users.update(row[0] for row in c.fetchall())

                                   
        c.execute('SELECT referrer_id, referred_id, bonus_days FROM referrals')
        for referrer_id, referred_id, bonus_days in c.fetchall():
            if referrer_id not in referral_data:
                referral_data[referrer_id] = {'referrals': [], 'bonus_days': 0}
            if referred_id not in referral_data[referrer_id]['referrals']:
                referral_data[referrer_id]['referrals'].append(referred_id)
                referral_data[referrer_id]['bonus_days'] += bonus_days

        conn.close()
        logger.info(f"Veriler yüklendi: {len(active_users)} kullanıcı, {len(user_subscriptions)} abonelik, {len(admin_ids)} yönetici, {len(banned_users)} banlı, {len(malware_whitelist)} whitelist.")
    except Exception as e:
        logger.error(f"❌ Veri yükleme hatası: {e}", exc_info=True)

                                        
init_db()
load_data()

def save_referral_db(referrer_id: int, referred_id: int, bonus_days: int = 3):
    """Referral kaydını veritabanına kaydet"""
    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        conn.execute(
            'INSERT OR IGNORE INTO referrals (referrer_id, referred_id, bonus_days, created_at) VALUES (?, ?, ?, ?)',
            (referrer_id, referred_id, bonus_days, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Referral DB kayıt hatası: {e}")
                            

                                                              
                         
                                                              
REQUIRED_CHANNELS = []
                        
REQUIRED_CHANNEL = None
REQUIRED_CHANNEL_URL = None

def check_channel_membership(user_id: int) -> bool:
    """Kullanıcının tüm zorunlu kanallara üye olup olmadığını kontrol et. Admin/sahip muaf."""
    if not REQUIRED_CHANNELS:
        return True                                       
    if user_id in admin_ids or user_id == OWNER_ID:
        return True
    for ch in REQUIRED_CHANNELS:
        try:
            member = bot.get_chat_member(ch["id"], user_id)
            if member.status not in ('member', 'administrator', 'creator'):
                return False
        except Exception as e:
            logger.warning(f"Kanal üyelik kontrolü başarısız [{ch['name']}] user={user_id}: {e}")
            return False                                            
    return True

def send_join_channel_message(chat_id: int):
    """Kanallara katılmayı isteyen mesaj gönder."""
    markup = types.InlineKeyboardMarkup(row_width=1)
    for ch in REQUIRED_CHANNELS:
        markup.add(types.InlineKeyboardButton(f"• {ch['name']}", url=ch["url"]))
    markup.add(types.InlineKeyboardButton("✅  Katıldım", callback_data="check_membership"))
    channel_list = "\n".join(f"› {ch['name']}" for ch in REQUIRED_CHANNELS)
    bot.send_message(
        chat_id,
        f"⛔️ *Devam etmek için kanallara katıl:*\n\n{channel_list}",
        parse_mode='Markdown',
        reply_markup=markup
    )

                                                              
                                        
                                                              
                                                               
user_support_mode = {}                          
                                                              
admin_reply_to = {}                           

def get_support_panel_markup():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✉️ Destek Talebi Oluştur", callback_data="support_new"))
    markup.add(types.InlineKeyboardButton("📋 Taleplerim", callback_data="support_list"))
    markup.add(types.InlineKeyboardButton("🔙 Ana Menü", callback_data="back_to_main"))
    return markup

support_tickets = {}                                                      
ticket_counter = [1]

@bot.message_handler(commands=['stopuser', 'kullanicidurdur'])
def cmd_stop_user_bots(message):
    """Belirli bir kullanıcının tüm botlarını durdur — sadece sahip"""
    user_id = message.from_user.id
    if user_id != OWNER_ID:
        bot.reply_to(message, "⚠️ Sadece sahip bu komutu kullanabilir!")
        return
    try:
        target_id = int(message.text.split(' ', 1)[1])
    except (IndexError, ValueError):
        bot.reply_to(message, "📌 Kullanım: `/stopuser <user_id>`", parse_mode='Markdown')
        return
    stopped = 0
    for sk in list(bot_scripts.keys()):
        si = bot_scripts[sk]
        if si['script_owner_id'] == target_id and is_bot_running(target_id, si['file_name']):
            kill_process_tree(si)
            del bot_scripts[sk]
            stopped += 1
    bot.reply_to(message,
        f"🛑 *Kullanıcı Botları Durduruldu*\n\n"
        f"🆔 Kullanıcı: `{target_id}`\n"
        f"🛑 Durdurulan bot: `{stopped}`",
        parse_mode='Markdown')
    try:
        bot.send_message(target_id,
            "⚠️ *Bildirim*\n\nBotlarınız yönetici tarafından durduruldu.\n"
            "Detay için /support yazın.", parse_mode='Markdown')
    except Exception: pass

@bot.message_handler(commands=['startuser', 'kullanicibaslat'])
def cmd_start_user_bots(message):
    """Belirli bir kullanıcının tüm botlarını başlat — sadece sahip"""
    user_id = message.from_user.id
    if user_id != OWNER_ID:
        bot.reply_to(message, "⚠️ Sadece sahip bu komutu kullanabilir!")
        return
    try:
        target_id = int(message.text.split(' ', 1)[1])
    except (IndexError, ValueError):
        bot.reply_to(message, "📌 Kullanım: `/startuser <user_id>`", parse_mode='Markdown')
        return
    files = user_files.get(target_id, [])
    if not files:
        bot.reply_to(message, f"⚠️ `{target_id}` kullanıcısının hiç dosyası yok.", parse_mode='Markdown')
        return
    started = 0
    user_folder = get_user_folder(target_id)
    for fn, ft in files:
        fp = os.path.join(user_folder, fn)
        if os.path.exists(fp) and not is_bot_running(target_id, fn):
            try:
                if ft == 'py':
                    threading.Thread(target=run_script, args=(fp, target_id, user_folder, fn, message)).start()
                elif ft == 'js':
                    threading.Thread(target=run_js_script, args=(fp, target_id, user_folder, fn, message)).start()
                started += 1
                time.sleep(0.5)
            except Exception as e:
                logger.error(f"startuser: {fn} başlatılamadı: {e}")
    bot.reply_to(message,
        f"▶️ *Kullanıcı Botları Başlatıldı*\n\n"
        f"🆔 Kullanıcı: `{target_id}`\n"
        f"▶️ Başlatılan: `{started}` bot",
        parse_mode='Markdown')
    try:
        bot.send_message(target_id,
            f"✅ *Bildirim*\n\nBotlarınız (`{started}` adet) yönetici tarafından başlatıldı!",
            parse_mode='Markdown')
    except Exception: pass

@bot.message_handler(commands=['deleteuser', 'kullanicisil'])
def cmd_delete_user_bots(message):
    """Belirli bir kullanıcının seçili botunu sil — sadece sahip. /deleteuser <user_id> <file_name>"""
    user_id = message.from_user.id
    if user_id != OWNER_ID:
        bot.reply_to(message, "⚠️ Sadece sahip bu komutu kullanabilir!")
        return
    try:
        parts = message.text.split(' ', 2)
        target_id = int(parts[1])
        file_name = os.path.basename(parts[2])
    except (IndexError, ValueError):
        bot.reply_to(message, "📌 Kullanım: `/deleteuser <user_id> <dosya_adi>`", parse_mode='Markdown')
        return
                   
    sk = f"{target_id}_{file_name}"
    if sk in bot_scripts:
        kill_process_tree(bot_scripts[sk])
        del bot_scripts[sk]
    user_folder = get_user_folder(target_id)
    fp = os.path.join(user_folder, file_name)
    deleted = False
    if os.path.exists(fp):
        try: os.remove(fp); deleted = True
        except Exception as e: logger.error(f"deleteuser dosya sil hatası: {e}")
    remove_user_file_db(target_id, file_name)
    bot.reply_to(message,
        f"🗑️ *Dosya Silindi*\n\n"
        f"🆔 Kullanıcı: `{target_id}`\n"
        f"📄 Dosya: `{file_name}`\n"
        f"💾 Diskten: {'✅ Silindi' if deleted else '⚠️ Bulunamadı'}",
        parse_mode='Markdown')
    try:
        bot.send_message(target_id,
            f"🗑️ *Bildirim*\n\n`{file_name}` dosyanız yönetici tarafından silindi.",
            parse_mode='Markdown')
    except Exception: pass

@bot.message_handler(commands=['userbots', 'kullanicibotlari'])
def cmd_user_bots_list(message):
    """Belirli bir kullanıcının botlarını listele ve yönet — sadece sahip"""
    user_id = message.from_user.id
    if user_id != OWNER_ID:
        bot.reply_to(message, "⚠️ Sadece sahip bu komutu kullanabilir!")
        return
    try:
        target_id = int(message.text.split(' ', 1)[1])
    except (IndexError, ValueError):
        bot.reply_to(message, "📌 Kullanım: `/userbots <user_id>`", parse_mode='Markdown')
        return
    files = user_files.get(target_id, [])
    if not files:
        bot.reply_to(message, f"⚠️ `{target_id}` kullanıcısının hiç dosyası yok.", parse_mode='Markdown')
        return
    markup = types.InlineKeyboardMarkup()
    for fn, ft in files:
        running = is_bot_running(target_id, fn)
        icon = "🟢" if running else "🔴"
        markup.add(types.InlineKeyboardButton(f"{icon} {fn} ({ft})", callback_data=f"file_{target_id}_{fn}"))
    markup.add(
        types.InlineKeyboardButton(f"🛑 Tüm Botları Durdur", callback_data=f"owner_stopall_{target_id}"),
        types.InlineKeyboardButton(f"▶️ Tüm Botları Başlat", callback_data=f"owner_startall_{target_id}")
    )
    bot.reply_to(message,
        f"🤖 *Kullanıcı `{target_id}` Botları*\n"
        f"Toplam: {len(files)} dosya",
        reply_markup=markup, parse_mode='Markdown')

@bot.message_handler(commands=['botstatus', 'tümdurum'])
def cmd_all_bot_status(message):
    """Tüm kullanıcıların bot durumu — sadece sahip"""
    user_id = message.from_user.id
    if user_id != OWNER_ID:
        bot.reply_to(message, "⚠️ Sadece sahip bu komutu kullanabilir!")
        return
    lines = ["🤖 *TÜM BOT DURUMLARI*\n━━━━━━━━━━━━━━━━"]
    total_running = 0
    total_stopped = 0
    for uid, files in user_files.items():
        running_files = [fn for fn, ft in files if is_bot_running(uid, fn)]
        stopped_files = [fn for fn, ft in files if not is_bot_running(uid, fn)]
        total_running += len(running_files)
        total_stopped += len(stopped_files)
        if files:
            sub_info = "⭐" if (uid in user_subscriptions and user_subscriptions[uid].get('expiry', datetime.min) > datetime.now()) else "🆓"
            lines.append(f"\n👤 `{uid}` {sub_info}\n   🟢 {len(running_files)} çalışıyor | 🔴 {len(stopped_files)} durdu")
    lines.append(f"\n━━━━━━━━━━━━━━━━\n📊 Özet: {total_running} çalışıyor, {total_stopped} durdurulmuş")
                 
    full_text = '\n'.join(lines)
    if len(full_text) > 4000:
        full_text = full_text[:4000] + "\n...(kısaltıldı)"
    bot.reply_to(message, full_text, parse_mode='Markdown')

@bot.message_handler(commands=['subreduce', 'abonelikkis'])
def cmd_reduce_subscription(message):
    """Abonelik azalt: /subreduce <user_id> <gün> — sadece admin"""
    user_id = message.from_user.id
    if user_id not in admin_ids:
        bot.reply_to(message, "⚠️ Yönetici yetkisi gerekli.")
        return
    try:
        parts = message.text.split()
        target_id = int(parts[1])
        days = int(parts[2])
        if days <= 0: raise ValueError
    except (IndexError, ValueError):
        bot.reply_to(message, "📌 Kullanım: `/subreduce <user_id> <gün>`\nÖrnek: `/subreduce 12345678 7`", parse_mode='Markdown')
        return
    ok, result = reduce_subscription_db(target_id, days)
    if not ok:
        bot.reply_to(message, f"⚠️ {result}")
        return
    if result == "removed":
        bot.reply_to(message, f"✅ `{target_id}` kullanıcısının aboneliği {days} gün azaltıldı ve sıfırlandı (süre doldu), abonelik kaldırıldı.", parse_mode='Markdown')
        try: bot.send_message(target_id, "ℹ️ Aboneliğiniz yönetici tarafından kısaltıldı ve süresi doldu. Artık ücretsiz kullanıcısınız.")
        except Exception: pass
    else:
        bot.reply_to(message, f"✅ `{target_id}` kullanıcısının aboneliği `{days}` gün azaltıldı.\nYeni bitiş: `{result.strftime('%Y-%m-%d')}`", parse_mode='Markdown')
        try: bot.send_message(target_id, f"ℹ️ Aboneliğiniz {days} gün kısaltıldı. Yeni bitiş: {result.strftime('%Y-%m-%d')}")
        except Exception: pass

                                                              
                          
                                                              

@bot.message_handler(commands=['uptime'])
def cmd_uptime(message):
    """Bot uptime bilgisi"""
    user_id = message.from_user.id
    if not check_channel_membership(user_id):
        send_join_channel_message(message.chat.id)
        return
    elapsed = datetime.now() - performance_tracker.start_time
    days = elapsed.days
    hours, remainder = divmod(elapsed.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    total_cmds = performance_tracker.command_count
    total_errors = performance_tracker.error_count
    avg_time = performance_tracker.get_average_response_time()
    bot.reply_to(message,
        f"⏱️ *BOT UPTIME BİLGİSİ*\n\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"🕐 Çalışma süresi: `{days}g {hours}s {minutes}dk {seconds}sn`\n"
        f"📊 Toplam komut: `{total_cmds}`\n"
        f"❌ Toplam hata: `{total_errors}`\n"
        f"⚡ Ort. yanıt süresi: `{avg_time:.0f}ms`\n"
        f"👥 Aktif kullanıcı: `{len(active_users)}`\n"
        f"🟢 Çalışan bot: `{len(bot_scripts)}`\n"
        f"━━━━━━━━━━━━━━━━",
        parse_mode='Markdown')

@bot.message_handler(commands=['myid'])
def cmd_myid(message):
    """Kullanıcı kendi bilgilerini görsün"""
    user_id = message.from_user.id
    uname = message.from_user.first_name
    username = message.from_user.username or 'yok'
    sub = user_subscriptions.get(user_id)
    if sub and sub.get('expiry', datetime.min) > datetime.now():
        expiry_dt = sub['expiry']
        remaining_str = format_remaining_time(expiry_dt)
        sub_str = f"⭐ Premium — {remaining_str} kaldı\n📅 Bitiş: `{expiry_dt.strftime('%Y-%m-%d %H:%M')}`"
    else:
        sub_str = "🆓 Ücretsiz"
    file_count = get_user_file_count(user_id)
    file_limit = get_user_file_limit(user_id)
    limit_str = str(file_limit) if file_limit != float('inf') else "∞"
    running = sum(1 for fn, ft in user_files.get(user_id, []) if is_bot_running(user_id, fn))
    bot.reply_to(message,
        f"🪪 *PROFİLİNİZ*\n\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"👤 İsim: *{uname}*\n"
        f"✳️ @{username}\n"
        f"🆔 ID: `{user_id}`\n"
        f"💳 Abonelik: {sub_str}\n"
        f"📁 Dosya: `{file_count}/{limit_str}`\n"
        f"🟢 Çalışan: `{running}` bot\n"
        f"━━━━━━━━━━━━━━━━",
        parse_mode='Markdown')

@bot.message_handler(commands=['allsubs', 'tümabonenlik'])
def cmd_all_subs(message):
    """Tüm aktif abonelikleri listele — sadece admin"""
    user_id = message.from_user.id
    if user_id not in admin_ids:
        bot.reply_to(message, "⚠️ Yönetici yetkisi gerekli.")
        return
    now = datetime.now()
    active_subs = [(uid, data) for uid, data in user_subscriptions.items()
                   if data.get('expiry', datetime.min) > now]
    active_subs.sort(key=lambda x: x[1]['expiry'])
    if not active_subs:
        bot.reply_to(message, "ℹ️ Aktif abonelik bulunmuyor.")
        return
    lines = [f"💳 *AKTİF ABONELİKLER* ({len(active_subs)} adet)\n━━━━━━━━━━━━━━━━"]
    for uid, data in active_subs:
        exp = data['expiry']
        days_left = (exp - now).days
        remaining_str = format_remaining_time(exp)
        lines.append(f"🆔 `{uid}` — {exp.strftime('%Y-%m-%d %H:%M')} ({remaining_str} kaldı)")
    lines.append("━━━━━━━━━━━━━━━━")
    full = '\n'.join(lines)
    if len(full) > 4000: full = full[:4000] + "\n...(kısaltıldı)"
    bot.reply_to(message, full, parse_mode='Markdown')

                                     
                                                              
                                        
             
                                             
                               
                                                   
                                                 
                                                  
                                                        
                                                              

import math
import re as _re

                                                            
BINARY_MAGIC_SIGNATURES = [
    (b'MZ',               'Windows PE Executable (.exe/.dll)'),
    (b'\x7fELF',          'Linux ELF Executable'),
    (b'\xfe\xed\xfa\xce', 'macOS Mach-O 32-bit'),
    (b'\xfe\xed\xfa\xcf', 'macOS Mach-O 64-bit'),
    (b'\xce\xfa\xed\xfe', 'macOS Mach-O (reversed)'),
    (b'\xcf\xfa\xed\xfe', 'macOS Mach-O 64-bit (reversed)'),
    (b'#!',               None),                                    
    (b'Rar!\x1a\x07',     'RAR Archive'),
    (b'\x1f\x8b',         None),                                                 
    (b'7z\xbc\xaf\x27',   '7-Zip Archive'),
    (b'\xd0\xcf\x11\xe0', 'Microsoft Office (OLE) — makro riski'),
    (b'\x4d\x5a\x90\x00', 'Windows PE (MZ variant)'),
    (b'CAFEBABE',         'Java Class File / JAR'),
]

                                         
BLOCKED_EXTENSIONS = {
    '.exe', '.dll', '.bat', '.cmd', '.scr', '.com', '.pif',
    '.application', '.gadget', '.msi', '.msp', '.hta', '.cpl',
    '.msc', '.jar', '.bin', '.deb', '.rpm', '.apk', '.app',
    '.dmg', '.iso', '.img', '.vbs', '.vbe', '.jse', '.wsf',
    '.wsh', '.ps1', '.ps2', '.reg', '.lnk', '.url', '.inf',
    '.sys', '.drv', '.ocx', '.ax', '.so', '.dylib',
    '.elf', '.out', '.run', '.sh',                     
}

                                                   
                                                            
PYTHON_RISK_PATTERNS = [
                                     
                                      
    (r'os\.system\s*\(',              90, 'os.system() çağrısı'),
    (r'subprocess\.(call|run|Popen)\s*\(', 85, 'subprocess çalıştırma'),
    (r'__import__\s*\(',              80, '__import__ dinamik yükleme'),
    (r'exec\s*\(',                    75, 'exec() çağrısı'),
    (r'eval\s*\(',                    70, 'eval() çağrısı'),
    (r'compile\s*\(',                 65, 'compile() çağrısı'),
                
    (r'socket\.connect\s*\(',         60, 'socket.connect — reverse shell riski'),
    (r'requests\.(get|post)\s*\(',    20, 'HTTP isteği'),
    (r'urllib.*urlopen\s*\(',         25, 'urllib.urlopen'),
                 
    (r'base64\.b64decode\s*\(',       55, 'base64 decode — obfuscation riski'),
    (r'bytes\.fromhex\s*\(',          50, 'hex decode — obfuscation riski'),
    (r'chr\(\d+\)',                   40, 'chr() obfuscation'),
    (r'\\x[0-9a-f]{2}' * 6,          60, 'uzun hex escape dizisi — obfuscation'),
                               
    (r'shutil\.rmtree\s*\(',          70, 'shutil.rmtree — toplu silme'),
    (r'os\.remove\s*\(',              20, 'os.remove'),
    (r'open\s*\(.*["\']w["\']',       15, 'dosyaya yazma'),
                          
    (r'os\.setuid\s*\(',              95, 'os.setuid — root escalation'),
    (r'ctypes\.cdll',                 80, 'ctypes native lib yükleme'),
                            
    (r'(?i)(token|api_key|password|secret)\s*=\s*["\'][^"\']{8,}', 30, 'hardcoded credential'),
                              
    (r'bash\s+-i\s+>&',               99, 'bash reverse shell'),
    (r'nc\s+.*-e\s+/bin',             99, 'netcat reverse shell'),
    (r'/bin/sh',                      60, '/bin/sh referansı'),
    (r'0\.0\.0\.0:\d{4,5}',          50, 'bind shell port dinleme'),
]

                                                       
JS_RISK_PATTERNS = [
    (r'child_process',                85, 'child_process — komut çalıştırma'),
    (r'require\s*\(\s*["\']child_process', 90, 'child_process require'),
    (r'exec\s*\(',                    70, 'exec() çağrısı'),
    (r'eval\s*\(',                    65, 'eval() çağrısı'),
    (r'Function\s*\(',                55, 'Function constructor — eval benzeri'),
    (r'fs\.unlink\s*\(',              60, 'fs.unlink — dosya silme'),
    (r'fs\.rmdir\s*\(',               65, 'fs.rmdir — dizin silme'),
    (r'process\.env',                 30, 'process.env — env erişimi'),
    (r'Buffer\.from\s*\(.*base64',    50, 'base64 decode'),
    (r'atob\s*\(',                    45, 'atob — base64 decode'),
    (r'net\.createServer\s*\(',       70, 'net.createServer — bind shell riski'),
    (r'require\s*\(\s*["\']net["\']', 40, 'net modülü'),
    (r'\.on\s*\(\s*["\']data["\']',   20, 'data event — pipe/shell riski'),
    (r'crypto\.createDecipheriv',     35, 'şifreli payload çözme'),
]

                                                         
SUSPICIOUS_NETWORK_PATTERNS = [
    r'(?i)(cobaltstrike|metasploit|empire|meterpreter)',
    r'\b(\d{1,3}\.){3}\d{1,3}:\d{4,5}\b',           
    r'(?i)(ngrok|serveo|localhost\.run)',                       
    r'(?i)(/etc/passwd|/etc/shadow)',                                
    r'(?i)(cmd\.exe|powershell\.exe)',
]

                                   
def _calculate_entropy(data: bytes) -> float:
    """Shannon entropy hesapla. Yüksek değer (>7.2) = şüpheli."""
    if not data:
        return 0.0
    freq = [0] * 256
    for byte in data:
        freq[byte] += 1
    length = len(data)
    entropy = 0.0
    for count in freq:
        if count > 0:
            p = count / length
            entropy -= p * math.log2(p)
    return entropy

                                      
def _detect_magic_bytes(content: bytes):
    """Dosya başına ve içindeki magic byte imzalarını tara."""
    for magic, desc in BINARY_MAGIC_SIGNATURES:
        if desc is None:
            continue                                 
        if content.startswith(magic):
            return True, f"Çalıştırılabilir/zararlı dosya imzası: {desc}"
                                                               
        idx = content.find(magic, 512)                              
        if idx != -1:
            return True, f"Gizli çalıştırılabilir imzası iç offset {idx}'de: {desc}"
    return False, ""

                                            
def _check_double_extension(file_name: str):
    """dosya.py.exe, bot.js.bat gibi gizleme tespiti."""
    name_lower = file_name.lower()
                       
    parts = name_lower.split('.')
    if len(parts) >= 3:
                              
        last_ext = '.' + parts[-1]
        second_ext = '.' + parts[-2]
        if last_ext in BLOCKED_EXTENSIONS:
            return True, f"Double extension saldırısı: {file_name} (son uzantı: {last_ext})"
        if second_ext in BLOCKED_EXTENSIONS and last_ext in ('.py', '.js', '.txt', '.log'):
            return True, f"Gizli tehlikeli uzantı: {file_name}"
    return False, ""

                                      
def _analyze_python_source(source: str, file_name: str):
    """Python kaynak kodunu risk puanlama ile analiz et."""
    total_score = 0
    findings = []

    for pattern, score, desc in PYTHON_RISK_PATTERNS:
        matches = _re.findall(pattern, source)
        if matches:
                                                                    
            total_score += score
            findings.append(f"{desc} (puan: +{score})")

                                                            
    lines = source.split('\n')
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if len(stripped) > 500 and not stripped.startswith('#'):
            total_score += 50
            findings.append(f"Satır {i}: Aşırı uzun satır ({len(stripped)} karakter) — obfuscation riski (+50)")
            break

                                                
    if _re.search(r'base64\.b64decode', source) and _re.search(r'exec\s*\(', source):
        total_score += 40
        findings.append("base64.decode + exec() kombinasyonu — gizli payload riski (+40)")

                                            
    chr_count = len(_re.findall(r'chr\(\d+\)', source))
    if chr_count > 10:
        total_score += min(chr_count * 3, 80)
        findings.append(f"{chr_count} adet chr() çağrısı — obfuscation (+{min(chr_count*3,80)})")

    threshold = 500                                                                   
    if total_score >= threshold:
        return True, f"Python kaynak kod analizi — Risk puanı: {total_score}/100+. Bulgular: {'; '.join(findings[:5])}"
    return False, f"Python analizi temiz (puan: {total_score})"

                                          
def _analyze_js_source(source: str, file_name: str):
    """JavaScript kaynak kodunu analiz et."""
    total_score = 0
    findings = []

    for pattern, score, desc in JS_RISK_PATTERNS:
        if _re.search(pattern, source):
            total_score += score
            findings.append(f"{desc} (+{score})")

                    
    for i, line in enumerate(source.split('\n'), 1):
        if len(line.strip()) > 500 and not line.strip().startswith('//'):
            total_score += 50
            findings.append(f"Satır {i}: Uzun satır ({len(line.strip())} karakter) (+50)")
            break

                                     
    if _re.search(r'eval\s*\(', source) and _re.search(r'(atob|Buffer\.from)', source):
        total_score += 35
        findings.append("eval() + decode kombinasyonu (+35)")

    threshold = 500
    if total_score >= threshold:
        return True, f"JS kaynak kod analizi — Risk puanı: {total_score}. Bulgular: {'; '.join(findings[:5])}"
    return False, f"JS analizi temiz (puan: {total_score})"

                                    
def _check_network_patterns(text: str):
    for pattern in SUSPICIOUS_NETWORK_PATTERNS:
        match = _re.search(pattern, text)
        if match:
            return True, f"Şüpheli ağ/komut kalıbı: '{match.group()[:60]}'"
    return False, ""

                               
def get_file_type(file_content):
    """Dosya türünü magic byte'a göre belirle."""
    for magic, desc in BINARY_MAGIC_SIGNATURES:
        if file_content.startswith(magic):
            return desc or 'unknown-binary'
    return 'text/unknown'

def is_suspicious_file(file_content: bytes, file_name: str):
    """
    Çok katmanlı dosya güvenlik taraması.
    Returns (is_suspicious: bool, reason: str)
    """
    file_name_clean = os.path.basename(file_name)
    file_lower = file_name_clean.lower()
    ext = os.path.splitext(file_lower)[1]

                                                                 
    if ext in BLOCKED_EXTENSIONS:
        return True, f"Yasaklı dosya uzantısı: '{ext}' ({file_name_clean})"

                                                                 
    flag, reason = _check_double_extension(file_name_clean)
    if flag:
        return True, reason

                                                                 
    flag, reason = _detect_magic_bytes(file_content)
    if flag:
        return True, reason

                                                                 
                                            
    if ext not in ('.zip', '.gz'):
        sample = file_content[:min(len(file_content), 65536)]
        entropy = _calculate_entropy(sample)
        if entropy > 7.5:
            return True, f"Çok yüksek entropy ({entropy:.2f}/8.0) — şifrelenmiş/packed payload şüphesi"
        elif entropy > 7.0 and ext not in ('.py', '.js'):
            return True, f"Yüksek entropy ({entropy:.2f}/8.0) — şüpheli içerik"

                                                                 
    if ext == '.py':
        try:
            source = file_content.decode('utf-8', errors='ignore')
            flag, reason = _analyze_python_source(source, file_name_clean)
            if flag:
                return True, reason
                          
            flag, reason = _check_network_patterns(source)
            if flag:
                return True, reason
        except Exception as e:
            logger.warning(f"Python analiz hatası ({file_name_clean}): {e}")

    elif ext == '.js':
        try:
            source = file_content.decode('utf-8', errors='ignore')
            flag, reason = _analyze_js_source(source, file_name_clean)
            if flag:
                return True, reason
            flag, reason = _check_network_patterns(source)
            if flag:
                return True, reason
        except Exception as e:
            logger.warning(f"JS analiz hatası ({file_name_clean}): {e}")

                                                                 
    elif ext == '.zip':
        try:
            import io as _io
            with zipfile.ZipFile(_io.BytesIO(file_content), 'r') as zf:
                                      
                for info in zf.infolist():
                    if info.flag_bits & 0x1:
                        return True, f"Parola korumalı ZIP — içerik doğrulanamıyor: {info.filename}"
                                  
                for info in zf.infolist():
                    inner_name = os.path.basename(info.filename)
                    inner_ext = os.path.splitext(inner_name.lower())[1]
                    if inner_ext in BLOCKED_EXTENSIONS:
                        return True, f"ZIP içinde yasaklı dosya: {info.filename}"
                    flag, reason = _check_double_extension(inner_name)
                    if flag:
                        return True, f"ZIP içinde: {reason}"
                                                         
                    if info.file_size > 0 and info.file_size < 5 * 1024 * 1024:
                        try:
                            inner_content = zf.read(info.filename)
                            flag, reason = _detect_magic_bytes(inner_content)
                            if flag:
                                return True, f"ZIP içinde '{info.filename}': {reason}"
                            if inner_ext == '.py':
                                src = inner_content.decode('utf-8', errors='ignore')
                                flag, reason = _analyze_python_source(src, info.filename)
                                if flag:
                                    return True, f"ZIP/{info.filename}: {reason}"
                            elif inner_ext == '.js':
                                src = inner_content.decode('utf-8', errors='ignore')
                                flag, reason = _analyze_js_source(src, info.filename)
                                if flag:
                                    return True, f"ZIP/{info.filename}: {reason}"
                        except Exception:
                            pass                      
        except zipfile.BadZipFile:
            return True, "Geçersiz/bozuk ZIP dosyası — zararlı içerik gizleme girişimi"
        except Exception as e:
            logger.warning(f"ZIP analiz hatası ({file_name_clean}): {e}")

    return False, "Tüm güvenlik katmanları geçildi — dosya güvenli"

def scan_file_for_malware(file_content, file_name, user_id):
    """
    Çok katmanlı güvenlik taraması.
    Zararlı dosya tespitinde kullanıcıyı banla ve sahibi bilgilendir.
    Returns (is_safe: bool, reason: str)
    """
    if user_id == OWNER_ID or user_id in admin_ids:
        return True, "Yönetici bypass — tarama atlandı"

    if user_id in malware_whitelist:
        logger.info(f"Whitelist bypass: kullanıcı {user_id} malware taramasından muaf.")
        return True, "Whitelist bypass — tarama atlandı"

    file_size_kb = len(file_content) / 1024
    logger.info(f"Güvenlik taraması başlatıldı: '{file_name}' ({file_size_kb:.1f} KB) kullanıcı={user_id}")

    is_suspicious, reason = is_suspicious_file(file_content, file_name)

    if is_suspicious:
                                             
        alert_msg = (
            f"⚠️ *ŞÜPHELİ DOSYA TESPİT EDİLDİ*\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"👤 Kullanıcı: `{user_id}`\n"
            f"📄 Dosya: `{os.path.basename(file_name)}`\n"
            f"📦 Boyut: {file_size_kb:.1f} KB\n"
            f"⚠️ Sebep: {reason[:400]}\n"
            f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"Dosya yüklenmeye devam etti, ban atılmadı."
        )
        try:
            bot.send_message(OWNER_ID, alert_msg, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Owner alarm gonderilemedi: {e}")

        logger.warning(f"SUSPICIOUS FILE (no ban): kullanici={user_id} dosya='{file_name}' sebep='{reason[:150]}'")
        return True, reason

    logger.info(f"Güvenlik taraması GEÇTİ: '{file_name}' kullanıcı={user_id} — {reason}")
    return True, reason
                          
def get_user_folder(user_id):
    """Get or create user's folder for storing files"""
    user_folder = os.path.join(UPLOAD_BOTS_DIR, str(user_id))
    os.makedirs(user_folder, exist_ok=True)
    return user_folder

def is_banned(user_id):
    """Kullanıcı banlı mı? Süreli bansa süre dolmuşsa otomatik kaldır."""
    if user_id not in banned_users:
        return False
                         
    until = banned_users_until.get(user_id)
    if until and datetime.now() >= until:
                                 
        banned_users.discard(user_id)
        banned_users_until.pop(user_id, None)
        with DB_LOCK:
            try:
                conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
                conn.execute('DELETE FROM banned_users WHERE user_id=?', (user_id,))
                conn.commit()
                conn.close()
            except Exception:
                pass
        logger.info(f"✅ Süreli ban sona erdi, otomatik kaldırıldı: {user_id}")
        return False
    return True

def ban_user(user_id, reason="AI Malware Detection", ban_until_dt=None):
    """Kullanıcıyı banla + DB kaydet. ban_until_dt=None ise sınırsız."""
    global banned_users, banned_users_until
    banned_users.add(user_id)
    if ban_until_dt:
        banned_users_until[user_id] = ban_until_dt
    else:
        banned_users_until.pop(user_id, None)
    
    ban_until_str = ban_until_dt.isoformat() if ban_until_dt else None
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('INSERT OR REPLACE INTO banned_users (user_id, ban_reason, ban_until) VALUES (?, ?, ?)', 
                 (user_id, reason, ban_until_str))
        conn.commit()
        conn.close()
    
    logger.critical(f"🚫 BAN: {user_id} - {reason} - {'Süresiz' if not ban_until_dt else ban_until_dt}")
    
                                                  
    if ban_until_dt:
        def _auto_unban():
            secs = max(0, (ban_until_dt - datetime.now()).total_seconds())
            time.sleep(secs)
            if is_banned(user_id) and banned_users_until.get(user_id) == ban_until_dt:
                unban_user(user_id)
                logger.info(f"✅ Süreli ban otomatik kaldırıldı: {user_id}")
                try:
                    bot.send_message(user_id,
                        "✅ *Banınız sona erdi!*\n\nBan süreniz doldu. Artık botu kullanabilirsiniz.\nBaşlamak için /start yazın.",
                        parse_mode='Markdown')
                except Exception:
                    pass
        threading.Thread(target=_auto_unban, daemon=True).start()
    return True

def unban_user(user_id):
    """Ban kaldir"""
    global banned_users, banned_users_until
    banned_users.discard(user_id)
    banned_users_until.pop(user_id, None)
    
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('DELETE FROM banned_users WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()
    
    logger.info(f"✅ UNBAN: {user_id}")
    return True

def get_user_file_limit(user_id):
    """Get the file upload limit for a user"""
    if is_banned(user_id):
        return 0                     
    if user_id == OWNER_ID: return OWNER_LIMIT
    if user_id in admin_ids: return ADMIN_LIMIT
    if user_id in stars_premium_users: return STARS_PREMIUM_LIMIT
    if user_id in user_subscriptions and user_subscriptions[user_id]['expiry'] > datetime.now():
        return SUBSCRIBED_USER_LIMIT
    return FREE_USER_LIMIT

def save_stars_premium_db(user_id: int, stars_paid: int = STARS_PRICE):
    """Stars premium satın almayı veritabanına kaydet"""
    try:
        stars_premium_users.add(user_id)
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        conn.execute(
            'INSERT OR REPLACE INTO stars_premium (user_id, bought_at, stars_paid) VALUES (?, ?, ?)',
            (user_id, datetime.now().isoformat(), stars_paid)
        )
        conn.commit()
        conn.close()
        logger.info(f"⭐ Stars premium kaydedildi: {user_id} ({stars_paid} Stars)")
    except Exception as e:
        logger.error(f"Stars premium DB kayıt hatası: {e}")

def get_user_file_count(user_id):
    """Get the number of files uploaded by a user"""
    return len(user_files.get(user_id, []))

def is_bot_running(script_owner_id, file_name):
    """Check if a bot script is currently running for a specific user"""
    script_key = f"{script_owner_id}_{file_name}"
    script_info = bot_scripts.get(script_key)
    if script_info and script_info.get('process'):
        try:
            try:
                import psutil as _psutil
                proc = _psutil.Process(script_info['process'].pid)
                is_running = proc.is_running() and proc.status() != _psutil.STATUS_ZOMBIE
            except ImportError:
                                                                                    
                is_running = script_info['process'].poll() is None
            if not is_running:
                logger.warning(f"{script_key} için PID {script_info['process'].pid} bulundu ancak çalışmıyor/zombi. Temizleniyor.")
                if 'log_file' in script_info and hasattr(script_info['log_file'], 'close') and not script_info['log_file'].closed:
                    try:
                        script_info['log_file'].close()
                    except Exception as log_e:
                        logger.error(f"{script_key} zombie temizliği sırasında log dosyası kapatma hatası: {log_e}")
                if script_key in bot_scripts:
                    del bot_scripts[script_key]
            return is_running
        except (ProcessLookupError, PermissionError) as e:
            logger.warning(f"{script_key} için işlem bulunamadı ({type(e).__name__}). Temizleniyor.")
            if 'log_file' in script_info and hasattr(script_info['log_file'], 'close') and not script_info['log_file'].closed:
                try:
                    script_info['log_file'].close()
                except Exception as log_e:
                    logger.error(f"{script_key} var olmayan işlem temizliği sırasında log dosyası kapatma hatası: {log_e}")
            if script_key in bot_scripts:
                del bot_scripts[script_key]
            return False
        except Exception as e:
            logger.error(f"{script_key} için işlem durumu kontrol hatası: {e}", exc_info=True)
            return False
    return False

def kill_process_tree(process_info):
    """Kill a process and all its children, ensuring log file is closed."""
    pid = None
    log_file_closed = False
    script_key = process_info.get('script_key', 'N/A')

    try:
        if 'log_file' in process_info and hasattr(process_info['log_file'], 'close') and not process_info['log_file'].closed:
            try:
                process_info['log_file'].close()
                log_file_closed = True
                logger.info(f"{script_key} için log dosyası kapatıldı (PID: {process_info.get('process', {}).get('pid', 'N/A')})")
            except Exception as log_e:
                logger.error(f"{script_key} öldürme sırasında log dosyası kapatma hatası: {log_e}")

        process = process_info.get('process')
        if process and hasattr(process, 'pid'):
            pid = process.pid
            if pid:
                try:
                                                                                
                    try:
                        import psutil as _psutil
                        _psutil_available = True
                    except ImportError:
                        _psutil_available = False

                    if _psutil_available:
                        try:
                            parent = _psutil.Process(pid)
                            children = parent.children(recursive=True)
                            logger.info(f"{script_key} için işlem ağacı öldürülüyor (PID: {pid}, Çocuklar: {[c.pid for c in children]})")
                            for child in children:
                                try:
                                    child.terminate()
                                    logger.info(f"{script_key} için çocuk işlem {child.pid} sonlandırıldı")
                                except _psutil.NoSuchProcess:
                                    logger.warning(f"{script_key} için çocuk işlem {child.pid} zaten gitmiş.")
                                except Exception as e:
                                    logger.error(f"{script_key} için çocuk {child.pid} sonlandırma hatası: {e}. Öldürülüyor...")
                                    try:
                                        child.kill()
                                    except Exception as e2:
                                        logger.error(f"{script_key} için çocuk {child.pid} öldürülemedi: {e2}")
                            gone, alive = _psutil.wait_procs(children, timeout=1)
                            for p in alive:
                                try: p.kill()
                                except Exception as e: logger.error(f"{script_key} için çocuk {p.pid} öldürülemedi: {e}")
                            try:
                                parent.terminate()
                                logger.info(f"{script_key} için ana işlem {pid} sonlandırıldı")
                                try:
                                    parent.wait(timeout=1)
                                except _psutil.TimeoutExpired:
                                    parent.kill()
                                    logger.info(f"{script_key} için ana işlem {pid} öldürüldü")
                            except _psutil.NoSuchProcess:
                                logger.warning(f"{script_key} için ana işlem {pid} zaten gitmiş.")
                            except Exception as e:
                                logger.error(f"{script_key} için ana {pid} sonlandırma hatası: {e}. Öldürülüyor...")
                                try: parent.kill()
                                except Exception as e2: logger.error(f"{script_key} için ana {pid} öldürülemedi: {e2}")
                        except _psutil.NoSuchProcess:
                            logger.warning(f"{script_key} için işlem {pid} bulunamadı. Zaten sonlanmış?")
                    else:
                                                              
                        logger.info(f"{script_key} için işlem öldürülüyor (PID: {pid}) [psutil yok, fallback kullanılıyor]")
                        if os.name == 'nt':
                                                                           
                            try:
                                subprocess.call(['taskkill', '/F', '/T', '/PID', str(pid)],
                                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                                logger.info(f"{script_key} için PID {pid} taskkill ile öldürüldü")
                            except Exception as e:
                                logger.error(f"{script_key} için taskkill hatası: {e}")
                                try: process.kill()
                                except Exception: pass
                        else:
                                                                   
                            import signal as _signal
                            try:
                                os.killpg(os.getpgid(pid), _signal.SIGTERM)
                                logger.info(f"{script_key} için işlem grubuna SIGTERM gönderildi (PID: {pid})")
                            except Exception:
                                try: os.kill(pid, _signal.SIGTERM)
                                except Exception: pass
                            time.sleep(1)
                            try:
                                os.killpg(os.getpgid(pid), _signal.SIGKILL)
                                logger.info(f"{script_key} için işlem grubuna SIGKILL gönderildi (PID: {pid})")
                            except Exception:
                                try: os.kill(pid, _signal.SIGKILL)
                                except Exception: pass
                        try: process.wait(timeout=2)
                        except Exception: pass
                except Exception as e:
                    logger.error(f"{script_key} için işlem öldürme hatası: {e}")
                    try: process.kill()
                    except Exception: pass
            else:
                logger.error(f"{script_key} için işlem PID'i None.")
        elif log_file_closed:
            logger.warning(f"{script_key} için işlem nesnesi eksik, ancak log dosyası kapatıldı.")
        else:
            logger.error(f"{script_key} için işlem nesnesi eksik ve log dosyası yok. Öldürülemez.")
    except Exception as e:
        logger.error(f"❌ PID {pid or 'N/A'} ({script_key}) için işlem ağacı öldürülürken beklenmeyen hata: {e}", exc_info=True)

                                                         

def attempt_install_pip(module_name, message):
                                                                                 
    if not re.match(r'^[a-zA-Z0-9_\-]+$', module_name):
        logger.warning(f"⚠️ Geçersiz paket ismi reddedildi: {module_name}")
        return False

    package_name = TELEGRAM_MODULES.get(module_name.lower(), module_name)
    if package_name is None: 
        logger.info(f"'{module_name}' modülü çekirdek. Pip kurulumu atlanıyor.")
        return False 
    try:
        bot.reply_to(message, f"🐍 `{module_name}` modülü bulunamadı. `{package_name}` kuruluyor...", parse_mode='Markdown')
        command = [sys.executable, '-m', 'pip', 'install', package_name]
        logger.info(f"Kurulum çalıştırılıyor: {' '.join(command)}")
        result = subprocess.run(command, capture_output=True, text=True, check=False, encoding='utf-8', errors='ignore')
        if result.returncode == 0:
            logger.info(f"{package_name} kuruldu. Çıktı:\n{result.stdout}")
            bot.reply_to(message, f"✅ `{package_name}` paketi (`{module_name}` için) kuruldu.", parse_mode='Markdown')
            return True
        else:
            error_msg = f"❌ `{module_name}` için `{package_name}` kurulumu başarısız.\nLog:\n```\n{result.stderr or result.stdout}\n```"
            logger.error(error_msg)
            if len(error_msg) > 4000: error_msg = error_msg[:4000] + "\n... (Log kısaltıldı)"
            bot.reply_to(message, error_msg, parse_mode='Markdown')
            return False
    except Exception as e:
        error_msg = f"❌ `{package_name}` kurulurken hata: {str(e)}"
        logger.error(error_msg, exc_info=True)
        bot.reply_to(message, error_msg)
        return False

def attempt_install_npm(module_name, user_folder, message):
                                                                                 
    if not re.match(r'^[a-zA-Z0-9_\-]+$', module_name):
        logger.warning(f"⚠️ Geçersiz Node paket ismi reddedildi: {module_name}")
        return False

    try:
        bot.reply_to(message, f"🟠 Node paketi `{module_name}` bulunamadı. Yerel olarak kuruluyor...", parse_mode='Markdown')
        command = ['npm', 'install', module_name]
        logger.info(f"npm kurulumu çalıştırılıyor: {' '.join(command)} {user_folder} içinde")
        result = subprocess.run(command, capture_output=True, text=True, check=False, cwd=user_folder, encoding='utf-8', errors='ignore')
        if result.returncode == 0:
            logger.info(f"{module_name} kuruldu. Çıktı:\n{result.stdout}")
            bot.reply_to(message, f"✅ Node paketi `{module_name}` yerel olarak kuruldu.", parse_mode='Markdown')
            return True
        else:
            error_msg = f"❌ Node paketi `{module_name}` kurulumu başarısız.\nLog:\n```\n{result.stderr or result.stdout}\n```"
            logger.error(error_msg)
            if len(error_msg) > 4000: error_msg = error_msg[:4000] + "\n... (Log kısaltıldı)"
            bot.reply_to(message, error_msg, parse_mode='Markdown')
            return False
    except FileNotFoundError:
         error_msg = "❌ Hata: 'npm' bulunamadı. Node.js/npm'in kurulu ve PATH'te olduğundan emin olun."
         logger.error(error_msg)
         bot.reply_to(message, error_msg)
         return False
    except Exception as e:
        error_msg = f"❌ Node paketi `{module_name}` kurulurken hata: {str(e)}"
        logger.error(error_msg, exc_info=True)
        bot.reply_to(message, error_msg)
        return False

def run_script(script_path, script_owner_id, user_folder, file_name, message_obj_for_reply, attempt=1):
    """Run Python script. script_owner_id is used for the script_key. message_obj_for_reply is for sending feedback."""
    max_attempts = 2 
    if attempt > max_attempts:
        bot.reply_to(message_obj_for_reply, f"❌ '{file_name}' {max_attempts} denemeden sonra çalıştırılamadı. Logları kontrol edin.")
        return

                                                                          
    running_count = sum(1 for sk, si in bot_scripts.items() if si['script_owner_id'] == script_owner_id)
    if running_count >= 5 and script_owner_id != OWNER_ID:
        bot.reply_to(message_obj_for_reply, "⚠️ Aynı anda en fazla 5 bot çalıştırabilirsiniz. Lütfen birini durdurun.")
        return

    script_key = f"{script_owner_id}_{file_name}"
    logger.info(f"{script_path} Python betiği çalıştırılıyor (Deneme {attempt}) (Anahtar: {script_key}) kullanıcı {script_owner_id} için")

    try:
        if not os.path.exists(script_path):
             bot.reply_to(message_obj_for_reply, f"❌ Hata: '{file_name}' betiği '{script_path}' adresinde bulunamadı!")
             logger.error(f"Betik bulunamadı: {script_path} kullanıcı {script_owner_id} için")
             if script_owner_id in user_files:
                 user_files[script_owner_id] = [f for f in user_files.get(script_owner_id, []) if f[0] != file_name]
             remove_user_file_db(script_owner_id, file_name)
             return

                                                                       
                                                                
        if script_owner_id != OWNER_ID and script_owner_id not in admin_ids and script_owner_id not in malware_whitelist:
            with open(script_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                is_suspicious, sus_reason = is_suspicious_file(content.encode('utf-8', errors='ignore'), file_name)
                if is_suspicious:
                    bot.reply_to(message_obj_for_reply, f"Guvenlik Engeli: {sus_reason}", parse_mode='Markdown')
                    return

        if attempt == 1:
            check_command = [sys.executable, script_path]
            logger.info(f"Python ön kontrolü çalıştırılıyor: {' '.join(check_command)}")
            check_proc = None
            try:
                check_proc = subprocess.Popen(check_command, cwd=user_folder, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='ignore')
                stdout, stderr = check_proc.communicate(timeout=5)
                return_code = check_proc.returncode
                logger.info(f"Python Ön kontrol erken. RC: {return_code}. Stderr: {stderr[:200]}...")
                if return_code != 0 and stderr:
                    match_py = re.search(r"ModuleNotFoundError: No module named '(.+?)'", stderr)
                    if match_py:
                        module_name = match_py.group(1).strip().strip("'\"")
                        logger.info(f"Eksik Python modülü tespit edildi: {module_name}")
                        if attempt_install_pip(module_name, message_obj_for_reply):
                            logger.info(f"{module_name} için kurulum tamam. run_script yeniden deneniyor...")
                            bot.reply_to(message_obj_for_reply, f"🔄 Kurulum başarılı. '{file_name}' yeniden deneniyor...")
                            time.sleep(2)
                            threading.Thread(target=run_script, args=(script_path, script_owner_id, user_folder, file_name, message_obj_for_reply, attempt + 1)).start()
                            return
                        else:
                            bot.reply_to(message_obj_for_reply, f"❌ Kurulum başarısız. '{file_name}' çalıştırılamıyor.")
                            return
                    else:
                         error_summary = stderr[:500]
                         bot.reply_to(message_obj_for_reply, f"❌ '{file_name}' için betik ön kontrolünde hata:\n```\n{error_summary}\n```\nBetiği düzeltin.", parse_mode='Markdown')
                         return
            except subprocess.TimeoutExpired:
                logger.info("Python Ön kontrol zaman aşımına uğradı (>5sn), importlar muhtemelen tamam. Kontrol işlemi öldürülüyor.")
                if check_proc and check_proc.poll() is None: check_proc.kill(); check_proc.communicate()
                logger.info("Python Kontrol işlemi öldürüldü. Uzun çalışmaya devam ediliyor.")
            except FileNotFoundError:
                 logger.error(f"Python yorumlayıcı bulunamadı: {sys.executable}")
                 bot.reply_to(message_obj_for_reply, f"❌ Hata: Python yorumlayıcı '{sys.executable}' bulunamadı.")
                 return
            except Exception as e:
                 logger.error(f"{script_key} için Python ön kontrolünde hata: {e}", exc_info=True)
                 bot.reply_to(message_obj_for_reply, f"❌ '{file_name}' için betik ön kontrolünde beklenmeyen hata: {e}")
                 return
            finally:
                 if check_proc and check_proc.poll() is None:
                     logger.warning(f"Python Kontrol işlemi {check_proc.pid} hala çalışıyor. Öldürülüyor.")
                     check_proc.kill(); check_proc.communicate()

        logger.info(f"{script_key} için uzun çalışan Python işlemi başlatılıyor")
        log_file_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        log_file = None; process = None
        try: log_file = open(log_file_path, 'w', encoding='utf-8', errors='ignore')
        except Exception as e:
             logger.error(f"{script_key} için '{log_file_path}' log dosyası açılamadı: {e}", exc_info=True)
             bot.reply_to(message_obj_for_reply, f"❌ '{log_file_path}' log dosyası açılamadı: {e}")
             return
        try:
            startupinfo = None; creationflags = 0
            if os.name == 'nt':
                 startupinfo = subprocess.STARTUPINFO(); startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                 startupinfo.wShowWindow = subprocess.SW_HIDE
            process = subprocess.Popen(
                [sys.executable, script_path], cwd=user_folder, stdout=log_file, stderr=log_file,
                stdin=subprocess.PIPE, startupinfo=startupinfo, creationflags=creationflags,
                encoding='utf-8', errors='ignore'
            )
                                                                             
            try:
                import psutil as _psutil
                p = _psutil.Process(process.pid)
                if os.name == 'nt': p.nice(_psutil.BELOW_NORMAL_PRIORITY_CLASS)
                else: p.nice(10)
            except Exception:
                                                             
                try:
                    if os.name != 'nt':
                        os.nice(10)
                except Exception:
                    pass

            logger.info(f"{script_key} için Python işlemi {process.pid} başlatıldı")
            bot_scripts[script_key] = {
                'process': process, 'log_file': log_file, 'file_name': file_name,
                'chat_id': message_obj_for_reply.chat.id,
                'script_owner_id': script_owner_id,
                'start_time': datetime.now(), 'user_folder': user_folder, 'type': 'py', 'script_key': script_key
            }
                            
            _update_analytics(script_owner_id, 'bot_start')
                                          
            threading.Thread(target=_watch_bot_process,
                args=(script_key, script_owner_id, file_name, 'py', user_folder, message_obj_for_reply.chat.id),
                daemon=True).start()
            bot.reply_to(message_obj_for_reply, f"✅ Python betiği '{file_name}' başlatıldı! (PID: {process.pid}) (Kullanıcı: {script_owner_id})")
        except FileNotFoundError:
             logger.error(f"Uzun çalışma için Python yorumlayıcı {sys.executable} bulunamadı {script_key}")
             bot.reply_to(message_obj_for_reply, f"❌ Hata: Python yorumlayıcı '{sys.executable}' bulunamadı.")
             if log_file and not log_file.closed: log_file.close()
             if script_key in bot_scripts: del bot_scripts[script_key]
        except Exception as e:
            if log_file and not log_file.closed: log_file.close()
            error_msg = f"❌ Python betiği '{file_name}' başlatılırken hata: {str(e)}"
            logger.error(error_msg, exc_info=True)
            bot.reply_to(message_obj_for_reply, error_msg)
            if process and process.poll() is None:
                 logger.warning(f"{script_key} için potansiyel olarak başlatılan Python işlemi {process.pid} öldürülüyor")
                 kill_process_tree({'process': process, 'log_file': log_file, 'script_key': script_key})
            if script_key in bot_scripts: del bot_scripts[script_key]
    except Exception as e:
        error_msg = f"❌ Python betiği '{file_name}' çalıştırılırken beklenmeyen hata: {str(e)}"
        logger.error(error_msg, exc_info=True)
        bot.reply_to(message_obj_for_reply, error_msg)
        if script_key in bot_scripts:
             logger.warning(f"run_script'te hata nedeniyle {script_key} temizleniyor.")
             kill_process_tree(bot_scripts[script_key])
             del bot_scripts[script_key]

def run_js_script(script_path, script_owner_id, user_folder, file_name, message_obj_for_reply, attempt=1):
    """Run JS script. script_owner_id is used for the script_key. message_obj_for_reply is for sending feedback."""
    max_attempts = 2
    if attempt > max_attempts:
        bot.reply_to(message_obj_for_reply, f"❌ '{file_name}' {max_attempts} denemeden sonra çalıştırılamadı. Logları kontrol edin.")
        return

                                                   
    running_count = sum(1 for sk, si in bot_scripts.items() if si['script_owner_id'] == script_owner_id)
    if running_count >= 5 and script_owner_id != OWNER_ID:
        bot.reply_to(message_obj_for_reply, "⚠️ Aynı anda en fazla 5 bot çalıştırabilirsiniz. Lütfen birini durdurun.")
        return

    script_key = f"{script_owner_id}_{file_name}"
    logger.info(f"{script_path} JS betiği çalıştırılıyor (Deneme {attempt}) (Anahtar: {script_key}) kullanıcı {script_owner_id} için")

    try:
        if not os.path.exists(script_path):
             bot.reply_to(message_obj_for_reply, f"❌ Hata: '{file_name}' betiği '{script_path}' adresinde bulunamadı!")
             logger.error(f"JS Betik bulunamadı: {script_path} kullanıcı {script_owner_id} için")
             if script_owner_id in user_files:
                 user_files[script_owner_id] = [f for f in user_files.get(script_owner_id, []) if f[0] != file_name]
             remove_user_file_db(script_owner_id, file_name)
             return

                                                    
                                                                
        if script_owner_id != OWNER_ID and script_owner_id not in admin_ids and script_owner_id not in malware_whitelist:
            with open(script_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                is_suspicious, sus_reason = is_suspicious_file(content.encode('utf-8', errors='ignore'), file_name)
                if is_suspicious:
                    bot.reply_to(message_obj_for_reply, f"Guvenlik Engeli: {sus_reason}", parse_mode='Markdown')
                    return

        if attempt == 1:
            check_command = ['node', script_path]
            logger.info(f"JS ön kontrolü çalıştırılıyor: {' '.join(check_command)}")
            check_proc = None
            try:
                check_proc = subprocess.Popen(check_command, cwd=user_folder, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='ignore')
                stdout, stderr = check_proc.communicate(timeout=5)
                return_code = check_proc.returncode
                logger.info(f"JS Ön kontrol erken. RC: {return_code}. Stderr: {stderr[:200]}...")
                if return_code != 0 and stderr:
                    match_js = re.search(r"Cannot find module '(.+?)'", stderr)
                    if match_js:
                        module_name = match_js.group(1).strip().strip("'\"")
                        if not module_name.startswith('.') and not module_name.startswith('/'):
                             logger.info(f"Eksik Node modülü tespit edildi: {module_name}")
                             if attempt_install_npm(module_name, user_folder, message_obj_for_reply):
                                 logger.info(f"{module_name} için NPM Kurulumu tamam. run_js_script yeniden deneniyor...")
                                 bot.reply_to(message_obj_for_reply, f"🔄 NPM Kurulumu başarılı. '{file_name}' yeniden deneniyor...")
                                 time.sleep(2)
                                 threading.Thread(target=run_js_script, args=(script_path, script_owner_id, user_folder, file_name, message_obj_for_reply, attempt + 1)).start()
                                 return
                             else:
                                 bot.reply_to(message_obj_for_reply, f"❌ NPM Kurulumu başarısız. '{file_name}' çalıştırılamıyor.")
                                 return
                        else: logger.info(f"Göreceli/çekirdek modül için npm kurulumu atlanıyor: {module_name}")
                    error_summary = stderr[:500]
                    bot.reply_to(message_obj_for_reply, f"❌ '{file_name}' için JS betik ön kontrolünde hata:\n```\n{error_summary}\n```\nBetiği düzeltin veya manuel kurun.", parse_mode='Markdown')
                    return
            except subprocess.TimeoutExpired:
                logger.info("JS Ön kontrol zaman aşımına uğradı (>5sn), importlar muhtemelen tamam. Kontrol işlemi öldürülüyor.")
                if check_proc and check_proc.poll() is None: check_proc.kill(); check_proc.communicate()
                logger.info("JS Kontrol işlemi öldürüldü. Uzun çalışmaya devam ediliyor.")
            except FileNotFoundError:
                 error_msg = "❌ Hata: 'node' bulunamadı. JS dosyaları için Node.js'in kurulu olduğundan emin olun."
                 logger.error(error_msg)
                 bot.reply_to(message_obj_for_reply, error_msg)
                 return
            except Exception as e:
                 logger.error(f"{script_key} için JS ön kontrolünde hata: {e}", exc_info=True)
                 bot.reply_to(message_obj_for_reply, f"❌ '{file_name}' için JS ön kontrolünde beklenmeyen hata: {e}")
                 return
            finally:
                 if check_proc and check_proc.poll() is None:
                     logger.warning(f"JS Kontrol işlemi {check_proc.pid} hala çalışıyor. Öldürülüyor.")
                     check_proc.kill(); check_proc.communicate()

        logger.info(f"{script_key} için uzun çalışan JS işlemi başlatılıyor")
        log_file_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        log_file = None; process = None
        try: log_file = open(log_file_path, 'w', encoding='utf-8', errors='ignore')
        except Exception as e:
            logger.error(f"{script_key} JS betiği için '{log_file_path}' log dosyası açılamadı: {e}", exc_info=True)
            bot.reply_to(message_obj_for_reply, f"❌ '{log_file_path}' log dosyası açılamadı: {e}")
            return
        try:
            startupinfo = None; creationflags = 0
            if os.name == 'nt':
                 startupinfo = subprocess.STARTUPINFO(); startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                 startupinfo.wShowWindow = subprocess.SW_HIDE
            process = subprocess.Popen(
                ['node', script_path], cwd=user_folder, stdout=log_file, stderr=log_file,
                stdin=subprocess.PIPE, startupinfo=startupinfo, creationflags=creationflags,
                encoding='utf-8', errors='ignore'
            )
                                                
            try:
                import psutil as _psutil
                p = _psutil.Process(process.pid)
                if os.name == 'nt': p.nice(_psutil.BELOW_NORMAL_PRIORITY_CLASS)
                else: p.nice(10)
            except Exception:
                try:
                    if os.name != 'nt': os.nice(10)
                except Exception:
                    pass

            logger.info(f"{script_key} için JS işlemi {process.pid} başlatıldı")
            bot_scripts[script_key] = {
                'process': process, 'log_file': log_file, 'file_name': file_name,
                'chat_id': message_obj_for_reply.chat.id,
                'script_owner_id': script_owner_id,
                'start_time': datetime.now(), 'user_folder': user_folder, 'type': 'js', 'script_key': script_key
            }
            bot.reply_to(message_obj_for_reply, f"✅ JS betiği '{file_name}' başlatıldı! (PID: {process.pid}) (Kullanıcı: {script_owner_id})")
        except FileNotFoundError:
             error_msg = "❌ Hata: Uzun çalışma için 'node' bulunamadı. Node.js'in kurulu olduğundan emin olun."
             logger.error(error_msg)
             if log_file and not log_file.closed: log_file.close()
             bot.reply_to(message_obj_for_reply, error_msg)
             if script_key in bot_scripts: del bot_scripts[script_key]
        except Exception as e:
            if log_file and not log_file.closed: log_file.close()
            error_msg = f"❌ JS betiği '{file_name}' başlatılırken hata: {str(e)}"
            logger.error(error_msg, exc_info=True)
            bot.reply_to(message_obj_for_reply, error_msg)
            if process and process.poll() is None:
                 logger.warning(f"{script_key} için potansiyel olarak başlatılan JS işlemi {process.pid} öldürülüyor")
                 kill_process_tree({'process': process, 'log_file': log_file, 'script_key': script_key})
            if script_key in bot_scripts: del bot_scripts[script_key]
    except Exception as e:
        error_msg = f"❌ JS betiği '{file_name}' çalıştırılırken beklenmeyen hata: {str(e)}"
        logger.error(error_msg, exc_info=True)
        bot.reply_to(message_obj_for_reply, error_msg)
        if script_key in bot_scripts:
             logger.warning(f"run_js_script'te hata nedeniyle {script_key} temizleniyor.")
             kill_process_tree(bot_scripts[script_key])
             del bot_scripts[script_key]

                                                                
TELEGRAM_MODULES = {
    'telebot': 'pyTelegramBotAPI',
    'telegram': 'python-telegram-bot',
    'python_telegram_bot': 'python-telegram-bot',
    'aiogram': 'aiogram',
    'pyrogram': 'pyrogram',
    'telethon': 'telethon',
    'telethon.sync': 'telethon',
    'from telethon.sync import telegramclient': 'telethon',
    'telepot': 'telepot',
    'pytg': 'pytg',
    'tgcrypto': 'tgcrypto',
    'telegram_upload': 'telegram-upload',
    'telegram_send': 'telegram-send',
    'telegram_text': 'telegram-text',
    'mtproto': 'telegram-mtproto',
    'tl': 'telethon',
    'telegram_utils': 'telegram-utils',
    'telegram_logger': 'telegram-logger',
    'telegram_handlers': 'python-telegram-handlers',
    'telegram_redis': 'telegram-redis',
    'telegram_sqlalchemy': 'telegram-sqlalchemy',
    'telegram_payment': 'telegram-payment',
    'telegram_shop': 'telegram-shop-sdk',
    'pytest_telegram': 'pytest-telegram',
    'telegram_debug': 'telegram-debug',
    'telegram_scraper': 'telegram-scraper',
    'telegram_analytics': 'telegram-analytics',
    'telegram_nlp': 'telegram-nlp-toolkit',
    'telegram_ai': 'telegram-ai',
    'telegram_api': 'telegram-api-client',
    'telegram_web': 'telegram-web-integration',
    'telegram_games': 'telegram-games',
    'telegram_quiz': 'telegram-quiz-bot',
    'telegram_ffmpeg': 'telegram-ffmpeg',
    'telegram_media': 'telegram-media-utils',
    'telegram_2fa': 'telegram-twofa',
    'telegram_crypto': 'telegram-crypto-bot',
    'telegram_i18n': 'telegram-i18n',
    'telegram_translate': 'telegram-translate',
    'bs4': 'beautifulsoup4',
    'requests': 'requests',
    'pillow': 'Pillow',
    'cv2': 'opencv-python',
    'yaml': 'PyYAML',
    'dotenv': 'python-dotenv',
    'dateutil': 'python-dateutil',
    'pandas': 'pandas',
    'numpy': 'numpy',
    'flask': 'Flask',
    'django': 'Django',
    'sqlalchemy': 'SQLAlchemy',
    'asyncio': None,
    'json': None,
    'datetime': None,
    'os': None,
    'sys': None,
    're': None,
    'time': None,
    'math': None,
    'random': None,
    'logging': None,
    'threading': None,
    'subprocess': None,
    'zipfile': None,
    'tempfile': None,
    'shutil': None,
    'sqlite3': None,
    'psutil': 'psutil',
    'atexit': None
}
                                                             

                             
DB_LOCK = threading.Lock() 

def save_user_file(user_id, file_name, file_type='py'):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('INSERT OR REPLACE INTO user_files (user_id, file_name, file_type) VALUES (?, ?, ?)',
                      (user_id, file_name, file_type))
            conn.commit()
            if user_id not in user_files: user_files[user_id] = []
            user_files[user_id] = [(fn, ft) for fn, ft in user_files[user_id] if fn != file_name]
            user_files[user_id].append((file_name, file_type))
            logger.info(f"{user_id} kullanıcısı için '{file_name}' ({file_type}) dosyası kaydedildi")
        except sqlite3.Error as e: logger.error(f"❌ {user_id}, {file_name} için dosya kaydedilirken SQLite hatası: {e}")
        except Exception as e: logger.error(f"❌ {user_id}, {file_name} için dosya kaydedilirken beklenmeyen hata: {e}", exc_info=True)
        finally: conn.close()

def remove_user_file_db(user_id, file_name):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('DELETE FROM user_files WHERE user_id = ? AND file_name = ?', (user_id, file_name))
            conn.commit()
            if user_id in user_files:
                user_files[user_id] = [f for f in user_files[user_id] if f[0] != file_name]
                if not user_files[user_id]: del user_files[user_id]
            logger.info(f"{user_id} kullanıcısı için '{file_name}' dosyası veritabanından kaldırıldı")
        except sqlite3.Error as e: logger.error(f"❌ {user_id}, {file_name} için dosya kaldırılırken SQLite hatası: {e}")
        except Exception as e: logger.error(f"❌ {user_id}, {file_name} için dosya kaldırılırken beklenmeyen hata: {e}", exc_info=True)
        finally: conn.close()

def add_active_user(user_id):
    active_users.add(user_id) 
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('INSERT OR IGNORE INTO active_users (user_id) VALUES (?)', (user_id,))
            conn.commit()
            logger.info(f"Aktif kullanıcı {user_id} veritabanına eklendi/onaylandı")
        except sqlite3.Error as e: logger.error(f"❌ Aktif kullanıcı {user_id} eklenirken SQLite hatası: {e}")
        except Exception as e: logger.error(f"❌ Aktif kullanıcı {user_id} eklenirken beklenmeyen hata: {e}", exc_info=True)
        finally: conn.close()

def save_subscription(user_id, expiry):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            expiry_str = expiry.isoformat()
            c.execute('INSERT OR REPLACE INTO subscriptions (user_id, expiry) VALUES (?, ?)', (user_id, expiry_str))
            conn.commit()
            user_subscriptions[user_id] = {'expiry': expiry}
            logger.info(f"{user_id} için abonelik kaydedildi, bitiş {expiry_str}")
        except sqlite3.Error as e: logger.error(f"❌ {user_id} için abonelik kaydedilirken SQLite hatası: {e}")
        except Exception as e: logger.error(f"❌ {user_id} için abonelik kaydedilirken beklenmeyen hata: {e}", exc_info=True)
        finally: conn.close()

def remove_subscription_db(user_id):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('DELETE FROM subscriptions WHERE user_id = ?', (user_id,))
            conn.commit()
            if user_id in user_subscriptions: del user_subscriptions[user_id]
            logger.info(f"{user_id} için abonelik veritabanından kaldırıldı")
        except sqlite3.Error as e: logger.error(f"❌ {user_id} için abonelik kaldırılırken SQLite hatası: {e}")
        except Exception as e: logger.error(f"❌ {user_id} için abonelik kaldırılırken beklenmeyen hata: {e}", exc_info=True)
        finally: conn.close()

def add_admin_db(admin_id):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('INSERT OR IGNORE INTO admins (user_id) VALUES (?)', (admin_id,))
            conn.commit()
            admin_ids.add(admin_id) 
            logger.info(f"Yönetici {admin_id} veritabanına eklendi")
        except sqlite3.Error as e: logger.error(f"❌ Yönetici {admin_id} eklenirken SQLite hatası: {e}")
        except Exception as e: logger.error(f"❌ Yönetici {admin_id} eklenirken beklenmeyen hata: {e}", exc_info=True)
        finally: conn.close()

def remove_admin_db(admin_id):
    if admin_id == OWNER_ID:
        logger.warning("Sahip ID'si yöneticilerden kaldırılmaya çalışıldı.")
        return False 
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        removed = False
        try:
            c.execute('SELECT 1 FROM admins WHERE user_id = ?', (admin_id,))
            if c.fetchone():
                c.execute('DELETE FROM admins WHERE user_id = ?', (admin_id,))
                conn.commit()
                removed = c.rowcount > 0 
                if removed: admin_ids.discard(admin_id); logger.info(f"Yönetici {admin_id} veritabanından kaldırıldı")
                else: logger.warning(f"Yönetici {admin_id} bulundu ancak silme 0 satır etkiledi.")
            else:
                logger.warning(f"Yönetici {admin_id} veritabanında bulunamadı.")
                admin_ids.discard(admin_id)
            return removed
        except sqlite3.Error as e: logger.error(f"❌ Yönetici {admin_id} kaldırılırken SQLite hatası: {e}"); return False
        except Exception as e: logger.error(f"❌ Yönetici {admin_id} kaldırılırken beklenmeyen hata: {e}", exc_info=True); return False
        finally: conn.close()
                                 

                                                   
def create_main_menu_inline(user_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton('𝐆𝐔𝐍𝐂𝐄𝐋𝐋𝐄𝐌𝐄 𝐊𝐀𝐍𝐀𝐋𝐈', url=UPDATE_CHANNEL),
        types.InlineKeyboardButton('📤 Dosya Yükle', callback_data='upload'),
        types.InlineKeyboardButton('📂 Dosyalarım', callback_data='check_files'),
        types.InlineKeyboardButton('⚡ Bot Hızı', callback_data='speed'),
        types.InlineKeyboardButton('📤 Komut Gönder', callback_data='send_command'),
        types.InlineKeyboardButton('📞 Sahiple İletişim', url=f'https://t.me/{YOUR_USERNAME.replace("@", "")}')
    ]

    if user_id in admin_ids:
        admin_buttons = [
            types.InlineKeyboardButton('💳 Abonelikler', callback_data='subscription'),
            types.InlineKeyboardButton('📊 İstatistikler', callback_data='stats'),
            types.InlineKeyboardButton('🔒 Botu Kilitle' if not bot_locked else '🔓 Kilidi Aç',
                                     callback_data='lock_bot' if not bot_locked else 'unlock_bot'),
            types.InlineKeyboardButton('📢 Duyuru', callback_data='broadcast'),
            types.InlineKeyboardButton('👑 Yönetici Paneli', callback_data='admin_panel'),
            types.InlineKeyboardButton('🟢 Tüm Kullanıcı Betiklerini Çalıştır', callback_data='run_all_scripts')
        ]
        markup.add(buttons[0])
        markup.add(buttons[1], buttons[2])
        markup.add(buttons[3], admin_buttons[0])
        markup.add(admin_buttons[1], admin_buttons[3])
        markup.add(admin_buttons[2], admin_buttons[5])
        markup.add(buttons[4])
        markup.add(admin_buttons[4])
        markup.add(buttons[5])
    else:
        markup.add(buttons[0])
        markup.add(buttons[1], buttons[2])
        markup.add(buttons[3])
        if user_id not in stars_premium_users:
            markup.add(types.InlineKeyboardButton(f'⭐ {STARS_PRICE} Stars ile Premium Al', callback_data=f'stars_buy_{user_id}'))
        markup.add(buttons[4])
        markup.add(types.InlineKeyboardButton('📊 İstatistikler', callback_data='stats'))
        markup.add(buttons[5])
    return markup

def create_reply_keyboard_main_menu(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    lang = USER_LANGUAGES.get(user_id, 'tr')
    ls = LANG_STRINGS.get(lang, LANG_STRINGS['tr'])
    
    user_layout = [
        [ls['btn_update']],
        [ls['btn_upload'], ls['btn_files']],
        [ls['btn_speed'], ls['btn_stats']],
        ["⭐ Stars ile Premium Al"],
        [ls['btn_lang']],
        ["⏱️ Uptime", "🤖 Bot Durumları"],
        ["🪪 Profilim"],
        [ls['btn_cmd'], ls['btn_contact']],
    ]
    admin_layout = [
        [ls['btn_update']],
        [ls['btn_upload'], ls['btn_files']],
        [ls['btn_speed'], ls['btn_stats']],
        [ls['btn_lang']],
        ["⏱️ Uptime", "🤖 Bot Durumları"],
        ["🪪 Profilim"],
        [ls['btn_subs'], ls['btn_announce']],
        [ls['btn_resmi_announce']],
        [ls['btn_lock'], ls['btn_runall']],
        [ls['btn_sysinfo'], ls['btn_userlist']],
        [ls['btn_backup'], ls['btn_ban'], ls['btn_unban']],
        [ls['btn_cmd'], ls['btn_adminpanel']],
        [ls['btn_contact']],
    ]
                                                               
    if user_id == OWNER_ID:
        admin_layout.insert(-1, [ls['btn_all_files']])
        admin_layout.insert(-1, [ls['btn_whitelist']])
    layout_to_use = admin_layout if user_id in admin_ids else user_layout
                                           
    if user_id in admin_ids:
        lock_text = '🔓 Kilidi Aç' if _is_bot_locked() else '🔒 Botu Kilitle'
        layout_to_use = [
            [lock_text if btn == ls['btn_lock'] else btn for btn in row]
            for row in layout_to_use
        ]
    for row_buttons_text in layout_to_use:
        markup.add(*[types.KeyboardButton(text) for text in row_buttons_text])
    return markup

def create_control_buttons(script_owner_id, file_name, is_running=True):
    markup = types.InlineKeyboardMarkup(row_width=2)
    if is_running:
        markup.row(
            types.InlineKeyboardButton("🔴 Durdur", callback_data=f'stop_{script_owner_id}_{file_name}'),
            types.InlineKeyboardButton("🔄 Yeniden Başlat", callback_data=f'restart_{script_owner_id}_{file_name}')
        )
        markup.row(
            types.InlineKeyboardButton("🗑️ Sil", callback_data=f'delete_{script_owner_id}_{file_name}'),
            types.InlineKeyboardButton("📜 Loglar", callback_data=f'logs_{script_owner_id}_{file_name}')
        )
    else:
        markup.row(
            types.InlineKeyboardButton("🟢 Başlat", callback_data=f'start_{script_owner_id}_{file_name}'),
            types.InlineKeyboardButton("🗑️ Sil", callback_data=f'delete_{script_owner_id}_{file_name}')
        )
        markup.row(
            types.InlineKeyboardButton("📜 Logları Görüntüle", callback_data=f'logs_{script_owner_id}_{file_name}')
        )
    markup.add(types.InlineKeyboardButton("🔙 Dosyalara Dön", callback_data='check_files'))
    return markup

def create_admin_panel():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(
        types.InlineKeyboardButton('➕ Yönetici Ekle', callback_data='add_admin'),
        types.InlineKeyboardButton('➖ Yönetici Kaldır', callback_data='remove_admin')
    )
    markup.row(types.InlineKeyboardButton('📋 Yöneticileri Listele', callback_data='list_admins'))
    markup.row(types.InlineKeyboardButton('🔙 Ana Menüye Dön', callback_data='back_to_main'))
    return markup

def create_subscription_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(
        types.InlineKeyboardButton('➕ Abonelik Ekle', callback_data='add_subscription'),
        types.InlineKeyboardButton('➖ Abonelik Kaldır', callback_data='remove_subscription')
    )
    markup.row(
        types.InlineKeyboardButton('⬇️ Abonelik Azalt', callback_data='reduce_subscription'),
        types.InlineKeyboardButton('🔍 Abonelik Sorgula', callback_data='check_subscription')
    )
    markup.row(types.InlineKeyboardButton('📋 Tüm Abonelikler', callback_data='list_all_subs'))
    markup.row(types.InlineKeyboardButton('🔙 Ana Menüye Dön', callback_data='back_to_main'))
    return markup

def create_send_command_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(
        types.InlineKeyboardButton('📝 İşleme Gönder', callback_data='send_to_process'),
        types.InlineKeyboardButton('🔍 Tüm Logları Görüntüle', callback_data='view_all_logs')
    )
    markup.row(types.InlineKeyboardButton('🔙 Ana Menüye Dön', callback_data='back_to_main'))
    return markup
                           

                                              
def handle_zip_file(downloaded_file_content, file_name_zip, message):
    user_id = message.from_user.id
    user_folder = get_user_folder(user_id)
    temp_dir = None
    
    is_safe, reason = scan_file_for_malware(downloaded_file_content, file_name_zip, user_id)
    if not is_safe:
                                                      
        try:
            bot.send_message(OWNER_ID, f"⚠️ Şüpheli ZIP: user={user_id} | {reason[:300]}", parse_mode='Markdown')
        except Exception:
            pass

    try:
        temp_dir = tempfile.mkdtemp(prefix=f"user_{user_id}_zip_")
        logger.info(f"Zip için geçici dizin: {temp_dir}")
        zip_path = os.path.join(temp_dir, file_name_zip)
        with open(zip_path, 'wb') as new_file:
            new_file.write(downloaded_file_content)
        
                             
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                                                           
            for member in zip_ref.infolist():
                member_basename = os.path.basename(member.filename)
                member_ext = os.path.splitext(member_basename.lower())[1]
                                                               
                if member_ext in BLOCKED_EXTENSIONS:
                    try:
                        bot.send_message(OWNER_ID, f"⚠️ ZIP İÇİNDE YASAK UZANTI\nKullanıcı: `{user_id}`\nDosya: `{member.filename}`\nBan atılmadı.", parse_mode='Markdown')
                    except Exception: pass
                    bot.reply_to(message, f"⚠️ ZIP içinde desteklenmeyen uzantı: `{member.filename}`", parse_mode='Markdown')
                    return
                                           
                flag_de, reason_de = _check_double_extension(member_basename)
                if flag_de:
                    try:
                        bot.send_message(OWNER_ID, f"⚠️ ZIP şüpheli dosya adı: user={user_id} | {reason_de}")
                    except Exception:
                        pass
                                                
                if member.flag_bits & 0x1:
                    bot.reply_to(message, f"⚠️ ZIP içinde parola korumalı dosya desteklenmiyor: `{member.filename}`", parse_mode='Markdown')
                    return
                                                                  
                member_path = os.path.abspath(os.path.join(temp_dir, member.filename))
                if not member_path.startswith(os.path.abspath(temp_dir)):
                    raise zipfile.BadZipFile(f"Zip güvensiz yol içeriyor (path traversal): {member.filename}")
            
                                
            zip_ref.extractall(temp_dir)
            logger.info(f"Zip {temp_dir} dizinine çıkarıldı")

                                                                                
        target_dir = temp_dir
        root_files = os.listdir(target_dir)
        
                                        
        if not any(f.endswith(('.py', '.js')) for f in root_files):
                                                                   
            for root, dirs, files in os.walk(temp_dir):
                                                                    
                dirs[:] = [d for d in dirs if not d.startswith('.') and not d.startswith('__')]
                
                if any(f.endswith(('.py', '.js')) for f in files):
                    target_dir = root
                    break
        
                                                                            
        if target_dir != temp_dir:
            logger.info(f"Çıkarılan dosyalar {target_dir} konumundan {temp_dir} konumuna düzleştiriliyor")
            for item in os.listdir(target_dir):
                s = os.path.join(target_dir, item)
                d = os.path.join(temp_dir, item)
                                                                                   
                if os.path.exists(d):
                    if os.path.isdir(d): shutil.rmtree(d)
                    else: os.remove(d)
                shutil.move(s, d)
                                           
            extracted_items = os.listdir(temp_dir)
        else:
            extracted_items = root_files
                         

        py_files = [f for f in extracted_items if f.endswith('.py')]
        js_files = [f for f in extracted_items if f.endswith('.js')]
        req_file = 'requirements.txt' if 'requirements.txt' in extracted_items else None
        pkg_json = 'package.json' if 'package.json' in extracted_items else None

        if req_file:
            req_path = os.path.join(temp_dir, req_file)
            logger.info(f"requirements.txt bulundu, kurulum: {req_path}")
            bot.reply_to(message, f"🔄 Python bağımlılıkları `{req_file}` dosyasından kuruluyor...")
            try:
                with open(req_path, "r", encoding="utf-8", errors="ignore") as rf:
                    req_body = rf.read()
                ok_req = True                   
                command = [sys.executable, '-m', 'pip', 'install', '-r', req_path]
                result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8', errors='ignore')
                logger.info(f"requirements.txt'den pip kurulumu tamam. Çıktı:\n{result.stdout}")
                bot.reply_to(message, f"✅ Python bağımlılıkları `{req_file}` dosyasından kuruldu.")
            except subprocess.CalledProcessError as e:
                error_msg = f"❌ `{req_file}` dosyasından Python bağımlılıkları kurulumu başarısız.\nLog:\n```\n{e.stderr or e.stdout}\n```"
                logger.error(error_msg)
                if len(error_msg) > 4000: error_msg = error_msg[:4000] + "\n... (Log kısaltıldı)"
                bot.reply_to(message, error_msg, parse_mode='Markdown'); return
            except Exception as e:
                 error_msg = f"❌ Python bağımlılıkları kurulurken beklenmeyen hata: {e}"
                 logger.error(error_msg, exc_info=True); bot.reply_to(message, error_msg); return

        if pkg_json:
            logger.info(f"package.json bulundu, npm kurulumu: {temp_dir}")
            bot.reply_to(message, f"🔄 Node bağımlılıkları `{pkg_json}` dosyasından kuruluyor...")
            try:
                command = ['npm', 'install']
                result = subprocess.run(command, capture_output=True, text=True, check=True, cwd=temp_dir, encoding='utf-8', errors='ignore')
                logger.info(f"npm kurulumu tamam. Çıktı:\n{result.stdout}")
                bot.reply_to(message, f"✅ Node bağımlılıkları `{pkg_json}` dosyasından kuruldu.")
            except FileNotFoundError:
                bot.reply_to(message, "❌ 'npm' bulunamadı. Node bağımlılıkları kurulamıyor."); return 
            except subprocess.CalledProcessError as e:
                error_msg = f"❌ `{pkg_json}` dosyasından Node bağımlılıkları kurulumu başarısız.\nLog:\n```\n{e.stderr or e.stdout}\n```"
                logger.error(error_msg)
                if len(error_msg) > 4000: error_msg = error_msg[:4000] + "\n... (Log kısaltıldı)"
                bot.reply_to(message, error_msg, parse_mode='Markdown'); return
            except Exception as e:
                 error_msg = f"❌ Node bağımlılıkları kurulurken beklenmeyen hata: {e}"
                 logger.error(error_msg, exc_info=True); bot.reply_to(message, error_msg); return

        main_script_name = None; file_type = None
        preferred_py = ['main.py', 'bot.py', 'app.py']; preferred_js = ['index.js', 'main.js', 'bot.js', 'app.js']
        for p in preferred_py:
            if p in py_files: main_script_name = p; file_type = 'py'; break
        if not main_script_name:
             for p in preferred_js:
                 if p in js_files: main_script_name = p; file_type = 'js'; break
        if not main_script_name:
            if py_files: main_script_name = py_files[0]; file_type = 'py'
            elif js_files: main_script_name = js_files[0]; file_type = 'js'
        if not main_script_name:
            bot.reply_to(message, "❌ Arşivde `.py` veya `.js` betiği bulunamadı!"); return

        logger.info(f"Çıkarılan dosyalar {temp_dir} konumundan {user_folder} konumuna taşınıyor")
        moved_count = 0
        for item_name in os.listdir(temp_dir):
            if item_name == file_name_zip: continue                                               
            src_path = os.path.join(temp_dir, item_name)
            dest_path = os.path.join(user_folder, item_name)
            if os.path.isdir(dest_path): shutil.rmtree(dest_path)
            elif os.path.exists(dest_path): os.remove(dest_path)
            shutil.move(src_path, dest_path); moved_count +=1
        logger.info(f"{moved_count} öğe {user_folder} konumuna taşındı")

        save_user_file(user_id, main_script_name, file_type)
        logger.info(f"{user_id} için zip'den ana betik '{main_script_name}' ({file_type}) kaydedildi.")
        main_script_path = os.path.join(user_folder, main_script_name)
        bot.reply_to(message, f"✅ Dosyalar çıkarıldı. Ana betik başlatılıyor: `{main_script_name}`...", parse_mode='Markdown')

        if file_type == 'py':
             threading.Thread(target=run_script, args=(main_script_path, user_id, user_folder, main_script_name, message)).start()
        elif file_type == 'js':
             threading.Thread(target=run_js_script, args=(main_script_path, user_id, user_folder, main_script_name, message)).start()

    except zipfile.BadZipFile as e:
        logger.error(f"{user_id} için geçersiz zip dosyası: {e}")
        bot.reply_to(message, f"❌ Hata: Geçersiz/bozuk ZIP. {e}")
    except Exception as e:
        logger.error(f"❌ {user_id} için zip işlenirken hata: {e}", exc_info=True)
        bot.reply_to(message, f"❌ Zip işlenirken hata: {str(e)}")
    finally:
        if temp_dir and os.path.exists(temp_dir):
            try: shutil.rmtree(temp_dir); logger.info(f"Geçici dizin temizlendi: {temp_dir}")
            except Exception as e: logger.error(f"Geçici dizin {temp_dir} temizlenemedi: {e}", exc_info=True)
def handle_js_file(file_path, script_owner_id, user_folder, file_name, message):
    try:
                                      
        if os.path.exists(file_path):
            save_bot_version(script_owner_id, file_name, file_path)
        save_user_file(script_owner_id, file_name, 'js')
        threading.Thread(target=run_js_script, args=(file_path, script_owner_id, user_folder, file_name, message)).start()
    except Exception as e:
        logger.error(f"❌ {script_owner_id} için JS dosyası {file_name} işlenirken hata: {e}", exc_info=True)
        bot.reply_to(message, f"❌ JS dosyası işlenirken hata: {str(e)}")

def handle_py_file(file_path, script_owner_id, user_folder, file_name, message):
    try:
                                      
        if os.path.exists(file_path):
            save_bot_version(script_owner_id, file_name, file_path)
        save_user_file(script_owner_id, file_name, 'py')
        threading.Thread(target=run_script, args=(file_path, script_owner_id, user_folder, file_name, message)).start()
    except Exception as e:
        logger.error(f"❌ {script_owner_id} için Python dosyası {file_name} işlenirken hata: {e}", exc_info=True)
        bot.reply_to(message, f"❌ Python dosyası işlenirken hata: {str(e)}")

                                                  
def _logic_send_command(message):
    """Handle send command functionality"""
    user_id = message.from_user.id
    if bot_locked and user_id not in admin_ids:
        bot.reply_to(message, "⚠️ Bot yönetici tarafından kilitlendi.")
        return
        
    bot.reply_to(message, "📤 Komut Gönderme Seçenekleri:", reply_markup=create_send_command_menu())

def send_to_process_init(message):
    """Initialize process for sending command to a running script"""
    user_id = message.from_user.id
    chat_id = message.chat.id
    
                                  
    user_running_scripts = []
    for script_key, script_info in bot_scripts.items():
        script_owner_id = script_info['script_owner_id']
        if (user_id == script_owner_id or user_id in admin_ids) and is_bot_running(script_owner_id, script_info['file_name']):
            user_running_scripts.append((script_key, script_info))
    
    if not user_running_scripts:
        bot.reply_to(message, "❌ Çalışan betik bulunamadı.")
        return
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    for script_key, script_info in user_running_scripts:
        btn_text = f"{script_info['file_name']} (Kullanıcı: {script_info['script_owner_id']})"
        markup.add(types.InlineKeyboardButton(btn_text, callback_data=f'sendcmd_select_{script_key}'))
    
    markup.add(types.InlineKeyboardButton("🔙 Geri", callback_data='send_command'))
    bot.reply_to(message, "📝 Komut göndermek için çalışan bir betik seçin:", reply_markup=markup)

def process_send_command(message, script_key):
    """Process the actual command to send to the script"""
    user_id = message.from_user.id
    chat_id = message.chat.id

    if script_key not in bot_scripts:
        bot.reply_to(message, "❌ Betik artık çalışmıyor.")
        return

    script_info = bot_scripts[script_key]
    if script_info.get("script_owner_id") != user_id and user_id not in admin_ids:
        bot.reply_to(message, "❌ Bu betiğe komut gönderme yetkiniz yok.")
        return

    command_text = (message.text or "").strip()
    if not command_text:
        bot.reply_to(message, "❌ Boş komut gönderilemez.")
        return
    if len(command_text) > 4000:
        bot.reply_to(message, "❌ Komut çok uzun (en fazla 4000 karakter).")
        return

    try:
        process = script_info['process']
        if process and process.poll() is None:
                                           
            process.stdin.write(command_text + '\n')
            process.stdin.flush()
            bot.reply_to(message, f"✅ Komut `{script_info['file_name']}` betiğine gönderildi:\n`{command_text}`", parse_mode='Markdown')
            
                                                              
            time.sleep(1)
            if process.poll() is not None:
                bot.reply_to(message, f"⚠️ `{script_info['file_name']}` betiği komut aldıktan sonra durdu.")
        else:
            bot.reply_to(message, f"❌ `{script_info['file_name']}` betiği çalışmıyor.")
    except Exception as e:
        logger.error(f"{script_key} komut gönderme hatası: {e}")
        bot.reply_to(message, f"❌ Komut gönderme hatası: {str(e)}")

def view_all_logs(message):
    """Show all available logs for user"""
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    user_logs = []
    
                                         
    user_folder = get_user_folder(user_id)
    if os.path.exists(user_folder):
        for file in os.listdir(user_folder):
            if file.endswith('.log'):
                log_path = os.path.join(user_folder, file)
                file_size = os.path.getsize(log_path)
                user_logs.append((file, file_size, log_path))
    
    if not user_logs:
        bot.reply_to(message, "📜 Log dosyası bulunamadı.")
        return
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    for log_file, size, log_path in sorted(user_logs):
        size_kb = size / 1024
        btn_text = f"{log_file} ({size_kb:.1f} KB)"
        markup.add(types.InlineKeyboardButton(btn_text, callback_data=f'viewlog_{user_id}_{log_file}'))
    
    markup.add(types.InlineKeyboardButton("🔙 Geri", callback_data='send_command'))
    bot.reply_to(message, "📜 Mevcut Log Dosyaları:", reply_markup=markup)

def send_log_file(message, log_path, log_filename):
    """Send log file as document"""
    try:
        file_size = os.path.getsize(log_path)
        if file_size > 50 * 1024 * 1024:              
            bot.reply_to(message, f"❌ Log dosyası çok büyük ({file_size/1024/1024:.1f} MB). Maksimum 50MB.")
            return
        
        with open(log_path, 'rb') as log_file:
            bot.send_document(message.chat.id, log_file, caption=f"📜 {log_filename}")
            
    except Exception as e:
        logger.error(f"Log dosyası gönderme hatası {log_path}: {e}")
        bot.reply_to(message, f"❌ Log dosyası gönderme hatası: {str(e)}")

                                                                
def _logic_send_welcome(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    user_name = message.from_user.first_name
    user_username = message.from_user.username

    logger.info(f"Hos geldin istegi user_id: {user_id}, kullanici adi: @{user_username}")

                    
    if is_banned(user_id):
        bot.send_message(chat_id, BAN_MESSAGE, parse_mode='Markdown')
        return

    if _is_bot_locked() and user_id not in admin_ids:
        bot.send_message(chat_id, get_lock_message(), parse_mode='Markdown')
        return

                             
    if not check_channel_membership(user_id):
        send_join_channel_message(chat_id)
        return

                                           
    try:
        start_param = message.text.split(' ', 1)[1] if message.text and ' ' in message.text else ''
        if start_param.startswith('ref_') and user_id != OWNER_ID:
            ref_owner_id = int(start_param.replace('ref_', ''))
                                        
            if ref_owner_id != user_id:
                if ref_owner_id not in referral_data:
                    referral_data[ref_owner_id] = {'referrals': [], 'bonus_days': 0}
                                                                      
                if user_id not in referral_data[ref_owner_id]['referrals']:
                    referral_data[ref_owner_id]['referrals'].append(user_id)
                    referral_data[ref_owner_id]['bonus_days'] += 3
                                  
                    save_referral_db(ref_owner_id, user_id, 3)
                                                                                         
                    current = user_subscriptions.get(ref_owner_id, {}).get('expiry', datetime.now())
                    if current <= datetime.now(): current = datetime.now()
                    save_subscription(ref_owner_id, current + timedelta(hours=72))
                    try:
                        bot.send_message(ref_owner_id,
                            f"🎁 *Referral Bonusu!*\n\nDavet ettiğiniz bir kullanıcı katıldı!\n+3 gün premium kazandınız! 🎉",
                            parse_mode='Markdown')
                    except Exception: pass
                                                                            
                    user_current = user_subscriptions.get(user_id, {}).get('expiry', datetime.now())
                    if user_current <= datetime.now(): user_current = datetime.now()
                    save_subscription(user_id, user_current + timedelta(hours=24))
                    bot.send_message(chat_id, "🎁 Davet linki ile geldiniz! +1 gün premium hediye kazandınız!", parse_mode='Markdown')
    except Exception as e:
        logger.warning(f"Referral işlem hatası: {e}")

                      
    photo_file_id = None
    try:
        user_profile_photos = bot.get_user_profile_photos(user_id, limit=1)
        if user_profile_photos.photos:
            photo_file_id = user_profile_photos.photos[0][-1].file_id
    except Exception:
        pass

                                   
    try:
        if photo_file_id:
            bot.send_photo(chat_id, photo_file_id)
    except Exception:
        pass

                                              
    try:
        bot.send_message(chat_id, "Kullanici: " + str(user_name) + " | ID: " + str(user_id) + " | @" + str(user_username or "Yok"))
    except Exception:
        pass

                                
    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    limit_str = str(file_limit) if file_limit != float('inf') else "Sinırsız"
    expiry_info = ""
    if user_id == OWNER_ID: user_status = "👑 Sahip"
    elif user_id in admin_ids: user_status = "🛡️ Yonetici"
    elif user_id in user_subscriptions:
        expiry_date = user_subscriptions[user_id].get('expiry')
        if expiry_date and expiry_date > datetime.now():
            user_status = "⭐ Premium"
            remaining_str = format_remaining_time(expiry_date)
            expiry_info = f"\n⏳ Abonelik bitiş: {expiry_date.strftime('%Y-%m-%d %H:%M')} ({remaining_str} kaldı)"
        else: user_status = "Ucretsiz Kullanici (Suresi Dolmus)"; remove_subscription_db(user_id)
    else: user_status = "🆓 Ucretsiz Kullanici"

    welcome_msg_text = (
        f"👋 *Hos geldin, {user_name}!*\n\n"
        f"🔰 Durumun: {user_status}{expiry_info}\n"
        f"📁 Dosyalar: {current_files} / {limit_str}\n\n"
        f"🤖 Python veya JS botlarini yukleyip calistirabilirsin.\n"
        f"👇 Asagidaki menuyu kullan."
    )
    main_reply_markup = create_reply_keyboard_main_menu(user_id)
    try:
        bot.send_message(chat_id, welcome_msg_text, reply_markup=main_reply_markup, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"{user_id} icin hos geldin mesaji gonderilemedi: {e}", exc_info=True)

                          
    if user_id not in active_users:
        add_active_user(user_id)

def _logic_updates_channel(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('𝐆𝐔𝐍𝐂𝐄𝐋𝐋𝐄𝐌𝐄 𝐊𝐀𝐍𝐀𝐋𝐈', url=UPDATE_CHANNEL))
    bot.reply_to(message, "👇", reply_markup=markup)

def _logic_upload_file(message):
    user_id = message.from_user.id
    if bot_locked and user_id not in admin_ids:
        bot.reply_to(message, "⚠️ Bot yönetici tarafından kilitlendi, dosya kabul edilmiyor.")
        return

    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    if current_files >= file_limit:
        limit_str = str(file_limit) if file_limit != float('inf') else "Sınırsız"
        bot.reply_to(message, f"⚠️ Dosya limitine ulaşıldı ({current_files}/{limit_str}). Önce dosya silin.")
        return

    limit_str = str(file_limit) if file_limit != float('inf') else "Sınırsız"
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📂 Dosyalarımı Göster", callback_data='check_files')
    )
    bot.reply_to(message,
        f"📤 *Dosya Yükleme*\n\n"
        f"Aşağıdaki dosya türlerini doğrudan bu sohbete gönderin:\n\n"
        f"🐍 `.py` — Python bot dosyası\n"
        f"🟨 `.js` — JavaScript (Node.js) bot dosyası\n"
        f"📦 `.zip` — İçinde `.py` veya `.js` olan ZIP arşivi\n\n"
        f"📁 Slot: *{current_files} / {limit_str}* kullanıldı\n\n"
        f"⚠️ *Nasıl gönderilir?*\n"
        f"Telegramda ataç (📎) simgesine basın → *Dosya* seçin → ilgili `.py` veya `.js` dosyasını seçin.\n"
        f"_(Fotoğraf veya medya olarak değil, **Dosya** olarak gönderin!)_",
        reply_markup=markup,
        parse_mode='Markdown'
    )

def _logic_check_files(message):
    user_id = message.from_user.id
    user_files_list = user_files.get(user_id, [])
    if not user_files_list:
        bot.reply_to(message, "📂 Dosyalarınız:\n\n(Henüz dosya yüklenmemiş)")
        return
    markup = types.InlineKeyboardMarkup(row_width=1)
    for file_name, file_type in sorted(user_files_list):
        is_running = is_bot_running(user_id, file_name)
        status_icon = "🟢 Çalışıyor" if is_running else "🔴 Durduruldu"
        btn_text = f"{file_name} ({file_type}) - {status_icon}"
        markup.add(types.InlineKeyboardButton(btn_text, callback_data=f'file_{user_id}_{file_name}'))
    bot.reply_to(message, "📂 Dosyalarınız:\nYönetmek için tıklayın.", reply_markup=markup, parse_mode='Markdown')

def _logic_bot_speed(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    start_time_ping = time.time()
    wait_msg = bot.reply_to(message, "🏃 Hız test ediliyor...")
    try:
        bot.send_chat_action(chat_id, 'typing')
        response_time = round((time.time() - start_time_ping) * 1000, 2)
        status = "🔓 Kilit Açık" if not bot_locked else "🔒 Kilitli"
        if user_id == OWNER_ID: user_level = "👑 Sahip"
        elif user_id in admin_ids: user_level = "🛡️ Yönetici"
        elif user_id in user_subscriptions and user_subscriptions[user_id].get('expiry', datetime.min) > datetime.now(): user_level = "⭐ Premium"
        else: user_level = "🆓 Ücretsiz Kullanıcı"
        speed_msg = (f"⚡ Bot Hızı ve Durumu:\n\n⏱️ API Yanıt Süresi: {response_time} ms\n"
                     f"🚦 Bot Durumu: {status}\n"
                     f"👤 Seviyeniz: {user_level}")
        bot.edit_message_text(speed_msg, chat_id, wait_msg.message_id)
    except Exception as e:
        logger.error(f"Hız testi sırasında hata (komut): {e}", exc_info=True)
        bot.edit_message_text("❌ Hız testi sırasında hata oluştu.", chat_id, wait_msg.message_id)

def _logic_contact_owner(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('📞 Sahiple İletişim', url=f'https://t.me/{YOUR_USERNAME.replace("@", "")}'))
    bot.reply_to(message, "Sahiple iletişime geçmek için butona tıklayın.", reply_markup=markup)
                                                  
    try:
        bot.send_message(OWNER_ID, f"🔔 *İletişim Talebi!*\n\nKullanıcı: {message.from_user.first_name}\nID: `{message.from_user.id}`\nUsername: @{message.from_user.username or 'Yok'}\n\nHey {YOUR_USERNAME}, bir kullanıcı seninle konuşmak istiyor!", parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Sahibe bildirim gönderilemedi: {e}")

                               
def _logic_subscriptions_panel(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "⚠️ Yönetici yetkisi gerekli.")
        return
    bot.reply_to(message, "💳 Abonelik Yönetimi\n/start veya yönetici komut menüsünden butonları kullanın.", reply_markup=create_subscription_menu())

def _logic_statistics(message):
    user_id = message.from_user.id
    total_users = len(active_users)
    total_files_records = sum(len(files) for files in user_files.values())

    running_bots_count = 0
    user_running_bots = 0

    for script_key_iter, script_info_iter in list(bot_scripts.items()):
        s_owner_id, _ = script_key_iter.split('_', 1)
        if is_bot_running(int(s_owner_id), script_info_iter['file_name']):
            running_bots_count += 1
            if int(s_owner_id) == user_id:
                user_running_bots +=1

    stats_msg_base = (f"📊 Bot İstatistikleri:\n\n"
                      f"👥 Toplam Kullanıcı: {total_users}\n"
                      f"📂 Toplam Dosya Kaydı: {total_files_records}\n"
                      f"🟢 Toplam Aktif Bot: {running_bots_count}\n")

    if user_id in admin_ids:
        stats_msg_admin = (f"🔒 Bot Durumu: {'🔴 Kilitli' if bot_locked else '🟢 Kilit Açık'}\n"
                           f"🤖 Çalışan Botlarınız: {user_running_bots}")
        stats_msg = stats_msg_base + stats_msg_admin
    else:
        stats_msg = stats_msg_base + f"🤖 Çalışan Botlarınız: {user_running_bots}"

    bot.reply_to(message, stats_msg)

def _logic_broadcast_init(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "⚠️ Yönetici yetkisi gerekli.")
        return
    msg = bot.reply_to(message, "📢 Tüm aktif kullanıcılara duyuru mesajını gönderin.\n/cancel ile iptal edin.")
    bot.register_next_step_handler(msg, process_broadcast_message)

def _logic_toggle_lock_bot(message):
    """
    Botu kilitle/kilidi aç.
    Kilitliyse hemen aç. Açıksa: sebep sor → süre sor → kilitle.
    Sahip dahil herkes adım adım soruya cevap verir.
    """
    global bot_locked, lock_info
    user_id = message.from_user.id
    if user_id not in admin_ids:
        bot.reply_to(message, "⚠️ Yönetici yetkisi gerekli.")
        return

                               
    if _is_bot_locked():
        bot_locked = False
        lock_info = {'reason': '', 'locker_id': None, 'locker_name': 'Yönetici', 'until': None}
        logger.warning(f"Bot kilidi açıldı — yönetici: {user_id}")
        bot.reply_to(message, "🔓 *Bot kilidi açıldı!* Kullanıcılar artık botu kullanabilir.",
                     parse_mode='Markdown', reply_markup=create_reply_keyboard_main_menu(user_id))
        _notify_all_users(
            "🔓 *Bot tekrar aktif!*\n\nBot bakımı tamamlandı, tüm özellikler kullanılabilir.",
            exclude_id=user_id
        )
        return

                                           
    msg = bot.reply_to(message,
        "🔒 *Bot Kilitleme — Adım 1/2*\n\n"
        "Kilitleme sebebini yazın.\n"
        "_(Örnek: Bakım, Güncelleme, Acil durum vb.)_\n\n"
        "Sebepsiz kilitlemek için `-` gönderin.\n"
        "İptal: /cancel",
        parse_mode='Markdown')
    bot.register_next_step_handler(msg, _lock_step_get_reason)

def _lock_step_get_reason(message):
    """Kilit adım 1: Sebep al"""
    user_id = message.from_user.id
    if user_id not in admin_ids:
        return
    if message.text and message.text.strip().lower() == '/cancel':
        bot.reply_to(message, "❌ Kilitleme işlemi iptal edildi.")
        return
    reason = message.text.strip() if message.text else "Bakım çalışması"
    if reason == '-':
        reason = "Bakım çalışması"

    msg = bot.reply_to(message,
        f"✅ *Adım 1/2 Tamamlandı* — Sebep: _{reason}_\n\n"
        f"*Adım 2/2:* Kilit süresini belirleyin.\n\n"
        f"📌 Format örnekleri:\n"
        f"  `sınırsız` → Süresiz kilit\n"
        f"  `30m` → 30 dakika\n"
        f"  `2h` → 2 saat\n"
        f"  `1d` → 1 gün\n\n"
        f"İptal: /cancel",
        parse_mode='Markdown')
    bot.register_next_step_handler(msg, lambda m: _lock_step_get_duration(m, reason))

def _lock_step_get_duration(message, reason):
    """Kilit adım 2: Süre al ve kilitle"""
    user_id = message.from_user.id
    if user_id not in admin_ids:
        return
    if message.text and message.text.strip().lower() == '/cancel':
        bot.reply_to(message, "❌ Kilitleme işlemi iptal edildi.")
        return

    raw = message.text.strip().lower() if message.text else "sınırsız"
    duration_minutes = None

    if raw not in ('sınırsız', 'sinırsız', 'sinırsiz', 'sinirsiz', '0'):
        dur_match = re.match(r'^(\d+)(d|h|m)$', raw, re.IGNORECASE)
        if dur_match:
            val, unit = int(dur_match.group(1)), dur_match.group(2).lower()
            if unit == 'd':   duration_minutes = val * 1440
            elif unit == 'h': duration_minutes = val * 60
            elif unit == 'm': duration_minutes = val
        else:
            msg = bot.reply_to(message,
                "❌ *Geçersiz süre!*\n\nÖrnekler: `sınırsız`, `30m`, `2h`, `1d`\n\nİptal: /cancel",
                parse_mode='Markdown')
            bot.register_next_step_handler(msg, lambda m: _lock_step_get_duration(m, reason))
            return

    _apply_lock(message, reason, duration_minutes)

def _do_lock_bot(message, raw_args):
    """Direkt komut argümanlarıyla kilitle (/lockbot sebep 30m)"""
    duration_minutes = None
    reason = "Bakım çalışması"
    tokens = raw_args.rsplit(None, 1)
    last = tokens[-1] if tokens else ""
    dur_match = re.match(r'^(\d+)(d|h|m)$', last, re.IGNORECASE)
    if dur_match and len(tokens) == 2:
        val, unit = int(dur_match.group(1)), dur_match.group(2).lower()
        if unit == 'd':   duration_minutes = val * 1440
        elif unit == 'h': duration_minutes = val * 60
        elif unit == 'm': duration_minutes = val
        reason = tokens[0].strip() or "Bakım çalışması"
    elif dur_match and len(tokens) == 1:
        val, unit = int(dur_match.group(1)), dur_match.group(2).lower()
        if unit == 'd':   duration_minutes = val * 1440
        elif unit == 'h': duration_minutes = val * 60
        elif unit == 'm': duration_minutes = val
    else:
        reason = raw_args
    _apply_lock(message, reason, duration_minutes)

def _apply_lock(message, reason, duration_minutes):
    """Kilidi uygula ve bildirimleri gönder"""
    global bot_locked, lock_info
    user_id = message.from_user.id
    until_dt = datetime.now() + timedelta(minutes=duration_minutes) if duration_minutes else None

    locker_name = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
    bot_locked = True
    lock_info = {
        'reason': reason,
        'locker_id': user_id,
        'locker_name': locker_name,
        'until': until_dt,
    }
    logger.warning(f"Bot kilitlendi — yönetici: {user_id}({locker_name}), sebep: {reason}, süre: {duration_minutes} dk")

    if duration_minutes:
        until_str = f"⏰ {duration_minutes} dakika — {until_dt.strftime('%Y-%m-%d %H:%M')} tarihine kadar"
    else:
        until_str = "🔴 Süresiz"

    bot.reply_to(message,
        f"🔒 *Bot kilitlendi!*\n\n"
        f"📝 Sebep: _{reason}_\n"
        f"👤 Kilitleyen: {locker_name}\n"
        f"⏳ Süre: {until_str}\n\n"
        f"Kullanıcılara kilit bildirimi gönderildi.",
        parse_mode='Markdown', reply_markup=create_reply_keyboard_main_menu(user_id))

    _notify_all_users(get_lock_message(), exclude_id=user_id)

    if until_dt:
        def _auto_unlock():
            time.sleep(duration_minutes * 60)
            global bot_locked, lock_info
            if bot_locked and lock_info.get('locker_id') == user_id:
                bot_locked = False
                lock_info = {'reason': '', 'locker_id': None, 'locker_name': 'Yönetici', 'until': None}
                logger.info("Bot kilidi süresi doldu, otomatik açıldı.")
                try:
                    bot.send_message(OWNER_ID, "🔓 Bot kilidi otomatik olarak açıldı (süre doldu).")
                except Exception:
                    pass
                _notify_all_users("🔓 *Bot tekrar aktif!*\n\nBakım süresi tamamlandı.")
        threading.Thread(target=_auto_unlock, daemon=True).start()

def _logic_premium(message):
    """Premium bilgi ekranı — sadece admin/sahip"""
    user_id = message.from_user.id
    if user_id not in admin_ids:
        bot.reply_to(message, "ℹ️ Bu komut artık kullanılmamaktadır.")
        return
    sub = user_subscriptions.get(user_id)
    if sub and sub.get('expiry', datetime.min) > datetime.now():
        expiry = sub['expiry']
        remaining = format_remaining_time(expiry)
        status_text = f"✅ *Premium Aktif*\n⏳ Bitiş: `{expiry.strftime('%Y-%m-%d %H:%M')}` ({remaining} kaldı)"
    else:
        status_text = "❌ Premium aboneliğiniz yok."
    bot.reply_to(message,
        f"💎 *PREMIUM BİLGİSİ*\n\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"{status_text}\n\n"
        f"📋 *Premium Avantajları:*\n"
        f"  • 📁 {SUBSCRIBED_USER_LIMIT} dosya slotu (Ücretsiz: {FREE_USER_LIMIT})\n"
        f"  • ⚡ Öncelikli destek\n"
        f"  • 🟢 Aynı anda daha fazla bot\n\n"
        f"💬 Premium almak için sahibiyle iletişime geçin:\n"
        f"{YOUR_USERNAME}",
        parse_mode='Markdown'
    )

def _logic_admin_panel(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "⚠️ Yönetici yetkisi gerekli.")
        return
    bot.reply_to(message, "👑 Yönetici Paneli\nYöneticileri yönetin. /start veya yönetici menüsünden butonları kullanın.",
                 reply_markup=create_admin_panel())

                                                              
                                     
                                                              

@bot.message_handler(commands=['satin_al', 'buy', 'premium'])
def cmd_satin_al(message):
    """/satin_al — 15 Telegram Stars ile 30 ek dosya slotu satın al"""
    user_id = message.from_user.id
    if is_banned(user_id): return
    if _check_ban_for_command(message): return

                             
    if user_id in stars_premium_users:
        bot.reply_to(message,
            "✅ *Zaten Stars Premium üyesiniz!*\n\n"
            f"📁 Dosya limitiniz: `{STARS_PREMIUM_LIMIT}` slot\n"
            f"⭐ {STARS_PRICE} Stars ödeyerek satın aldınız.",
            parse_mode='Markdown')
        return

                                           
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(
        f"⭐ {STARS_PRICE} Stars ile Satın Al",
        callback_data=f'stars_buy_{user_id}'
    ))
    bot.reply_to(message,
        f"🛒 *PREMIUM SATIN AL*\n"
        f"━━━━━━━━━━━━━━━━\n\n"
        f"⭐ *Fiyat:* `{STARS_PRICE} Telegram Stars`\n"
        f"📁 *Kazanç:* `+30 ek dosya slotu` (toplam {STARS_PREMIUM_LIMIT})\n"
        f"♾️ *Süre:* Kalıcı (sınırsız süre)\n\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"💡 Ödeme *Telegram Stars* ile yapılır.\n"
        f"✅ Kurucu onayından sonra hemen aktif edilir.",
        parse_mode='Markdown',
        reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('stars_buy_'))
def stars_buy_callback(call):
    """Manuel Stars ödeme talimatı gönder"""
    user_id = call.from_user.id
    if is_banned(user_id): return
    bot.answer_callback_query(call.id)

    if user_id in stars_premium_users:
        bot.send_message(call.message.chat.id, "✅ Zaten Stars Premium üyesiniz!")
        return

                                      
    pending_stars_payments[user_id] = {
        'amount': STARS_PRICE,
        'time': datetime.now(),
        'name': call.from_user.first_name or "Kullanıcı",
        'username': f"@{call.from_user.username}" if call.from_user.username else "Yok",
    }

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(
        f"✅ Gönderdim, onayla!",
        callback_data=f"stars_sent_{user_id}"
    ))

    bot.send_message(call.message.chat.id,
        f"⭐ *ÖDEME TALİMATI*\n"
        f"━━━━━━━━━━━━━━━━\n\n"
        f"1️⃣ Telegram'da *{YOUR_USERNAME}* profilini aç\n"
        f"2️⃣ Sağ üstteki **⋮** menüsüne tıkla\n"
        f"3️⃣ *'Hediye Gönder'* veya *'Stars Gönder'* seç\n"
        f"4️⃣ Miktar: ⭐ *{STARS_PRICE} Stars* gir ve gönder\n\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"✅ Gönderdikten sonra aşağıdaki butona bas:",
        parse_mode='Markdown',
        reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('stars_sent_'))
def stars_sent_callback(call):
    """Kullanıcı Stars gönderdiğini bildirdi — kurucuya onay isteği yolla"""
    user_id = call.from_user.id
    if is_banned(user_id): return
    bot.answer_callback_query(call.id, "✅ Talebiniz alındı, onay bekleniyor...")

    if user_id in stars_premium_users:
        bot.send_message(call.message.chat.id, "✅ Zaten Stars Premium üyesiniz!")
        return

    pinfo = pending_stars_payments.get(user_id, {})
    uname = pinfo.get('name', call.from_user.first_name or "Kullanıcı")
    uusername = pinfo.get('username', f"@{call.from_user.username}" if call.from_user.username else "Yok")
    stars = pinfo.get('amount', STARS_PRICE)

                           
    bot.send_message(call.message.chat.id,
        f"⏳ *Talebiniz alındı!*\n\n"
        f"Kurucu onayladıktan sonra premium hemen aktif edilir.\n"
        f"Genellikle birkaç dakika içinde onaylanır.\n\n"
        f"Sorun için: {YOUR_USERNAME}",
        parse_mode='Markdown')

                                              
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("✅ ONAYLA", callback_data=f"stars_approve_{user_id}_{stars}"),
        types.InlineKeyboardButton("❌ REDDET", callback_data=f"stars_reject_{user_id}_{stars}")
    )
    try:
        bot.send_message(OWNER_ID,
            f"⭐ *YENİ PREMIUM TALEBİ*\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"👤 *{uname}* ({uusername})\n"
            f"🆔 `{user_id}`\n"
            f"⭐ İddia edilen ödeme: `{stars} Stars`\n"
            f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"Hesabına {stars} Stars geldi mi kontrol et, sonra onayla:",
            parse_mode='Markdown',
            reply_markup=markup)
    except Exception as e:
        logger.error(f"Kurucuya Stars onay mesajı gönderilemedi: {e}")

@bot.message_handler(commands=['onayla'])
def cmd_onayla(message):
    """/onayla — Stars gönderdiğini manuel bildir"""
    user_id = message.from_user.id
    if is_banned(user_id): return

    if user_id in stars_premium_users:
        bot.reply_to(message, "✅ Zaten Stars Premium üyesiniz!")
        return

    if user_id not in pending_stars_payments:
                                
        pending_stars_payments[user_id] = {
            'amount': STARS_PRICE,
            'time': datetime.now(),
            'name': message.from_user.first_name or "Kullanıcı",
            'username': f"@{message.from_user.username}" if message.from_user.username else "Yok",
        }

    pinfo = pending_stars_payments[user_id]
    uname = pinfo.get('name', message.from_user.first_name or "Kullanıcı")
    uusername = pinfo.get('username', f"@{message.from_user.username}" if message.from_user.username else "Yok")
    stars = pinfo.get('amount', STARS_PRICE)

    bot.reply_to(message,
        f"⏳ *Talebiniz alındı!*\n\n"
        f"Kurucu Stars'ı kontrol edip onaylayacak.\n"
        f"Genellikle birkaç dakika sürer.\n\n"
        f"Sorun için: {YOUR_USERNAME}",
        parse_mode='Markdown')

    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("✅ ONAYLA", callback_data=f"stars_approve_{user_id}_{stars}"),
        types.InlineKeyboardButton("❌ REDDET", callback_data=f"stars_reject_{user_id}_{stars}")
    )
    try:
        bot.send_message(OWNER_ID,
            f"⭐ *YENİ PREMIUM TALEBİ (/onayla)*\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"👤 *{uname}* ({uusername})\n"
            f"🆔 `{user_id}`\n"
            f"⭐ İddia edilen ödeme: `{stars} Stars`\n"
            f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"Hesabına {stars} Stars geldi mi kontrol et:",
            parse_mode='Markdown',
            reply_markup=markup)
    except Exception as e:
        logger.error(f"Kurucuya /onayla bildirimi gönderilemedi: {e}")

                                                                                         
@bot.pre_checkout_query_handler(func=lambda query: True)
def handle_pre_checkout(query):
    try:
        bot.answer_pre_checkout_query(query.id, ok=False, error_message="Lütfen manuel ödeme yolunu kullanın.")
    except Exception:
        pass

@bot.message_handler(content_types=['successful_payment'])
def handle_successful_payment(message):
    pass                       

def _handle_stars_approve(call):
    """Kurucu Stars premium'u onayladı"""
    if call.from_user.id != OWNER_ID:
        bot.answer_callback_query(call.id, "⚠️ Sadece kurucu onaylayabilir!", show_alert=True)
        return

    try:
        parts = call.data.replace("stars_approve_", "").split("_")
        buyer_id = int(parts[0])
        stars_paid = int(parts[1]) if len(parts) > 1 else STARS_PRICE
    except Exception:
        bot.answer_callback_query(call.id, "❌ Geçersiz veri.", show_alert=True)
        return

    if buyer_id in stars_premium_users:
        bot.answer_callback_query(call.id, "⚠️ Bu kullanıcı zaten Stars Premium!", show_alert=True)
        return

                              
    save_stars_premium_db(buyer_id, stars_paid)
    pending_stars_payments.pop(buyer_id, None)

    bot.answer_callback_query(call.id, f"✅ Kullanıcı {buyer_id} aktif edildi!", show_alert=True)
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        bot.edit_message_text(
            call.message.text + f"\n\n✅ *ONAYLANDI* — {datetime.now().strftime('%H:%M:%S')}",
            call.message.chat.id, call.message.message_id, parse_mode='Markdown')
    except Exception:
        pass

                        
    try:
        bot.send_message(buyer_id,
            f"🎉 *Stars Premium Aktif Edildi!*\n\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"⭐ Ödediğin Stars: `{stars_paid}`\n"
            f"📁 Yeni dosya limitin: `{STARS_PREMIUM_LIMIT}` slot\n"
            f"➕ Kazandığın ek slot: `+30`\n"
            f"♾️ Süre: Kalıcı\n"
            f"━━━━━━━━━━━━━━━━\n\n"
            f"Artık /checkfiles veya 📂 Dosyalarım butonundan yeni limiti görebilirsin.",
            parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Stars onay bildirimi gönderilemedi: {e}")

    logger.info(f"⭐ Stars Premium onaylandı: {buyer_id} ({stars_paid} Stars)")

def _handle_stars_reject(call):
    """Kurucu Stars premium'u reddetti — iade bilgisi ver"""
    if call.from_user.id != OWNER_ID:
        bot.answer_callback_query(call.id, "⚠️ Sadece kurucu reddedebilir!", show_alert=True)
        return

    try:
        parts = call.data.replace("stars_reject_", "").split("_")
        buyer_id = int(parts[0])
        stars_paid = int(parts[1]) if len(parts) > 1 else STARS_PRICE
    except Exception:
        bot.answer_callback_query(call.id, "❌ Geçersiz veri.", show_alert=True)
        return

    pending_stars_payments.pop(buyer_id, None)
    bot.answer_callback_query(call.id, f"❌ Reddedildi.", show_alert=True)
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        bot.edit_message_text(
            call.message.text + f"\n\n❌ *REDDEDİLDİ* — {datetime.now().strftime('%H:%M:%S')}",
            call.message.chat.id, call.message.message_id, parse_mode='Markdown')
    except Exception:
        pass

    try:
        bot.send_message(buyer_id,
            f"⚠️ *Premium Talebiniz Onaylanamadı*\n\n"
            f"Hesabımıza ⭐ *{stars_paid} Stars* ulaştığı doğrulanamadı.\n\n"
            f"Lütfen şunları kontrol edin:\n"
            f"• Stars'ı *{YOUR_USERNAME}* hesabına gönderdiniz mi?\n"
            f"• Miktar doğru mu? (⭐ {STARS_PRICE} Stars)\n\n"
            f"Gönderdiğinizden eminseniz {YOUR_USERNAME} ile iletişime geçin.",
            parse_mode='Markdown')
    except Exception:
        pass

    logger.warning(f"⭐ Stars Premium reddedildi: {buyer_id} ({stars_paid} Stars)")

                                              
@bot.message_handler(commands=['stars_list', 'starspremium'])
def cmd_stars_list(message):
    """Stars premium kullanıcılarını listele — sadece kurucu"""
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "⚠️ Sadece kurucu!")
        return
    if not stars_premium_users:
        bot.reply_to(message, "⭐ Henüz Stars Premium kullanıcısı yok.")
        return
    lines = [f"⭐ *STARS PREMIUM LİSTESİ* ({len(stars_premium_users)} kullanıcı)\n━━━━━━━━━━━━━━━━"]
    for uid in sorted(stars_premium_users):
        lines.append(f"• `{uid}`")
    bot.reply_to(message, '\n'.join(lines), parse_mode='Markdown')

KNOWN_COMMANDS.update({'satin_al', 'buy', 'premium', 'stars_list', 'starspremium', 'onayla'})

def _logic_run_all_scripts(message_or_call):
    if isinstance(message_or_call, telebot.types.Message):
        admin_user_id = message_or_call.from_user.id
        admin_chat_id = message_or_call.chat.id
        reply_func = lambda text, **kwargs: bot.reply_to(message_or_call, text, **kwargs)
        admin_message_obj_for_script_runner = message_or_call
    elif isinstance(message_or_call, telebot.types.CallbackQuery):
        admin_user_id = message_or_call.from_user.id
        admin_chat_id = message_or_call.message.chat.id
        bot.answer_callback_query(message_or_call.id)
        reply_func = lambda text, **kwargs: bot.send_message(admin_chat_id, text, **kwargs)
        admin_message_obj_for_script_runner = message_or_call.message 
    else:
        logger.error("_logic_run_all_scripts için geçersiz argüman")
        return

    if admin_user_id != OWNER_ID:
        reply_func("⚠️ Yönetici yetkisi gerekli.")
        return

    reply_func("⏳ Tüm kullanıcı betiklerini çalıştırma işlemi başlatılıyor. Bu biraz zaman alabilir...")
    logger.info(f"Yönetici {admin_user_id} 'tüm betikleri çalıştır' işlemini {admin_chat_id} sohbetinden başlattı.")

    started_count = 0; attempted_users = 0; skipped_files = 0; error_files_details = []

    all_user_files_snapshot = dict(user_files)

    for target_user_id, files_for_user in all_user_files_snapshot.items():
        if not files_for_user: continue
        attempted_users += 1
        logger.info(f"{target_user_id} kullanıcısı için betikler işleniyor...")
        user_folder = get_user_folder(target_user_id)

        for file_name, file_type in files_for_user:
            if not is_bot_running(target_user_id, file_name):
                file_path = os.path.join(user_folder, file_name)
                if os.path.exists(file_path):
                    logger.info(f"Yönetici {admin_user_id}, {target_user_id} kullanıcısı için '{file_name}' ({file_type}) başlatmayı deniyor.")
                    try:
                        if file_type == 'py':
                            threading.Thread(target=run_script, args=(file_path, target_user_id, user_folder, file_name, admin_message_obj_for_script_runner)).start()
                            started_count += 1
                        elif file_type == 'js':
                            threading.Thread(target=run_js_script, args=(file_path, target_user_id, user_folder, file_name, admin_message_obj_for_script_runner)).start()
                            started_count += 1
                        else:
                            logger.warning(f"{file_name} (kullanıcı {target_user_id}) için bilinmeyen dosya türü '{file_type}'. Atlanıyor.")
                            error_files_details.append(f"`{file_name}` (Kullanıcı {target_user_id}) - Bilinmeyen tür")
                            skipped_files += 1
                        time.sleep(0.7)
                    except Exception as e:
                        logger.error(f"'{file_name}' (kullanıcı {target_user_id}) başlatma kuyruğa alma hatası: {e}")
                        error_files_details.append(f"`{file_name}` (Kullanıcı {target_user_id}) - Başlatma hatası")
                        skipped_files += 1
                else:
                    logger.warning(f"{target_user_id} kullanıcısı için '{file_name}' dosyası '{file_path}' adresinde bulunamadı. Atlanıyor.")
                    error_files_details.append(f"`{file_name}` (Kullanıcı {target_user_id}) - Dosya bulunamadı")
                    skipped_files += 1

    summary_msg = (f"✅ Tüm Kullanıcı Betikleri - İşlem Tamamlandı:\n\n"
                   f"▶️ Başlatılmaya çalışılan: {started_count} betik.\n"
                   f"👥 İşlenen kullanıcı: {attempted_users}.\n")
    if skipped_files > 0:
        summary_msg += f"⚠️ Atlanan/Hatalı dosyalar: {skipped_files}\n"
        if error_files_details:
             summary_msg += "Detaylar (ilk 5):\n" + "\n".join([f"  - {err}" for err in error_files_details[:5]])
             if len(error_files_details) > 5: summary_msg += "\n  ... ve daha fazlası (logları kontrol edin)."

    reply_func(summary_msg, parse_mode='Markdown')
    logger.info(f"Tüm betikleri çalıştır işlemi tamamlandı. Yönetici: {admin_user_id}. Başlatılan: {started_count}. Atlanan/Hata: {skipped_files}")

                                                            
@bot.message_handler(commands=['start', 'help'])
def command_send_welcome(message):
                                                       
    _logic_send_welcome(message)

                                                        
def _is_bot_locked():
    global bot_locked, lock_info
    if not bot_locked:
        return False
    until = lock_info.get('until')
    if until and datetime.now() >= until:
        bot_locked = False
        lock_info = {'reason': '', 'locker_id': None, 'locker_name': 'Yönetici', 'until': None}
        logger.info("Bot kilidi süresi doldu, otomatik açıldı.")
        return False
    return True

                                                                     
def _check_ban_for_command(message):
    user_id = message.from_user.id
    if is_banned(user_id) and user_id not in admin_ids:
        bot.reply_to(message, BAN_MESSAGE, parse_mode='Markdown')
        return True
    if _is_bot_locked() and user_id not in admin_ids:
        bot.reply_to(message, get_lock_message(), parse_mode='Markdown')
        return True
    return False

@bot.message_handler(commands=['status'])
def command_show_status(message): _logic_statistics(message)

BUTTON_TEXT_TO_LOGIC = {
    "𝐆𝐔𝐍𝐂𝐄𝐋𝐋𝐄𝐌𝐄 𝐊𝐀𝐍𝐀𝐋𝐈": _logic_updates_channel,
    "📤 Dosya Yükle": _logic_upload_file,
    "📂 Dosyalarım": _logic_check_files,
    "⚡ Bot Hızı": _logic_bot_speed,
    "📤 Komut Gönder": _logic_send_command,
    "📞 Sahiple İletişim": _logic_contact_owner,
    "📊 İstatistikler": _logic_statistics,
    "💳 Abonelikler": _logic_subscriptions_panel,
    "⭐ Stars ile Premium Al": lambda m: cmd_satin_al(m),
    "📢 Duyuru": _logic_broadcast_init,
    "📢 Resmi Duyuru": lambda m: resmi_duyuru_init(m),
    "🔒 Botu Kilitle": _logic_toggle_lock_bot,
    "🔓 Kilidi Aç": _logic_toggle_lock_bot,
    "🟢 Tüm Kodları Çalıştır": _logic_run_all_scripts,
    "👑 Yönetici Paneli": _logic_admin_panel,
    "🖥️ Sistem Bilgisi": lambda m: cmd_sysinfo(m),
    "👥 Kullanıcı Listesi": lambda m: cmd_userlist(m),
    "💾 Yedek Al": lambda m: cmd_backup(m),
    "🔓 Ban Kaldır": lambda m: _logic_unban_user_button(m),
    "🚫 Kullanıcı Banla": lambda m: _logic_ban_user_button(m),
    "🚫 Ban User": lambda m: _logic_ban_user_button(m),
    "🚫 Забанить пользователя": lambda m: _logic_ban_user_button(m),
    "🌍 Dil Seç": lambda m: cmd_lang(m),
    "🔔 Webhook": lambda m: bot.send_message(m.chat.id,
        "🔔 *WEBHOOK & ALERT SİSTEMİ*\n\n"
        "`/webhook <etiket>` — Yeni webhook URL oluştur\n"
        "`/webhook_history` — Son bildirimler\n\n"
        "📌 Örnek: `/webhook mybotserver`", parse_mode='Markdown'),
    "⏱️ Uptime": lambda m: cmd_uptime(m),
    "🪪 Profilim": lambda m: cmd_myid(m),
    "🤖 Bot Durumları": lambda m: cmd_all_bot_status(m),
}

                                                               
_dm_waiting = {}                                                                 

def _logic_dm_to_user(message):
    """Admin 'Mesaj Gönder' butonuna basınca hedef kullanıcı ID'si ister."""
    user_id = message.from_user.id
    if user_id not in admin_ids:
        bot.reply_to(message, "⛔ Bu özellik sadece yöneticilere açıktır.")
        return
    _dm_waiting[user_id] = 'awaiting_target'
    msg = bot.send_message(
        message.chat.id,
        "📩 *Kullanıcıya Mesaj Gönder*\n\n"
        "Mesaj göndermek istediğiniz kullanıcının *Telegram ID*'sini girin:\n\n"
        "Örnek: `123456789`\n\n"
        "_İptal için_ /cancel",
        parse_mode='Markdown'
    )
    bot.register_next_step_handler(msg, _dm_get_target_id)

def _dm_get_target_id(message):
    user_id = message.from_user.id
                               
    if user_id not in admin_ids:
        _dm_waiting.pop(user_id, None)
        return
    text = (message.text or '').strip()
                    
    if text.lower() in ('/cancel', 'iptal'):
        _dm_waiting.pop(user_id, None)
        bot.reply_to(message, "❌ İşlem iptal edildi.")
        return
                  
    try:
        target_id = int(text)
        if target_id <= 0:
            raise ValueError("Negatif ID")
    except (ValueError, AttributeError):
                                                        
        msg = bot.reply_to(
            message,
            "⚠️ *Geçersiz ID!*\n\n"
            "Lütfen yalnızca rakamlardan oluşan bir Telegram kullanıcı ID'si girin.\n\n"
            "Örnek: `123456789`\n\n"
            "_İptal için_ /cancel",
            parse_mode='Markdown'
        )
        bot.register_next_step_handler(msg, _dm_get_target_id)
        return
    _dm_waiting[user_id] = f'awaiting_message:{target_id}'
    msg = bot.send_message(
        message.chat.id,
        f"✅ *Hedef kullanıcı:* `{target_id}`\n\n"
        f"📝 Göndermek istediğiniz mesajı yazın:\n\n"
        f"_İptal için_ /cancel",
        parse_mode='Markdown'
    )
    bot.register_next_step_handler(msg, _dm_send_message)

def _dm_send_message(message):
    user_id = message.from_user.id
                               
    if user_id not in admin_ids:
        _dm_waiting.pop(user_id, None)
        return
    text = (message.text or '').strip()
                    
    if text.lower() in ('/cancel', 'iptal'):
        _dm_waiting.pop(user_id, None)
        bot.reply_to(message, "❌ İşlem iptal edildi.")
        return
    state = _dm_waiting.get(user_id, '')
    if not state.startswith('awaiting_message:'):
        bot.reply_to(message, "⚠️ Oturum süresi dolmuş. Lütfen tekrar 📩 Mesaj Gönder butonuna basın.")
        _dm_waiting.pop(user_id, None)
        return
    target_id = int(state.split(':')[1])
                        
    if not text:
        msg = bot.reply_to(
            message,
            "⚠️ Boş mesaj gönderilemez. Lütfen bir mesaj yazın:\n\n_İptal için_ /cancel",
            parse_mode='Markdown'
        )
        bot.register_next_step_handler(msg, _dm_send_message)
        return
    try:
        bot.send_message(target_id, text)
        bot.reply_to(
            message,
            f"✅ *Mesaj gönderildi!*\n\n"
            f"👤 Alıcı ID: `{target_id}`\n"
            f"📝 Mesaj: _{text[:100]}{'...' if len(text) > 100 else ''}_",
            parse_mode='Markdown'
        )
    except Exception as e:
        bot.reply_to(message, f"❌ Mesaj gönderilemedi!\n\nHata: `{e}`", parse_mode='Markdown')
    _dm_waiting.pop(user_id, None)

def _get_all_button_texts():
    all_texts = set(BUTTON_TEXT_TO_LOGIC.keys())
    for lang_data in LANG_STRINGS.values():
        for key, val in lang_data.items():
            if key.startswith('btn_'):
                all_texts.add(val)
    return all_texts

BTN_KEY_TO_LOGIC = {
    'btn_update': _logic_updates_channel,
    'btn_upload': _logic_upload_file,
    'btn_files': _logic_check_files,
    'btn_speed': _logic_bot_speed,
    'btn_stats': _logic_statistics,
    'btn_cmd': _logic_send_command,
    'btn_contact': _logic_contact_owner,
    'btn_subs': _logic_subscriptions_panel,
    'btn_announce': _logic_broadcast_init,
    'btn_resmi_announce': lambda m: resmi_duyuru_init(m),
    'btn_lock': _logic_toggle_lock_bot,
    'btn_runall': _logic_run_all_scripts,
    'btn_adminpanel': _logic_admin_panel,
    'btn_lang': lambda m: cmd_lang(m),
    'btn_webhook': lambda m: bot.send_message(m.chat.id,
        "🔔 *WEBHOOK*\n\n`/webhook <etiket>` `/webhook_history`", parse_mode='Markdown'),
    'btn_sysinfo': lambda m: cmd_sysinfo(m),
    'btn_userlist': lambda m: cmd_userlist(m),
    'btn_backup': lambda m: cmd_backup(m),
    'btn_unban': lambda m: _logic_unban_user_button(m),
    'btn_ban': lambda m: _logic_ban_user_button(m),
    'btn_all_files': lambda m: _logic_all_user_files(m),
    'btn_whitelist': lambda m: _logic_whitelist_menu(m),
}

def _resolve_btn_key(text):
    for lang_data in LANG_STRINGS.values():
        for key, val in lang_data.items():
            if key.startswith('btn_') and val == text:
                return key
    return None

@bot.message_handler(func=lambda message: message.text in _get_all_button_texts())
def handle_button_text(message):
    user_id = message.from_user.id
    if is_banned(user_id) and user_id not in admin_ids:
        bot.reply_to(message, BAN_MESSAGE, parse_mode='Markdown')
        return
    if _is_bot_locked() and user_id not in admin_ids:
        bot.reply_to(message, get_lock_message(), parse_mode='Markdown')
        return
    logic_func = BUTTON_TEXT_TO_LOGIC.get(message.text)
    if logic_func:
        logic_func(message)
        return
    btn_key = _resolve_btn_key(message.text)
    if btn_key and btn_key in BTN_KEY_TO_LOGIC:
        BTN_KEY_TO_LOGIC[btn_key](message)

@bot.message_handler(commands=['updateschannel'])
def command_updates_channel(message): _logic_updates_channel(message)
@bot.message_handler(commands=['uploadfile'])
def command_upload_file(message):
    if _check_ban_for_command(message): return
    _logic_upload_file(message)
@bot.message_handler(commands=['checkfiles'])
def command_check_files(message):
    if _check_ban_for_command(message): return
    _logic_check_files(message)
@bot.message_handler(commands=['botspeed'])
def command_bot_speed(message): _logic_bot_speed(message)

@bot.message_handler(commands=['sendcommand'])
def command_send_command(message):
    if _check_ban_for_command(message): return
    _logic_send_command(message)
@bot.message_handler(commands=['contactowner'])
def command_contact_owner(message): _logic_contact_owner(message)
@bot.message_handler(commands=['subscriptions'])
def command_subscriptions(message): _logic_subscriptions_panel(message)
@bot.message_handler(commands=['statistics'])
def command_statistics(message): _logic_statistics(message)
@bot.message_handler(commands=['broadcast'])
def command_broadcast(message): _logic_broadcast_init(message)
@bot.message_handler(commands=['lockbot']) 
def command_lock_bot(message): _logic_toggle_lock_bot(message)
@bot.message_handler(commands=['adminpanel'])
def command_admin_panel(message): _logic_admin_panel(message)
@bot.message_handler(commands=['runningallcode'])
def command_run_all_code(message): _logic_run_all_scripts(message)

@bot.message_handler(commands=['ping'])
def ping(message):
    if _check_ban_for_command(message): return
    start_ping_time = time.time() 
    msg = bot.reply_to(message, "Pong!")
    latency = round((time.time() - start_ping_time) * 1000, 2)
    bot.edit_message_text(f"Pong! Gecikme: {latency} ms", message.chat.id, msg.message_id)

                                                      
def get_available_commands(user_id):
    """Dinamik komut listesi - user level bazlı"""
    base_cmds = [
        "📤 `uploadfile` - Dosya yükle",
        "📂 `checkfiles` - Dosyalarım",
        "⚡ `botspeed` - Bot hızı",
        "📊 `statistics` - İstatistikler",
        "📤 `sendcommand` - Komut gönder",
        "🔐 `encode <mod> <metin>` - Encode (base64/hex/url/binary/rot13/morse/ascii)",
        "🔓 `decode <mod> <metin>` - Decode",
        "🔑 `hash_password <metin>` - SHA256 hash",
        "🎲 `randpass [uzunluk]` - Güçlü şifre üret",
        "🔗 `shorten <url>` - URL kısalt",
        "🔍 `search <dosya>` - Dosya ara",
        "👤 `myinfo` - Hesap bilgilerin",
        "`start` - Ana menü",
        "`ping` - Gecikme testi",
                                     
        "🤖 `ai <soru>` - AI ile sohbet",
        "🤖 `chat <soru>` - AI ile sohbet (alternatif)",
        "🔍 `debugai <dosya>` - Kodu AI ile analiz et",
        "📜 `loganaliz <dosya>` - Logları AI ile incele",
        "🔄 `ai_reset` - AI sohbet geçmişini sıfırla",
        "⭐ `satin_al` - 15 Stars ile 30 ek dosya slotu satın al",
        "🌍 `lang` - Dil seç (TR/EN/RU)",
        "🌍 `dil` - Dil seç",
        "🎴 `profil` - Görsel profil kartı",
        "🎴 `profile` - Görsel profil kartı",
        "🎴 `kart` - Görsel profil kartı",
        "🔔 `webhook <etiket>` - Webhook URL oluştur",
        "🔔 `webhook_history` - Webhook geçmişi",
        "⏰ `zamanla <dosya> start|stop SS:DD` - Zamanlayıcı kur",
        "📅 `takvim` - Aktif zamanlayıcılar",
        "❌ `schedule_cancel <dosya> <aksiyon>` - Zamanlayıcı iptal",
        "🔐 `2fa_enable` - 2FA'yı etkinleştir",
        "🔐 `2fa_disable` - 2FA'yı kapat",
        "🔐 `2fa_send` - Yeni doğrulama kodu",
        "🔐 `2fa_verify <kod>` - 2FA kodunu doğrula",
        "🔐 `2fa_status` - 2FA durumu",
        "🆕 `yenikomutlar` - Tüm yeni komutlar",
    ]

    if user_id in admin_ids:
        base_cmds.extend([
            "💳 `subscriptions` - Abonelikler",
            "📢 `broadcast` - Duyuru",
            "👑 `adminpanel` - Admin panel",
            "🖥️ `sysinfo` - Sistem bilgisi",
            "👥 `userlist` - Kullanıcı listesi",
            "💾 `backup` - Yedek al",
            "🚫 `ban <id> [sebep]` - Kullanıcı banla",
            "🔓 `unban <id>` - Ban kaldır",
            "📢 `announce <mesaj>` - Hızlı duyuru",
        ])

    return "**KULLANILABİLİR KOMUTLAR:**\n" + "\n".join(base_cmds)

@bot.message_handler(content_types=['photo', 'sticker', 'animation', 'video', 'voice', 'audio'])
def handle_media_invalid(message):
    """GIF/Emoji/Sticker vb. desteklenmiyor"""
    if _check_ban_for_command(message):
        return
    cmd_list = get_available_commands(message.from_user.id)
    bot.reply_to(message, f"❌ GIF/Emoji/Sticker desteklenmiyor!\n\n{cmd_list}", parse_mode='Markdown')

                                                              

@bot.message_handler(commands=['announce'])
def cmd_announce(message):
    """Toplu duyuru — resmi veya normal mod
    /announce resmi <mesaj>  → Başında 'Duyuru' başlığıyla gönder
    /announce normal <mesaj> → Olduğu gibi gönder
    """
    user_id = message.from_user.id
    if user_id not in admin_ids:
        bot.reply_to(message, "⚠️ Sadece yöneticiler duyuru yapabilir!")
        return
    try:
        parts = message.text.split(' ', 2)
        if len(parts) < 3:
            raise IndexError
        mod = parts[1].lower()
        text = parts[2]
        if mod == 'resmi':
            send_text = f"📢 *Duyuru*\n\n{text}"
            parse_mode = 'Markdown'
        elif mod == 'normal':
            send_text = text
            parse_mode = None
        else:
            bot.reply_to(message,
                "📌 Kullanım:\n"
                "`/announce resmi <mesaj>` — Başında 'Duyuru' başlığıyla gönder\n"
                "`/announce normal <mesaj>` — Olduğu gibi gönder", parse_mode='Markdown')
            return
        sent = 0
        for uid in list(active_users):
            try:
                if parse_mode:
                    bot.send_message(uid, send_text, parse_mode=parse_mode)
                else:
                    bot.send_message(uid, send_text)
                sent += 1
                time.sleep(0.05)
            except Exception:
                pass
        bot.reply_to(message, f"✅ Duyuru {sent} kullanıcıya gönderildi!")
    except IndexError:
        bot.reply_to(message,
            "📌 Kullanım:\n"
            "`/announce resmi <mesaj>` — Başında 'Duyuru' başlığıyla gönder\n"
            "`/announce normal <mesaj>` — Olduğu gibi gönder", parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_invalid_command(message):
    """Fallback - Geçersiz text komut"""
    if message.text and message.text.startswith('/'):
                                                                  
        cmd_part = message.text[1:].split()[0].split('@')[0].lower()
        if cmd_part not in KNOWN_COMMANDS:
            cmd_list = get_available_commands(message.from_user.id)
            bot.reply_to(message, f"❌ **GEÇERSİZ KOMUT:** `/{cmd_part}`\n\n{cmd_list}", parse_mode='Markdown')
                                                                      

                                                        
@bot.message_handler(content_types=['document'])
def handle_file_upload_doc(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    doc = message.document
    logger.info(f"{user_id} kullanıcısından dosya: {doc.file_name} ({doc.mime_type}), Boyut: {doc.file_size}")

                                  
    if is_banned(user_id):
        bot.reply_to(message, BAN_MESSAGE, parse_mode='Markdown')
        return
    
    if _is_bot_locked() and user_id not in admin_ids:
        bot.reply_to(message, get_lock_message(), parse_mode='Markdown')
        return

                                     
    if user_id not in admin_ids and not rate_limiter.is_allowed(user_id):
        remaining_str = f"{rate_limiter.time_window // 60} dakika"
        bot.reply_to(message,
            f"⏱️ *Çok fazla istek!*\n\n"
            f"Spam koruması devreye girdi. Lütfen {remaining_str} bekleyin.\n"
            f"Kalan hakkınız: `0/{rate_limiter.max_requests}`",
            parse_mode='Markdown')
        return

    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    if current_files >= file_limit:
        limit_str = str(file_limit) if file_limit != float('inf') else "Sınırsız"
        bot.reply_to(message, f"⚠️ Dosya limitine ulaşıldı ({current_files}/{limit_str}). /checkfiles ile dosya silin.")
        return

    file_name = os.path.basename(doc.file_name)
    if not file_name: bot.reply_to(message, "⚠️ Dosya adı yok. Dosyanın bir adı olduğundan emin olun."); return
    file_ext = os.path.splitext(file_name)[1].lower()
    if file_ext not in ['.py', '.js', '.zip']:
        bot.reply_to(message, "⚠️ Desteklenmeyen tür! Sadece `.py`, `.js`, `.zip` izinlidir.")
        return
    max_file_size = 20 * 1024 * 1024
    if doc.file_size > max_file_size:
        bot.reply_to(message, f"⚠️ Dosya çok büyük (Maks: {max_file_size // 1024 // 1024} MB)."); return

    try:
                                                        
        try:
            uname = message.from_user.first_name or "Bilinmiyor"
            uusername = message.from_user.username or "yok"
                                         
            dosya_bilgi = (
                f"📂 YENİ DOSYA YUKLENDI\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"👤 Gonderen: {uname}\n"
                f"🆔 ID: {user_id}\n"
                f"✳️ @{uusername}\n"
                f"📄 Dosya: {file_name}\n"
                f"📦 Boyut: {doc.file_size / 1024:.1f} KB\n"
                f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"━━━━━━━━━━━━━━━━"
            )
                                       
            bot.send_message(OWNER_ID, dosya_bilgi)
                                           
            bot.forward_message(OWNER_ID, chat_id, message.message_id)
        except Exception as e: logger.error(f"Sahibe dosya bildirimi gonderilemedi: {e}")

        download_wait_msg = bot.reply_to(message, f"⏳ `{file_name}` indiriliyor...")
        file_info_tg_doc = bot.get_file(doc.file_id)
        downloaded_file_content = bot.download_file(file_info_tg_doc.file_path)
        
                                         
        if user_id != OWNER_ID:
            is_safe, reason = scan_file_for_malware(downloaded_file_content, file_name, user_id)
            if not is_safe:
                try:
                    bot.send_message(OWNER_ID, f"⚠️ Şüpheli dosya: user={user_id} | {reason[:300]}")
                except Exception:
                    pass
                return
        
        bot.edit_message_text(f"✅ `{file_name}` indirildi. İşleniyor...", chat_id, download_wait_msg.message_id)
        logger.info(f"{file_name} dosyası {user_id} kullanıcısı için indirildi")
        user_folder = get_user_folder(user_id)

        if file_ext == '.zip':
            handle_zip_file(downloaded_file_content, file_name, message)
        else:
            file_path = os.path.join(user_folder, file_name)
            with open(file_path, 'wb') as f: f.write(downloaded_file_content)
            logger.info(f"Tek dosya {file_path} konumuna kaydedildi")
            if file_ext == '.js': handle_js_file(file_path, user_id, user_folder, file_name, message)
            elif file_ext == '.py': handle_py_file(file_path, user_id, user_folder, file_name, message)
    except telebot.apihelper.ApiTelegramException as e:
         logger.error(f"{user_id} için dosya işlenirken Telegram API Hatası: {e}", exc_info=True)
         if "file is too big" in str(e).lower():
              bot.reply_to(message, f"❌ Telegram API Hatası: Dosya indirmek için çok büyük (~20MB limit).")
         else: bot.reply_to(message, f"❌ Telegram API Hatası: {str(e)}. Daha sonra deneyin.")
    except Exception as e:
        logger.error(f"❌ {user_id} için dosya işlenirken genel hata: {e}", exc_info=True)
        bot.reply_to(message, f"❌ Beklenmeyen hata: {str(e)}")

                                                      
@bot.callback_query_handler(func=lambda call: True) 
def handle_callbacks(call):
    user_id = call.from_user.id
    data = call.data
    logger.info(f"Callback: Kullanıcı={user_id}, Veri='{data}'")

                                                                          
    if is_banned(user_id) and user_id not in admin_ids:
        bot.answer_callback_query(call.id, "🚫 Bot yöneticisi tarafından banlandınız!", show_alert=True)
        try:
            bot.send_message(call.message.chat.id, BAN_MESSAGE, parse_mode='Markdown')
        except Exception:
            pass
        return

    if _is_bot_locked() and user_id not in admin_ids and data not in ['back_to_main', 'speed', 'stats']:
        bot.answer_callback_query(call.id, "🔒 Bot yönetici tarafından kilitlendi!", show_alert=True)
        try:
            bot.send_message(call.message.chat.id, get_lock_message(), parse_mode='Markdown')
        except Exception:
            pass
        return
    try:
        if data == 'upload': upload_callback(call)
        elif data == 'check_files': check_files_callback(call)
        elif data.startswith('file_'): file_control_callback(call)
        elif data.startswith('start_'): start_bot_callback(call)
        elif data.startswith('stop_'): stop_bot_callback(call)
        elif data.startswith('restart_'): restart_bot_callback(call)
        elif data.startswith('delete_'): delete_bot_callback(call)
        elif data.startswith('logs_'): logs_bot_callback(call)
        elif data == 'speed': speed_callback(call)
        elif data == 'back_to_main': back_to_main_callback(call)
        elif data.startswith('confirm_broadcast_'): handle_confirm_broadcast(call)
        elif data == 'cancel_broadcast': handle_cancel_broadcast(call)
                                            
        elif data == 'send_command': send_command_callback(call)
        elif data == 'send_to_process': send_to_process_callback(call)
        elif data.startswith('sendcmd_select_'): sendcmd_select_callback(call)
        elif data == 'view_all_logs': view_all_logs_callback(call)
        elif data.startswith('viewlog_'): viewlog_callback(call)
                                 
        elif data == 'subscription': owner_required_callback(call, subscription_management_callback)
        elif data == 'stats': stats_callback(call)
        elif data == 'lock_bot': owner_required_callback(call, lock_bot_callback)
        elif data == 'unlock_bot': owner_required_callback(call, unlock_bot_callback)
        elif data == 'run_all_scripts': owner_required_callback(call, run_all_scripts_callback)
        elif data == 'broadcast': owner_required_callback(call, broadcast_init_callback) 
        elif data == 'broadcast_type_resmi': owner_required_callback(call, lambda c: broadcast_type_callback(c, 'resmi'))
        elif data == 'broadcast_type_normal': owner_required_callback(call, lambda c: broadcast_type_callback(c, 'normal'))
                                         
        elif data.startswith('timer_file_'): timer_file_selected_callback(call)
        elif data.startswith('timer_action_'): timer_action_selected_callback(call)
        elif data == 'timer_cancel':
            bot.answer_callback_query(call.id, "İptal edildi.")
            try: bot.delete_message(call.message.chat.id, call.message.message_id)
            except: pass
        elif data.startswith('stars_approve_'): _handle_stars_approve(call)
        elif data.startswith('stars_reject_'): _handle_stars_reject(call)
        elif data == 'admin_panel': owner_required_callback(call, admin_panel_callback)
        elif data == 'add_admin': owner_required_callback(call, add_admin_init_callback) 
        elif data == 'remove_admin': owner_required_callback(call, remove_admin_init_callback) 
        elif data == 'list_admins': admin_required_callback(call, list_admins_callback)
        elif data == 'add_subscription': admin_required_callback(call, add_subscription_init_callback) 
        elif data == 'remove_subscription': admin_required_callback(call, remove_subscription_init_callback) 
        elif data == 'check_subscription': admin_required_callback(call, check_subscription_init_callback)
        elif data == 'list_all_subs':
            if call.from_user.id not in admin_ids:
                bot.answer_callback_query(call.id, "⚠️ Yetkisiz.", show_alert=True); return
            bot.answer_callback_query(call.id)
            cmd_all_subs(call.message)
        elif data.startswith('lang_'): _handle_lang_select(call)
        elif data.startswith('confirm_ban_'): _confirm_ban_callback(call)
        elif data == 'cancel_ban':
            bot.answer_callback_query(call.id, "❌ Ban iptal edildi.")
            try: bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            except: pass
                                     
        elif data in ('wl_add', 'wl_remove', 'wl_list'): _whitelist_callback(call)
                                       
        elif data == 'check_membership':
            uid = call.from_user.id
            if check_channel_membership(uid):
                bot.answer_callback_query(call.id, "✅ Üyelik onaylandı! Bot kullanıma hazır.", show_alert=True)
                try: bot.delete_message(call.message.chat.id, call.message.message_id)
                except: pass
                _logic_send_welcome(call.message)
            else:
                bot.answer_callback_query(call.id, "❌ Kanala henüz katılmadınız! Lütfen önce katılın.", show_alert=True)
                                          
        elif data == 'support_new':
            bot.answer_callback_query(call.id)
            msg = bot.send_message(call.message.chat.id,
                "✉️ *Destek Mesajınızı Yazın*\n\nMesajınızı yazın, yöneticiye iletilecektir.\n/cancel ile iptal.",
                parse_mode='Markdown')
            bot.register_next_step_handler(msg, _process_support_message_step)
        elif data == 'support_list':
            bot.answer_callback_query(call.id)
            uid = call.from_user.id
            user_tickets = [(tid, t) for tid, t in support_tickets.items() if t['user_id'] == uid]
            if not user_tickets:
                bot.send_message(call.message.chat.id, "📋 Henüz destek talebiniz bulunmuyor.")
            else:
                lines = ["📋 *TALEPLERİNİZ*\n━━━━━━━━━━━━━━━━"]
                for tid, t in user_tickets[-5:]:
                    icon = "🟢" if t['status'] == 'open' else "✅"
                    lines.append(f"{icon} #{tid} — {t['timestamp'].strftime('%d/%m %H:%M')}\n   _{t['message'][:50]}_")
                bot.send_message(call.message.chat.id, '\n'.join(lines), parse_mode='Markdown')
                                        
        elif data.startswith('reply_user_'):
            parts = data.split('_')
            target_uid = int(parts[2])
            tid = int(parts[3]) if len(parts) > 3 else 0
            bot.answer_callback_query(call.id)
            admin_reply_to[call.from_user.id] = target_uid
            msg = bot.send_message(call.message.chat.id,
                f"↩️ `{target_uid}` kullanıcısına yanıtınızı yazın:\n/cancel ile iptal.",
                parse_mode='Markdown')
            bot.register_next_step_handler(msg, lambda m: _process_admin_reply_step(m, target_uid, tid))
        elif data.startswith('ticket_close_'):
            if call.from_user.id not in admin_ids:
                bot.answer_callback_query(call.id, "⚠️ Yetki yok.", show_alert=True); return
            tid = int(data.replace('ticket_close_', ''))
            if tid in support_tickets:
                support_tickets[tid]['status'] = 'closed'
            bot.answer_callback_query(call.id, "✅ Talep çözüldü olarak işaretlendi.")
                                                  
        elif data.startswith('owner_stopall_'):
            if call.from_user.id != OWNER_ID:
                bot.answer_callback_query(call.id, "⚠️ Sadece sahip.", show_alert=True); return
            target_id = int(data.replace('owner_stopall_', ''))
            stopped = 0
            for sk in list(bot_scripts.keys()):
                si = bot_scripts[sk]
                if si['script_owner_id'] == target_id and is_bot_running(target_id, si['file_name']):
                    kill_process_tree(si); del bot_scripts[sk]; stopped += 1
            bot.answer_callback_query(call.id, f"🛑 {stopped} bot durduruldu!", show_alert=True)
        elif data.startswith('owner_startall_'):
            if call.from_user.id != OWNER_ID:
                bot.answer_callback_query(call.id, "⚠️ Sadece sahip.", show_alert=True); return
            target_id = int(data.replace('owner_startall_', ''))
            files = user_files.get(target_id, [])
            user_folder = get_user_folder(target_id)
            started = 0
            for fn, ft in files:
                fp = os.path.join(user_folder, fn)
                if os.path.exists(fp) and not is_bot_running(target_id, fn):
                    try:
                        if ft == 'py': threading.Thread(target=run_script, args=(fp, target_id, user_folder, fn, call.message)).start()
                        elif ft == 'js': threading.Thread(target=run_js_script, args=(fp, target_id, user_folder, fn, call.message)).start()
                        started += 1; time.sleep(0.5)
                    except Exception: pass
            bot.answer_callback_query(call.id, f"▶️ {started} bot başlatıldı!", show_alert=True)
                                              
        elif data == 'reduce_subscription':
            admin_required_callback(call, reduce_subscription_init_callback)

        else:
            bot.answer_callback_query(call.id, "Bilinmeyen işlem.")
            logger.warning(f"İşlenmeyen callback verisi: {data} kullanıcı {user_id} tarafından")
    except Exception as e:
        logger.error(f"'{data}' callback'i {user_id} için işlenirken hata: {e}", exc_info=True)
        try: bot.answer_callback_query(call.id, "İstek işlenirken hata oluştu.", show_alert=True)
        except Exception as e_ans: logger.error(f"Hata sonrası callback yanıtı gönderilemedi: {e_ans}")

def admin_required_callback(call, func_to_run):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, "⚠️ Yönetici yetkisi gerekli.", show_alert=True)
        return
    func_to_run(call) 

def owner_required_callback(call, func_to_run):
    if call.from_user.id != OWNER_ID:
        bot.answer_callback_query(call.id, "⚠️ Sahip yetkisi gerekli.", show_alert=True)
        return
    func_to_run(call)

                                             
def send_command_callback(call):
    bot.answer_callback_query(call.id)
    try:
        bot.edit_message_text("📤 Komut Gönderme Seçenekleri:",
                              call.message.chat.id, call.message.message_id, 
                              reply_markup=create_send_command_menu())
    except Exception as e:
        logger.error(f"Komut gönderme menüsü gösterilirken hata: {e}")

def send_to_process_callback(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "📝 Çalıştırmak istediğiniz komutu gönderin:")
    bot.register_next_step_handler(msg, lambda m: send_to_process_init(m))

def sendcmd_select_callback(call):
    try:
        script_key = call.data.replace('sendcmd_select_', '')
        bot.answer_callback_query(call.id, f"Betik seçildi: {script_key}")
        msg = bot.send_message(call.message.chat.id, f"📝 {script_key} betiğine gönderilecek komutu yazın:")
        bot.register_next_step_handler(msg, lambda m: process_send_command(m, script_key))
    except Exception as e:
        logger.error(f"sendcmd_select_callback hatası: {e}")
        bot.answer_callback_query(call.id, "Betik seçilirken hata oluştu.")

def view_all_logs_callback(call):
    bot.answer_callback_query(call.id)
    view_all_logs(call.message)

def viewlog_callback(call):
    try:
        _, user_id_str, log_filename = call.data.split('_', 2); log_filename = os.path.basename(log_filename)
        user_id = int(user_id_str)
        requesting_user_id = call.from_user.id
        
        if not (requesting_user_id == user_id or requesting_user_id in admin_ids):
            bot.answer_callback_query(call.id, "⚠️ Sadece kendi loglarınızı görüntüleyebilirsiniz.", show_alert=True)
            return
            
        user_folder = get_user_folder(user_id)
        log_path = os.path.join(user_folder, log_filename)
        
        if not os.path.exists(log_path):
            bot.answer_callback_query(call.id, "❌ Log dosyası bulunamadı.", show_alert=True)
            return
            
        bot.answer_callback_query(call.id, "📜 Log dosyası gönderiliyor...")
        send_log_file(call.message, log_path, log_filename)
        
    except Exception as e:
        logger.error(f"viewlog_callback hatası: {e}")
        bot.answer_callback_query(call.id, "Log görüntüleme hatası.")

                                                               

def upload_callback(call):
    user_id = call.from_user.id
    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    if current_files >= file_limit:
        limit_str = str(file_limit) if file_limit != float('inf') else "Sınırsız"
        bot.answer_callback_query(call.id, f"⚠️ Dosya limitine ulaşıldı ({current_files}/{limit_str}).", show_alert=True)
        return
    bot.answer_callback_query(call.id)
    limit_str = str(file_limit) if file_limit != float('inf') else "Sınırsız"
    bot.send_message(call.message.chat.id,
        f"📤 *Dosya Yükleme*\n\n"
        f"Aşağıdaki dosya türlerini doğrudan bu sohbete gönderin:\n\n"
        f"🐍 `.py` — Python bot dosyası\n"
        f"🟨 `.js` — JavaScript (Node.js) bot dosyası\n"
        f"📦 `.zip` — İçinde `.py` veya `.js` olan ZIP arşivi\n\n"
        f"📁 Slot: *{current_files} / {limit_str}* kullanıldı\n\n"
        f"⚠️ *Nasıl gönderilir?*\n"
        f"Telegramda ataç (📎) simgesine basın → *Dosya* seçin → ilgili `.py` veya `.js` dosyasını seçin.\n"
        f"_(Fotoğraf veya medya olarak değil, **Dosya** olarak gönderin!)_",
        parse_mode='Markdown'
    )

def check_files_callback(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id 
    user_files_list = user_files.get(user_id, [])
    if not user_files_list:
        bot.answer_callback_query(call.id, "⚠️ Dosya yüklenmemiş.", show_alert=True)
        try:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Ana Menüye Dön", callback_data='back_to_main'))
            bot.edit_message_text("📂 Dosyalarınız:\n\n(Henüz dosya yüklenmemiş)", chat_id, call.message.message_id, reply_markup=markup)
        except Exception as e: logger.error(f"Boş dosya listesi için mesaj düzenleme hatası: {e}")
        return
    bot.answer_callback_query(call.id) 
    markup = types.InlineKeyboardMarkup(row_width=1) 
    for file_name, file_type in sorted(user_files_list): 
        is_running = is_bot_running(user_id, os.path.basename(file_name))
        status_icon = "🟢 Çalışıyor" if is_running else "🔴 Durduruldu"
        btn_text = f"{file_name} ({file_type}) - {status_icon}"
        markup.add(types.InlineKeyboardButton(btn_text, callback_data=f'file_{user_id}_{file_name}'))
    markup.add(types.InlineKeyboardButton("🔙 Ana Menüye Dön", callback_data='back_to_main'))
    try:
        bot.edit_message_text("📂 Dosyalarınız:\nYönetmek için tıklayın.", chat_id, call.message.message_id, reply_markup=markup, parse_mode='Markdown')
    except telebot.apihelper.ApiTelegramException as e:
         if "message is not modified" in str(e): logger.warning("Mesaj değiştirilmedi (dosyalar).")
         else: logger.error(f"Dosya listesi için mesaj düzenleme hatası: {e}")
    except Exception as e: logger.error(f"Dosya listesi için mesaj düzenlemede beklenmeyen hata: {e}", exc_info=True)

def file_control_callback(call):
    try:
        _, script_owner_id_str, file_name = call.data.split('_', 2); file_name = os.path.basename(file_name)
        script_owner_id = int(script_owner_id_str)
        requesting_user_id = call.from_user.id

        if not (requesting_user_id == script_owner_id or requesting_user_id in admin_ids):
            logger.warning(f"Kullanıcı {requesting_user_id}, {script_owner_id} kullanıcısının '{file_name}' dosyasına izinsiz erişmeye çalıştı.")
            bot.answer_callback_query(call.id, "⚠️ Sadece kendi dosyalarınızı yönetebilirsiniz.", show_alert=True)
            check_files_callback(call)
            return

        user_files_list = user_files.get(script_owner_id, [])
        if not any(f[0] == file_name for f in user_files_list):
            logger.warning(f"Kontrol sırasında {script_owner_id} kullanıcısı için '{file_name}' dosyası bulunamadı.")
            bot.answer_callback_query(call.id, "⚠️ Dosya bulunamadı.", show_alert=True)
            check_files_callback(call) 
            return

        bot.answer_callback_query(call.id) 
        is_running = is_bot_running(script_owner_id, file_name)
        status_text = '🟢 Çalışıyor' if is_running else '🔴 Durduruldu'
        file_type = next((f[1] for f in user_files_list if f[0] == file_name), '?') 
        try:
            bot.edit_message_text(
                f"⚙️ Kontroller: `{file_name}` ({file_type}) (Kullanıcı: `{script_owner_id}`)\nDurum: {status_text}",
                call.message.chat.id, call.message.message_id,
                reply_markup=create_control_buttons(script_owner_id, file_name, is_running),
                parse_mode='Markdown'
            )
        except telebot.apihelper.ApiTelegramException as e:
             if "message is not modified" in str(e): logger.warning(f"{file_name} için kontroller mesajı değiştirilmedi")
             else: raise 
    except (ValueError, IndexError) as ve:
        logger.error(f"Dosya kontrol callback ayrıştırma hatası: {ve}. Veri: '{call.data}'")
        bot.answer_callback_query(call.id, "Hata: Geçersiz işlem verisi.", show_alert=True)
    except Exception as e:
        logger.error(f"'{call.data}' verisi için file_control_callback hatası: {e}", exc_info=True)
        bot.answer_callback_query(call.id, "Bir hata oluştu.", show_alert=True)

def start_bot_callback(call):
    try:
        _, script_owner_id_str, file_name = call.data.split('_', 2); file_name = os.path.basename(file_name)
        script_owner_id = int(script_owner_id_str)
        requesting_user_id = call.from_user.id
        chat_id_for_reply = call.message.chat.id

        logger.info(f"Başlatma isteği: İsteyen={requesting_user_id}, Sahip={script_owner_id}, Dosya='{file_name}'")

        if not (requesting_user_id == script_owner_id or requesting_user_id in admin_ids):
            bot.answer_callback_query(call.id, "⚠️ Bu betiği başlatma izniniz yok.", show_alert=True); return

        user_files_list = user_files.get(script_owner_id, [])
        file_info = next((f for f in user_files_list if f[0] == file_name), None)
        if not file_info:
            bot.answer_callback_query(call.id, "⚠️ Dosya bulunamadı.", show_alert=True); check_files_callback(call); return

        file_type = file_info[1]
        user_folder = get_user_folder(script_owner_id)
        file_path = os.path.join(user_folder, file_name)

        if not os.path.exists(file_path):
            bot.answer_callback_query(call.id, f"⚠️ Hata: `{file_name}` dosyası eksik! Yeniden yükleyin.", show_alert=True)
            remove_user_file_db(script_owner_id, file_name); check_files_callback(call); return

        if is_bot_running(script_owner_id, file_name):
            bot.answer_callback_query(call.id, f"⚠️ '{file_name}' betiği zaten çalışıyor.", show_alert=True)
            try: bot.edit_message_reply_markup(chat_id_for_reply, call.message.message_id, reply_markup=create_control_buttons(script_owner_id, file_name, True))
            except Exception as e: logger.error(f"Buton güncelleme hatası (zaten çalışıyor): {e}")
            return

        bot.answer_callback_query(call.id, f"⏳ {file_name} başlatılıyor (kullanıcı {script_owner_id})...")

        if file_type == 'py':
            threading.Thread(target=run_script, args=(file_path, script_owner_id, user_folder, file_name, call.message)).start()
        elif file_type == 'js':
            threading.Thread(target=run_js_script, args=(file_path, script_owner_id, user_folder, file_name, call.message)).start()
        else:
             bot.send_message(chat_id_for_reply, f"❌ Hata: '{file_name}' için bilinmeyen dosya türü '{file_type}'."); return 

        time.sleep(1.5)
        is_now_running = is_bot_running(script_owner_id, file_name) 
        status_text = '🟢 Çalışıyor' if is_now_running else '🟡 Başlatılıyor (veya başarısız, logları/repleri kontrol edin)'
        try:
            bot.edit_message_text(
                f"⚙️ Kontroller: `{file_name}` ({file_type}) (Kullanıcı: `{script_owner_id}`)\nDurum: {status_text}",
                chat_id_for_reply, call.message.message_id,
                reply_markup=create_control_buttons(script_owner_id, file_name, is_now_running), parse_mode='Markdown'
            )
        except telebot.apihelper.ApiTelegramException as e:
             if "message is not modified" in str(e): logger.warning(f"{file_name} başlatıldıktan sonra mesaj değiştirilmedi")
             else: raise
    except (ValueError, IndexError) as e:
        logger.error(f"Başlatma callback ayrıştırma hatası '{call.data}': {e}")
        bot.answer_callback_query(call.id, "Hata: Geçersiz başlatma komutu.", show_alert=True)
    except Exception as e:
        logger.error(f"start_bot_callback için '{call.data}' hatası: {e}", exc_info=True)
        bot.answer_callback_query(call.id, "Betik başlatma hatası.", show_alert=True)
        try:
            _, script_owner_id_err_str, file_name_err = call.data.split('_', 2)
            script_owner_id_err = int(script_owner_id_err_str)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=create_control_buttons(script_owner_id_err, file_name_err, False))
        except Exception as e_btn: logger.error(f"Başlatma hatası sonrası buton güncelleme başarısız: {e_btn}")

def stop_bot_callback(call):
    try:
        _, script_owner_id_str, file_name = call.data.split('_', 2); file_name = os.path.basename(file_name)
        script_owner_id = int(script_owner_id_str)
        requesting_user_id = call.from_user.id
        chat_id_for_reply = call.message.chat.id

        logger.info(f"Durdurma isteği: İsteyen={requesting_user_id}, Sahip={script_owner_id}, Dosya='{file_name}'")
        if not (requesting_user_id == script_owner_id or requesting_user_id in admin_ids):
            bot.answer_callback_query(call.id, "⚠️ İzin reddedildi.", show_alert=True); return

        user_files_list = user_files.get(script_owner_id, [])
        file_info = next((f for f in user_files_list if f[0] == file_name), None)
        if not file_info:
            bot.answer_callback_query(call.id, "⚠️ Dosya bulunamadı.", show_alert=True); check_files_callback(call); return

        file_type = file_info[1] 
        script_key = f"{script_owner_id}_{file_name}"

        if not is_bot_running(script_owner_id, file_name): 
            bot.answer_callback_query(call.id, f"⚠️ '{file_name}' betiği zaten durdurulmuş.", show_alert=True)
            try:
                 bot.edit_message_text(
                     f"⚙️ Kontroller: `{file_name}` ({file_type}) (Kullanıcı: `{script_owner_id}`)\nDurum: 🔴 Durduruldu",
                     chat_id_for_reply, call.message.message_id,
                     reply_markup=create_control_buttons(script_owner_id, file_name, False), parse_mode='Markdown')
            except Exception as e: logger.error(f"Buton güncelleme hatası (zaten durdurulmuş): {e}")
            return

        bot.answer_callback_query(call.id, f"⏳ {file_name} durduruluyor (kullanıcı {script_owner_id})...")
        process_info = bot_scripts.get(script_key)
        if process_info:
            kill_process_tree(process_info)
            if script_key in bot_scripts: del bot_scripts[script_key]; logger.info(f"Durdurma sonrası {script_key} çalışanlardan kaldırıldı.")
        else: logger.warning(f"{script_key} psutil tarafından çalışıyor görünüyor ancak bot_scripts sözlüğünde yok.")

        try:
            bot.edit_message_text(
                f"⚙️ Kontroller: `{file_name}` ({file_type}) (Kullanıcı: `{script_owner_id}`)\nDurum: 🔴 Durduruldu",
                chat_id_for_reply, call.message.message_id,
                reply_markup=create_control_buttons(script_owner_id, file_name, False), parse_mode='Markdown'
            )
        except telebot.apihelper.ApiTelegramException as e:
             if "message is not modified" in str(e): logger.warning(f"{file_name} durdurulduktan sonra mesaj değiştirilmedi")
             else: raise
    except (ValueError, IndexError) as e:
        logger.error(f"Durdurma callback ayrıştırma hatası '{call.data}': {e}")
        bot.answer_callback_query(call.id, "Hata: Geçersiz durdurma komutu.", show_alert=True)
    except Exception as e:
        logger.error(f"stop_bot_callback için '{call.data}' hatası: {e}", exc_info=True)
        bot.answer_callback_query(call.id, "Betik durdurma hatası.", show_alert=True)

def restart_bot_callback(call):
    try:
        _, script_owner_id_str, file_name = call.data.split('_', 2); file_name = os.path.basename(file_name)
        script_owner_id = int(script_owner_id_str)
        requesting_user_id = call.from_user.id
        chat_id_for_reply = call.message.chat.id

        logger.info(f"Yeniden başlatma: İsteyen={requesting_user_id}, Sahip={script_owner_id}, Dosya='{file_name}'")
        if not (requesting_user_id == script_owner_id or requesting_user_id in admin_ids):
            bot.answer_callback_query(call.id, "⚠️ İzin reddedildi.", show_alert=True); return

        user_files_list = user_files.get(script_owner_id, [])
        file_info = next((f for f in user_files_list if f[0] == file_name), None)
        if not file_info:
            bot.answer_callback_query(call.id, "⚠️ Dosya bulunamadı.", show_alert=True); check_files_callback(call); return

        file_type = file_info[1]; user_folder = get_user_folder(script_owner_id)
        file_path = os.path.join(user_folder, file_name); script_key = f"{script_owner_id}_{file_name}"

        if not os.path.exists(file_path):
            bot.answer_callback_query(call.id, f"⚠️ Hata: `{file_name}` dosyası eksik! Yeniden yükleyin.", show_alert=True)
            remove_user_file_db(script_owner_id, file_name)
            if script_key in bot_scripts: del bot_scripts[script_key]
            check_files_callback(call); return

        bot.answer_callback_query(call.id, f"⏳ {file_name} yeniden başlatılıyor (kullanıcı {script_owner_id})...")
        if is_bot_running(script_owner_id, file_name):
            logger.info(f"Yeniden başlatma: Mevcut {script_key} durduruluyor...")
            process_info = bot_scripts.get(script_key)
            if process_info: kill_process_tree(process_info)
            if script_key in bot_scripts: del bot_scripts[script_key]
            time.sleep(1.5) 

        logger.info(f"Yeniden başlatma: {script_key} betiği başlatılıyor...")
        if file_type == 'py':
            threading.Thread(target=run_script, args=(file_path, script_owner_id, user_folder, file_name, call.message)).start()
        elif file_type == 'js':
            threading.Thread(target=run_js_script, args=(file_path, script_owner_id, user_folder, file_name, call.message)).start()
        else:
             bot.send_message(chat_id_for_reply, f"❌ '{file_name}' için bilinmeyen tür '{file_type}'."); return

        time.sleep(1.5) 
        is_now_running = is_bot_running(script_owner_id, file_name) 
        status_text = '🟢 Çalışıyor' if is_now_running else '🟡 Başlatılıyor (veya başarısız)'
        try:
            bot.edit_message_text(
                f"⚙️ Kontroller: `{file_name}` ({file_type}) (Kullanıcı: `{script_owner_id}`)\nDurum: {status_text}",
                chat_id_for_reply, call.message.message_id,
                reply_markup=create_control_buttons(script_owner_id, file_name, is_now_running), parse_mode='Markdown'
            )
        except telebot.apihelper.ApiTelegramException as e:
             if "message is not modified" in str(e): logger.warning(f"{file_name} yeniden başlatma sonrası mesaj değiştirilmedi")
             else: raise
    except (ValueError, IndexError) as e:
        logger.error(f"Yeniden başlatma callback ayrıştırma hatası '{call.data}': {e}")
        bot.answer_callback_query(call.id, "Hata: Geçersiz yeniden başlatma komutu.", show_alert=True)
    except Exception as e:
        logger.error(f"restart_bot_callback için '{call.data}' hatası: {e}", exc_info=True)
        bot.answer_callback_query(call.id, "Yeniden başlatma hatası.", show_alert=True)
        try:
            _, script_owner_id_err_str, file_name_err = call.data.split('_', 2)
            script_owner_id_err = int(script_owner_id_err_str)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=create_control_buttons(script_owner_id_err, file_name_err, False))
        except Exception as e_btn: logger.error(f"Yeniden başlatma hatası sonrası buton güncelleme başarısız: {e_btn}")

def delete_bot_callback(call):
    try:
        _, script_owner_id_str, file_name = call.data.split('_', 2); file_name = os.path.basename(file_name)
        script_owner_id = int(script_owner_id_str)
        requesting_user_id = call.from_user.id
        chat_id_for_reply = call.message.chat.id

        logger.info(f"Silme: İsteyen={requesting_user_id}, Sahip={script_owner_id}, Dosya='{file_name}'")
        if not (requesting_user_id == script_owner_id or requesting_user_id in admin_ids):
            bot.answer_callback_query(call.id, "⚠️ İzin reddedildi.", show_alert=True); return

        user_files_list = user_files.get(script_owner_id, [])
        if not any(f[0] == file_name for f in user_files_list):
            bot.answer_callback_query(call.id, "⚠️ Dosya bulunamadı.", show_alert=True); check_files_callback(call); return

        bot.answer_callback_query(call.id, f"🗑️ {file_name} siliniyor (kullanıcı {script_owner_id})...")
        script_key = f"{script_owner_id}_{file_name}"
        if is_bot_running(script_owner_id, file_name):
            logger.info(f"Silme: {script_key} durduruluyor...")
            process_info = bot_scripts.get(script_key)
            if process_info: kill_process_tree(process_info)
            if script_key in bot_scripts: del bot_scripts[script_key]
            time.sleep(0.5) 

        user_folder = get_user_folder(script_owner_id)
        file_path = os.path.join(user_folder, file_name)
        log_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        deleted_disk = []
        if os.path.exists(file_path):
            try: os.remove(file_path); deleted_disk.append(file_name); logger.info(f"Dosya silindi: {file_path}")
            except OSError as e: logger.error(f"{file_path} silinirken hata: {e}")
        if os.path.exists(log_path):
            try: os.remove(log_path); deleted_disk.append(os.path.basename(log_path)); logger.info(f"Log silindi: {log_path}")
            except OSError as e: logger.error(f"Log {log_path} silinirken hata: {e}")

        remove_user_file_db(script_owner_id, file_name)
        deleted_str = ", ".join(f"`{f}`" for f in deleted_disk) if deleted_disk else "ilişkili dosyalar"
        try:
            bot.edit_message_text(
                f"🗑️ `{file_name}` kaydı (Kullanıcı `{script_owner_id}`) ve {deleted_str} silindi!",
                chat_id_for_reply, call.message.message_id, reply_markup=None, parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Silme sonrası mesaj düzenleme hatası: {e}")
            bot.send_message(chat_id_for_reply, f"🗑️ `{file_name}` kaydı silindi.", parse_mode='Markdown')
    except (ValueError, IndexError) as e:
        logger.error(f"Silme callback ayrıştırma hatası '{call.data}': {e}")
        bot.answer_callback_query(call.id, "Hata: Geçersiz silme komutu.", show_alert=True)
    except Exception as e:
        logger.error(f"delete_bot_callback için '{call.data}' hatası: {e}", exc_info=True)
        bot.answer_callback_query(call.id, "Silme hatası.", show_alert=True)

def logs_bot_callback(call):
    try:
        _, script_owner_id_str, file_name = call.data.split('_', 2); file_name = os.path.basename(file_name)
        script_owner_id = int(script_owner_id_str)
        requesting_user_id = call.from_user.id
        chat_id_for_reply = call.message.chat.id

        logger.info(f"Loglar: İsteyen={requesting_user_id}, Sahip={script_owner_id}, Dosya='{file_name}'")
        if not (requesting_user_id == script_owner_id or requesting_user_id in admin_ids):
            bot.answer_callback_query(call.id, "⚠️ İzin reddedildi.", show_alert=True); return

        user_files_list = user_files.get(script_owner_id, [])
        if not any(f[0] == file_name for f in user_files_list):
            bot.answer_callback_query(call.id, "⚠️ Dosya bulunamadı.", show_alert=True); check_files_callback(call); return

        user_folder = get_user_folder(script_owner_id)
        log_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        if not os.path.exists(log_path):
            bot.answer_callback_query(call.id, f"⚠️ '{file_name}' için log yok.", show_alert=True); return

        bot.answer_callback_query(call.id) 
        try:
            log_content = ""; file_size = os.path.getsize(log_path)
            max_log_kb = 100; max_tg_msg = 4096
            if file_size == 0: log_content = "(Log boş)"
            elif file_size > max_log_kb * 1024:
                 with open(log_path, 'rb') as f: f.seek(-max_log_kb * 1024, os.SEEK_END); log_bytes = f.read()
                 log_content = log_bytes.decode('utf-8', errors='ignore')
                 log_content = f"(Son {max_log_kb} KB)\n...\n" + log_content
            else:
                 with open(log_path, 'r', encoding='utf-8', errors='ignore') as f: log_content = f.read()

            if len(log_content) > max_tg_msg:
                log_content = log_content[-max_tg_msg:]
                first_nl = log_content.find('\n')
                if first_nl != -1: log_content = "...\n" + log_content[first_nl+1:]
                else: log_content = "...\n" + log_content 
            if not log_content.strip(): log_content = "(Görünür içerik yok)"

            bot.send_message(chat_id_for_reply, f"📜 `{file_name}` için loglar (Kullanıcı `{script_owner_id}`):\n```\n{log_content}\n```", parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Log {log_path} okuma/gönderme hatası: {e}", exc_info=True)
            bot.send_message(chat_id_for_reply, f"❌ `{file_name}` için log okunurken hata oluştu.")
    except (ValueError, IndexError) as e:
        logger.error(f"Loglar callback ayrıştırma hatası '{call.data}': {e}")
        bot.answer_callback_query(call.id, "Hata: Geçersiz loglar komutu.", show_alert=True)
    except Exception as e:
        logger.error(f"logs_bot_callback için '{call.data}' hatası: {e}", exc_info=True)
        bot.answer_callback_query(call.id, "Loglar alınırken hata.", show_alert=True)

def speed_callback(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    start_cb_ping_time = time.time() 
    try:
        bot.edit_message_text("🏃 Hız test ediliyor...", chat_id, call.message.message_id)
        bot.send_chat_action(chat_id, 'typing') 
        response_time = round((time.time() - start_cb_ping_time) * 1000, 2)
        status = "🔓 Kilit Açık" if not bot_locked else "🔒 Kilitli"
        if user_id == OWNER_ID: user_level = "👑 Sahip"
        elif user_id in admin_ids: user_level = "🛡️ Yönetici"
        elif user_id in user_subscriptions and user_subscriptions[user_id].get('expiry', datetime.min) > datetime.now(): user_level = "⭐ Premium"
        else: user_level = "🆓 Ücretsiz Kullanıcı"
        speed_msg = (f"⚡ Bot Hızı ve Durumu:\n\n⏱️ API Yanıt Süresi: {response_time} ms\n"
                     f"🚦 Bot Durumu: {status}\n"
                     f"👤 Seviyeniz: {user_level}")
        bot.answer_callback_query(call.id) 
        bot.edit_message_text(speed_msg, chat_id, call.message.message_id, reply_markup=create_main_menu_inline(user_id))
    except Exception as e:
         logger.error(f"Hız testi sırasında hata (cb): {e}", exc_info=True)
         bot.answer_callback_query(call.id, "Hız testinde hata oluştu.", show_alert=True)
         try: bot.edit_message_text("〽️ Ana Menü", chat_id, call.message.message_id, reply_markup=create_main_menu_inline(user_id))
         except Exception: pass

def back_to_main_callback(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    limit_str = str(file_limit) if file_limit != float('inf') else "Sınırsız"
    expiry_info = ""
    if user_id == OWNER_ID: user_status = "👑 Sahip"
    elif user_id in admin_ids: user_status = "🛡️ Yönetici"
    elif user_id in user_subscriptions:
        expiry_date = user_subscriptions[user_id].get('expiry')
        if expiry_date and expiry_date > datetime.now():
            user_status = "⭐ Premium"
            remaining_str = format_remaining_time(expiry_date)
            expiry_info = f"\n⏳ Abonelik bitiş: {expiry_date.strftime('%Y-%m-%d %H:%M')} ({remaining_str} kaldı)"
        else: user_status = "🆓 Ücretsiz Kullanıcı (Süresi Dolmuş)"
    else: user_status = "🆓 Ücretsiz Kullanıcı"
    main_menu_text = (f"〽️ Tekrar hoş geldin, {call.from_user.first_name}!\n\n🆔 ID: `{user_id}`\n"
                      f"🔰 Durum: {user_status}{expiry_info}\n📁 Dosyalar: {current_files} / {limit_str}\n\n"
                      f"👇 Butonları kullanın veya komut yazın.")
    try:
        bot.answer_callback_query(call.id)
        bot.edit_message_text(main_menu_text, chat_id, call.message.message_id,
                              reply_markup=create_main_menu_inline(user_id), parse_mode='Markdown')
    except telebot.apihelper.ApiTelegramException as e:
         if "message is not modified" in str(e): logger.warning("Mesaj değiştirilmedi (ana menüye dön).")
         else: logger.error(f"ana menüye dön API hatası: {e}")
    except Exception as e: logger.error(f"ana menüye dön işlenirken hata: {e}", exc_info=True)

                                        
def subscription_management_callback(call):
    bot.answer_callback_query(call.id)
    try:
        bot.edit_message_text("💳 Abonelik Yönetimi\nİşlem seçin:",
                              call.message.chat.id, call.message.message_id, reply_markup=create_subscription_menu())
    except Exception as e: logger.error(f"Abonelik menüsü gösterilirken hata: {e}")

def stats_callback(call):
    bot.answer_callback_query(call.id)
    _logic_statistics(call.message)
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                      reply_markup=create_main_menu_inline(call.from_user.id))
    except Exception as e:
        logger.error(f"stats_callback sonrası menü güncelleme hatası: {e}")

def lock_bot_callback(call):
    global bot_locked; bot_locked = True
    logger.warning(f"Bot Yönetici {call.from_user.id} tarafından kilitlendi")
    bot.answer_callback_query(call.id, "🔒 Bot kilitlendi.")
    try: bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=create_main_menu_inline(call.from_user.id))
    except Exception as e: logger.error(f"Menü güncelleme hatası (kilit): {e}")

def unlock_bot_callback(call):
    global bot_locked; bot_locked = False
    logger.warning(f"Bot Yönetici {call.from_user.id} tarafından kilidi açıldı")
    bot.answer_callback_query(call.id, "🔓 Bot kilidi açıldı.")
    try: bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=create_main_menu_inline(call.from_user.id))
    except Exception as e: logger.error(f"Menü güncelleme hatası (kilit açma): {e}")

def run_all_scripts_callback(call):
    _logic_run_all_scripts(call)

                                 
def resmi_duyuru_init(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "⚠️ Yetkisiz."); return
    msg = bot.reply_to(message, "📢 Resmi duyuru mesajını yazın:\n/cancel ile iptal.")
    bot.register_next_step_handler(msg, resmi_duyuru_gonder)

def resmi_duyuru_gonder(message):
    user_id = message.from_user.id
    if user_id not in admin_ids: return
    if message.text and message.text.strip() == '/cancel':
        bot.reply_to(message, "İptal edildi."); return
    if not message.text:
        msg = bot.reply_to(message, "⚠️ Metin girin veya /cancel.")
        bot.register_next_step_handler(msg, resmi_duyuru_gonder); return
    send_text = f"📢 *Duyuru*\n\n{message.text}"
    sent = 0
    for uid in list(active_users):
        try:
            bot.send_message(uid, send_text, parse_mode='Markdown')
            sent += 1
            import time as _t; _t.sleep(0.05)
        except Exception: pass
    bot.reply_to(message, f"✅ Resmi duyuru {sent} kullanıcıya gönderildi!")

                                     
def timer_button_handler(message):
    """Zamanlayıcı butonuna basılınca: kullanıcının dosyalarını listele"""
    user_id = message.from_user.id
    if is_banned(user_id): return

    files = user_files.get(user_id, [])
    if not files:
        bot.send_message(user_id,
            "❌ *Zamanlayıcı kurmak için önce bir dosya yüklemelisiniz.*\n\n"
            "Dosyanızı bu bota gönderin, ardından zamanlayıcı kurabilirsiniz.",
            parse_mode='Markdown')
        return

    markup = types.InlineKeyboardMarkup()
    for fname, ftype in files:
        markup.add(types.InlineKeyboardButton(
            f"📄 {fname}", callback_data=f"timer_file_{fname}"
        ))
    markup.add(types.InlineKeyboardButton("❌ İptal", callback_data="timer_cancel"))

    bot.send_message(user_id,
        "⏰ *Zamanlayıcı Kur*\n\nHangi dosya için zamanlayıcı kurmak istiyorsunuz?",
        reply_markup=markup, parse_mode='Markdown')

def timer_file_selected_callback(call):
    """Dosya seçildi — start/stop sor"""
    fname = call.data.replace('timer_file_', '', 1)
    bot.answer_callback_query(call.id)
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("🟢 Başlat (start)", callback_data=f"timer_action_{fname}_start"),
        types.InlineKeyboardButton("🔴 Durdur (stop)",  callback_data=f"timer_action_{fname}_stop")
    )
    markup.add(types.InlineKeyboardButton("❌ İptal", callback_data="timer_cancel"))
    bot.edit_message_text(
        f"⏰ *{fname}* için ne yapmak istiyorsunuz?",
        call.message.chat.id, call.message.message_id,
        reply_markup=markup, parse_mode='Markdown')

def timer_action_selected_callback(call):
    """Aksiyon seçildi — saat sor"""
                                                  
                                                              
    parts = call.data.replace('timer_action_', '', 1).rsplit('_', 1)
    fname = parts[0]
    action = parts[1]
    bot.answer_callback_query(call.id)
    action_tr = "🟢 Başlat" if action == 'start' else "🔴 Durdur"
    msg = bot.edit_message_text(
        f"⏰ *{fname}* — {action_tr}\n\n"
        f"Saat girin (örnek: `08:00`):",
        call.message.chat.id, call.message.message_id,
        parse_mode='Markdown')
                                      
    ask_msg = bot.send_message(call.message.chat.id,
        f"⌨️ Saati girin (SS:DD formatında, örnek: `08:00`):", parse_mode='Markdown')
    bot.register_next_step_handler(ask_msg, lambda m: timer_time_entered(m, fname, action))

def timer_time_entered(message, fname, action):
    """Saat girildi — zamanlayıcıyı kur"""
    user_id = message.from_user.id
    if is_banned(user_id): return
    if message.text and message.text.strip() == '/cancel':
        bot.reply_to(message, "İptal edildi."); return
    try:
        time_str = message.text.strip()
        if ':' not in time_str:
            raise ValueError("Saat SS:DD formatında olmalı")
        hour, minute = map(int, time_str.split(':'))
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError(f"Geçersiz saat: {time_str}")
    except (ValueError, AttributeError) as e:
        ask_msg = bot.reply_to(message, f"❌ {e}\n\nTekrar girin (örnek: `08:00`) veya /cancel:", parse_mode='Markdown')
        bot.register_next_step_handler(ask_msg, lambda m: timer_time_entered(m, fname, action))
        return

    task_id = f"{user_id}_{fname}_{action}"
    with _sched_lock:
        SCHEDULED_TASKS[task_id] = {
            'user_id': user_id, 'file_name': fname, 'action': action,
            'type': 'daily', 'hour': hour, 'minute': minute,
            'active': True, 'last_run': None, 'created': datetime.now().isoformat()
        }
    action_tr = '🟢 Başlat' if action == 'start' else '🔴 Durdur'
    logger.info(f"Zamanlayıcı kuruldu (buton): {task_id} @ {hour:02d}:{minute:02d}")
    bot.reply_to(message,
        f"✅ *Zamanlayıcı Kuruldu!*\n\n"
        f"📄 Dosya: `{fname}`\n"
        f"⚡ Aksiyon: {action_tr}\n"
        f"🕐 Saat: `{hour:02d}:{minute:02d}` (her gün)\n\n"
        f"📋 Görevlerim: /takvim\n"
        f"❌ İptal: `/schedule_cancel {fname} {action}`",
        parse_mode='Markdown')

                                          

def broadcast_init_callback(call):
    bot.answer_callback_query(call.id)
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("📢 Resmi Duyuru", callback_data='broadcast_type_resmi'),
        types.InlineKeyboardButton("💬 Normal Duyuru", callback_data='broadcast_type_normal')
    )
    markup.row(types.InlineKeyboardButton("❌ İptal", callback_data='cancel_broadcast'))
    bot.send_message(call.message.chat.id,
        "📢 *Duyuru türünü seçin:*\n\n"
        "📢 *Resmi* — Başında 'Duyuru' başlığı eklenir\n"
        "💬 *Normal* — Mesaj olduğu gibi gönderilir",
        reply_markup=markup, parse_mode='Markdown')

def broadcast_type_callback(call, btype):
    """Resmi veya normal seçildi — mesaj iste"""
    bot.answer_callback_query(call.id)
    label = "📢 Resmi Duyuru" if btype == 'resmi' else "💬 Normal Duyuru"
    msg = bot.send_message(call.message.chat.id,
        f"*{label}* seçildi.\n\nMesajı yazın ve gönderin:\n/cancel ile iptal.", parse_mode='Markdown')
    bot.register_next_step_handler(msg, lambda m: process_broadcast_message(m, btype))

def process_broadcast_message(message, btype='normal'):
    user_id = message.from_user.id
    if user_id not in admin_ids: bot.reply_to(message, "⚠️ Yetkili değil."); return
    if message.text and message.text.lower() == '/cancel': bot.reply_to(message, "Duyuru iptal edildi."); return

    broadcast_content = message.text
    if not broadcast_content and not (message.photo or message.video or message.document or message.sticker or message.voice or message.audio):
         bot.reply_to(message, "⚠️ Boş mesaj duyurulamaz. Metin veya medya gönderin, veya /cancel.")
         msg = bot.send_message(message.chat.id, "📢 Duyuru mesajını gönderin veya /cancel.")
         bot.register_next_step_handler(msg, lambda m: process_broadcast_message(m, btype))
         return

                                
    if btype == 'resmi' and broadcast_content:
        broadcast_content = f"📢 *Duyuru*\n\n{broadcast_content}"

    target_count = len(active_users)
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("✅ Onayla ve Gönder", callback_data=f"confirm_broadcast_{message.message_id}"),
               types.InlineKeyboardButton("❌ İptal", callback_data="cancel_broadcast"))

    type_label = "📢 Resmi" if btype == 'resmi' else "💬 Normal"
    preview_text = broadcast_content[:1000].strip() if broadcast_content else "(Medya mesajı)"
    bot.reply_to(message, f"⚠️ Duyuruyu Onaylayın ({type_label}):\n\n```\n{preview_text}\n```\n"
                          f"*{target_count}* kullanıcıya gönderilecek. Emin misiniz?", reply_markup=markup, parse_mode='Markdown')

def handle_confirm_broadcast(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    if user_id not in admin_ids: bot.answer_callback_query(call.id, "⚠️ Sadece yönetici.", show_alert=True); return
    try:
        original_message = call.message.reply_to_message
        if not original_message: raise ValueError("Orijinal mesaj alınamadı.")

        broadcast_text = None
        broadcast_photo_id = None
        broadcast_video_id = None

        if original_message.text:
            broadcast_text = original_message.text
        elif original_message.photo:
            broadcast_photo_id = original_message.photo[-1].file_id
        elif original_message.video:
            broadcast_video_id = original_message.video.file_id
        else:
            raise ValueError("Duyuru için mesajda metin veya desteklenen medya yok.")

        bot.answer_callback_query(call.id, "🚀 Duyuru başlatılıyor...")
        bot.edit_message_text(f"📢 {len(active_users)} kullanıcıya duyuru yapılıyor...",
                              chat_id, call.message.message_id, reply_markup=None)
        thread = threading.Thread(target=execute_broadcast, args=(
            broadcast_text, broadcast_photo_id, broadcast_video_id, 
            original_message.caption if (broadcast_photo_id or broadcast_video_id) else None,
            chat_id))
        thread.start()
    except ValueError as ve: 
        logger.error(f"Duyuru onayı için mesaj alınırken hata: {ve}")
        bot.edit_message_text(f"❌ Duyuru başlatma hatası: {ve}", chat_id, call.message.message_id, reply_markup=None)
    except Exception as e:
        logger.error(f"handle_confirm_broadcast hatası: {e}", exc_info=True)
        bot.edit_message_text("❌ Duyuru onayı sırasında beklenmeyen hata.", chat_id, call.message.message_id, reply_markup=None)

def handle_cancel_broadcast(call):
    bot.answer_callback_query(call.id, "Duyuru iptal edildi.")
    bot.delete_message(call.message.chat.id, call.message.message_id)
    if call.message.reply_to_message:
        try: bot.delete_message(call.message.chat.id, call.message.reply_to_message.message_id)
        except: pass

def execute_broadcast(broadcast_text, photo_id, video_id, caption, admin_chat_id):
    sent_count = 0; failed_count = 0; blocked_count = 0
    start_exec_time = time.time() 
    users_to_broadcast = list(active_users); total_users = len(users_to_broadcast)
    logger.info(f"{total_users} kullanıcıya duyuru yapılıyor.")
    batch_size = 25; delay_batches = 1.5

    for i, user_id_bc in enumerate(users_to_broadcast):
        try:
            if broadcast_text:
                bot.send_message(user_id_bc, broadcast_text, parse_mode='Markdown')
            elif photo_id:
                bot.send_photo(user_id_bc, photo_id, caption=caption, parse_mode='Markdown' if caption else None)
            elif video_id:
                bot.send_video(user_id_bc, video_id, caption=caption, parse_mode='Markdown' if caption else None)
            sent_count += 1
        except telebot.apihelper.ApiTelegramException as e:
            err_desc = str(e).lower()
            if any(s in err_desc for s in ["bot was blocked", "user is deactivated", "chat not found", "kicked from", "restricted"]): 
                logger.warning(f"{user_id_bc} adresine duyuru başarısız: Kullanıcı engellemiş/aktif değil.")
                blocked_count += 1
            elif "flood control" in err_desc or "too many requests" in err_desc:
                retry_after = 5; match = re.search(r"retry after (\d+)", err_desc)
                if match: retry_after = int(match.group(1)) + 1 
                logger.warning(f"Flood kontrolü. {retry_after}s bekleniyor...")
                time.sleep(retry_after)
                try:
                    if broadcast_text: bot.send_message(user_id_bc, broadcast_text, parse_mode='Markdown')
                    elif photo_id: bot.send_photo(user_id_bc, photo_id, caption=caption, parse_mode='Markdown' if caption else None)
                    elif video_id: bot.send_video(user_id_bc, video_id, caption=caption, parse_mode='Markdown' if caption else None)
                    sent_count += 1
                except Exception as e_retry: logger.error(f"{user_id_bc} adresine duyuru yeniden denemesi başarısız: {e_retry}"); failed_count +=1
            else: logger.error(f"{user_id_bc} adresine duyuru başarısız: {e}"); failed_count += 1
        except Exception as e: logger.error(f"{user_id_bc} adresine duyuru yapılırken beklenmeyen hata: {e}"); failed_count += 1

        if (i + 1) % batch_size == 0 and i < total_users - 1:
            logger.info(f"Duyuru partisi {i//batch_size + 1} gönderildi. {delay_batches}s bekleniyor...")
            time.sleep(delay_batches)
        elif i % 5 == 0: time.sleep(0.2) 

    duration = round(time.time() - start_exec_time, 2)
    result_msg = (f"📢 Duyuru Tamamlandı!\n\n✅ Gönderilen: {sent_count}\n❌ Başarısız: {failed_count}\n"
                  f"🚫 Engellenen/Aktif Olmayan: {blocked_count}\n👥 Hedef: {total_users}\n⏱️ Süre: {duration}s")
    logger.info(result_msg)
    try: bot.send_message(admin_chat_id, result_msg)
    except Exception as e: logger.error(f"Duyuru sonucu yöneticiye {admin_chat_id} gönderilemedi: {e}")

def admin_panel_callback(call):
    bot.answer_callback_query(call.id)
    try:
        bot.edit_message_text("👑 Yönetici Paneli\nYöneticileri yönetin (Sahip işlemleri kısıtlı olabilir).",
                              call.message.chat.id, call.message.message_id, reply_markup=create_admin_panel())
    except Exception as e: logger.error(f"Yönetici paneli gösterilirken hata: {e}")

def add_admin_init_callback(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "👑 Yönetici yapılacak Kullanıcı ID'sini girin.\n/cancel ile iptal edin.")
    bot.register_next_step_handler(msg, process_add_admin_id)

def process_add_admin_id(message):
    owner_id_check = message.from_user.id 
    if owner_id_check != OWNER_ID: bot.reply_to(message, "⚠️ Sadece sahip."); return
    if message.text.lower() == '/cancel': bot.reply_to(message, "Yönetici ekleme iptal edildi."); return
    try:
        new_admin_id = int(message.text.strip())
        if new_admin_id <= 0: raise ValueError("ID pozitif olmalı")
        if new_admin_id == OWNER_ID: bot.reply_to(message, "⚠️ Sahip zaten sahiptir."); return
        if new_admin_id in admin_ids: bot.reply_to(message, f"⚠️ Kullanıcı `{new_admin_id}` zaten yönetici."); return
        add_admin_db(new_admin_id) 
        logger.warning(f"Yönetici {new_admin_id} Sahip {owner_id_check} tarafından eklendi.")
        bot.reply_to(message, f"✅ Kullanıcı `{new_admin_id}` yönetici yapıldı.")
        try: bot.send_message(new_admin_id, "🎉 Tebrikler! Artık yöneticisiniz.")
        except Exception as e: logger.error(f"Yeni yönetici {new_admin_id} bilgilendirilemedi: {e}")
    except ValueError:
        bot.reply_to(message, "⚠️ Geçersiz ID. Sayısal ID girin veya /cancel.")
        msg = bot.send_message(message.chat.id, "👑 Yönetici yapılacak Kullanıcı ID'sini girin veya /cancel.")
        bot.register_next_step_handler(msg, process_add_admin_id)
    except Exception as e: logger.error(f"Yönetici ekleme işlenirken hata: {e}", exc_info=True); bot.reply_to(message, "Hata.")

def remove_admin_init_callback(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "👑 Kaldırılacak Yönetici Kullanıcı ID'sini girin.\n/cancel ile iptal edin.")
    bot.register_next_step_handler(msg, process_remove_admin_id)

def process_remove_admin_id(message):
    owner_id_check = message.from_user.id
    if owner_id_check != OWNER_ID: bot.reply_to(message, "⚠️ Sadece sahip."); return
    if message.text.lower() == '/cancel': bot.reply_to(message, "Yönetici kaldırma iptal edildi."); return
    try:
        admin_id_remove = int(message.text.strip())
        if admin_id_remove <= 0: raise ValueError("ID pozitif olmalı")
        if admin_id_remove == OWNER_ID: bot.reply_to(message, "⚠️ Sahip kendini kaldıramaz."); return
        if admin_id_remove not in admin_ids: bot.reply_to(message, f"⚠️ Kullanıcı `{admin_id_remove}` yönetici değil."); return
        if remove_admin_db(admin_id_remove): 
            logger.warning(f"Yönetici {admin_id_remove} Sahip {owner_id_check} tarafından kaldırıldı.")
            bot.reply_to(message, f"✅ Yönetici `{admin_id_remove}` kaldırıldı.")
            try: bot.send_message(admin_id_remove, "ℹ️ Artık yönetici değilsiniz.")
            except Exception as e: logger.error(f"Kaldırılan yönetici {admin_id_remove} bilgilendirilemedi: {e}")
        else: bot.reply_to(message, f"❌ Yönetici `{admin_id_remove}` kaldırılamadı. Logları kontrol edin.")
    except ValueError:
        bot.reply_to(message, "⚠️ Geçersiz ID. Sayısal ID girin veya /cancel.")
        msg = bot.send_message(message.chat.id, "👑 Kaldırılacak Yönetici ID'sini girin veya /cancel.")
        bot.register_next_step_handler(msg, process_remove_admin_id)
    except Exception as e: logger.error(f"Yönetici kaldırma işlenirken hata: {e}", exc_info=True); bot.reply_to(message, "Hata.")

def list_admins_callback(call):
    bot.answer_callback_query(call.id)
    try:
        admin_list_str = "\n".join(f"- `{aid}` {'(Sahip)' if aid == OWNER_ID else ''}" for aid in sorted(list(admin_ids)))
        if not admin_list_str: admin_list_str = "(Sahip/Yönetici yapılandırılmamış!)"
        bot.edit_message_text(f"👑 Mevcut Yöneticiler:\n\n{admin_list_str}", call.message.chat.id,
                              call.message.message_id, reply_markup=create_admin_panel(), parse_mode='Markdown')
    except Exception as e: logger.error(f"Yöneticiler listelenirken hata: {e}")

def add_subscription_init_callback(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "💳 Kullanıcı ID ve gün sayısını girin (örn: `12345678 30`).\n/cancel ile iptal edin.")
    bot.register_next_step_handler(msg, process_add_subscription_details)

def process_add_subscription_details(message):
    admin_id_check = message.from_user.id 
    if admin_id_check not in admin_ids: bot.reply_to(message, "⚠️ Yetkili değil."); return
    if message.text.lower() == '/cancel': bot.reply_to(message, "Abonelik ekleme iptal edildi."); return
    try:
        parts = message.text.split();
        if len(parts) != 2: raise ValueError("Yanlış format")
        sub_user_id = int(parts[0].strip()); days = int(parts[1].strip())
        if sub_user_id <= 0 or days <= 0: raise ValueError("Kullanıcı ID/gün sayısı pozitif olmalı")

        current_expiry = user_subscriptions.get(sub_user_id, {}).get('expiry')
        start_date_new_sub = datetime.now()
        if current_expiry and current_expiry > start_date_new_sub: start_date_new_sub = current_expiry
        new_expiry = start_date_new_sub + timedelta(days=days)
        save_subscription(sub_user_id, new_expiry)

        logger.info(f"{sub_user_id} için abonelik yönetici {admin_id_check} tarafından eklendi. Bitiş: {new_expiry:%Y-%m-%d}")
        bot.reply_to(message, f"✅ `{sub_user_id}` için {days} günlük abonelik eklendi.\nYeni bitiş: {new_expiry:%Y-%m-%d}")
        try: bot.send_message(sub_user_id, f"🎉 Aboneliğiniz {days} gün uzatıldı/eklendi! Bitiş: {new_expiry:%Y-%m-%d}.")
        except Exception as e: logger.error(f"{sub_user_id} kullanıcısına yeni abonelik bildirilemedi: {e}")
    except ValueError as e:
        bot.reply_to(message, f"⚠️ Geçersiz: {e}. Format: `ID gün` veya /cancel.")
        msg = bot.send_message(message.chat.id, "💳 Kullanıcı ID ve gün sayısını girin, veya /cancel.")
        bot.register_next_step_handler(msg, process_add_subscription_details)
    except Exception as e: logger.error(f"Abonelik ekleme işlenirken hata: {e}", exc_info=True); bot.reply_to(message, "Hata.")

def remove_subscription_init_callback(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "💳 Aboneliği kaldırılacak Kullanıcı ID'sini girin.\n/cancel ile iptal edin.")
    bot.register_next_step_handler(msg, process_remove_subscription_id)

def process_remove_subscription_id(message):
    admin_id_check = message.from_user.id
    if admin_id_check not in admin_ids: bot.reply_to(message, "⚠️ Yetkili değil."); return
    if message.text.lower() == '/cancel': bot.reply_to(message, "Abonelik kaldırma iptal edildi."); return
    try:
        sub_user_id_remove = int(message.text.strip())
        if sub_user_id_remove <= 0: raise ValueError("ID pozitif olmalı")
        if sub_user_id_remove not in user_subscriptions:
            bot.reply_to(message, f"⚠️ Kullanıcı `{sub_user_id_remove}` için bellekte aktif abonelik yok."); return
        remove_subscription_db(sub_user_id_remove) 
        logger.warning(f"{sub_user_id_remove} için abonelik yönetici {admin_id_check} tarafından kaldırıldı.")
        bot.reply_to(message, f"✅ `{sub_user_id_remove}` için abonelik kaldırıldı.")
        try: bot.send_message(sub_user_id_remove, "ℹ️ Aboneliğiniz yönetici tarafından kaldırıldı.")
        except Exception as e: logger.error(f"{sub_user_id_remove} kullanıcısına abonelik kaldırma bildirilemedi: {e}")
    except ValueError:
        bot.reply_to(message, "⚠️ Geçersiz ID. Sayısal ID girin veya /cancel.")
        msg = bot.send_message(message.chat.id, "💳 Aboneliği kaldırılacak Kullanıcı ID'sini girin, veya /cancel.")
        bot.register_next_step_handler(msg, process_remove_subscription_id)
    except Exception as e: logger.error(f"Abonelik kaldırma işlenirken hata: {e}", exc_info=True); bot.reply_to(message, "Hata.")

def check_subscription_init_callback(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "💳 Aboneliği sorgulanacak Kullanıcı ID'sini girin.\n/cancel ile iptal edin.")
    bot.register_next_step_handler(msg, process_check_subscription_id)

def process_check_subscription_id(message):
    admin_id_check = message.from_user.id
    if admin_id_check not in admin_ids: bot.reply_to(message, "⚠️ Yetkili değil."); return
    if message.text.lower() == '/cancel': bot.reply_to(message, "Abonelik sorgulama iptal edildi."); return
    try:
        sub_user_id_check = int(message.text.strip())
        if sub_user_id_check <= 0: raise ValueError("ID pozitif olmalı")
        if sub_user_id_check in user_subscriptions:
            expiry_dt = user_subscriptions[sub_user_id_check].get('expiry')
            if expiry_dt:
                if expiry_dt > datetime.now():
                    remaining_str = format_remaining_time(expiry_dt)
                    bot.reply_to(message, f"✅ Kullanıcı `{sub_user_id_check}` aktif aboneliğe sahip.\nBitiş: {expiry_dt:%Y-%m-%d %H:%M:%S} ({remaining_str} kaldı).")
                else:
                    bot.reply_to(message, f"⚠️ Kullanıcı `{sub_user_id_check}` süresi dolmuş abonelik (Tarih: {expiry_dt:%Y-%m-%d %H:%M:%S}).")
                    remove_subscription_db(sub_user_id_check)
            else: bot.reply_to(message, f"⚠️ Kullanıcı `{sub_user_id_check}` abonelik listesinde ancak bitiş tarihi eksik. Gerekirse yeniden ekleyin.")
        else: bot.reply_to(message, f"ℹ️ Kullanıcı `{sub_user_id_check}` için aktif abonelik kaydı yok.")
    except ValueError:
        bot.reply_to(message, "⚠️ Geçersiz ID. Sayısal ID girin veya /cancel.")
        msg = bot.send_message(message.chat.id, "💳 Sorgulanacak Kullanıcı ID'sini girin, veya /cancel.")
        bot.register_next_step_handler(msg, process_check_subscription_id)
    except Exception as e: logger.error(f"Abonelik sorgulama işlenirken hata: {e}", exc_info=True); bot.reply_to(message, "Hata.")


                                                
                                 
                                      
                                 
                      
                                 
                            
                   
                               
                         

try:
    import psutil as _psutil_monitor
except ImportError:
    _psutil_monitor = None

                                                          

                                                 

                            
_AI_DAILY_QUESTIONS = [
    "🧠 Bugünün sorusu: Python'da en sık kullandığın veri yapısı hangisi ve neden?",
    "💡 Bugünün sorusu: Bir bot yazarken ilk dikkat etmen gereken şey ne?",
    "🚀 Bugünün sorusu: Kod yazarken en büyük zorluğun nedir?",
    "🔐 Bugünün sorusu: Güvenlik açısından bir bot yazarken nelere dikkat edersin?",
    "⚡ Bugünün sorusu: Botunu daha hızlı yapmak için ne yaparsın?",
    "🤔 Bugünün sorusu: Async ve sync programlama arasındaki farkı nasıl açıklarsın?",
    "📊 Bugünün sorusu: Veritabanı seçerken nelere dikkat edersin?",
    "🎯 Bugünün sorusu: Hangi Python kütüphanesi olmadan yapamazsın?",
    "🔄 Bugünün sorusu: API hata yönetimini nasıl yapıyorsun?",
    "🛡️ Bugünün sorusu: Botun çöktüğünde ne yaparsın?",
    "📝 Bugünün sorusu: Kod yorumlamayı önemli buluyor musun? Neden?",
    "🌐 Bugünün sorusu: Bir web scraper yazmak istesen hangi kütüphaneyi seçersin?",
    "💾 Bugünün sorusu: Büyük dosyaları işlerken hafıza sorunlarını nasıl çözersin?",
    "🔍 Bugünün sorusu: Regex mi, string metodları mı? Hangisini tercih edersin?",
    "🎨 Bugünün sorusu: Kodunu başkasının anlayabilmesi için ne yaparsın?",
]




                                  
USER_LANGUAGES = {}                                 

LANG_STRINGS = {
    'tr': {
        'welcome': '👋 Merhaba! VDS Bot Manager\'a hoş geldiniz.',
        'no_permission': '❌ Bu komutu kullanma yetkiniz yok.',
        'bot_started': '✅ Bot başlatıldı!',
        'bot_stopped': '🔴 Bot durduruldu.',
        'file_uploaded': '📤 Dosya yüklendi!',
        'lang_changed': '✅ Dil Türkçe olarak ayarlandı.',
        'choose_lang': '🌍 Lütfen bir dil seçin:',
                               
        'btn_update': '𝐆𝐔𝐍𝐂𝐄𝐋𝐋𝐄𝐌𝐄 𝐊𝐀𝐍𝐀𝐋𝐈',
        'btn_upload': '📤 Dosya Yükle',
        'btn_files': '📂 Dosyalarım',
        'btn_speed': '⚡ Bot Hızı',
        'btn_stats': '📊 İstatistikler',
        'btn_encode': '🔐 Şifrele/Çöz',
        'btn_analysis': '📈 Dosya Analizi',
        'btn_convert': '🔄 Format Dönüştür',
        'btn_search': '🔍 Dosya Ara',
        'btn_activity': '📜 Aktivite Geçmişi',
        'btn_url': '🌐 URL Kısalt',
        'btn_premium': '💎 Premium Al',
        'btn_profile': '🎴 Profil Kartım',
        'btn_lang': '🌍 Dil Seç',
        'btn_webhook': '🔔 Webhook',
        'btn_timer': '⏰ Zamanlayıcı',
        'btn_cmd': '📤 Komut Gönder',
        'btn_contact': '📞 Sahiple İletişim',
        'btn_subs': '💳 Abonelikler',
        'btn_announce': '📢 Duyuru',
        'btn_resmi_announce': '📢 Resmi Duyuru',
        'btn_lock': '🔒 Botu Kilitle',
        'btn_runall': '🟢 Tüm Kodları Çalıştır',
        'btn_sysinfo': '🖥️ Sistem Bilgisi',
        'btn_userlist': '👥 Kullanıcı Listesi',
        'btn_backup': '💾 Yedek Al',
        'btn_ban': '🚫 Kullanıcı Banla',
        'btn_unban': '🔓 Ban Kaldır',
        'btn_adminpanel': '👑 Yönetici Paneli',
        'btn_ai_daily': '🧠 Günlük AI Sorusu',
        'btn_all_files': '📁 Tüm Kullanıcı Dosyaları',
        'btn_whitelist': '✅ Malware Whitelist',
    },
    'en': {
        'welcome': '👋 Hello! Welcome to VDS Bot Manager.',
        'no_permission': '❌ You do not have permission to use this command.',
        'bot_started': '✅ Bot started!',
        'bot_stopped': '🔴 Bot stopped.',
        'file_uploaded': '📤 File uploaded!',
        'lang_changed': '✅ Language set to English.',
        'choose_lang': '🌍 Please choose a language:',
                                
        'btn_update': '𝐆𝐔𝐍𝐂𝐄𝐋𝐋𝐄𝐌𝐄 𝐊𝐀𝐍𝐀𝐋𝐈',
        'btn_upload': '📤 Upload File',
        'btn_files': '📂 My Files',
        'btn_speed': '⚡ Bot Speed',
        'btn_stats': '📊 Statistics',
        'btn_encode': '🔐 Encrypt/Decode',
        'btn_analysis': '📈 File Analysis',
        'btn_convert': '🔄 Convert Format',
        'btn_search': '🔍 Search File',
        'btn_activity': '📜 Activity History',
        'btn_url': '🌐 Shorten URL',
        'btn_premium': '💎 Get Premium',
        'btn_profile': '🎴 My Profile Card',
        'btn_lang': '🌍 Language',
        'btn_webhook': '🔔 Webhook',
        'btn_timer': '⏰ Scheduler',
        'btn_cmd': '📤 Send Command',
        'btn_contact': '📞 Contact Owner',
        'btn_subs': '💳 Subscriptions',
        'btn_announce': '📢 Announce',
        'btn_resmi_announce': '📢 Official Announce',
        'btn_lock': '🔒 Lock Bot',
        'btn_runall': '🟢 Run All Scripts',
        'btn_sysinfo': '🖥️ System Info',
        'btn_userlist': '👥 User List',
        'btn_backup': '💾 Backup',
        'btn_ban': '🚫 Ban User',
        'btn_unban': '🔓 Unban',
        'btn_adminpanel': '👑 Admin Panel',
        'btn_ai_daily': '🧠 Daily AI Question',
        'btn_all_files': '📁 All User Files',
        'btn_whitelist': '✅ Malware Whitelist',
    },
    'ru': {
        'welcome': '👋 Привет! Добро пожаловать в VDS Bot Manager.',
        'no_permission': '❌ У вас нет прав для использования этой команды.',
        'bot_started': '✅ Бот запущен!',
        'bot_stopped': '🔴 Бот остановлен.',
        'file_uploaded': '📤 Файл загружен!',
        'lang_changed': '✅ Язык установлен на русский.',
        'choose_lang': '🌍 Пожалуйста, выберите язык:',
                                
        'btn_update': '𝐆𝐔𝐍𝐂𝐄𝐋𝐋𝐄𝐌𝐄 𝐊𝐀𝐍𝐀𝐋𝐈',
        'btn_upload': '📤 Загрузить файл',
        'btn_files': '📂 Мои файлы',
        'btn_speed': '⚡ Скорость бота',
        'btn_stats': '📊 Статистика',
        'btn_encode': '🔐 Шифровать/Декод',
        'btn_analysis': '📈 Анализ файлов',
        'btn_convert': '🔄 Конвертировать',
        'btn_search': '🔍 Поиск файла',
        'btn_activity': '📜 История активности',
        'btn_url': '🌐 Укоротить URL',
        'btn_premium': '💎 Получить Premium',
        'btn_profile': '🎴 Мой профиль',
        'btn_lang': '🌍 Язык',
        'btn_webhook': '🔔 Вебхук',
        'btn_timer': '⏰ Планировщик',
        'btn_cmd': '📤 Отправить команду',
        'btn_contact': '📞 Связь с владельцем',
        'btn_subs': '💳 Подписки',
        'btn_announce': '📢 Объявление',
        'btn_resmi_announce': '📢 Офиц. объявление',
        'btn_lock': '🔒 Заблокировать бота',
        'btn_runall': '🟢 Запустить всё',
        'btn_sysinfo': '🖥️ Инфо системы',
        'btn_userlist': '👥 Список пользователей',
        'btn_backup': '💾 Резервная копия',
        'btn_ban': '🚫 Забанить пользователя',
        'btn_unban': '🔓 Разблокировать',
        'btn_adminpanel': '👑 Панель админа',
        'btn_ai_daily': '🧠 Вопрос дня от AI',
        'btn_all_files': '📁 Файлы всех пользователей',
        'btn_whitelist': '✅ Whitelist (Malware)',
    }
}

def get_text(user_id, key):
    lang = USER_LANGUAGES.get(user_id, 'tr')
    return LANG_STRINGS.get(lang, LANG_STRINGS['tr']).get(key, key)

@bot.message_handler(commands=['lang', 'language', 'dil'])
def cmd_lang(message):
    """Dil seç"""
    user_id = message.from_user.id
    if is_banned(user_id): return
    markup = types.InlineKeyboardMarkup(row_width=3)
    markup.add(
        types.InlineKeyboardButton("🇹🇷 Türkçe", callback_data='lang_tr'),
        types.InlineKeyboardButton("🇬🇧 English", callback_data='lang_en'),
        types.InlineKeyboardButton("🇷🇺 Русский", callback_data='lang_ru'),
    )
    bot.reply_to(message, get_text(user_id, 'choose_lang'), reply_markup=markup)

def _handle_lang_select(call):
    user_id = call.from_user.id
    lang = call.data.replace('lang_', '')
    if lang in LANG_STRINGS:
        USER_LANGUAGES[user_id] = lang
        bot.answer_callback_query(call.id, get_text(user_id, 'lang_changed'))
        try:
            bot.edit_message_text(get_text(user_id, 'lang_changed'), call.message.chat.id, call.message.message_id)
        except Exception:
            pass
                                          
        try:
            bot.send_message(
                call.message.chat.id,
                get_text(user_id, 'lang_changed'),
                reply_markup=create_reply_keyboard_main_menu(user_id)
            )
        except Exception:
            pass
    else:
        bot.answer_callback_query(call.id, "Geçersiz dil seçimi.")


                                        
WEBHOOK_TOKENS = {}                                            
WEBHOOK_HISTORY = {}                   

def generate_webhook_token(user_id, label="default"):
    token = hashlib.sha256(f"{user_id}_{label}_{time.time()}".encode()).hexdigest()[:24]
    WEBHOOK_TOKENS[token] = {'user_id': user_id, 'label': label, 'created': datetime.now().isoformat()}
    return token

@app.route('/webhook/<token>', methods=['GET', 'POST'])
def webhook_receive(token):
    """Dışarıdan gelen HTTP isteklerini Telegram bildirime çevir"""
    from flask import request, jsonify
    if token not in WEBHOOK_TOKENS:
        return jsonify({'error': 'Invalid token'}), 403
    info = WEBHOOK_TOKENS[token]
    user_id = info['user_id']
    label = info['label']
    try:
        if request.method == 'POST':
            data = request.get_json(silent=True) or {}
            event = data.get('event', 'Bilinmeyen Olay')
            detail = data.get('detail', '')
            level = data.get('level', 'info').upper()
        else:
            event = request.args.get('event', 'GET isteği alındı')
            detail = request.args.get('detail', '')
            level = request.args.get('level', 'INFO').upper()
        emoji = {'INFO': 'ℹ️', 'WARNING': '⚠️', 'ERROR': '🔴', 'CRITICAL': '🚨'}.get(level, 'ℹ️')
        msg = (f"{emoji} **Webhook Bildirimi**\n"
               f"🏷️ Etiket: `{label}`\n"
               f"📋 Olay: {event}\n"
               f"📝 Detay: {detail[:300] if detail else '-'}\n"
               f"🕐 {datetime.now().strftime('%H:%M:%S')}")
        if user_id not in WEBHOOK_HISTORY:
            WEBHOOK_HISTORY[user_id] = []
        WEBHOOK_HISTORY[user_id].append({'event': event, 'level': level, 'time': datetime.now().isoformat()})
        WEBHOOK_HISTORY[user_id] = WEBHOOK_HISTORY[user_id][-50:]
        try:
            bot.send_message(user_id, msg, parse_mode='Markdown')
        except: pass
        return jsonify({'ok': True, 'event': event}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bot.message_handler(commands=['webhook'])
def cmd_webhook(message):
    """Webhook URL'si oluştur"""
    user_id = message.from_user.id
    if is_banned(user_id): return
    add_active_user(user_id)
    try:
        parts = message.text.split()
        label = parts[1] if len(parts) > 1 else "default"
    except:
        label = "default"
    token = generate_webhook_token(user_id, label)
    base_url = os.environ.get("WEBHOOK_BASE_URL", "http://your-server.com")
    webhook_url = f"{base_url}/webhook/{token}"
    bot.reply_to(message,
        f"🔔 **Webhook Oluşturuldu!**\n\n"
        f"🔗 URL: `{webhook_url}`\n"
        f"🏷️ Etiket: `{label}`\n\n"
        f"**Kullanım örnekleri:**\n"
        f"```\n# GET\ncurl '{webhook_url}?event=Bot+Çöktü&level=ERROR'\n\n"
        f"# POST\ncurl -X POST '{webhook_url}' \\\n  -H 'Content-Type: application/json' \\\n  -d '{{\"event\":\"hata\",\"detail\":\"Port açık\",\"level\":\"WARNING\"}}'\n```\n\n"
        f"⏳ Token ömrü: Sunucu yeniden başlayana kadar geçerli.",
        parse_mode='Markdown')

@bot.message_handler(commands=['webhook_history'])
def cmd_webhook_history(message):
    """Webhook geçmişini göster"""
    user_id = message.from_user.id
    history = WEBHOOK_HISTORY.get(user_id, [])
    if not history:
        bot.reply_to(message, "📭 Henüz webhook bildirimi almadınız.")
        return
    lines = ["📜 **Son Webhook Bildirimleri:**\n"]
    for h in reversed(history[-10:]):
        emoji = {'INFO': 'ℹ️', 'WARNING': '⚠️', 'ERROR': '🔴', 'CRITICAL': '🚨'}.get(h.get('level',''), 'ℹ️')
        lines.append(f"{emoji} `{h.get('time','')[:16]}` — {h.get('event','')}")
    bot.reply_to(message, '\n'.join(lines), parse_mode='Markdown')


                               

                                           
SCHEDULED_TASKS = {}                    
_sched_lock = threading.Lock()

def scheduler_daemon():
    """Zamanlayıcı daemon — her 20 saniyede kontrol eder (±29 saniye tolerans)"""
    while True:
        try:
            time.sleep(20)
            now = datetime.now()
            with _sched_lock:
                for task_id, task in list(SCHEDULED_TASKS.items()):
                    if not task.get('active'):
                        continue
                    action = task.get('action')
                    user_id = task.get('user_id')
                    file_name = task.get('file_name')
                    if task.get('type') == 'daily':
                        target_h = task.get('hour', 8)
                        target_m = task.get('minute', 0)
                        target_dt = now.replace(hour=target_h, minute=target_m, second=0, microsecond=0)
                        diff = (now - target_dt).total_seconds()
                                                                               
                        if not (0 <= diff <= 29):
                            continue
                                                 
                        last_run = task.get('last_run')
                        if last_run and last_run.date() == now.date():
                            continue
                        task['last_run'] = now
                        logger.info(f"Zamanlayıcı tetiklendi: {task_id} ({action} @ {target_h:02d}:{target_m:02d}, fark: {diff:.1f}sn)")
                        threading.Thread(
                            target=_execute_scheduled_action,
                            args=(user_id, file_name, action, task_id),
                            daemon=True
                        ).start()
        except Exception as e:
            logger.error(f"Scheduler daemon hatası: {e}")

def _execute_scheduled_action(user_id, file_name, action, task_id):
    """Zamanlı aksiyonu çalıştır"""
    try:
        user_folder = get_user_folder(user_id)
        script_key = f"{user_id}_{file_name}"
        if action == 'start':
            if script_key not in bot_scripts:
                script_path = os.path.join(user_folder, file_name)
                if os.path.exists(script_path):
                    class FakeMsg:
                        chat = type('C', (), {'id': user_id})()
                        message_id = 0
                        from_user = type('U', (), {'id': user_id})()
                    if file_name.endswith('.py'):
                        threading.Thread(target=run_script, args=(script_path, user_id, user_folder, file_name, FakeMsg())).start()
                    elif file_name.endswith('.js'):
                        threading.Thread(target=run_js_script, args=(script_path, user_id, user_folder, file_name, FakeMsg())).start()
                    try:
                        bot.send_message(user_id, f"⏰ **Zamanlayıcı:** `{file_name}` başlatıldı.", parse_mode='Markdown')
                    except: pass
        elif action == 'stop':
            if script_key in bot_scripts:
                kill_process_tree(bot_scripts[script_key])
                del bot_scripts[script_key]
                try:
                    bot.send_message(user_id, f"⏰ **Zamanlayıcı:** `{file_name}` durduruldu.", parse_mode='Markdown')
                except: pass
    except Exception as e:
        logger.error(f"Scheduled action hatası {task_id}: {e}")

scheduler_t = threading.Thread(target=scheduler_daemon, daemon=True)
scheduler_t.start()


                                 
                                                                                      
                                                                                           

                                                 
@bot.message_handler(commands=['yenikomutlar', 'newcmds', 'komutlar', 'commands'])
def cmd_new_commands_help(message):
    """Tüm komutların listesi"""
    user_id = message.from_user.id
    bot.reply_to(message,
        "📋 *TÜM KOMUTLAR*\n\n"
        "━━━━━━━━━━━━━━━━\n"
        "🤖 *AI KOMUTLARI*\n"
        "  /ai <soru> — Genel AI sohbet\n"
        "  /ai_ask <soru> — Detaylı soru\n"
        "  /ai_code <açıklama> — Kod yazdır\n"
        "  /ai_fix <kod> — Kodu düzelt\n"
        "  /ai_explain <kod> — Kodu açıkla\n"
        "  /ai_translate <metin> — Çeviri\n"
        "  /ai_summary <metin> — Özetle\n"
        "  /ai_daily — Günlük AI sorusu\n"
        "  /debugai <dosya> — Dosya analizi\n"
        "  /loganaliz <dosya> — Log analizi\n"
        "  /ai_reset — Sohbet geçmişini sıfırla\n\n"
        "━━━━━━━━━━━━━━━━\n"
        "📁 *DOSYA KOMUTLARI*\n"
        "  /checkfiles — Dosyalarım\n"
        "  /search <isim> — Dosya ara\n"
        "  /file_size — Depolama boyutu\n"
        "  /file_hash <dosya> — SHA256 hash\n"
        "  /compress_file <dosya> — Sıkıştır\n\n"
        "━━━━━━━━━━━━━━━━\n"
        "🔐 *ŞİFRELEME*\n"
        "  /encode <mod> <metin> — Kodla\n"
        "  /decode <mod> <kod> — Çöz\n"
        "  /hash_password <şifre> — Hash\n"
        "  /randpass [uzunluk] — Şifre üret\n\n"
        "━━━━━━━━━━━━━━━━\n"
        "⚙️ *BOT YÖNETİMİ*\n"
        "  /myinfo — Profilim\n"
        "  /profil — Görsel kart\n"
        "  /lang — Dil seç (TR/EN/RU)\n"
        "  /shorten <url> — URL kısalt\n"
        "  /webhook <etiket> — Webhook\n"
        "  /webhook_history — Webhook geçmişi\n"
        "  /zamanla <dosya> start|stop SS:DD\n"
        "  /takvim — Zamanlayıcılar\n\n"
        "━━━━━━━━━━━━━━━━\n"
        "👑 *ADMİN KOMUTLARI*\n"
        "  /sysinfo — Sistem bilgisi\n"
        "  /userlist — Kullanıcı listesi\n"
        "  /userinfo <id> — Kullanıcı detayı\n"
        "  /admins — Yönetici listesi\n"
        "  /addadmin <id> — Yönetici ekle\n"
        "  /removeadmin <id> — Yönetici kaldır\n"
        "  /backup — Yedek al\n"
        "  /ban <id> [sebep] — Kullanıcı banla\n"
        "  /unban <id> — Ban kaldır\n"
        "  /kickuser <id> — Dosyaları sil (bansız)\n"
        "  /lockbot [sebep] [30m/2h/1d] — Kilitle/Aç\n"
        "  /lockstatus — Kilit durumu\n"
        "  /announce <mesaj> — Duyuru\n",
        parse_mode='Markdown')

                                                     

                                       

def _logic_whitelist_menu(message):
    """Malware whitelist yönetim menüsünü göster — SADECE SAHİP"""
    user_id = message.from_user.id
    if user_id != OWNER_ID:
        bot.reply_to(message, "⛔ Bu özellik yalnızca bot sahibine özeldir!")
        return

    wl_list = ", ".join(f"`{uid}`" for uid in sorted(malware_whitelist)) if malware_whitelist else "_(boş)_"
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(
        types.InlineKeyboardButton("➕ Ekle", callback_data="wl_add"),
        types.InlineKeyboardButton("➖ Kaldır", callback_data="wl_remove")
    )
    markup.row(types.InlineKeyboardButton("📋 Listeyi Yenile", callback_data="wl_list"))
    bot.reply_to(
        message,
        f"✅ *MALWARE WHİTELİST YÖNETİMİ*\n\n"
        f"Bu listedeki kullanıcıların dosyaları malware taramasına tabi tutulmaz ve otomatik ban uygulanmaz.\n\n"
        f"📋 *Mevcut Whitelist:*\n{wl_list}\n\n"
        f"Toplam: {len(malware_whitelist)} kullanıcı",
        parse_mode='Markdown',
        reply_markup=markup
    )

def _whitelist_callback(call):
    user_id = call.from_user.id
    if user_id != OWNER_ID:
        bot.answer_callback_query(call.id, "⛔ Sadece sahip!", show_alert=True)
        return

    if call.data == 'wl_list':
        wl_list = ", ".join(f"`{uid}`" for uid in sorted(malware_whitelist)) if malware_whitelist else "_(boş)_"
        bot.answer_callback_query(call.id)
        try:
            bot.edit_message_text(
                f"✅ *MALWARE WHİTELİST*\n\n📋 *Mevcut Liste:*\n{wl_list}\n\nToplam: {len(malware_whitelist)} kullanıcı",
                call.message.chat.id, call.message.message_id,
                parse_mode='Markdown', reply_markup=call.message.reply_markup
            )
        except Exception:
            pass
        return

    if call.data == 'wl_add':
        bot.answer_callback_query(call.id)
        msg = bot.send_message(call.message.chat.id,
            "➕ *Whitelist'e Ekle*\n\nEklemek istediğiniz kullanıcının ID'sini gönderin:\n_(İptal için /cancel)_",
            parse_mode='Markdown')
        bot.register_next_step_handler(msg, _wl_add_step)

    elif call.data == 'wl_remove':
        bot.answer_callback_query(call.id)
        if not malware_whitelist:
            bot.send_message(call.message.chat.id, "⚠️ Whitelist zaten boş.")
            return
        msg = bot.send_message(call.message.chat.id,
            f"➖ *Whitelist'ten Kaldır*\n\nMevcut liste: {', '.join(str(u) for u in sorted(malware_whitelist))}\n\nKaldırmak istediğiniz kullanıcı ID'sini gönderin:\n_(İptal için /cancel)_",
            parse_mode='Markdown')
        bot.register_next_step_handler(msg, _wl_remove_step)

def _wl_add_step(message):
    if message.text and message.text.strip().lower() in ('/cancel', 'cancel'):
        bot.reply_to(message, "❌ İptal edildi.")
        return
    try:
        target_id = int(message.text.strip())
    except (ValueError, AttributeError):
        bot.reply_to(message, "❌ Geçersiz ID! Sadece sayı girin.")
        return

    if target_id in malware_whitelist:
        bot.reply_to(message, f"⚠️ `{target_id}` zaten whitelist'te.", parse_mode='Markdown')
        return

    malware_whitelist.add(target_id)
    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        conn.execute(
            'INSERT OR IGNORE INTO malware_whitelist (user_id, added_by, added_at) VALUES (?, ?, ?)',
            (target_id, OWNER_ID, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Whitelist DB kayıt hatası: {e}")

    bot.reply_to(message,
        f"✅ *`{target_id}` whitelist'e eklendi!*\n\n"
        f"Bu kullanıcının dosyaları artık malware taramasından muaftır.\n"
        f"Toplam whitelist: {len(malware_whitelist)} kullanıcı",
        parse_mode='Markdown')
    logger.info(f"Whitelist'e eklendi: {target_id} (sahip tarafından)")

                                                               
    try:
        bot.send_message(target_id,
            "✅ *Whitelist'e Alındınız!*\n\nDosyalarınız artık otomatik güvenlik taramasından muaftır.",
            parse_mode='Markdown')
    except Exception:
        pass

def _wl_remove_step(message):
    if message.text and message.text.strip().lower() in ('/cancel', 'cancel'):
        bot.reply_to(message, "❌ İptal edildi.")
        return
    try:
        target_id = int(message.text.strip())
    except (ValueError, AttributeError):
        bot.reply_to(message, "❌ Geçersiz ID! Sadece sayı girin.")
        return

    if target_id not in malware_whitelist:
        bot.reply_to(message, f"⚠️ `{target_id}` whitelist'te değil.", parse_mode='Markdown')
        return

    malware_whitelist.discard(target_id)
    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        conn.execute('DELETE FROM malware_whitelist WHERE user_id=?', (target_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Whitelist DB silme hatası: {e}")

    bot.reply_to(message,
        f"✅ *`{target_id}` whitelist'ten kaldırıldı.*\n\n"
        f"Bu kullanıcının dosyaları artık tekrar taranacak.\n"
        f"Toplam whitelist: {len(malware_whitelist)} kullanıcı",
        parse_mode='Markdown')
    logger.info(f"Whitelist'ten kaldırıldı: {target_id} (sahip tarafından)")

@bot.message_handler(commands=['wl_add', 'whitelist_add'])
def cmd_wl_add(message):
    """Whitelist'e kullanıcı ekle — sadece sahip. Kullanım: /wl_add <id>"""
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "⛔ Sadece sahip!")
        return
    try:
        target_id = int(message.text.split()[1])
    except (IndexError, ValueError):
        bot.reply_to(message, "❌ Kullanım: `/wl_add <kullanici_id>`", parse_mode='Markdown')
        return
    if target_id in malware_whitelist:
        bot.reply_to(message, f"⚠️ `{target_id}` zaten whitelist'te.", parse_mode='Markdown')
        return
    malware_whitelist.add(target_id)
    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        conn.execute('INSERT OR IGNORE INTO malware_whitelist (user_id, added_by, added_at) VALUES (?, ?, ?)',
                     (target_id, OWNER_ID, datetime.now().isoformat()))
        conn.commit(); conn.close()
    except Exception as e:
        logger.error(f"Whitelist DB kayıt hatası: {e}")
    bot.reply_to(message, f"✅ `{target_id}` whitelist'e eklendi!", parse_mode='Markdown')

@bot.message_handler(commands=['wl_remove', 'whitelist_remove'])
def cmd_wl_remove(message):
    """Whitelist'ten kullanıcı kaldır — sadece sahip. Kullanım: /wl_remove <id>"""
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "⛔ Sadece sahip!")
        return
    try:
        target_id = int(message.text.split()[1])
    except (IndexError, ValueError):
        bot.reply_to(message, "❌ Kullanım: `/wl_remove <kullanici_id>`", parse_mode='Markdown')
        return
    if target_id not in malware_whitelist:
        bot.reply_to(message, f"⚠️ `{target_id}` whitelist'te değil.", parse_mode='Markdown')
        return
    malware_whitelist.discard(target_id)
    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        conn.execute('DELETE FROM malware_whitelist WHERE user_id=?', (target_id,))
        conn.commit(); conn.close()
    except Exception as e:
        logger.error(f"Whitelist DB silme hatası: {e}")
    bot.reply_to(message, f"✅ `{target_id}` whitelist'ten kaldırıldı.", parse_mode='Markdown')

@bot.message_handler(commands=['wl_list', 'whitelist'])
def cmd_wl_list(message):
    """Whitelist'i göster — sadece sahip"""
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "⛔ Sadece sahip!")
        return
    wl_list = "\n".join(f"• `{uid}`" for uid in sorted(malware_whitelist)) if malware_whitelist else "_(boş)_"
    bot.reply_to(message, f"✅ *Malware Whitelist* ({len(malware_whitelist)} kullanıcı):\n\n{wl_list}", parse_mode='Markdown')

def _logic_all_user_files(message):
    """Tüm kullanıcıların dosyalarını gerçek dosya olarak sahibe gönder — SADECE SAHİP"""
    user_id = message.from_user.id
    if user_id != OWNER_ID:
        bot.reply_to(message, "⛔ Bu özellik yalnızca bot sahibine özeldir!")
        return

    wait_msg = bot.reply_to(message, "⏳ Dosyalar taranıyor, gönderiliyor...")

                                                
    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('SELECT user_id, file_name, file_type FROM user_files ORDER BY user_id, file_name')
        db_rows = c.fetchall()
        conn.close()
    except Exception as e:
        db_rows = []

                            
    from collections import OrderedDict
    user_file_map = OrderedDict()
    for uid, fname, ftype in db_rows:
        if uid not in user_file_map:
            user_file_map[uid] = []
        user_file_map[uid].append((fname, ftype))

                                                               
    for uid, files in user_files.items():
        if uid not in user_file_map:
            user_file_map[uid] = list(files)

    if not user_file_map:
        bot.edit_message_text("📭 Henüz hiçbir kullanıcıya ait dosya bulunamadı.", message.chat.id, wait_msg.message_id)
        return

    total_files_sent = 0
    total_files_missing = 0
    total_users = 0

    try:
        bot.delete_message(message.chat.id, wait_msg.message_id)
    except Exception:
        pass

    for uid, files in user_file_map.items():
        total_users += 1

                                
        if uid == OWNER_ID:
            role = "👑 Sahip"
        elif uid in admin_ids:
            role = "🛡️ Yönetici"
        elif is_banned(uid):
            role = "🚫 Banlı"
        elif uid in user_subscriptions and user_subscriptions[uid].get('expiry', datetime.min) > datetime.now():
            role = "⭐ Premium"
        else:
            role = "👤 Kullanıcı"

                                    
        existing = []
        for item in files:
            fname = item[0] if isinstance(item, (list, tuple)) else item
            fpath = os.path.join(get_user_folder(uid), fname)
            if os.path.exists(fpath):
                existing.append((fname, fpath))
            else:
                total_files_missing += 1

        if not existing:
                                                                 
            bot.send_message(
                message.chat.id,
                f"👤 *Kullanıcı:* `{uid}`  {role}\n"
                f"📂 Kayıtlı dosya var ama disk'te bulunamadı ({len(files)} adet).",
                parse_mode='Markdown'
            )
            continue

                                 
        size_total = sum(os.path.getsize(fp) for _, fp in existing)
        if size_total >= 1024 * 1024:
            size_str = f"{size_total / (1024*1024):.1f} MB"
        elif size_total >= 1024:
            size_str = f"{size_total / 1024:.1f} KB"
        else:
            size_str = f"{size_total} B"

        bot.send_message(
            message.chat.id,
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 *Kullanıcı ID:* `{uid}`\n"
            f"{role}  |  📄 {len(existing)} dosya  |  💾 {size_str}\n"
            f"━━━━━━━━━━━━━━━━━━━━",
            parse_mode='Markdown'
        )

                                    
        for fname, fpath in existing:
            try:
                size_bytes = os.path.getsize(fpath)
                if size_bytes >= 1024 * 1024:
                    fsize_str = f"{size_bytes / (1024*1024):.1f} MB"
                elif size_bytes >= 1024:
                    fsize_str = f"{size_bytes / 1024:.1f} KB"
                else:
                    fsize_str = f"{size_bytes} B"

                with open(fpath, 'rb') as f:
                    bot.send_document(
                        message.chat.id,
                        f,
                        visible_file_name=fname,
                        caption=f"📄 `{fname}`\n👤 Kullanıcı: `{uid}`  {role}\n💾 {fsize_str}",
                        parse_mode='Markdown'
                    )
                total_files_sent += 1
                time.sleep(0.3)                           
            except Exception as e:
                bot.send_message(
                    message.chat.id,
                    f"❌ `{fname}` gönderilemedi: {e}",
                    parse_mode='Markdown'
                )

                 
    bot.send_message(
        message.chat.id,
        f"✅ *Gönderim Tamamlandı!*\n\n"
        f"👥 Kullanıcı sayısı: {total_users}\n"
        f"📤 Gönderilen dosya: {total_files_sent}\n"
        f"❌ Disk'te bulunamayan: {total_files_missing}\n"
        f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        parse_mode='Markdown'
    )

@bot.message_handler(commands=['allfiles'])
def cmd_allfiles(message):
    """Tüm kullanıcı dosyalarını listele — sadece sahip"""
    _logic_all_user_files(message)

@bot.message_handler(commands=['backup'])
def cmd_backup(message):
    """Tum bot dosyalarini ZIP olarak yedekle"""
    user_id = message.from_user.id
    if user_id not in admin_ids:
        bot.reply_to(message, "Sadece yoneticiler yedek alabilir!")
        return
    wait_msg = bot.reply_to(message, "Yedek olusturuluyor...")
    try:
        backup_path = os.path.join(IROTECH_DIR, f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip")
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            if os.path.exists(DATABASE_PATH):
                zf.write(DATABASE_PATH, 'bot_data.db')
            for root, dirs, files_in_dir in os.walk(UPLOAD_BOTS_DIR):
                for file in files_in_dir:
                    fpath = os.path.join(root, file)
                    arcname = os.path.relpath(fpath, BASE_DIR)
                    zf.write(fpath, arcname)
        size_mb = os.path.getsize(backup_path) / (1024*1024)
        bot.edit_message_text(f"Yedek hazir! ({size_mb:.2f} MB)", message.chat.id, wait_msg.message_id)
        if size_mb <= 50:
            with open(backup_path, 'rb') as bf:
                bot.send_document(message.chat.id, bf, caption=f"Yedek: {os.path.basename(backup_path)}")
        os.remove(backup_path)
    except Exception as e:
        bot.edit_message_text(f"Yedekleme hatasi: {e}", message.chat.id, wait_msg.message_id)

@bot.message_handler(commands=['sysinfo'])
def cmd_sysinfo(message):
    """Sunucu sistem bilgilerini goster"""
    user_id = message.from_user.id
    if user_id not in admin_ids:
        bot.reply_to(message, "Sadece yoneticiler kullanabilir!")
        return
    try:
        import platform
        try:
            cpu_count = os.cpu_count() or 1
            with open('/proc/loadavg') as f:
                load = f.read().split()[:3]
            cpu_info = f"{cpu_count} cekirdek | Yuk: {', '.join(load)}"
        except Exception:
            cpu_info = f"{os.cpu_count() or '?'} cekirdek"
        try:
            with open('/proc/meminfo') as f:
                mem_lines = f.readlines()
            mem_total = int(mem_lines[0].split()[1]) // 1024
            mem_free = int(mem_lines[1].split()[1]) // 1024
            mem_used = mem_total - mem_free
            ram_info = f"{mem_used} MB / {mem_total} MB (%{int(mem_used/mem_total*100)})"
        except Exception:
            ram_info = "Bilgi alinamadi"
        try:
            disk = os.statvfs('/')
            disk_total = disk.f_blocks * disk.f_frsize // (1024**3)
            disk_free = disk.f_bfree * disk.f_frsize // (1024**3)
            disk_used = disk_total - disk_free
            disk_info = f"Toplam: {disk_total}GB | Kullanilan: {disk_used}GB | Bos: {disk_free}GB"
        except Exception:
            disk_info = "Bilgi alinamadi"
        bot_size = file_manager.get_directory_size(UPLOAD_BOTS_DIR)
        running_count = sum(1 for sk, si in bot_scripts.items() if is_bot_running(si['script_owner_id'], si['file_name']))
        sysinfo = (
            f"SISTEM BILGISI\n"
            f"Platform: {platform.system()} {platform.release()}\n"
            f"Python: {sys.version.split()[0]}\n"
            f"CPU: {cpu_info}\n"
            f"RAM: {ram_info}\n"
            f"Disk: {disk_info}\n"
            f"Bot Depolama: {bot_size:.1f} MB\n"
            f"Calisma Suresi: {performance_tracker.get_uptime():.1f} saat\n"
            f"Aktif Bot: {running_count}\n"
            f"Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        bot.reply_to(message, sysinfo)
    except Exception as e:
        bot.reply_to(message, f"Sistem bilgisi alinamadi: {e}")

@bot.message_handler(commands=['userlist'])
def cmd_userlist(message):
    """Tum kullanicilari listele"""
    user_id = message.from_user.id
    if user_id not in admin_ids:
        bot.reply_to(message, "Yetkisiz!")
        return
    total = len(active_users)
    premium = sum(1 for uid, sub in user_subscriptions.items() if sub.get('expiry', datetime.min) > datetime.now())
    banned_count = len(banned_users)
    banned_ids_str = ', '.join(str(u) for u in list(banned_users)[:10]) or 'Kimse'
    msg = (
        f"KULLANICI LISTESI\n"
        f"Toplam: {total}\n"
        f"Admin/Sahip: {len(admin_ids)}\n"
        f"Premium: {premium}\n"
        f"Banli: {banned_count}\n"
        f"Banli ID'ler: {banned_ids_str}"
    )
    bot.reply_to(message, msg)

def _logic_unban_user_button(message):
    """Butondan tetiklenen ban kaldırma akışı: ID sor → banı kaldır"""
    user_id = message.from_user.id
    if user_id not in admin_ids:
        bot.reply_to(message, "⚠️ Sadece yöneticiler ban kaldırabilir!")
        return
    msg = bot.reply_to(message,
        "🔓 *Ban Kaldırma*\n\n"
        "Banını kaldırmak istediğiniz kullanıcının *Telegram ID*'sini girin.\n\n"
        "İptal etmek için /cancel yazın.",
        parse_mode='Markdown')
    bot.register_next_step_handler(msg, _unban_step_get_id)

def _unban_step_get_id(message):
    """Ban kaldırma: ID al ve işlemi uygula"""
    user_id = message.from_user.id
    if user_id not in admin_ids:
        return
    if message.text and message.text.strip().lower() == '/cancel':
        bot.reply_to(message, "❌ Ban kaldırma işlemi iptal edildi.")
        return
    if not message.text or not message.text.strip().lstrip('-').isdigit():
        msg = bot.reply_to(message,
            "❌ *Geçersiz ID!*\n\nLütfen sayısal bir Telegram ID girin.\nİptal: /cancel",
            parse_mode='Markdown')
        bot.register_next_step_handler(msg, _unban_step_get_id)
        return
    try:
        target_id = int(message.text.strip())
    except (ValueError, AttributeError):
        msg = bot.reply_to(message, "❌ Geçersiz ID! Sayısal bir Telegram ID girin.\n\nİptal: /cancel")
        bot.register_next_step_handler(msg, _unban_step_get_id)
        return

    if not is_banned(target_id):
        bot.reply_to(message, f"⚠️ Kullanıcı `{target_id}` zaten banlı değil.", parse_mode='Markdown')
        return

    unban_user(target_id)
    bot.reply_to(message,
        f"✅ *Ban Kaldırıldı!*\n\n"
        f"🆔 Kullanıcı: `{target_id}`\n"
        f"👮 Yetkili: `{user_id}`\n"
        f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        parse_mode='Markdown')
    try:
        bot.send_message(target_id,
            "✅ *Banınız kaldırıldı!*\n\nYönetici tarafından banınız kaldırıldı. Artık botu kullanabilirsiniz.\nBaşlamak için /start yazın.",
            parse_mode='Markdown')
    except Exception:
        pass
    if user_id != OWNER_ID:
        try:
            bot.send_message(OWNER_ID,
                f"🔓 *Admin Ban Kaldırdı*\n\n"
                f"👮 Admin: `{user_id}`\n"
                f"🎯 Hedef: `{target_id}`\n"
                f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                parse_mode='Markdown')
        except Exception:
            pass

def _logic_ban_user_button(message):
    """Butondan tetiklenen ban akışı: ID sor → sebep sor → süre sor → onay → banla"""
    user_id = message.from_user.id
    if user_id not in admin_ids:
        bot.reply_to(message, "⚠️ Sadece yöneticiler ban uygulayabilir!")
        return
    msg = bot.reply_to(message,
        "🚫 *Kullanıcı Banlama — Adım 1/3*\n\n"
        "Banlamak istediğiniz kullanıcının *Telegram ID*'sini girin.\n\n"
        "_(ID öğrenmek için kullanıcıya /myinfo yazdırabilirsiniz)_\n\n"
        "İptal etmek için /cancel yazın.",
        parse_mode='Markdown')
    bot.register_next_step_handler(msg, _ban_step_get_id)

def _ban_step_get_id(message):
    """Ban akışı adım 1: Kullanıcı ID al"""
    user_id = message.from_user.id
    if user_id not in admin_ids:
        return
    if message.text and message.text.strip().lower() == '/cancel':
        bot.reply_to(message, "❌ Ban işlemi iptal edildi.")
        return
    if not message.text or not message.text.strip().lstrip('-').isdigit():
        msg = bot.reply_to(message,
            "❌ *Geçersiz ID!*\n\n"
            "Lütfen sayısal bir Telegram ID girin.\n"
            "Örnek: `123456789`\n\n"
            "İptal: /cancel",
            parse_mode='Markdown')
        bot.register_next_step_handler(msg, _ban_step_get_id)
        return
    try:
        target_id = int(message.text.strip())
    except (ValueError, AttributeError):
        msg = bot.reply_to(message, "❌ Geçersiz ID! Sayısal bir Telegram ID girin.\n\nİptal: /cancel")
        bot.register_next_step_handler(msg, _ban_step_get_id)
        return

    if target_id == OWNER_ID:
        bot.reply_to(message, "❌ Sahibi banlayamazsınız!")
        return
    if target_id in admin_ids and user_id != OWNER_ID:
        bot.reply_to(message, "❌ Sadece sahip başka yöneticileri banlar!")
        return
    if is_banned(target_id):
        until = banned_users_until.get(target_id)
        until_str = f"\n⏰ Bitiş: {until.strftime('%Y-%m-%d %H:%M')}" if until else "\n🔴 Tür: Sınırsız"
        bot.reply_to(message,
            f"⚠️ Kullanıcı `{target_id}` zaten banlı.{until_str}\n\n"
            f"Banını kaldırmak için /unban {target_id} kullanın.",
            parse_mode='Markdown')
        return

    msg = bot.reply_to(message,
        f"✅ *Adım 1/3 Tamamlandı* — ID: `{target_id}`\n\n"
        f"*Adım 2/3:* Ban sebebini yazın.\n"
        f"_(Örnek: Spam, Kural ihlali, Zararlı dosya)_\n\n"
        f"Sebepsiz banlamak için sadece `-` gönderin.\n"
        f"İptal: /cancel",
        parse_mode='Markdown')
    bot.register_next_step_handler(msg, lambda m: _ban_step_get_reason(m, target_id))

def _ban_step_get_reason(message, target_id):
    """Ban akışı adım 2: Sebep al"""
    user_id = message.from_user.id
    if user_id not in admin_ids:
        return
    if message.text and message.text.strip().lower() == '/cancel':
        bot.reply_to(message, "❌ Ban işlemi iptal edildi.")
        return

    reason = message.text.strip() if message.text else "Admin kararı"
    if reason == '-':
        reason = "Admin kararı"

    msg = bot.reply_to(message,
        f"✅ *Adım 2/3 Tamamlandı* — Sebep: _{reason}_\n\n"
        f"*Adım 3/3:* Ban süresini belirleyin.\n\n"
        f"📌 Format örnekleri:\n"
        f"  `sınırsız` veya `0` → Kalıcı ban\n"
        f"  `30m` → 30 dakika\n"
        f"  `2h` → 2 saat\n"
        f"  `1d` → 1 gün\n"
        f"  `7d` → 7 gün\n\n"
        f"İptal: /cancel",
        parse_mode='Markdown')
    bot.register_next_step_handler(msg, lambda m: _ban_step_get_duration(m, target_id, reason))

def _ban_step_get_duration(message, target_id, reason):
    """Ban akışı adım 3: Süre al ve onay göster"""
    user_id = message.from_user.id
    if user_id not in admin_ids:
        return
    if message.text and message.text.strip().lower() == '/cancel':
        bot.reply_to(message, "❌ Ban işlemi iptal edildi.")
        return

    raw = message.text.strip().lower() if message.text else "sınırsız"
    ban_until_dt = None
    duration_str = "Sınırsız"

    if raw in ('sınırsız', 'sinırsız', 'sinırsiz', 'sinirsiz', '0', 'kalıcı', 'kalici'):
        ban_until_dt = None
        duration_str = "🔴 Sınırsız (Kalıcı)"
    else:
        dur_match = re.match(r'^(\d+)(d|h|m)$', raw, re.IGNORECASE)
        if dur_match:
            val, unit = int(dur_match.group(1)), dur_match.group(2).lower()
            if unit == 'd':
                minutes = val * 1440
                duration_str = f"⏰ {val} gün"
            elif unit == 'h':
                minutes = val * 60
                duration_str = f"⏰ {val} saat"
            elif unit == 'm':
                minutes = val
                duration_str = f"⏰ {val} dakika"
            ban_until_dt = datetime.now() + timedelta(minutes=minutes)
        else:
            msg = bot.reply_to(message,
                "❌ *Geçersiz süre formatı!*\n\n"
                "Örnekler: `sınırsız`, `30m`, `2h`, `1d`\n\n"
                "İptal: /cancel",
                parse_mode='Markdown')
            bot.register_next_step_handler(msg, lambda m: _ban_step_get_duration(m, target_id, reason))
            return

                           
    until_encoded = ban_until_dt.isoformat() if ban_until_dt else "none"
                                                                                  
    safe_reason = reason[:60].replace('||', '|')
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(
        types.InlineKeyboardButton("✅ Evet, Banla", callback_data=f'confirm_ban_{target_id}||{safe_reason}||{until_encoded}'),
        types.InlineKeyboardButton("❌ İptal", callback_data='cancel_ban')
    )
    bot.reply_to(message,
        f"⚠️ *Ban Onayı*\n\n"
        f"🆔 Kullanıcı: `{target_id}`\n"
        f"📝 Sebep: _{reason}_\n"
        f"⏳ Süre: {duration_str}\n\n"
        f"Bu kullanıcıyı banlıyor musunuz?",
        reply_markup=markup,
        parse_mode='Markdown')

def _confirm_ban_callback(call):
    """Onay butonuna basınca gerçek ban işlemini uygula"""
    user_id = call.from_user.id
    if user_id not in admin_ids:
        bot.answer_callback_query(call.id, "⚠️ Yönetici yetkisi gerekli.", show_alert=True)
        return
    try:
                                                                               
        data = call.data
        rest = data[len('confirm_ban_'):]
        parts2 = rest.split('||')
        target_id = int(parts2[0])
        reason = parts2[1] if len(parts2) > 1 else "Admin kararı"
        until_str = parts2[2] if len(parts2) > 2 else 'none'
        ban_until_dt = None
        if until_str and until_str != 'none':
            try:
                ban_until_dt = datetime.fromisoformat(until_str)
            except Exception:
                ban_until_dt = None
    except Exception as e:
        bot.answer_callback_query(call.id, "❌ Geçersiz veri.", show_alert=True)
        return

    if target_id == OWNER_ID:
        bot.answer_callback_query(call.id, "❌ Sahibi banlayamazsınız!", show_alert=True)
        return
    if is_banned(target_id):
        bot.answer_callback_query(call.id, f"⚠️ Kullanıcı {target_id} zaten banlı.", show_alert=True)
        return

    ban_user(target_id, reason, ban_until_dt)
    duration_str = f"{ban_until_dt.strftime('%Y-%m-%d %H:%M')}" if ban_until_dt else "Sınırsız"
    banner_name = f"@{call.from_user.username}" if call.from_user.username else call.from_user.first_name
    bot.answer_callback_query(call.id, f"🚫 Kullanıcı {target_id} banlandı!")
    try:
        bot.edit_message_text(
            f"🚫 *Kullanıcı Banlandı!*\n\n"
            f"🆔 ID: `{target_id}`\n"
            f"📝 Sebep: _{reason}_\n"
            f"⏳ Süre: {duration_str}\n"
            f"👮 Banlayan: {banner_name}\n"
            f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            call.message.chat.id, call.message.message_id,
            parse_mode='Markdown', reply_markup=None)
    except Exception:
        pass
                                                                 
    try:
        bot.send_message(target_id, get_ban_message(reason, ban_until_dt, banner_name), parse_mode='Markdown')
        logger.info(f"Ban bildirimi kullanıcıya gönderildi: {target_id}")
    except Exception as e:
        logger.warning(f"Ban bildirimi {target_id} kullanıcısına gönderilemedi: {e}")
                                           
    if user_id != OWNER_ID:
        try:
            bot.send_message(OWNER_ID,
                f"🚫 *Admin BAN Uyguladı*\n\n"
                f"👮 Admin: {banner_name} (`{user_id}`)\n"
                f"🎯 Hedef: `{target_id}`\n"
                f"📝 Sebep: {reason}\n"
                f"⏳ Süre: {duration_str}\n"
                f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                parse_mode='Markdown')
        except Exception:
            pass
    logger.warning(f"Buton ban: admin={user_id}({banner_name}) → hedef={target_id}, sebep={reason}, bitiş={duration_str}")

@bot.message_handler(commands=['ban'])
def cmd_ban(message):
    """Kullanıcıyı manuel olarak banla — sadece sahip/admin yapabilir
    Kullanım: /ban <id> [sebep] [süre: 30m / 2h / 1d / sınırsız]
    """
    user_id = message.from_user.id
    if user_id not in admin_ids:
        bot.reply_to(message, "⚠️ Sadece yöneticiler ban uygulayabilir!")
        return
    try:
        parts = message.text.split(' ', 3)
        target_id = int(parts[1])
        reason = parts[2] if len(parts) > 2 else "Admin kararı"
        raw_dur = parts[3].strip() if len(parts) > 3 else "sınırsız"

        if target_id == OWNER_ID:
            bot.reply_to(message, "❌ Sahibi banlayamazsınız!")
            return
        if target_id in admin_ids and user_id != OWNER_ID:
            bot.reply_to(message, "❌ Sadece sahip başka yöneticileri banlar!")
            return
        if is_banned(target_id):
            bot.reply_to(message, f"⚠️ Kullanıcı {target_id} zaten banlı.")
            return

                    
        ban_until_dt = None
        duration_str = "Sınırsız"
        if raw_dur.lower() not in ('sınırsız', 'sinırsız', 'sinırsiz', 'sinirsiz', '0', 'kalıcı'):
            dur_match = re.match(r'^(\d+)(d|h|m)$', raw_dur, re.IGNORECASE)
            if dur_match:
                val, unit = int(dur_match.group(1)), dur_match.group(2).lower()
                if unit == 'd':   minutes = val * 1440; duration_str = f"{val} gün"
                elif unit == 'h': minutes = val * 60;   duration_str = f"{val} saat"
                elif unit == 'm': minutes = val;         duration_str = f"{val} dakika"
                ban_until_dt = datetime.now() + timedelta(minutes=minutes)

        ban_user(target_id, reason, ban_until_dt)
        banner_name = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
        bot.reply_to(message,
            f"🚫 Kullanıcı `{target_id}` banlandı!\n"
            f"📝 Sebep: {reason}\n"
            f"⏳ Süre: {duration_str}",
            parse_mode='Markdown')
                                                                    
        try:
            bot.send_message(target_id, get_ban_message(reason, ban_until_dt, banner_name), parse_mode='Markdown')
            logger.info(f"Ban bildirimi kullanıcıya gönderildi: {target_id}")
        except Exception as e:
            logger.warning(f"Ban bildirimi {target_id} kullanıcısına gönderilemedi: {e}")
                                                    
        if user_id != OWNER_ID:
            try:
                bot.send_message(OWNER_ID,
                    f"🚫 *Admin BAN Uyguladı*\n\n"
                    f"👮 Admin: {banner_name} (`{user_id}`)\n"
                    f"🎯 Hedef: `{target_id}`\n"
                    f"📝 Sebep: {reason}\n"
                    f"⏳ Süre: {duration_str}\n"
                    f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    parse_mode='Markdown')
            except Exception:
                pass
    except (IndexError, ValueError):
        bot.reply_to(message,
            "❌ Kullanım: `/ban <id> [sebep] [süre]`\n"
            "Örnekler:\n"
            "  `/ban 123456 Spam sınırsız`\n"
            "  `/ban 123456 Kural ihlali 7d`\n"
            "  `/ban 123456 Test 2h`",
            parse_mode='Markdown')

@bot.message_handler(commands=['unban'])
def cmd_unban(message):
    """Banli kullanicinin banini kaldir"""
    user_id = message.from_user.id
    if user_id != OWNER_ID:
        bot.reply_to(message, "Sadece sahip unban yapabilir!")
        return
    try:
        target_id = int(message.text.split(' ', 1)[1])
        unban_user(target_id)
        bot.reply_to(message, f"✅ Kullanıcı `{target_id}` unbanlandi!", parse_mode='Markdown')
        try:
            bot.send_message(target_id,
                "✅ *Banınız kaldırıldı!*\n\nArtık botu kullanabilirsiniz.\nBaşlamak için /start yazın.",
                parse_mode='Markdown')
        except Exception:
            pass
    except Exception:
        bot.reply_to(message, "Kullanim: /unban <kullanici_id>")

@bot.message_handler(commands=['addadmin'])
def cmd_addadmin(message):
    """Yönetici ekle — sadece sahip"""
    user_id = message.from_user.id
    if user_id != OWNER_ID:
        bot.reply_to(message, "⚠️ Sadece sahip yönetici ekleyebilir!")
        return
    try:
        target_id = int(message.text.split(' ', 1)[1])
        if target_id in admin_ids:
            bot.reply_to(message, f"⚠️ `{target_id}` zaten yönetici.", parse_mode='Markdown')
            return
        add_admin_db(target_id)
        bot.reply_to(message,
            f"✅ *Yönetici Eklendi!*\n\n"
            f"👤 Kullanıcı `{target_id}` artık yönetici.",
            parse_mode='Markdown')
        try:
            bot.send_message(target_id,
                "🛡️ *Tebrikler!*\n\nBot yöneticisi olarak atandınız.\nYönetici komutlarına erişebilirsiniz.",
                parse_mode='Markdown')
        except Exception:
            pass
    except (IndexError, ValueError):
        bot.reply_to(message, "❌ Kullanım: `/addadmin <kullanici_id>`", parse_mode='Markdown')

@bot.message_handler(commands=['removeadmin'])
def cmd_removeadmin(message):
    """Yönetici kaldır — sadece sahip"""
    user_id = message.from_user.id
    if user_id != OWNER_ID:
        bot.reply_to(message, "⚠️ Sadece sahip yönetici kaldırabilir!")
        return
    try:
        target_id = int(message.text.split(' ', 1)[1])
        if target_id == OWNER_ID:
            bot.reply_to(message, "❌ Sahibi kaldıramazsınız!")
            return
        if target_id not in admin_ids:
            bot.reply_to(message, f"⚠️ `{target_id}` yönetici değil.", parse_mode='Markdown')
            return
        success = remove_admin_db(target_id)
        if success:
            bot.reply_to(message, f"✅ `{target_id}` yöneticilikten kaldırıldı.", parse_mode='Markdown')
            try:
                bot.send_message(target_id, "⚠️ Yöneticilik yetkiniz kaldırıldı.")
            except Exception:
                pass
        else:
            bot.reply_to(message, "❌ İşlem başarısız.")
    except (IndexError, ValueError):
        bot.reply_to(message, "❌ Kullanım: `/removeadmin <kullanici_id>`", parse_mode='Markdown')

@bot.message_handler(commands=['admins'])
def cmd_admins(message):
    """Yönetici listesini göster"""
    user_id = message.from_user.id
    if user_id not in admin_ids:
        bot.reply_to(message, "⚠️ Yönetici yetkisi gerekli!")
        return
    lines = ["👑 *YÖNETİCİ LİSTESİ*\n"]
    for aid in sorted(admin_ids):
        role = "👑 Sahip" if aid == OWNER_ID else "🛡️ Yönetici"
        lines.append(f"{role}: `{aid}`")
    lines.append(f"\nToplam: {len(admin_ids)} yönetici")
    bot.reply_to(message, '\n'.join(lines), parse_mode='Markdown')

@bot.message_handler(commands=['userinfo'])
def cmd_userinfo(message):
    """Kullanıcı hakkında detaylı bilgi — sadece admin"""
    user_id = message.from_user.id
    if user_id not in admin_ids:
        bot.reply_to(message, "⚠️ Yönetici yetkisi gerekli!")
        return
    try:
        target_id = int(message.text.split(' ', 1)[1])
    except (IndexError, ValueError):
        bot.reply_to(message, "❌ Kullanım: `/userinfo <kullanici_id>`", parse_mode='Markdown')
        return

                   
    if target_id == OWNER_ID:          role = "👑 Sahip"
    elif target_id in admin_ids:       role = "🛡️ Yönetici"
    elif is_banned(target_id):         role = "🚫 Banlı"
    elif target_id in user_subscriptions and user_subscriptions[target_id].get('expiry', datetime.min) > datetime.now():
                                        role = "⭐ Premium"
    elif target_id in active_users:    role = "🆓 Ücretsiz"
    else:                              role = "❓ Bilinmiyor"

    files_list = user_files.get(target_id, [])
    running = sum(1 for sk, si in bot_scripts.items()
                  if si['script_owner_id'] == target_id and is_bot_running(target_id, si['file_name']))
    sub = user_subscriptions.get(target_id)
    sub_str = sub['expiry'].strftime('%Y-%m-%d') if sub else "Yok"

                
    ban_reason = ""
    if is_banned(target_id):
        try:
            conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute('SELECT ban_reason FROM banned_users WHERE user_id=?', (target_id,))
            row = c.fetchone()
            conn.close()
            ban_reason = f"\n📝 Ban Sebebi: {row[0] if row else 'Belirtilmemiş'}"
        except Exception:
            pass

    bot.reply_to(message,
        f"👤 *KULLANICI BİLGİSİ*\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"🆔 ID: `{target_id}`\n"
        f"🔰 Durum: {role}{ban_reason}\n"
        f"📁 Dosya: {len(files_list)}\n"
        f"🟢 Çalışan Bot: {running}\n"
        f"⭐ Abonelik: {sub_str}\n"
        f"━━━━━━━━━━━━━━━━",
        parse_mode='Markdown')

@bot.message_handler(commands=['kickuser'])
def cmd_kickuser(message):
    """Kullanıcının tüm dosyalarını sil (ban uygulamadan) — sadece sahip"""
    user_id = message.from_user.id
    if user_id != OWNER_ID:
        bot.reply_to(message, "⚠️ Sadece sahip bu komutu kullanabilir!")
        return
    try:
        target_id = int(message.text.split(' ', 1)[1])
        if target_id == OWNER_ID:
            bot.reply_to(message, "❌ Kendinizi kick edemezsiniz!")
            return
    except (IndexError, ValueError):
        bot.reply_to(message, "❌ Kullanım: `/kickuser <kullanici_id>`\n_(Dosyaları siler, ban uygulamaz)_", parse_mode='Markdown')
        return

                            
    stopped = 0
    for sk in list(bot_scripts.keys()):
        si = bot_scripts[sk]
        if si['script_owner_id'] == target_id:
            kill_process_tree(si)
            del bot_scripts[sk]
            stopped += 1

                   
    user_folder = get_user_folder(target_id)
    deleted_files = 0
    if os.path.exists(user_folder):
        try:
            shutil.rmtree(user_folder)
            deleted_files = len(user_files.get(target_id, []))
        except Exception as e:
            logger.error(f"kickuser klasör silme hatası: {e}")

                    
    files_to_remove = [fn for fn, ft in user_files.get(target_id, [])]
    for fn in files_to_remove:
        remove_user_file_db(target_id, fn)
    if target_id in user_files:
        del user_files[target_id]

    bot.reply_to(message,
        f"🦵 *Kick Tamamlandı!*\n\n"
        f"🆔 Kullanıcı: `{target_id}`\n"
        f"📁 Silinen dosya: {deleted_files}\n"
        f"🛑 Durdurulan bot: {stopped}\n"
        f"_(Ban uygulanmadı, giriş yapabilir)_",
        parse_mode='Markdown')
    try:
        bot.send_message(target_id,
            "⚠️ *Dikkat!*\n\nTüm dosyalarınız ve çalışan botlarınız yönetici tarafından kaldırıldı.\n"
            "Yeni dosya yüklemek için /start yazabilirsiniz.",
            parse_mode='Markdown')
    except Exception:
        pass

@bot.message_handler(commands=['lockstatus'])
def cmd_lockstatus(message):
    """Bot kilit durumunu göster"""
    user_id = message.from_user.id
    if user_id not in admin_ids:
        bot.reply_to(message, "⚠️ Yönetici yetkisi gerekli!")
        return
    if not _is_bot_locked():
        bot.reply_to(message, "🔓 *Bot şu an açık* — herkes kullanabilir.", parse_mode='Markdown')
        return
    until = lock_info.get('until')
    until_str = until.strftime('%Y-%m-%d %H:%M:%S') if until else "Süresiz"
    remaining = ""
    if until:
        secs = max(0, int((until - datetime.now()).total_seconds()))
        remaining = f"\n⏳ Kalan: {secs//60} dk {secs%60} sn"
    bot.reply_to(message,
        f"🔒 *Bot KİLİTLİ*\n\n"
        f"📝 Sebep: _{lock_info.get('reason', '-')}_\n"
        f"👤 Kilitleyen: {lock_info.get('locker_name', '?')}\n"
        f"⏰ Bitiş: {until_str}{remaining}",
        parse_mode='Markdown')

@bot.message_handler(commands=['search'])
def cmd_search(message):
    """Dosya adi arama"""
    user_id = message.from_user.id
    try:
        query = message.text.split(' ', 1)[1].lower()
    except Exception:
        bot.reply_to(message, "Kullanim: /search <dosya_adi>")
        return
    found = []
    scope = user_files if user_id in admin_ids else {user_id: user_files.get(user_id, [])}
    for uid, files in scope.items():
        for fname, ftype in files:
            if query in fname.lower():
                status = "Calisiyor" if is_bot_running(uid, fname) else "Durduruldu"
                found.append(f"{fname} ({ftype}) - Kullanici {uid} - {status}")
    if found:
        result = f"'{query}' arama sonuclari ({len(found)}):\n\n" + "\n".join(found[:20])
    else:
        result = f"'{query}' icin sonuc bulunamadi."
    bot.reply_to(message, result)

def _process_support_message_step(message):
    """Destek mesajı adımı — kullanıcının mesajını işle"""
    user_id = message.from_user.id
    if is_banned(user_id): return
    if message.text and message.text.strip() == '/cancel':
        bot.reply_to(message, "❌ İptal edildi."); return
    if not message.text or len(message.text.strip()) < 3:
        msg = bot.reply_to(message, "⚠️ Çok kısa. En az 3 karakter yazın veya /cancel.")
        bot.register_next_step_handler(msg, _process_support_message_step); return
                           
    fake_msg = type('obj', (object,), {
        'text': f"/msg {message.text.strip()}",
        'from_user': message.from_user,
        'chat': message.chat
    })()
    try:
        msg_text = message.text.strip()
        tid = ticket_counter[0]; ticket_counter[0] += 1
        support_tickets[tid] = {
            'user_id': user_id, 'message': msg_text,
            'timestamp': datetime.now(), 'status': 'open',
            'user_name': message.from_user.first_name,
            'username': message.from_user.username or 'yok'
        }
        uname = message.from_user.first_name
        uusername = message.from_user.username or 'yok'
        admin_markup = types.InlineKeyboardMarkup()
        admin_markup.add(types.InlineKeyboardButton(f"↩️ {uname}'e Cevap Ver", callback_data=f"reply_user_{user_id}_{tid}"))
        admin_markup.add(types.InlineKeyboardButton("✅ Çözüldü", callback_data=f"ticket_close_{tid}"))
        for aid in admin_ids:
            try:
                bot.send_message(aid,
                    f"📩 *YENİ DESTEK TALEBİ — #{tid}*\n\n"
                    f"👤 {uname} | 🆔 `{user_id}` | @{uusername}\n"
                    f"🕐 {datetime.now().strftime('%d/%m %H:%M')}\n\n"
                    f"💬 _{msg_text}_",
                    parse_mode='Markdown', reply_markup=admin_markup)
            except Exception: pass
        bot.reply_to(message,
            f"✅ *Destek talebiniz alındı!*\n🎫 Talep #`{tid}`\nYanıt gelince bildirim alacaksınız.",
            parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Support step hatası: {e}")
        bot.reply_to(message, "❌ Mesaj gönderilirken hata oluştu.")

def _process_admin_reply_step(message, target_uid: int, ticket_id: int):
    """Admin yanıt adımı"""
    admin_id = message.from_user.id
    if admin_id not in admin_ids: return
    if message.text and message.text.strip() == '/cancel':
        bot.reply_to(message, "❌ İptal edildi.")
        if admin_id in admin_reply_to: del admin_reply_to[admin_id]
        return
    if not message.text:
        msg = bot.reply_to(message, "⚠️ Metin girin veya /cancel.")
        bot.register_next_step_handler(msg, lambda m: _process_admin_reply_step(m, target_uid, ticket_id))
        return
    reply_text = message.text.strip()
    sender_name = message.from_user.first_name
    try:
        bot.send_message(target_uid,
            f"📨 *YÖNETİCİ YANITI*\n\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"👤 Yanıtlayan: *{sender_name}*\n"
            f"━━━━━━━━━━━━━━━━\n\n"
            f"💬 _{reply_text}_\n\n"
            f"📌 Yanıtlamak için: /msg <mesajınız>",
            parse_mode='Markdown')
        bot.reply_to(message, f"✅ Yanıt `{target_uid}` kullanıcısına gönderildi!")
        if ticket_id in support_tickets:
            support_tickets[ticket_id]['status'] = 'answered'
    except Exception as e:
        bot.reply_to(message, f"❌ Gönderilemedi: {e}")
    if admin_id in admin_reply_to: del admin_reply_to[admin_id]

def reduce_subscription_init_callback(call):
    """Abonelik azaltma callback başlangıcı"""
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id,
        "➖ *Abonelik Azalt*\n\nKullanıcı ID ve azaltılacak gün sayısını girin.\nFormat: `ID gün`\nÖrnek: `12345678 7`\n\n/cancel ile iptal.",
        parse_mode='Markdown')
    bot.register_next_step_handler(msg, _process_reduce_subscription_step)

def _process_reduce_subscription_step(message):
    admin_id = message.from_user.id
    if admin_id not in admin_ids: return
    if message.text and message.text.strip().lower() == '/cancel':
        bot.reply_to(message, "❌ İptal edildi."); return
    try:
        parts = message.text.split()
        target_id = int(parts[0]); days = int(parts[1])
        if days <= 0: raise ValueError
    except (ValueError, IndexError):
        msg = bot.reply_to(message, "⚠️ Format: `ID gün` (örn: `12345678 7`) veya /cancel", parse_mode='Markdown')
        bot.register_next_step_handler(msg, _process_reduce_subscription_step); return
    ok, result = reduce_subscription_db(target_id, days)
    if not ok:
        bot.reply_to(message, f"⚠️ {result}"); return
    if result == "removed":
        bot.reply_to(message, f"✅ `{target_id}` için abonelik {days} gün azaltıldı ve sıfırlandı.", parse_mode='Markdown')
        try: bot.send_message(target_id, "ℹ️ Aboneliğiniz kısaltıldı ve süresi doldu.")
        except Exception: pass
    else:
        bot.reply_to(message, f"✅ `{target_id}` için {days} gün azaltıldı. Yeni bitiş: {result.strftime('%Y-%m-%d')}", parse_mode='Markdown')
        try: bot.send_message(target_id, f"ℹ️ Aboneliğiniz {days} gün kısaltıldı. Yeni bitiş: {result.strftime('%Y-%m-%d')}")
        except Exception: pass


def watchdog_thread():
    """Durmus bot kayitlarini periyodik temizle"""
    logger.info("Watchdog basladi")
    while True:
        try:
            time.sleep(60)
            for script_key in list(bot_scripts.keys()):
                si = bot_scripts.get(script_key)
                if si and not is_bot_running(si.get('script_owner_id'), si.get('file_name', '')):
                    logger.warning(f"Watchdog: {script_key} durmus, temizleniyor.")
                    del bot_scripts[script_key]
        except Exception as e:
            logger.error(f"Watchdog hatasi: {e}")

watchdog_t = threading.Thread(target=watchdog_thread, daemon=True)
watchdog_t.start()

                                            

                                                              
                                        
                                                     
                                                              

BOT_RESTART_LOG = []                                                         
BOT_RESTART_COUNTS = {}                          
BOT_AUTO_RESTART_ENABLED = {}                                       
_MAX_AUTO_RESTART = 5                                           

def auto_restart_bot(script_key, user_id, file_name, file_type, user_folder, chat_id):
    """Bot çöküldüğünde otomatik yeniden başlatma"""
    count = BOT_RESTART_COUNTS.get(script_key, 0) + 1
    BOT_RESTART_COUNTS[script_key] = count

    log_entry = {
        'file_name': file_name,
        'user_id': user_id,
        'restart_time': datetime.now().isoformat(),
        'attempt': count
    }
    BOT_RESTART_LOG.append(log_entry)
    if len(BOT_RESTART_LOG) > 200:
        BOT_RESTART_LOG.pop(0)

    logger.warning(f"🔄 OTO-RESTART #{count}: {script_key} (kullanıcı: {user_id})")

    if count > _MAX_AUTO_RESTART:
        try:
            bot.send_message(chat_id,
                f"⛔ *Otomatik Restart Durdu*\n\n"
                f"📄 Dosya: `{file_name}`\n"
                f"🔁 {_MAX_AUTO_RESTART} denemeden sonra durduruldu.\n"
                f"Lütfen dosyayı kontrol edip manuel başlatın.",
                parse_mode='Markdown')
        except Exception: pass
        return

    time.sleep(5)
    fp = os.path.join(user_folder, file_name)
    if not os.path.exists(fp):
        logger.error(f"OTO-RESTART: {fp} bulunamadı, iptal.")
        return

    class FakeMsg:
        class chat:
            id = chat_id
        message_id = 0
        class from_user:
            id = user_id

    try:
        bot.send_message(chat_id,
            f"🔄 *Otomatik Yeniden Başlatma* #{count}\n\n"
            f"📄 `{file_name}` çöktü. {3}sn içinde yeniden başlatılıyor...\n"
            f"🕐 {datetime.now().strftime('%H:%M:%S')}",
            parse_mode='Markdown')
    except Exception: pass

    if file_type == 'py':
        threading.Thread(target=run_script, args=(fp, user_id, user_folder, file_name, FakeMsg())).start()
    elif file_type == 'js':
        threading.Thread(target=run_js_script, args=(fp, user_id, user_folder, file_name, FakeMsg())).start()

def _watch_bot_process(script_key, user_id, file_name, file_type, user_folder, chat_id):
    """Çalışan bir bot process'ini izle, çökünce auto-restart tetikle"""
    while True:
        time.sleep(10)
        si = bot_scripts.get(script_key)
        if not si:
            break
        proc = si.get('process')
        if proc and proc.poll() is not None:
            logger.warning(f"Process çöktü: {script_key}")
            if script_key in bot_scripts:
                del bot_scripts[script_key]
            if BOT_AUTO_RESTART_ENABLED.get(script_key, True):
                auto_restart_bot(script_key, user_id, file_name, file_type, user_folder, chat_id)
            break

@bot.message_handler(commands=['restart_log', 'yeniden_log'])
def cmd_restart_log(message):
    """Otomatik restart loglarını göster"""
    user_id = message.from_user.id
    if is_banned(user_id): return
    if user_id in admin_ids:
        logs = BOT_RESTART_LOG[-20:]
    else:
        logs = [l for l in BOT_RESTART_LOG if l['user_id'] == user_id][-10:]
    if not logs:
        bot.reply_to(message, "📜 Henüz otomatik restart kaydı yok.")
        return
    lines = ["🔄 *Otomatik Restart Kayıtları:*\n"]
    for l in reversed(logs):
        uid_info = f" (ID:{l['user_id']})" if user_id in admin_ids else ""
        lines.append(f"🔁 `{l['file_name']}`{uid_info} — Deneme #{l['attempt']} — {l['restart_time'][:16]}")
    bot.reply_to(message, '\n'.join(lines), parse_mode='Markdown')

@bot.message_handler(commands=['auto_restart_off', 'auto_restart_on'])
def cmd_toggle_auto_restart(message):
    """Belirli bot için otomatik restart aç/kapat"""
    user_id = message.from_user.id
    if is_banned(user_id): return
    try:
        file_name = message.text.split(' ', 1)[1].strip()
    except IndexError:
        bot.reply_to(message, "Kullanım: `/auto_restart_off bot.py` veya `/auto_restart_on bot.py`", parse_mode='Markdown')
        return
    script_key = f"{user_id}_{file_name}"
    enable = 'on' in message.text.split()[0].lower()
    BOT_AUTO_RESTART_ENABLED[script_key] = enable
    status = "✅ Açık" if enable else "❌ Kapalı"
    bot.reply_to(message, f"🔄 `{file_name}` otomatik restart: *{status}*", parse_mode='Markdown')


                                                              
                                
                                                         
                                                              

USER_ANALYTICS = {}                                                                                                

def _update_analytics(user_id, event_type='command'):
    """Kullanıcı analitiğini güncelle"""
    if user_id not in USER_ANALYTICS:
        USER_ANALYTICS[user_id] = {
            'bot_starts': 0, 'commands': 0,
            'last_active': datetime.now().isoformat(),
            'total_uptime_min': 0
        }
    USER_ANALYTICS[user_id]['last_active'] = datetime.now().isoformat()
    if event_type == 'bot_start':
        USER_ANALYTICS[user_id]['bot_starts'] += 1
    else:
        USER_ANALYTICS[user_id]['commands'] += 1

@bot.message_handler(commands=['analytics', 'analitik'])
def cmd_analytics(message):
    """Kullanıcı analitik paneli"""
    user_id = message.from_user.id
    if is_banned(user_id): return

    if user_id in admin_ids:
                                         
        sorted_users = sorted(
            USER_ANALYTICS.items(),
            key=lambda x: x[1].get('commands', 0) + x[1].get('bot_starts', 0) * 3,
            reverse=True
        )[:15]
        lines = ["📊 *KULLANICI ANALİTİK PANELİ* (Admin)\n━━━━━━━━━━━━━━━━"]
        for uid, data in sorted_users:
            last = data.get('last_active', '')[:16].replace('T', ' ')
            lines.append(
                f"👤 `{uid}`\n"
                f"   🤖 Bot Başlatma: {data.get('bot_starts', 0)}  |  📟 Komut: {data.get('commands', 0)}\n"
                f"   🕐 Son: {last}"
            )
        if not sorted_users:
            lines.append("_(Veri yok)_")
        lines.append("━━━━━━━━━━━━━━━━")
        bot.reply_to(message, '\n'.join(lines), parse_mode='Markdown')
    else:
                                        
        data = USER_ANALYTICS.get(user_id, {'bot_starts': 0, 'commands': 0, 'last_active': '-', 'total_uptime_min': 0})
        running = sum(1 for sk, si in bot_scripts.items() if si.get('script_owner_id') == user_id and is_bot_running(user_id, si.get('file_name', '')))
        bot.reply_to(message,
            f"📊 *ANALİTİK PANELİNİZ*\n\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"🤖 Toplam Bot Başlatma: *{data.get('bot_starts', 0)}*\n"
            f"📟 Toplam Komut: *{data.get('commands', 0)}*\n"
            f"🟢 Şu An Çalışan: *{running}*\n"
            f"🕐 Son Aktivite: `{data.get('last_active', '-')[:16].replace('T', ' ')}`\n"
            f"━━━━━━━━━━━━━━━━",
            parse_mode='Markdown')


                                                              
                                                                   
                                                              

_SENSITIVE_PATTERNS = [
    (re.compile(r'(TOKEN\s*=\s*["\'])([^"\']{10,})', re.IGNORECASE), r'\1***MASKED***'),
    (re.compile(r'(API_KEY\s*=\s*["\'])([^"\']{6,})', re.IGNORECASE), r'\1***MASKED***'),
    (re.compile(r'(password\s*=\s*["\'])([^"\']{4,})', re.IGNORECASE), r'\1***MASKED***'),
    (re.compile(r'(secret\s*=\s*["\'])([^"\']{4,})', re.IGNORECASE), r'\1***MASKED***'),
    (re.compile(r'\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b'), r'***IP***'),
    (re.compile(r'\b(\d{8,12}:[A-Za-z0-9_\-]{30,50})\b'), r'***BOT_TOKEN***'),
]

def mask_sensitive_data(text: str) -> str:
    """Token/IP içeren metni maskele"""
    result = text
    for pattern, replacement in _SENSITIVE_PATTERNS:
        result = pattern.sub(replacement, result)
    return result

_LEAK_DESCRIPTIONS = ['TOKEN', 'API_KEY', 'PASSWORD', 'SECRET', 'IP_ADDRESS', 'BOT_TOKEN']

def check_file_for_leaks(file_path: str) -> list:
    """Dosyada token/IP/şifre sızıntısı var mı kontrol et — bulunanları satır ve değer ile göster"""
    findings = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines_content = f.readlines()
        for lineno, line in enumerate(lines_content, 1):
            for i, pattern_tuple in enumerate(_SENSITIVE_PATTERNS):
                pattern = pattern_tuple[0]
                matches = pattern.findall(line)
                if matches:
                    desc = _LEAK_DESCRIPTIONS[i] if i < len(_LEAK_DESCRIPTIONS) else 'HASSAS_VERİ'
                    for m in matches:
                        val = ''.join(m) if isinstance(m, tuple) else str(m)
                        display_val = val if len(val) <= 60 else val[:57] + '...'
                        findings.append(f"⚠️ *{desc}* — satır {lineno}:\n`{display_val}`")
    except Exception as e:
        findings.append(f"Dosya okunamadı: {e}")
    return findings

@bot.message_handler(commands=['check_leaks', 'siziinti_kontrol'])
def cmd_check_leaks(message):
    """Yüklü bot dosyalarında token/IP sızıntısı kontrol et.
    Admin ve whitelist kullanıcıları tüm taramalardan muaftır."""
    user_id = message.from_user.id
    if is_banned(user_id): return
    is_exempt = user_id in admin_ids or user_id in malware_whitelist
    files = user_files.get(user_id, [])
    if not files:
        bot.reply_to(message, "📂 Kontrol edilecek dosya yok.")
        return
    user_folder = get_user_folder(user_id)
    exempt_note = "\n_ℹ️ Hesabınız tüm taramalardan muaftır (yönetici/whitelist)._\n" if is_exempt else ""
    lines = [f"🔐 *TOKEN/IP SIZIINTI TARAMASI*{exempt_note}\n━━━━━━━━━━━━━━━━"]
    found_any = False
    for fname, ftype in files:
        fpath = os.path.join(user_folder, fname)
        if not os.path.exists(fpath):
            continue
        findings = check_file_for_leaks(fpath)
        if findings:
            found_any = True
            lines.append(f"\n📄 `{fname}`:")
            for finding in findings:
                lines.append(f"  {finding}")
        else:
            lines.append(f"✅ `{fname}` — Temiz")
    if not found_any:
        lines.append("\n✅ Tüm dosyalar temiz, sızıntı bulunamadı!")
    lines.append("━━━━━━━━━━━━━━━━")
    full_text = '\n'.join(lines)
    if len(full_text) > 4000:
        chunks = [full_text[i:i+4000] for i in range(0, len(full_text), 4000)]
        for chunk in chunks:
            bot.reply_to(message, chunk, parse_mode='Markdown')
    else:
        bot.reply_to(message, full_text, parse_mode='Markdown')


                                                              
                                                              
                                                               
                                                              

BOT_VERSIONS = {}                                                                              
_VERSION_DIR = os.path.join(BASE_DIR, 'bot_versions')
os.makedirs(_VERSION_DIR, exist_ok=True)

def save_bot_version(user_id: int, file_name: str, file_path: str):
    """Mevcut dosyayı versiyonla sakla"""
    if not os.path.exists(file_path):
        return
    key = f"{user_id}_{file_name}"
    versions = BOT_VERSIONS.get(key, [])
    version_num = len(versions) + 1
    version_path = os.path.join(_VERSION_DIR, f"{key}_v{version_num}.bak")
    try:
        shutil.copy2(file_path, version_path)
        versions.append({
            'version': version_num,
            'path': version_path,
            'saved_at': datetime.now().isoformat(),
            'size': os.path.getsize(file_path)
        })
                                   
        if len(versions) > 5:
            old = versions.pop(0)
            try: os.remove(old['path'])
            except Exception: pass
        BOT_VERSIONS[key] = versions
        logger.info(f"Versiyon kaydedildi: {key} v{version_num}")
    except Exception as e:
        logger.error(f"Versiyon kaydetme hatası: {e}")

                                                           
@bot.message_handler(commands=['ip', 'sunucuip'])
def cmd_server_ip(message):
    """/ip — Sunucunun genel IP ve konum bilgisini göster (sadece admin)"""
    user_id = message.from_user.id
    if user_id not in admin_ids:
        bot.reply_to(message, "⚠️ Yönetici yetkisi gerekli!"); return
    wait_msg = bot.reply_to(message, "🌐 IP bilgisi alınıyor...")
    try:
        import socket
        local_ip = socket.gethostbyname(socket.gethostname())
        hostname = socket.gethostname()
        resp = requests.get("https://ipapi.co/json/", timeout=8)
        data = resp.json()
        public_ip   = data.get('ip', 'Bilinmiyor')
        country     = data.get('country_name', 'Bilinmiyor')
        city        = data.get('city', 'Bilinmiyor')
        org         = data.get('org', 'Bilinmiyor')
        asn         = data.get('asn', 'Bilinmiyor')
        timezone    = data.get('timezone', 'Bilinmiyor')
        result = (
            f"🌐 *SUNUCU IP BİLGİSİ*\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"🖥️ Hostname: `{hostname}`\n"
            f"🔒 Yerel IP: `{local_ip}`\n"
            f"🌍 Genel IP: `{public_ip}`\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"🏳️ Ülke: {country}\n"
            f"🏙️ Şehir: {city}\n"
            f"🏢 Sağlayıcı: {org}\n"
            f"🔢 ASN: {asn}\n"
            f"⏰ Zaman Dilimi: {timezone}\n"
            f"━━━━━━━━━━━━━━━━"
        )
        bot.edit_message_text(result, message.chat.id, wait_msg.message_id, parse_mode='Markdown')
    except requests.exceptions.RequestException:
        import socket
        try:
            local_ip = socket.gethostbyname(socket.gethostname())
            hostname = socket.gethostname()
        except Exception:
            local_ip = 'Bilinmiyor'
            hostname = 'Bilinmiyor'
        bot.edit_message_text(
            f"🌐 *SUNUCU IP (Çevrimdışı)*\n\n"
            f"🖥️ Hostname: `{hostname}`\n"
            f"🔒 Yerel IP: `{local_ip}`\n"
            f"⚠️ Genel IP alınamadı (ağ hatası)",
            message.chat.id, wait_msg.message_id, parse_mode='Markdown')
    except Exception as e:
        bot.edit_message_text(f"❌ IP bilgisi alınamadı: {e}", message.chat.id, wait_msg.message_id)

KNOWN_COMMANDS.update({'ip', 'sunucuip'})


                                                            
@bot.message_handler(commands=['ping'])
def cmd_ping(message):
    """/ping — Bot yanıt süresini ölç"""
    user_id = message.from_user.id
    if is_banned(user_id): return
    t0 = time.time()
    sent = bot.reply_to(message, "⏱️ Pong...")
    t1 = time.time()
    latency_ms = round((t1 - t0) * 1000)
    uptime_h = round((datetime.now() - performance_tracker.start_time).total_seconds() / 3600, 1)
    emoji = "🟢" if latency_ms < 500 else ("🟡" if latency_ms < 1500 else "🔴")
    bot.edit_message_text(
        f"{emoji} *Pong!*\n\n"
        f"⚡ Gecikme: `{latency_ms}ms`\n"
        f"⏱️ Uptime: `{uptime_h}s`\n"
        f"🤖 Çalışan bot: `{len(bot_scripts)}`",
        message.chat.id, sent.message_id, parse_mode='Markdown')

KNOWN_COMMANDS.add('ping')


                                                            
@bot.message_handler(commands=['diskusage', 'disk'])
def cmd_disk_usage(message):
    """/diskusage — Kullanıcı disk kullanımı (admin: tüm kullanıcılar)"""
    user_id = message.from_user.id
    if user_id not in admin_ids:
                                
        folder = get_user_folder(user_id)
        size_mb = file_manager.get_directory_size(folder)
        file_count = get_user_file_count(user_id)
        limit = get_user_file_limit(user_id)
        limit_str = str(limit) if limit != float('inf') else "∞"
        bot.reply_to(message,
            f"💾 *DİSK KULLANIMIM*\n\n"
            f"📁 Dosya sayısı: `{file_count}/{limit_str}`\n"
            f"💿 Kullanılan alan: `{size_mb:.2f} MB`",
            parse_mode='Markdown')
        return
                             
    wait_msg = bot.reply_to(message, "⏳ Disk kullanımı hesaplanıyor...")
    lines = ["💾 *TÜM KULLANICI DİSK KULLANIMI*\n━━━━━━━━━━━━━━━━"]
    total_mb = 0.0
    entries = []
    for uid in list(user_files.keys()):
        folder = get_user_folder(uid)
        size_mb = file_manager.get_directory_size(folder)
        fc = get_user_file_count(uid)
        entries.append((uid, size_mb, fc))
        total_mb += size_mb
    entries.sort(key=lambda x: x[1], reverse=True)
    for uid, size_mb, fc in entries[:15]:
        role = "👑" if uid == OWNER_ID else ("🛡️" if uid in admin_ids else "👤")
        lines.append(f"{role} `{uid}` — {fc} dosya | `{size_mb:.1f} MB`")
    lines.append(f"━━━━━━━━━━━━━━━━\n📊 Toplam: `{total_mb:.1f} MB`")
    bot.edit_message_text('\n'.join(lines), message.chat.id, wait_msg.message_id, parse_mode='Markdown')

KNOWN_COMMANDS.update({'diskusage', 'disk'})


                                                           
def _auto_backup_scheduler():
    """Her gece 03:00'da otomatik yedek al (sadece veritabanı)"""
    while True:
        try:
            now = datetime.now()
                                     
            next_run = now.replace(hour=3, minute=0, second=0, microsecond=0)
            if now >= next_run:
                next_run += timedelta(days=1)
            wait_secs = (next_run - now).total_seconds()
            time.sleep(wait_secs)
                      
            backup_path = os.path.join(IROTECH_DIR, f"auto_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip")
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                if os.path.exists(DATABASE_PATH):
                    zf.write(DATABASE_PATH, 'bot_data.db')
                              
                activity_db = os.path.join(IROTECH_DIR, 'activities.json')
                if os.path.exists(activity_db):
                    zf.write(activity_db, 'activities.json')
            backup_size_kb = os.path.getsize(backup_path) / 1024
            logger.info(f"✅ Otomatik yedek alındı: {backup_path} ({backup_size_kb:.1f} KB)")
                           
            try:
                bot.send_message(OWNER_ID,
                    f"💾 *Otomatik Yedek Alındı*\n\n"
                    f"📅 Tarih: `{datetime.now().strftime('%Y-%m-%d %H:%M')}`\n"
                    f"💿 Boyut: `{backup_size_kb:.1f} KB`\n"
                    f"📁 Konum: `{os.path.basename(backup_path)}`",
                    parse_mode='Markdown')
            except Exception: pass
                                                
            cutoff = time.time() - (7 * 86400)
            for f in os.listdir(IROTECH_DIR):
                if f.startswith('auto_backup_') and f.endswith('.zip'):
                    fp = os.path.join(IROTECH_DIR, f)
                    if os.path.getmtime(fp) < cutoff:
                        try: os.remove(fp)
                        except Exception: pass
        except Exception as e:
            logger.error(f"Auto backup scheduler hatası: {e}")
            time.sleep(3600)                            

                    
_auto_backup_thread = threading.Thread(target=_auto_backup_scheduler, daemon=True)
_auto_backup_thread.start()
logger.info("🔄 Otomatik backup scheduler başlatıldı (her gece 03:00)")



                          
def cleanup():
    logger.warning("Kapatılıyor. İşlemler temizleniyor...")
    script_keys_to_stop = list(bot_scripts.keys())
    if not script_keys_to_stop: logger.info("Çalışan betik yok. Çıkılıyor."); return
    logger.info(f"{len(script_keys_to_stop)} betik durduruluyor...")
    for key in script_keys_to_stop:
        if key in bot_scripts: logger.info(f"Durduruluyor: {key}"); kill_process_tree(bot_scripts[key])
        else: logger.info(f"{key} betiği zaten kaldırılmış.")
    logger.warning("Temizlik tamamlandı.")
atexit.register(cleanup)

                        
if __name__ == '__main__':
    logger.info("="*40 + "\n🤖 Bot Başlatılıyor...\n" + f"🐍 Python: {sys.version.split()[0]}\n" +
                f"🔧 Ana Dizin: {BASE_DIR}\n📁 Yükleme Dizini: {UPLOAD_BOTS_DIR}\n" +
                f"📊 Veri Dizini: {IROTECH_DIR}\n🔑 Sahip ID: {OWNER_ID}\n🛡️ Yöneticiler: {admin_ids}\n" + "="*40)
    keep_alive()
    logger.info("🚀 Polling başlatılıyor...")
    while True:
        try:
            bot.infinity_polling(logger_level=logging.INFO, timeout=60, long_polling_timeout=30)
        except requests.exceptions.ReadTimeout: logger.warning("Polling ReadTimeout. 5sn içinde yeniden başlatılıyor..."); time.sleep(5)
        except requests.exceptions.ConnectionError as ce: logger.error(f"Polling Bağlantı Hatası: {ce}. 15sn içinde yeniden deneniyor..."); time.sleep(15)
        except Exception as e:
            logger.critical(f"💥 Kurtarılamaz polling hatası: {e}", exc_info=True)
            logger.info("Kritik hata nedeniyle polling 30sn içinde yeniden başlatılıyor..."); time.sleep(30)
        finally: logger.warning("Polling denemesi tamamlandı. Döngüde yeniden başlatılacak."); time.sleep(1)