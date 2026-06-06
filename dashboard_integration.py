"""
DASHBOARD INTEGRATION MODULE
Mengintegrasikan logging otomatis dari agent.py, login.py, loop.py, dan modul_bot.py
Inject ke sistem monitoring tanpa mengubah logic utama
"""

import os
import sys
import time
import threading
import json
import sqlite3
from datetime import datetime
from functools import wraps
import requests

# ==========================================
# KONFIGURASI INTEGRATION
# ==========================================
DASHBOARD_API = os.environ.get('DASHBOARD_API', 'http://localhost:7861/api/dashboard')
BATCH_ID = f"batch_{int(time.time())}"
METRICS_QUEUE = []
METRICS_LOCK = threading.Lock()

class DashboardLogger:
    """
    Logger yang tidak invasif untuk tracking events & metrics
    Bisa diimport dan dipakai dari modul manapun
    """
    
    def __init__(self, db_path="dashboard_metrics.db"):
        self.db_path = db_path
        self.ensure_db()
    
    def ensure_db(self):
        """Buat/pastikan database ada"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    event_type TEXT,
                    profile_name TEXT,
                    status TEXT,
                    message TEXT,
                    duration INTEGER,
                    metadata TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS worker_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_name TEXT UNIQUE,
                    total_links_processed INTEGER DEFAULT 0,
                    successful_links INTEGER DEFAULT 0,
                    failed_links INTEGER DEFAULT 0,
                    total_runtime INTEGER DEFAULT 0,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS email_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE,
                    login_timestamp DATETIME,
                    profile_name TEXT,
                    success BOOLEAN,
                    error_msg TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS batch_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    batch_id TEXT UNIQUE,
                    start_time DATETIME,
                    end_time DATETIME,
                    total_workers INTEGER,
                    total_links INTEGER,
                    successful_links INTEGER,
                    failed_links INTEGER,
                    status TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"❌ Database initialization error: {e}")
    
    def log_event(self, event_type, profile_name="SYSTEM", status="INFO", message="", duration=0, metadata=None):
        """
        Log event ke database
        
        Contoh penggunaan:
            logger.log_event('LOGIN', 'dotaja01', 'SUCCESS', 'Email login berhasil')
            logger.log_event('LINK_PROCESS', 'dotaja02', 'SUCCESS', 'Iframe detected', metadata={'link': 'https://...'})
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            meta_str = json.dumps(metadata) if metadata else None
            
            cursor.execute('''
                INSERT INTO events (event_type, profile_name, status, message, duration, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (event_type, profile_name, status, message, duration, meta_str))
            
            conn.commit()
            conn.close()
            print(f"📊 [{event_type}] {profile_name}: {message}", flush=True)
        except Exception as e:
            print(f"❌ Log event error: {e}")
    
    def log_login(self, email, profile_name, success=True, error_msg=""):
        """Track email login"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO email_history (email, login_timestamp, profile_name, success, error_msg)
                VALUES (?, CURRENT_TIMESTAMP, ?, ?, ?)
            ''', (email, profile_name, success, error_msg if not success else ""))
            
            conn.commit()
            conn.close()
            
            status = "✅ SUCCESS" if success else f"❌ FAILED: {error_msg}"
            self.log_event('LOGIN', profile_name, 'SUCCESS' if success else 'ERROR', 
                          f"Email login attempt: {email} - {status}")
        except Exception as e:
            print(f"❌ Login tracking error: {e}")
    
    def update_worker_stats(self, profile_name, links_processed=0, successful=0, failed=0, runtime=0):
        """Update worker performance"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO worker_stats 
                (profile_name, total_links_processed, successful_links, failed_links, total_runtime, last_updated)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (profile_name, links_processed, successful, failed, runtime))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"❌ Worker stats update error: {e}")
    
    def log_link_process(self, profile_name, link, success=True, message=""):
        """Track link processing"""
        self.log_event(
            'LINK_PROCESS',
            profile_name,
            'SUCCESS' if success else 'FAILED',
            message,
            metadata={'link': link}
        )
    
    def start_batch(self, total_workers, total_links):
        """Mark batch start"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO batch_history (batch_id, start_time, total_workers, total_links, status)
                VALUES (?, CURRENT_TIMESTAMP, ?, ?, 'RUNNING')
            ''', (BATCH_ID, total_workers, total_links))
            
            conn.commit()
            conn.close()
            self.log_event('BATCH_START', 'SYSTEM', 'INFO', 
                          f"Batch started: {total_workers} workers, {total_links} links")
        except Exception as e:
            print(f"❌ Batch start error: {e}")
    
    def end_batch(self, successful_links, failed_links):
        """Mark batch end"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE batch_history 
                SET end_time = CURRENT_TIMESTAMP, 
                    successful_links = ?,
                    failed_links = ?,
                    status = 'COMPLETED'
                WHERE batch_id = ?
            ''', (successful_links, failed_links, BATCH_ID))
            
            conn.commit()
            conn.close()
            self.log_event('BATCH_END', 'SYSTEM', 'INFO',
                          f"Batch ended: {successful_links} successful, {failed_links} failed")
        except Exception as e:
            print(f"❌ Batch end error: {e}")

