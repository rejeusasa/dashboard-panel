import os
import json
import time
from datetime import datetime

# ==========================================
# FILE-BASED LOGGING SYSTEM (NO DATABASE)
# ==========================================

BASE_DIR = os.getcwd()

# Log Files
BOT_LOG_FILE = os.path.join(BASE_DIR, "bot_log.txt")
EMAIL_HISTORY_FILE = os.path.join(BASE_DIR, "email_history.txt")
WORKER_STATS_FILE = os.path.join(BASE_DIR, "worker_stats.json")
BATCH_HISTORY_FILE = os.path.join(BASE_DIR, "batch_history.json")
EVENTS_LOG_FILE = os.path.join(BASE_DIR, "events_log.txt")

class DashboardLogger:
    """
    File-based logging system. Writes all events to text/JSON files.
    Dashboard reads these files directly.
    """

    @staticmethod
    def init_files():
        """Initialize log files if they don't exist"""
        for file_path in [BOT_LOG_FILE, EMAIL_HISTORY_FILE, EVENTS_LOG_FILE]:
            if not os.path.exists(file_path):
                open(file_path, 'w').close()
        
        if not os.path.exists(WORKER_STATS_FILE):
            with open(WORKER_STATS_FILE, 'w') as f:
                json.dump({}, f)
        
        if not os.path.exists(BATCH_HISTORY_FILE):
            with open(BATCH_HISTORY_FILE, 'w') as f:
                json.dump([], f)

    @staticmethod
    def log_event(event_type, profile_name, status, message, duration=0, metadata=""):
        """
        Write event to bot_log.txt
        Format: [TIMESTAMP] EVENT_TYPE | PROFILE | STATUS | MESSAGE | DURATION | METADATA
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] {event_type} | {profile_name} | {status} | {message} | {duration}s | {metadata}\n"
        
        try:
            with open(BOT_LOG_FILE, "a") as f:
                f.write(log_line)
        except Exception as e:
            print(f"Error logging event: {e}")

    @staticmethod
    def log_email_attempt(email, profile_name, success, error_msg=""):
        """
        Write email login attempt to email_history.txt
        Format: [TIMESTAMP] EMAIL | PROFILE | SUCCESS/FAILED | ERROR_MSG
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "SUCCESS" if success else "FAILED"
        log_line = f"[{timestamp}] {email} | {profile_name} | {status} | {error_msg}\n"
        
        try:
            with open(EMAIL_HISTORY_FILE, "a") as f:
                f.write(log_line)
        except Exception as e:
            print(f"Error logging email attempt: {e}")

    @staticmethod
    def log_simple_event(text):
        """
        Write simple text line to events_log.txt (for quick tracking)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] {text}\n"
        
        try:
            with open(EVENTS_LOG_FILE, "a") as f:
                f.write(log_line)
        except Exception as e:
            print(f"Error logging simple event: {e}")

    @staticmethod
    def update_worker_stats(profile_name, total_processed, successful, failed, runtime):
        """
        Update worker_stats.json with per-worker statistics
        """
        try:
            # Read existing stats
            if os.path.exists(WORKER_STATS_FILE):
                with open(WORKER_STATS_FILE, "r") as f:
                    try:
                        stats = json.load(f)
                    except:
                        stats = {}
            else:
                stats = {}
            
            # Update/Add worker
            stats[profile_name] = {
                "total_processed": total_processed,
                "successful": successful,
                "failed": failed,
                "success_rate": round((successful / total_processed * 100), 2) if total_processed > 0 else 0,
                "runtime": runtime,
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Write back
            with open(WORKER_STATS_FILE, "w") as f:
                json.dump(stats, f, indent=2)
        except Exception as e:
            print(f"Error updating worker stats: {e}")

    @staticmethod
    def add_batch_history(batch_id, start_time, total_workers, total_links, successful, failed):
        """
        Add batch record to batch_history.json
        """
        try:
            # Read existing batches
            if os.path.exists(BATCH_HISTORY_FILE):
                with open(BATCH_HISTORY_FILE, "r") as f:
                    try:
                        batches = json.load(f)
                    except:
                        batches = []
            else:
                batches = []
            
            # Add new batch
            batch_record = {
                "batch_id": batch_id,
                "start_time": start_time,
                "end_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_workers": total_workers,
                "total_links": total_links,
                "successful_links": successful,
                "failed_links": failed,
                "success_rate": round((successful / total_links * 100), 2) if total_links > 0 else 0
            }
            
            batches.append(batch_record)
            
            # Write back (keep only last 100 batches to avoid huge file)
            if len(batches) > 100:
                batches = batches[-100:]
            
            with open(BATCH_HISTORY_FILE, "w") as f:
                json.dump(batches, f, indent=2)
        except Exception as e:
            print(f"Error adding batch history: {e}")

    @staticmethod
    def get_tail_log(filename, lines=50):
        """
        Get last N lines from a log file
        """
        try:
            if not os.path.exists(filename):
                return []
            
            with open(filename, "r") as f:
                all_lines = f.readlines()
                return all_lines[-lines:] if len(all_lines) > lines else all_lines
        except:
            return []

    @staticmethod
    def read_json_file(filename):
        """
        Read and parse JSON file
        """
        try:
            if not os.path.exists(filename):
                return {} if "stats" in filename else []
            
            with open(filename, "r") as f:
                return json.load(f)
        except:
            return {} if "stats" in filename else []

    @staticmethod
    def cleanup_old_logs(days=30):
        """
        Clean up old log entries (keep only recent logs)
        This prevents log files from growing too large
        """
        import re
        
        cutoff_time = datetime.now().timestamp() - (days * 86400)
        
        for log_file in [BOT_LOG_FILE, EMAIL_HISTORY_FILE, EVENTS_LOG_FILE]:
            if not os.path.exists(log_file):
                continue
            
            try:
                with open(log_file, "r") as f:
                    lines = f.readlines()
                
                # Filter out old entries
                filtered_lines = []
                for line in lines:
                    try:
                        # Extract timestamp from line format: [YYYY-MM-DD HH:MM:SS]
                        match = re.search(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]', line)
                        if match:
                            time_str = match.group(1)
                            line_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S").timestamp()
                            if line_time > cutoff_time:
                                filtered_lines.append(line)
                    except:
                        filtered_lines.append(line)  # Keep lines that can't be parsed
                
                # Write back cleaned logs
                with open(log_file, "w") as f:
                    f.writelines(filtered_lines)
            except Exception as e:
                print(f"Error cleaning log file {log_file}: {e}")

# Initialize files on import
DashboardLogger.init_files()

if __name__ == "__main__":
    print("✅ Dashboard logger initialized!")
    print(f"Log files created in: {BASE_DIR}")
    print(f"  - {BOT_LOG_FILE}")
    print(f"  - {EMAIL_HISTORY_FILE}")
    print(f"  - {WORKER_STATS_FILE}")
    print(f"  - {BATCH_HISTORY_FILE}")
    print(f"  - {EVENTS_LOG_FILE}")
