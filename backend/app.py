"""
Dashboard Panel - Main Flask Application
"""
import os
import sys
import logging
from flask import Flask, render_template, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO

from config import (
    FLASK_ENV, HOST, PORT, SECRET_KEY, JWT_SECRET,
    CORS_ORIGIN, LOG_LEVEL, AUTH_KEY
)

# ==========================================
# 🔧 SETUP
# ==========================================

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['JSON_SORT_KEYS'] = False

# CORS Setup
CORS(app, resources={r"/api/*": {"origins": CORS_ORIGIN}})

# SocketIO Setup
socketio = SocketIO(
    app,
    cors_allowed_origins=CORS_ORIGIN,
    async_mode='threading'
)

# Logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==========================================
# 📦 IMPORT ROUTES
# ==========================================

try:
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.workers import workers_bp
    from routes.commands import commands_bp
    from routes.files import files_bp
    from routes.analytics import analytics_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/api/v1')
    app.register_blueprint(workers_bp, url_prefix='/api/v1/workers')
    app.register_blueprint(commands_bp, url_prefix='/api/v1/commands')
    app.register_blueprint(files_bp, url_prefix='/api/v1/files')
    app.register_blueprint(analytics_bp, url_prefix='/api/v1/analytics')
    
    logger.info("✅ Routes loaded successfully")
except Exception as e:
    logger.error(f"❌ Error loading routes: {e}")
    sys.exit(1)

# ==========================================
# 🌐 MAIN ROUTES
# ==========================================

@app.route('/')
def index():
    return jsonify({
        "status": "online",
        "service": "Dashboard Panel",
        "version": "1.0.0",
        "endpoints": {
            "api": "/api/v1",
            "auth": "/api/v1/auth",
            "dashboard": "/api/v1/status",
            "workers": "/api/v1/workers",
            "commands": "/api/v1/commands",
            "files": "/api/v1/files",
            "analytics": "/api/v1/analytics",
            "websocket": "/ws/live"
        }
    })

@app.route('/api/v1/health')
def health():
    return jsonify({"status": "healthy", "timestamp": __import__('time').time()})

# ==========================================
# ❌ ERROR HANDLERS
# ==========================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({"error": "Unauthorized"}), 401

@app.errorhandler(403)
def forbidden(error):
    return jsonify({"error": "Forbidden"}), 403

@app.errorhandler(500)
def server_error(error):
    logger.error(f"Server error: {error}")
    return jsonify({"error": "Internal server error"}), 500

# ==========================================
# 🚀 RUN
# ==========================================

if __name__ == '__main__':
    logger.info(f"🚀 Starting Dashboard Panel")
    logger.info(f"Environment: {FLASK_ENV}")
    logger.info(f"Listening on {HOST}:{PORT}")
    logger.info(f"CORS Origin: {CORS_ORIGIN}")
    
    socketio.run(
        app,
        host=HOST,
        port=PORT,
        debug=FLASK_ENV == 'development',
        allow_unsafe_werkzeug=True
    )
