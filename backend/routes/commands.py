"""
Command Routes - Control Bot Actions
"""
from flask import Blueprint, request, jsonify
from services.bot_controller import BotController
from services.process_manager import ProcessManager

commands_bp = Blueprint('commands', __name__)
bot_controller = BotController()
process_manager = ProcessManager()

@commands_bp.route('/start-login', methods=['POST'])
def start_login():
    """
    Start login.py process
    """
    try:
        if bot_controller.is_busy():
            return jsonify({"error": "Bot is busy"}), 409
        
        success = bot_controller.start_login()
        if success:
            return jsonify({"message": "Login started", "status": "ok"}), 200
        else:
            return jsonify({"error": "Failed to start login"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@commands_bp.route('/start-loop', methods=['POST'])
def start_loop():
    """
    Start loop.py process
    """
    try:
        if bot_controller.is_busy():
            return jsonify({"error": "Bot is busy"}), 409
        
        success = bot_controller.start_loop()
        if success:
            return jsonify({"message": "Loop started", "status": "ok"}), 200
        else:
            return jsonify({"error": "Failed to start loop"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@commands_bp.route('/stop', methods=['POST'])
def stop():
    """
    Stop all processes
    """
    try:
        bot_controller.stop_all()
        return jsonify({"message": "All processes stopped", "status": "ok"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@commands_bp.route('/clean', methods=['POST'])
def clean():
    """
    Clean RAM and system resources
    """
    try:
        memory_freed = bot_controller.clean_system()
        return jsonify({
            "message": "System cleaned",
            "memory_freed_mb": memory_freed
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@commands_bp.route('/restart', methods=['POST'])
def restart():
    """
    Restart loop process
    """
    try:
        bot_controller.stop_all()
        success = bot_controller.start_loop()
        if success:
            return jsonify({"message": "Loop restarted", "status": "ok"}), 200
        else:
            return jsonify({"error": "Failed to restart"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
