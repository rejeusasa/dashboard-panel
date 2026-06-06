import os
import json
import re
import sys
import requests
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import psutil
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import dashboard integration
try:
    from dashboard_integration import (
        DashboardLogger, BOT_LOG_FILE, EMAIL_HISTORY_FILE, 
        WORKER_STATS_FILE, BATCH_HISTORY_FILE, EVENTS_LOG_FILE,
        dashboard_logger
    )
except ImportError:
    print("⚠️ dashboard_integration module not found - using fallback", flush=True)
    
    class DummyLogger:
        @staticmethod
        def get_tail_log(file, count):
            return []
        @staticmethod
        def read_json_file(file):
            return {}
        @staticmethod
        def cleanup_old_logs(days=30):
            pass
    
    DashboardLogger = DummyLogger()
    BOT_LOG_FILE = "bot_log.txt"
    EMAIL_HISTORY_FILE = "email_history.txt"
    WORKER_STATS_FILE = "worker_stats.json"
    BATCH_HISTORY_FILE = "batch_history.json"
    EVENTS_LOG_FILE = "events.log"
    
    class DummyDashboardLogger:
        def log_event(self, *args, **kwargs):
            pass
    dashboard_logger = DummyDashboardLogger()

app = Flask(__name__)
CORS(app)

BASE_DIR = os.getcwd()
MONITOR_FILE = os.path.join(BASE_DIR, "monitor.json")

# ==========================================
# CONFIGURATION
# ==========================================
TUNNEL_ENABLED = os.getenv('CLOUDFLARE_TUNNEL', 'true').lower() == 'true'
HOST = '127.0.0.1' if TUNNEL_ENABLED else os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 7861))
DEBUG_MODE = os.getenv('DEBUG', 'false').lower() == 'true'
AUTH_KEY = os.getenv('AUTH_KEY', 'GHOST_SECRET_2026')

# Global registry untuk panel yang terdaftar
REGISTERED_PANELS = {}

print(f"[INIT] Dashboard Backend listening on {HOST}:{PORT}", flush=True)
print(f"[INIT] AUTH_KEY: {AUTH_KEY}", flush=True)
print(f"[INIT] Cloudflare Tunnel: {'ENABLED' if TUNNEL_ENABLED else 'DISABLED'}", flush=True)

# ==========================================
# UTILITY FUNCTIONS
# ==========================================

