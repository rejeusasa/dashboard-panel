"""
DASHBOARD BACKEND - Monitoring & Analytics untuk Bot Panel
Menyediakan API endpoints untuk real-time monitoring, history, dan analytics
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import json
import sqlite3
import time
import threading
from datetime import datetime, timedelta
from collections import defaultdict
import psutil
import glob

# ==========================================
# KONFIGURASI DASHBOARD
# ==========================================
DB_FILE = "dashboard_metrics.db"
HISTORY_DIR = "history"
SCREENSHOT_DIR = "screenshots"
METRICS_FILE = "realtime_metrics.json"

app = Flask(__name__)
CORS(app)

# ==========================================
# DATABASE INITIALIZATION
# ==========================================
def init_database():
    """Initialize SQLite database untuk tracking metrics"""
    os.makedirs(HISTORY_DIR, exist_ok=True)
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Table untuk event history
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
    
    # Table untuk worker performance
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
    
    # Table untuk email tracking
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
    
    # Table untuk batch history
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

def log_event(event_type, profile_name="SYSTEM", status="INFO", message="", duration=0, metadata=None):
    """Log event ke database"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        meta_str = json.dumps(metadata) if metadata else None
        
        cursor.execute('''
            INSERT INTO events (event_type, profile_name, status, message, duration, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (event_type, profile_name, status, message, duration, meta_str))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"❌ Database log error: {e}")

def update_worker_stats(profile_name, links_processed=0, successful=0, failed=0, runtime=0):
    """Update worker performance statistics"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO worker_stats 
            (profile_name, total_links_processed, successful_links, failed_links, total_runtime, last_updated)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (profile_name, links_processed, successful, failed, runtime))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"❌ Stats update error: {e}")

# ==========================================
# REAL-TIME METRICS TRACKING
# ==========================================
class MetricsCollector:
    def __init__(self):
        self.current_batch = {
            "batch_id": None,
            "start_time": None,
            "workers": {},
            "total_links": 0,
            "processed_links": 0,
            "successful_links": 0,
            "failed_links": 0,
            "system_status": "IDLE"
        }
        self.lock = threading.Lock()
    
    def start_batch(self, batch_id, total_links):
        with self.lock:
            self.current_batch = {
                "batch_id": batch_id,
                "start_time": time.time(),
                "workers": {},
                "total_links": total_links,
                "processed_links": 0,
                "successful_links": 0,
                "failed_links": 0,
                "system_status": "RUNNING"
            }
    
    def update_worker(self, profile_name, status, current_link=None):
        with self.lock:
            self.current_batch["workers"][profile_name] = {
                "status": status,
                "current_link": current_link,
                "updated_at": time.time()
            }
    
    def add_processed_link(self, success=True):
        with self.lock:
            self.current_batch["processed_links"] += 1
            if success:
                self.current_batch["successful_links"] += 1
            else:
                self.current_batch["failed_links"] += 1
    
    def get_metrics(self):
        with self.lock:
            metrics = dict(self.current_batch)
            if metrics["start_time"]:
                metrics["elapsed_time"] = int(time.time() - metrics["start_time"])
                metrics["estimated_remaining"] = self._estimate_remaining()
            return metrics
    
    def _estimate_remaining(self):
        if self.current_batch["processed_links"] == 0:
            return 0
        avg_time_per_link = self.current_batch["elapsed_time"] / self.current_batch["processed_links"]
        remaining = self.current_batch["total_links"] - self.current_batch["processed_links"]
        return int(avg_time_per_link * remaining)

metrics_collector = MetricsCollector()

def save_metrics_periodically():
    """Periodic save metrics ke file (untuk persistence)"""
    while True:
        try:
            with open(METRICS_FILE, 'w') as f:
                json.dump(metrics_collector.get_metrics(), f, indent=2)
        except:
            pass
        time.sleep(5)

# Start metrics saver thread
threading.Thread(target=save_metrics_periodically, daemon=True).start()

# ==========================================
# SYSTEM MONITORING
# ==========================================
def get_system_health():
    """Dapatkan health check sistem"""
    try:
        cpu = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Check Chrome processes
        chrome_procs = 0
        for p in psutil.process_iter(['name']):
            try:
                if 'chrome' in p.info['name'].lower():
                    chrome_procs += 1
            except:
                pass
        
        return {
            "cpu_percent": cpu,
            "memory": {
                "total_mb": mem.total // 1048576,
                "available_mb": mem.available // 1048576,
                "percent": mem.percent
            },
            "disk": {
                "total_gb": disk.total // 1073741824,
                "free_gb": disk.free // 1073741824,
                "percent": disk.percent
            },
            "chrome_processes": chrome_procs,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}

# ==========================================
# API ENDPOINTS - DASHBOARD
# ==========================================

@app.route('/api/dashboard/realtime', methods=['GET'])
def get_realtime_metrics():
    """Get real-time metrics dashboard"""
    metrics = metrics_collector.get_metrics()
    system = get_system_health()
    
    return jsonify({
        "metrics": metrics,
        "system": system,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/dashboard/history', methods=['GET'])
def get_history():
    """Get historical events"""
    limit = request.args.get('limit', 100, type=int)
    event_type = request.args.get('type', None)
    
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = 'SELECT * FROM events'
        params = []
        
        if event_type:
            query += ' WHERE event_type = ?'
            params.append(event_type)
        
        query += ' ORDER BY timestamp DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        events = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({"events": events})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/dashboard/worker-stats', methods=['GET'])
def get_worker_stats():
    """Get per-worker performance statistics"""
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM worker_stats ORDER BY last_updated DESC')
        stats = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({"workers": stats})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/dashboard/batch-history', methods=['GET'])
def get_batch_history():
    """Get batch execution history"""
    limit = request.args.get('limit', 50, type=int)
    
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM batch_history 
            ORDER BY start_time DESC 
            LIMIT ?
        ''', (limit,))
        
        batches = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({"batches": batches})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/dashboard/email-tracking', methods=['GET'])
