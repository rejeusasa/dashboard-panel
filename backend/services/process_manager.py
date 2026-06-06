"""
Process Management Service
"""
import psutil
import subprocess
import os
import time

class ProcessManager:
    
    @staticmethod
    def check_process(script_name):
        """
        Check if process is running
        """
        try:
            for p in psutil.process_iter(['cmdline']):
                try:
                    if p.info['cmdline']:
                        cmd_str = ' '.join(p.info['cmdline'])
                        if script_name in cmd_str:
                            return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except:
            pass
        return False
    
    @staticmethod
    def get_cpu_percent():
        """
        Get CPU percentage
        """
        try:
            return psutil.cpu_percent(interval=1)
        except:
            return 0
    
    @staticmethod
    def get_memory_info():
        """
        Get memory information
        """
        try:
            mem = psutil.virtual_memory()
            return {
                'percent': mem.percent,
                'mb': mem.used // 1024 // 1024,
                'available': mem.available // 1024 // 1024,
                'total': mem.total // 1024 // 1024
            }
        except:
            return {
                'percent': 0,
                'mb': 0,
                'available': 0,
                'total': 0
            }
    
    @staticmethod
    def kill_processes(targets):
        """
        Kill processes by name
        """
        my_pid = os.getpid()
        killed = 0
        
        try:
            for p in psutil.process_iter(['name', 'cmdline']):
                try:
                    if p.pid == my_pid:
                        continue
                    
                    name = p.info['name'].lower()
                    cmd = ' '.join(p.info['cmdline']) if p.info['cmdline'] else ''
                    
                    if any(t in cmd or t in name for t in targets):
                        p.kill()
                        killed += 1
                except:
                    pass
        except:
            pass
        
        time.sleep(1)
        return killed
