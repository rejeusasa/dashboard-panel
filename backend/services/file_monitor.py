"""
File Monitoring Service
"""
import os
import json
from datetime import datetime
from config import WATCH_FILES

class FileMonitor:
    def __init__(self):
        self.last_modified = {}
        self.cache = {}
    
    def read_file(self, file_type, file_path):
        """
        Read file with caching
        """
        try:
            if not os.path.exists(file_path):
                return None
            
            # Check if modified
            mtime = os.path.getmtime(file_path)
            if file_type in self.last_modified:
                if self.last_modified[file_type] == mtime:
                    return self.cache.get(file_type)
            
            # Read file
            with open(file_path, 'r') as f:
                if file_type == 'monitor':
                    content = json.load(f)
                else:
                    content = [x.strip() for x in f if x.strip()]
            
            # Cache it
            self.last_modified[file_type] = mtime
            self.cache[file_type] = content
            
            return content
        except Exception as e:
            print(f"Error reading {file_type}: {e}")
            return None
    
    def get_all_files(self):
        """
        Get all monitored files data
        """
        result = {}
        for file_type, file_path in WATCH_FILES.items():
            result[file_type] = self.read_file(file_type, file_path)
        return result
