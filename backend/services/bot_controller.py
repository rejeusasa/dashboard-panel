"""
Bot Control Service
"""
import subprocess
import sys
import os
import time
import psutil
from config import FILE_LOGIN, FILE_LOOP, SCREEN_LOGIN, SCREEN_LOOP, WORK_DIR
from services.process_manager import ProcessManager

class BotController:
    
    def is_busy(self):
        """
        Check if bot is busy
        """
        return (
            ProcessManager.check_process(FILE_LOGIN) or
            ProcessManager.check_process(FILE_LOOP)
        )
    
    def start_login(self):
        """
        Start login.py
        """
        try:
            cmd = (
                f"xvfb-run -a --server-args='-screen 0 {SCREEN_LOGIN}' "
                f"{sys.executable} {FILE_LOGIN}"
            )
            subprocess.Popen(cmd, shell=True, cwd=WORK_DIR)
            return True
        except Exception as e:
            print(f"Error starting login: {e}")
            return False
    
    def start_loop(self):
        """
        Start loop.py
        """
        try:
            cmd = (
                f"xvfb-run -a --server-args='-screen 0 {SCREEN_LOOP}' "
                f"{sys.executable} -u {FILE_LOOP}"
            )
            subprocess.Popen(cmd, shell=True, cwd=WORK_DIR)
            return True
        except Exception as e:
            print(f"Error starting loop: {e}")
            return False
    
    def stop_all(self):
        """
        Stop all bot processes
        """
        targets = [FILE_LOGIN, FILE_LOOP, 'chrome', 'chromedriver', 'xvfb']
        ProcessManager.kill_processes(targets)
        return True
    
    def clean_system(self):
        """
        Clean system resources
        """
        try:
            # Clean zombies
            for p in psutil.process_iter(['status']):
                try:
                    if p.info['status'] == psutil.STATUS_ZOMBIE:
                        p.wait(timeout=0)
                except:
                    pass
            
            # Get freed memory
            mem_before = psutil.virtual_memory().available
            os.system("sync")
            time.sleep(1)
            mem_after = psutil.virtual_memory().available
            
            freed_mb = (mem_after - mem_before) // 1024 // 1024
            return abs(freed_mb)
        except Exception as e:
            print(f"Error cleaning system: {e}")
            return 0
