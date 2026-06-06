"""
Dashboard Main Routes
"""
from flask import Blueprint, request, jsonify
import json
import os
from config import (
    LOG_FILE, EMAIL_FILE, LINK_FILE, MAPPING_FILE,
    HISTORY_FILE, MONITOR_FILE, PROFILE_DIR
)
from services.file_monitor import FileMonitor
from services.process_manager import ProcessManager

dashboard_bp = Blueprint('dashboard', __name__)
file_monitor = FileMonitor()
process_manager = ProcessManager()

@dashboard_bp.route('/status', methods=['GET'])
def status():
    """
    Get current system status
    """
    try:
        # Read monitor.json
        monitor_data = {}
        if os.path.exists(MONITOR_FILE):
            try:
                with open(MONITOR_FILE, 'r') as f:
                    monitor_data = json.load(f)
            except:
                pass
        
        # Check processes
        login_running = process_manager.check_process('login.py')
        loop_running = process_manager.check_process('loop.py')
        
        # Determine state
        if login_running:
            state = "BUSY_LOGIN"
        elif loop_running:
            state = "BUSY_LOOP"
        else:
            state = "IDLE"
        
        # Count queue items
        email_count = 0
        link_count = 0
        profile_count = 0
        
        if os.path.exists(EMAIL_FILE):
            with open(EMAIL_FILE, 'r') as f:
                email_count = len([x for x in f if x.strip()])
        
        if os.path.exists(LINK_FILE):
            with open(LINK_FILE, 'r') as f:
                link_count = len([x for x in f if x.strip()])
        
        if os.path.exists(MAPPING_FILE):
            with open(MAPPING_FILE, 'r') as f:
                profile_count = len([x for x in f if x.strip()])
        
        # Get system metrics
        cpu_percent = process_manager.get_cpu_percent()
        memory_info = process_manager.get_memory_info()
        
        return jsonify({
            "status": "online",
            "state": state,
            "login_running": login_running,
            "loop_running": loop_running,
            "queue": {
                "emails": email_count,
                "links": link_count,
                "profiles": profile_count
            },
            "monitor": monitor_data,
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_info['percent'],
                "memory_mb": memory_info['mb'],
                "available_mb": memory_info['available']
            }
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@dashboard_bp.route('/logs', methods=['GET'])
def logs():
    """
    Get bot logs (tail)
    """
    try:
        lines = request.args.get('lines', default=50, type=int)
        if not os.path.exists(LOG_FILE):
            return jsonify({"logs": []}), 200
        
        with open(LOG_FILE, 'r') as f:
            all_lines = f.readlines()
            tail_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
        
        return jsonify({
            "logs": tail_lines,
            "total_lines": len(all_lines)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@dashboard_bp.route('/summary', methods=['GET'])
def summary():
    """
    Get dashboard summary
    """
    try:
        # Count completed
        completed = 0
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r') as f:
                completed = len([x for x in f if x.strip()])
        
        # Count profiles
        profiles = 0
        if os.path.exists(PROFILE_DIR):
            profiles = len([x for x in os.listdir(PROFILE_DIR) if os.path.isdir(os.path.join(PROFILE_DIR, x))])
        
        # Read monitor.json for worker count
        workers_active = 0
        if os.path.exists(MONITOR_FILE):
            try:
                with open(MONITOR_FILE, 'r') as f:
                    data = json.load(f)
                    workers = data.get('workers', {})
                    workers_active = len([x for x in workers.keys() if x != 'SYSTEM'])
            except:
                pass
        
        return jsonify({
            "completed_emails": completed,
            "total_profiles": profiles,
            "active_workers": workers_active,
            "success_rate": f"{(completed / max(profiles, 1)) * 100:.1f}%" if profiles > 0 else "0%"
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
