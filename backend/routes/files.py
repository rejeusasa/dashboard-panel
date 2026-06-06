"""
File Monitoring Routes
"""
from flask import Blueprint, jsonify, request
import json
import os
from config import (
    EMAIL_FILE, LINK_FILE, MAPPING_FILE,
    HISTORY_FILE, MONITOR_FILE, LOG_FILE
)

files_bp = Blueprint('files', __name__)

@files_bp.route('/monitor', methods=['GET'])
def monitor():
    """
    Get all monitored files status
    """
    try:
        files_info = {}
        
        # Email file
        if os.path.exists(EMAIL_FILE):
            with open(EMAIL_FILE, 'r') as f:
                lines = [x.strip() for x in f if x.strip()]
            files_info['email'] = {
                "exists": True,
                "count": len(lines),
                "size_bytes": os.path.getsize(EMAIL_FILE),
                "sample": lines[:5]
            }
        else:
            files_info['email'] = {"exists": False, "count": 0}
        
        # Link file
        if os.path.exists(LINK_FILE):
            with open(LINK_FILE, 'r') as f:
                lines = [x.strip() for x in f if x.strip()]
            files_info['link'] = {
                "exists": True,
                "count": len(lines),
                "size_bytes": os.path.getsize(LINK_FILE),
                "sample": lines[:5]
            }
        else:
            files_info['link'] = {"exists": False, "count": 0}
        
        # Mapping file
        if os.path.exists(MAPPING_FILE):
            with open(MAPPING_FILE, 'r') as f:
                lines = [x.strip() for x in f if x.strip()]
            files_info['mapping'] = {
                "exists": True,
                "count": len(lines),
                "size_bytes": os.path.getsize(MAPPING_FILE)
            }
        else:
            files_info['mapping'] = {"exists": False, "count": 0}
        
        # History file
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r') as f:
                lines = [x.strip() for x in f if x.strip()]
            files_info['history'] = {
                "exists": True,
                "count": len(lines),
                "size_bytes": os.path.getsize(HISTORY_FILE)
            }
        else:
            files_info['history'] = {"exists": False, "count": 0}
        
        # Monitor file
        if os.path.exists(MONITOR_FILE):
            with open(MONITOR_FILE, 'r') as f:
                data = json.load(f)
            files_info['monitor'] = {
                "exists": True,
                "data": data,
                "size_bytes": os.path.getsize(MONITOR_FILE)
            }
        else:
            files_info['monitor'] = {"exists": False}
        
        return jsonify(files_info), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@files_bp.route('/email', methods=['GET'])
def get_email_file():
    """
    Get email.txt content
    """
    try:
        if not os.path.exists(EMAIL_FILE):
            return jsonify({"emails": []}), 200
        
        with open(EMAIL_FILE, 'r') as f:
            lines = [x.strip() for x in f if x.strip()]
        
        return jsonify({"emails": lines}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@files_bp.route('/link', methods=['GET'])
def get_link_file():
    """
    Get link.txt content
    """
    try:
        if not os.path.exists(LINK_FILE):
            return jsonify({"links": []}), 200
        
        with open(LINK_FILE, 'r') as f:
            lines = [x.strip() for x in f if x.strip()]
        
        return jsonify({"links": lines}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
