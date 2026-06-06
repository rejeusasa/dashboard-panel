"""
Konfigurasi Dashboard Panel
"""
import os
from pathlib import Path

# ==========================================
# 📍 PATHS
# ==========================================
BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = BASE_DIR / "backend"
WORK_DIR = os.environ.get("WORK_DIR", "/app")  # Default untuk Docker

# ==========================================
# 🔐 AUTHENTICATION
# ==========================================
AUTH_KEY = os.environ.get("AUTH_KEY", "GHOST_SECRET_2026")
SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key-change-this")
JWT_SECRET = os.environ.get("JWT_SECRET", "jwt-secret-change-this")

# Default users (production: gunakan database)
DEFAULT_USERS = {
    "admin": {
        "password": "admin123",
        "role": "admin"
    },
    "operator": {
        "password": "operator123",
        "role": "operator"
    },
    "viewer": {
        "password": "viewer123",
        "role": "viewer"
    }
}

# ==========================================
# 🤖 BOT CONFIGURATION
# ==========================================
PANEL_URL = os.environ.get("PANEL_URL", "https://ghost.devdot.qzz.io")
PANEL_URLS = [PANEL_URL]

# Bot files
FILE_LOGIN = "login.py"
FILE_LOOP = "loop.py"
LOG_FILE = os.path.join(WORK_DIR, "bot_log.txt")
EMAIL_FILE = os.path.join(WORK_DIR, "email.txt")
LINK_FILE = os.path.join(WORK_DIR, "link.txt")
MAPPING_FILE = os.path.join(WORK_DIR, "mapping_profil.txt")
HISTORY_FILE = os.path.join(WORK_DIR, "history_sukses.txt")
MONITOR_FILE = os.path.join(WORK_DIR, "monitor.json")
PROFILE_DIR = os.path.join(WORK_DIR, "chrome_profiles")

# ==========================================
# 🌐 SERVER CONFIGURATION
# ==========================================
FLASK_ENV = os.environ.get("FLASK_ENV", "development")
FLASK_DEBUG = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", 5000))
CORS_ORIGIN = os.environ.get("CORS_ORIGIN", "http://localhost:5173")

# ==========================================
# 📊 MONITORING CONFIGURATION
# ==========================================
MONITOR_INTERVAL = 2  # seconds
LOG_TAIL_LINES = 50
WORKER_TIMEOUT = 43200  # 12 hours
PROCESS_CHECK_INTERVAL = 5  # seconds

# ==========================================
# 🔔 NOTIFICATIONS
# ==========================================
ENABLE_NOTIFICATIONS = os.environ.get("ENABLE_NOTIFICATIONS", "True").lower() == "true"
NOTIFICATION_WEBHOOK = os.environ.get("NOTIFICATION_WEBHOOK", "")

# ==========================================
# 📁 FILE MONITORING
# ==========================================
WATCH_FILES = {
    "bot_log": LOG_FILE,
    "email": EMAIL_FILE,
    "link": LINK_FILE,
    "mapping": MAPPING_FILE,
    "history": HISTORY_FILE,
    "monitor": MONITOR_FILE
}

# ==========================================
# 🛡️ SECURITY
# ==========================================
ALLOWED_UPLOAD_EXTENSIONS = {'txt', 'json', 'csv'}
MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50MB

# ==========================================
# 📈 LOGGING
# ==========================================
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ==========================================
# 🔗 EXTERNAL SERVICES (Optional)
# ==========================================
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///dashboard.db")