def get_email_tracking():
    """Get email login history"""
    email = request.args.get('email', None)
    limit = request.args.get('limit', 100, type=int)
    
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if email:
            cursor.execute('''
                SELECT * FROM email_history 
                WHERE email = ? 
                ORDER BY login_timestamp DESC
            ''', (email,))
        else:
            cursor.execute('''
                SELECT * FROM email_history 
                ORDER BY login_timestamp DESC 
                LIMIT ?
            ''', (limit,))
        
        emails = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({"emails": emails})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/dashboard/analytics', methods=['GET'])
def get_analytics():
    """Get aggregated analytics"""
    days = request.args.get('days', 7, type=int)
    
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Success rate
        cursor.execute('''
            SELECT COUNT(*) as total, 
                   SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful
            FROM email_history 
            WHERE datetime(login_timestamp) >= datetime('now', ? || ' days')
        ''', (f'-{days}',))
        
        email_stats = dict(zip([col[0] for col in cursor.description], cursor.fetchone()))
        
        # Worker efficiency
        cursor.execute('''
            SELECT profile_name,
                   total_links_processed,
                   successful_links,
                   failed_links,
                   ROUND(CAST(successful_links AS FLOAT) / CAST(total_links_processed AS FLOAT) * 100, 2) as success_rate
            FROM worker_stats
            WHERE total_links_processed > 0
            ORDER BY success_rate DESC
        ''')
        
        worker_efficiency = [dict(zip([col[0] for col in cursor.description], row)) 
                           for row in cursor.fetchall()]
        
        # Event breakdown
        cursor.execute('''
            SELECT event_type, COUNT(*) as count
            FROM events
            WHERE datetime(timestamp) >= datetime('now', ? || ' days')
            GROUP BY event_type
        ''', (f'-{days}',))
        
        event_breakdown = [dict(zip([col[0] for col in cursor.description], row)) 
                          for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            "period_days": days,
            "email_stats": email_stats,
            "worker_efficiency": worker_efficiency,
            "event_breakdown": event_breakdown
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/dashboard/logs-export', methods=['GET'])
def export_logs():
    """Export logs sebagai file"""
    format_type = request.args.get('format', 'json')  # json, csv
    
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM events ORDER BY timestamp DESC LIMIT 10000')
        events = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        if format_type == 'json':
            filename = f"logs_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join(HISTORY_DIR, filename)
            with open(filepath, 'w') as f:
                json.dump(events, f, indent=2)
            return send_file(filepath, as_attachment=True)
        
        elif format_type == 'csv':
            import csv
            filename = f"logs_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = os.path.join(HISTORY_DIR, filename)
            with open(filepath, 'w', newline='') as f:
                if events:
                    writer = csv.DictWriter(f, fieldnames=events[0].keys())
                    writer.writeheader()
                    writer.writerows(events)
            return send_file(filepath, as_attachment=True)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/dashboard/cleanup', methods=['POST'])
def cleanup_old_data():
    """Cleanup old data (older than 30 days)"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Delete old events
        cursor.execute('''
            DELETE FROM events 
            WHERE datetime(timestamp) < datetime('now', '-30 days')
        ''')
        
        deleted_events = cursor.rowcount
        
        # Delete old batches
        cursor.execute('''
            DELETE FROM batch_history 
            WHERE datetime(start_time) < datetime('now', '-30 days')
        ''')
        
        deleted_batches = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        # Cleanup old screenshots
        cutoff = time.time() - (30 * 86400)  # 30 days
        old_screenshots = 0
        for f in glob.glob(os.path.join(SCREENSHOT_DIR, "*.png")):
            if os.path.getmtime(f) < cutoff:
                os.remove(f)
                old_screenshots += 1
        
        return jsonify({
            "deleted_events": deleted_events,
            "deleted_batches": deleted_batches,
            "deleted_screenshots": old_screenshots
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    init_database()
    app.run(host='0.0.0.0', port=7861, debug=False)
