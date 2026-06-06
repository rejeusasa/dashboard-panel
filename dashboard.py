import os
import json
import re
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import psutil
from dashboard_integration import (
    DashboardLogger, BOT_LOG_FILE, EMAIL_HISTORY_FILE, 
    WORKER_STATS_FILE, BATCH_HISTORY_FILE, EVENTS_LOG_FILE
)

app = Flask(__name__)
CORS(app)

BASE_DIR = os.getcwd()
MONITOR_FILE = os.path.join(BASE_DIR, "monitor.json")

# ==========================================
# UTILITY FUNCTIONS
# ==========================================

def parse_log_line(line):
    """
    Parse log line: [TIMESTAMP] TYPE | PROFILE | STATUS | MESSAGE | DURATION | METADATA
    """
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
    """
    Get current system resource usage
    """
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        # Count Chrome processes
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
    """
    Read monitor.json for current batch status
    """
    try:
        if os.path.exists(MONITOR_FILE):
            with open(MONITOR_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {}

# ==========================================
# API ENDPOINTS
# ==========================================

@app.route('/api/dashboard/realtime', methods=['GET'])
def realtime():
    """
    Get real-time metrics: system health + monitor.json data
    """
    monitor_data = read_monitor_json()
    system_health = get_system_health()
    
    # Parse latest events from bot_log.txt
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
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/dashboard/history', methods=['GET'])
def history():
    """
    Get event history with optional filtering
    Query params: limit, filter_type, filter_profile
    """
    limit = request.args.get('limit', 100, type=int)
    filter_type = request.args.get('filter_type', '')
    filter_profile = request.args.get('filter_profile', '')
    
    events = []
    tail_logs = DashboardLogger.get_tail_log(BOT_LOG_FILE, limit)
    
    for line in tail_logs:
        parsed = parse_log_line(line.strip())
        if parsed:
            # Apply filters
            if filter_type and parsed['event_type'] != filter_type:
                continue
            if filter_profile and filter_profile not in parsed['profile_name']:
                continue
            events.append(parsed)
    
    return jsonify({'events': events, 'count': len(events)})

@app.route('/api/dashboard/worker-stats', methods=['GET'])
def worker_stats():
    """
    Get all worker statistics from worker_stats.json
    """
    stats = DashboardLogger.read_json_file(WORKER_STATS_FILE)
    
    # Sort by success rate
    sorted_stats = sorted(stats.items(), key=lambda x: x[1].get('success_rate', 0), reverse=True)
    
    return jsonify({
        'workers': {k: v for k, v in sorted_stats},
        'total_workers': len(stats)
    })

@app.route('/api/dashboard/batch-history', methods=['GET'])
def batch_history():
    """
    Get batch execution history from batch_history.json
    """
    limit = request.args.get('limit', 50, type=int)
    
    batches = DashboardLogger.read_json_file(BATCH_HISTORY_FILE)
    
    # Keep only last N batches
    batches = batches[-limit:] if len(batches) > limit else batches
    
    # Calculate summary stats
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
    """
    Get email login history from email_history.txt
    """
    limit = request.args.get('limit', 100, type=int)
    
    emails = []
    tail_logs = DashboardLogger.get_tail_log(EMAIL_HISTORY_FILE, limit)
    
    for line in tail_logs:
        try:
            # Parse: [TIMESTAMP] EMAIL | PROFILE | SUCCESS/FAILED | ERROR_MSG
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
    
    # Count successes
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
    """
    Get aggregated analytics summary
    """
    # Worker stats
    worker_stats_data = DashboardLogger.read_json_file(WORKER_STATS_FILE)
    total_workers = len(worker_stats_data)
    avg_success_rate = round(sum(w.get('success_rate', 0) for w in worker_stats_data.values()) / total_workers, 2) if total_workers > 0 else 0
    
    # Batch history
    batches = DashboardLogger.read_json_file(BATCH_HISTORY_FILE)
    total_batches = len(batches)
    
    # Email tracking
    tail_emails = DashboardLogger.get_tail_log(EMAIL_HISTORY_FILE, 500)
    successful_emails = sum(1 for line in tail_emails if 'SUCCESS' in line)
    failed_emails = sum(1 for line in tail_emails if 'FAILED' in line)
    
    return jsonify({
        'workers': {
            'total': total_workers,
            'avg_success_rate': avg_success_rate,
            'top_performer': max((w for w in worker_stats_data.items()), key=lambda x: x[1].get('success_rate', 0), default=(None, {}))[0] if worker_stats_data else None
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
        }
    })

@app.route('/api/dashboard/logs-export', methods=['GET'])
def logs_export():
    """
    Export logs in JSON or CSV format
    Query param: format (json or csv)
    """
    export_format = request.args.get('format', 'json')
    
    # Read all logs
    events = []
    logs = DashboardLogger.get_tail_log(BOT_LOG_FILE, 10000)  # Get last 10k events
    
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
    """
    Cleanup old log entries (>30 days)
    """
    try:
        DashboardLogger.cleanup_old_logs(days=30)
        return jsonify({'status': 'success', 'message': 'Old logs cleaned up'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ==========================================
# MAIN
# ==========================================

if __name__ == '__main__':
    print("🚀 Dashboard API Server Starting on Port 7861...")
    print(f"📁 Reading logs from: {BASE_DIR}")
    print(f"📊 Endpoints: /api/dashboard/*")
    app.run(host='0.0.0.0', port=7861, debug=False)
