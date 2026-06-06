"""
Worker Management Routes
"""
from flask import Blueprint, jsonify
import json
import os
from config import MONITOR_FILE, MAPPING_FILE

workers_bp = Blueprint('workers', __name__)

@workers_bp.route('/', methods=['GET'])
def list_workers():
    """
    Get all workers and their status
    """
    try:
        workers = []
        
        if os.path.exists(MONITOR_FILE):
            try:
                with open(MONITOR_FILE, 'r') as f:
                    data = json.load(f)
                    workers_dict = data.get('workers', {})
                    time_remaining = data.get('time_remaining', 0)
                    
                    for name, status in workers_dict.items():
                        if name != 'SYSTEM':
                            workers.append({
                                "name": name,
                                "status": status,
                                "batch_time_remaining": time_remaining
                            })
            except:
                pass
        
        return jsonify({
            "workers": workers,
            "total": len(workers)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@workers_bp.route('/<name>', methods=['GET'])
def get_worker(name):
    """
    Get specific worker details
    """
    try:
        if os.path.exists(MONITOR_FILE):
            try:
                with open(MONITOR_FILE, 'r') as f:
                    data = json.load(f)
                    worker_status = data.get('workers', {}).get(name)
                    
                    if worker_status:
                        return jsonify({
                            "name": name,
                            "status": worker_status,
                            "batch_time_remaining": data.get('time_remaining', 0)
                        }), 200
            except:
                pass
        
        return jsonify({"error": "Worker not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
