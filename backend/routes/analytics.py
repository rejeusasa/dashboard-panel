"""
Analytics Routes - Historical Data & Charts
"""
from flask import Blueprint, jsonify
import os
from datetime import datetime, timedelta
from config import HISTORY_FILE, MONITOR_FILE, MAPPING_FILE
import json

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/summary', methods=['GET'])
def summary():
    """
    Get analytics summary
    """
    try:
        completed = 0
        total_profiles = 0
        
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r') as f:
                completed = len([x for x in f if x.strip()])
        
        if os.path.exists(MAPPING_FILE):
            with open(MAPPING_FILE, 'r') as f:
                total_profiles = len([x for x in f if x.strip()])
        
        success_rate = (completed / max(total_profiles, 1)) * 100 if total_profiles > 0 else 0
        
        return jsonify({
            "completed_emails": completed,
            "total_profiles": total_profiles,
            "success_rate_percent": round(success_rate, 2),
            "pending_emails": max(total_profiles - completed, 0)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analytics_bp.route('/completed', methods=['GET'])
def completed():
    """
    Get completed emails list
    """
    try:
        completed_emails = []
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r') as f:
                completed_emails = [x.strip() for x in f if x.strip()]
        
        return jsonify({
            "completed": completed_emails,
            "total": len(completed_emails)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analytics_bp.route('/worker-stats', methods=['GET'])
def worker_stats():
    """
    Get worker statistics from monitor.json
    """
    try:
        stats = {}
        if os.path.exists(MONITOR_FILE):
            try:
                with open(MONITOR_FILE, 'r') as f:
                    data = json.load(f)
                    workers = data.get('workers', {})
                    
                    for worker_name, status in workers.items():
                        if worker_name != 'SYSTEM':
                            stats[worker_name] = {
                                "status": status,
                                "type": "profile"
                            }
            except:
                pass
        
        return jsonify({
            "workers": stats,
            "total_workers": len(stats)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