def parse_log_line(line):
    """Parse log line"""
    try:
        match = re.match(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] ([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|(.*)$', line)
        if match:
            return {
                'timestamp': match.group(1),
                'event_type': match.group(2).strip(),
                'profile_name': match.group(3).strip(),
                'status': match.group(4).strip(),
                'message': match.group(5).strip(),
                'duration': match.group(6).strip(),
                'metadata': match.group(7).strip()
            }
    except:
        pass
    return None

def get_system_health():
    """Get current system resource usage"""
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        chrome_count = 0
        for proc in psutil.process_iter(['name', 'cmdline']):
            try:
                if 'chrome' in proc.info['name'].lower() or (proc.info['cmdline'] and 'chrome' in ' '.join(proc.info['cmdline']).lower()):
                    chrome_count += 1
            except:
                pass
        
        return {
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_available_mb': memory.available // 1048576,
            'memory_used_mb': memory.used // 1048576,
            'chrome_processes': chrome_count,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except:
        return {}

def read_monitor_json():
    """Read monitor.json for current batch status"""
    try:
        if os.path.exists(MONITOR_FILE):
            with open(MONITOR_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {}

def check_auth():
    """Check authentication"""
    auth_key = request.headers.get('X-Auth-Key', '')
    if auth_key != AUTH_KEY:
        return False
    return True

# ==========================================
# PANEL REGISTRATION & CONTROL ENDPOINTS
# (Kompatibel dengan panel automation)
# ==========================================

@app.route('/api/register', methods=['POST'])
def api_register():
    """Register a new panel worker"""
    if not check_auth():
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        data = request.get_json()
        url = data.get('url', '')
        ip = data.get('ip', '')
        
        if not url:
            return jsonify({"error": "Missing url parameter"}), 400
        
        # Generate slot ID
        slot_id = f"slot_{len(REGISTERED_PANELS) + 1}"
        
        # Store panel info
        REGISTERED_PANELS[slot_id] = {
            'url': url,
            'ip': ip,
            'registered_at': datetime.now().isoformat(),
            'state': 'IDLE'
        }
        
        print(f"✅ [REGISTER] Panel registered: {slot_id} ({url})", flush=True)
        
        # Log to dashboard
        if dashboard_logger:
            dashboard_logger.log_event(
                'REGISTER', slot_id, 'SUCCESS',
                f'Panel registered: {url} (IP: {ip})'
            )
        
        # Read email.txt dan link.txt untuk dikirim ke panel
        emails = []
        links = []
        
        if os.path.exists('email.txt'):
            with open('email.txt', 'r') as f:
                emails = [line.strip() for line in f if line.strip()]
        
        if os.path.exists('link.txt'):
            with open('link.txt', 'r') as f:
                links = [line.strip() for line in f if line.strip()]
        
        return jsonify({
            "slot": slot_id,
            "locker": {
                "emails": emails,
                "links": links
            }
        }), 200
        
    except Exception as e:
        print(f"❌ [REGISTER] Error: {e}", flush=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/report', methods=['POST'])
def api_report():
    """Panel reports status"""
    if not check_auth():
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        data = request.get_json()
        slot = data.get('slot', '')
        state = data.get('state', '')
        msg = data.get('msg', '')
        
        if slot in REGISTERED_PANELS:
            REGISTERED_PANELS[slot]['state'] = state
            REGISTERED_PANELS[slot]['last_report'] = datetime.now().isoformat()
        
        print(f"📡 [REPORT] {slot}: {state} - {msg}", flush=True)
        
        # Log to dashboard
        if dashboard_logger:
            dashboard_logger.log_event(
                'REPORT', slot, 'INFO',
                f'{state}: {msg}'
            )
        
        return jsonify({"status": "success"}), 200
        
    except Exception as e:
        print(f"❌ [REPORT] Error: {e}", flush=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/ack', methods=['POST'])
def api_ack():
    """Acknowledge panel registration"""
    if not check_auth():
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        data = request.get_json()
        slot = data.get('slot', '')
        
        if slot in REGISTERED_PANELS:
            REGISTERED_PANELS[slot]['ack'] = True
        
        print(f"✅ [ACK] Acknowledged: {slot}", flush=True)
        
        return jsonify({"status": "acknowledged"}), 200
        
    except Exception as e:
        print(f"❌ [ACK] Error: {e}", flush=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/panels', methods=['GET'])
def api_panels():
    """Get all registered panels"""
    return jsonify({
        "panels": REGISTERED_PANELS,
        "total": len(REGISTERED_PANELS)
    }), 200

# ==========================================
# MONITORING ENDPOINTS
# ==========================================

@app.route('/')
def index():
    """Dashboard landing page"""
    return jsonify({
        "status": "online",
        "service": "Dashboard Panel Backend",
        "version": "1.0",
        "endpoints": {
            "register": "/api/register (POST)",
            "report": "/api/report (POST)",
            "ack": "/api/ack (POST)",
            "panels": "/api/panels (GET)",
            "realtime": "/api/dashboard/realtime (GET)",
            "history": "/api/dashboard/history (GET)",
            "worker_stats": "/api/dashboard/worker-stats (GET)",
            "batch_history": "/api/dashboard/batch-history (GET)",
            "email_tracking": "/api/dashboard/email-tracking (GET)",
            "analytics": "/api/dashboard/analytics (GET)"
        }
    }), 200

@app.route('/api/dashboard/realtime', methods=['GET'])
def realtime():
    """Get real-time metrics"""
    monitor_data = read_monitor_json()
    system_health = get_system_health()
    
    recent_events = []
    tail_logs = DashboardLogger.get_tail_log(BOT_LOG_FILE, 20)
    for line in tail_logs:
        parsed = parse_log_line(line.strip())
        if parsed:
            recent_events.append(parsed)
    
    return jsonify({
        'monitor': monitor_data,
        'system_health': system_health,
        'recent_events': recent_events,
        'registered_panels': len(REGISTERED_PANELS),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/dashboard/history', methods=['GET'])
def history():
    """Get event history"""
    limit = request.args.get('limit', 100, type=int)
    filter_type = request.args.get('filter_type', '')
    filter_profile = request.args.get('filter_profile', '')
    
    events = []
    tail_logs = DashboardLogger.get_tail_log(BOT_LOG_FILE, limit)
    
    for line in tail_logs:
        parsed = parse_log_line(line.strip())
        if parsed:
            if filter_type and parsed['event_type'] != filter_type:
                continue
            if filter_profile and filter_profile not in parsed['profile_name']:
                continue
            events.append(parsed)
    
    return jsonify({'events': events, 'count': len(events)})

@app.route('/api/dashboard/worker-stats', methods=['GET'])
def worker_stats():
    """Get worker statistics"""
    stats = DashboardLogger.read_json_file(WORKER_STATS_FILE)
    sorted_stats = sorted(stats.items(), key=lambda x: x[1].get('success_rate', 0), reverse=True)
    
    return jsonify({
        'workers': {k: v for k, v in sorted_stats},
        'total_workers': len(stats)
    })

@app.route('/api/dashboard/batch-history', methods=['GET'])
def batch_history():
    """Get batch execution history"""
    limit = request.args.get('limit', 50, type=int)
    batches = DashboardLogger.read_json_file(BATCH_HISTORY_FILE)
    
    batches = batches[-limit:] if len(batches) > limit else batches
    
    if batches:
        total_successful = sum(b.get('successful_links', 0) for b in batches)
        total_failed = sum(b.get('failed_links', 0) for b in batches)
        overall_success_rate = round((total_successful / (total_successful + total_failed) * 100), 2) if (total_successful + total_failed) > 0 else 0
    else:
        total_successful = 0
        total_failed = 0
        overall_success_rate = 0
    
    return jsonify({
        'batches': batches,
        'count': len(batches),
        'summary': {
            'total_successful': total_successful,
            'total_failed': total_failed,
            'overall_success_rate': overall_success_rate
        }
    })

@app.route('/api/dashboard/email-tracking', methods=['GET'])
def email_tracking():
    """Get email login history"""
    limit = request.args.get('limit', 100, type=int)
    
    emails = []
    tail_logs = DashboardLogger.get_tail_log(EMAIL_HISTORY_FILE, limit)
    
    for line in tail_logs:
        try:
            match = re.match(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] ([^|]+)\|([^|]+)\|([^|]+)\|(.*)$', line.strip())
            if match:
                emails.append({
                    'timestamp': match.group(1),
                    'email': match.group(2).strip(),
                    'profile': match.group(3).strip(),
                    'status': match.group(4).strip(),
                    'error_msg': match.group(5).strip()
                })
        except:
            pass
    
    successful = sum(1 for e in emails if e['status'] == 'SUCCESS')
    failed = len(emails) - successful
    
    return jsonify({
        'emails': emails,
        'count': len(emails),
        'summary': {
            'successful': successful,
            'failed': failed,
            'success_rate': round((successful / len(emails) * 100), 2) if emails else 0
        }
    })

@app.route('/api/dashboard/analytics', methods=['GET'])
def analytics():
    """Get aggregated analytics"""
    worker_stats_data = DashboardLogger.read_json_file(WORKER_STATS_FILE)
    total_workers = len(worker_stats_data)
    avg_success_rate = round(sum(w.get('success_rate', 0) for w in worker_stats_data.values()) / total_workers, 2) if total_workers > 0 else 0
    
    batches = DashboardLogger.read_json_file(BATCH_HISTORY_FILE)
    total_batches = len(batches)
    
    tail_emails = DashboardLogger.get_tail_log(EMAIL_HISTORY_FILE, 500)
    successful_emails = sum(1 for line in tail_emails if 'SUCCESS' in line)
    failed_emails = sum(1 for line in tail_emails if 'FAILED' in line)
    
    return jsonify({
        'workers': {
            'total': total_workers,
            'avg_success_rate': avg_success_rate
        },
        'batches': {
            'total': total_batches,
            'total_successful': sum(b.get('successful_links', 0) for b in batches),
            'total_failed': sum(b.get('failed_links', 0) for b in batches)
        },
        'emails': {
            'total_attempts': successful_emails + failed_emails,
            'successful': successful_emails,
            'failed': failed_emails,
            'success_rate': round((successful_emails / (successful_emails + failed_emails) * 100), 2) if (successful_emails + failed_emails) > 0 else 0
        },
        'registered_panels': len(REGISTERED_PANELS)
    })

@app.route('/api/dashboard/logs-export', methods=['GET'])
def logs_export():
    """Export logs"""
    export_format = request.args.get('format', 'json')
    
    events = []
    logs = DashboardLogger.get_tail_log(BOT_LOG_FILE, 10000)
    
    for line in logs:
        parsed = parse_log_line(line.strip())
        if parsed:
            events.append(parsed)
    
    if export_format == 'csv':
        import io
        output = io.StringIO()
        output.write('Timestamp,Event Type,Profile,Status,Message,Duration,Metadata\n')
        for event in events:
            output.write(f"{event['timestamp']},{event['event_type']},{event['profile_name']},{event['status']},{event['message']},{event['duration']},{event['metadata']}\n")
        
        output.seek(0)
        return output.getvalue(), 200, {
            'Content-Disposition': 'attachment;filename=bot_logs.csv',
            'Content-Type': 'text/csv'
        }
    else:
        return jsonify({'events': events, 'count': len(events)})

@app.route('/api/dashboard/cleanup', methods=['POST'])
def cleanup():
    """Cleanup old log entries"""
    try:
        DashboardLogger.cleanup_old_logs(days=30)
        return jsonify({'status': 'success', 'message': 'Old logs cleaned up'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ==========================================
# MAIN
# ==========================================

if __name__ == '__main__':
    try:
        print("\n" + "="*70)
        print("🚀 DASHBOARD BACKEND API SERVER STARTING")
        print("="*70)
        print(f"📁 Base Directory: {BASE_DIR}")
        print(f"🌐 Host: {HOST}")
        print(f"🔌 Port: {PORT}")
        print(f"🔧 Debug Mode: {DEBUG_MODE}")
        print(f"🔐 Auth Key: {AUTH_KEY}")
        print("-"*70)
        print("✅ Panel Registration Endpoints Available:")
        print("   /api/register    - Panel registration")
        print("   /api/report      - Panel status reporting")
        print("   /api/ack         - Acknowledge registration")
        print("   /api/panels      - List registered panels")
        print("-"*70)
        print("✅ Monitoring Endpoints Available:")
        print("   /api/dashboard/* - Real-time monitoring")
        print("="*70 + "\n")
        
        app.run(host=HOST, port=PORT, debug=DEBUG_MODE)
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}", file=sys.stderr)
        sys.exit(1)