# ==========================================
# GLOBAL LOGGER INSTANCE
# ==========================================
dashboard_logger = DashboardLogger()

# ==========================================
# DECORATOR UNTUK AUTO-LOGGING
# ==========================================
def track_execution(event_type="EXECUTION", profile_name_arg=None):
    """
    Decorator untuk auto-track function execution
    
    Contoh:
        @track_execution("LOGIN", "profile_name")
        def login_user(profile_name, password):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            profile_name = "SYSTEM"
            
            # Extract profile name dari args/kwargs
            if profile_name_arg:
                if isinstance(profile_name_arg, int) and profile_name_arg < len(args):
                    profile_name = str(args[profile_name_arg])
                elif profile_name_arg in kwargs:
                    profile_name = str(kwargs[profile_name_arg])
            
            try:
                result = func(*args, **kwargs)
                duration = int(time.time() - start_time)
                dashboard_logger.log_event(
                    event_type, profile_name, 'SUCCESS',
                    f"{func.__name__} completed", duration
                )
                return result
            except Exception as e:
                duration = int(time.time() - start_time)
                dashboard_logger.log_event(
                    event_type, profile_name, 'ERROR',
                    f"{func.__name__} failed: {str(e)}", duration
                )
                raise
        return wrapper
    return decorator

# ==========================================
# HELPER FUNCTIONS UNTUK DIPAKAI MODUL LAIN
# ==========================================
def log_login_attempt(email, profile_name, success=True, error=""):
    """Wrapper untuk tracking login"""
    dashboard_logger.log_login(email, profile_name, success, error)

def log_link_processing(profile_name, link, success=True, message=""):
    """Wrapper untuk tracking link processing"""
    dashboard_logger.log_link_process(profile_name, link, success, message)

def update_worker_performance(profile_name, links_processed, successful, failed, runtime):
    """Wrapper untuk update worker stats"""
    dashboard_logger.update_worker_stats(profile_name, links_processed, successful, failed, runtime)

def mark_batch_start(total_workers, total_links):
    """Mark batch start"""
    dashboard_logger.start_batch(total_workers, total_links)

def mark_batch_end(successful, failed):
    """Mark batch end"""
    dashboard_logger.end_batch(successful, failed)

# ==========================================
# AUTO-INJECT KE MODUL YANG ADA (OPTIONAL)
# ==========================================
def inject_into_agent():
    """
    Inject dashboard logging ke agent.py
    Tambahkan line ini ke agent.py:
        from dashboard_integration import dashboard_logger
        
    Kemudian replace:
        log_event(...) dengan dashboard_logger.log_event(...)
        report_status(...) dengan logging ke dashboard
    """
    pass

def inject_into_login():
    """
    Inject ke login.py
    Tambahkan:
        from dashboard_integration import log_login_attempt
        
    Kemudian di bagian login success:
        log_login_attempt(EMAIL, folder_name, True)
    """
    pass

def inject_into_modul_bot():
    """
    Inject ke modul_bot.py
    Tambahkan:
        from dashboard_integration import log_link_processing, update_worker_performance
        
    Di process_single_link():
        log_link_processing(profile_name, link, success, message)
    
    Di worker():
        update_worker_performance(profile_name, links_count, success_count, fail_count, runtime)
    """
    pass

# ==========================================
# MONITORING THREAD (OPTIONAL)
# ==========================================
class MetricsReporter(threading.Thread):
    """Background thread untuk reporting metrics ke dashboard"""
    
    def __init__(self, interval=5):
        super().__init__(daemon=True)
        self.interval = interval
        self.running = True
    
    def run(self):
        while self.running:
            try:
                # Report ke dashboard API
                with METRICS_LOCK:
                    if METRICS_QUEUE:
                        # Kirim metrics batch ke dashboard
                        requests.post(
                            f"{DASHBOARD_API}/report",
                            json={"metrics": METRICS_QUEUE},
                            timeout=5
                        )
                        METRICS_QUEUE.clear()
            except:
                pass
            
            time.sleep(self.interval)
    
    def stop(self):
        self.running = False

# Start reporter
metrics_reporter = MetricsReporter()
metrics_reporter.start()

if __name__ == "__main__":
    # Test dashboard logger
    logger = DashboardLogger()
    
    print("📊 Testing Dashboard Logger...")
    logger.log_event('TEST', 'test_profile', 'INFO', 'Testing event logging')
    logger.log_login('test@example.com', 'dotaja01', True)
    logger.update_worker_stats('dotaja01', 100, 95, 5, 3600)
    logger.log_link_process('dotaja01', 'https://example.com', True, 'Iframe detected')
    
    print("✅ Dashboard logger is working!")
