import time
import os
import threading
from collections import deque

class LogMonitor(threading.Thread):
    def __init__(self, log_paths, callback, window_size=20, stride=1):
        super().__init__()
        self.log_paths = log_paths
        self.callback = callback
        self.window_size = window_size
        self.stride = stride
        self.daemon = True
        self.running = False
        
        # Buffer for each log source
        self.buffers = {path: deque(maxlen=window_size) for path in log_paths}
        self.stop_event = threading.Event()

    def run(self):
        self.running = True
        print(f"[*] Monitoring {len(self.log_paths)} log files...")
        
        threads = []
        for path in self.log_paths:
            t = threading.Thread(target=self.tail_file, args=(path,))
            t.daemon = True
            t.start()
            threads.append(t)
            
        while not self.stop_event.is_set():
            time.sleep(1)

    def tail_file(self, path):
        if not os.path.exists(path):
            print(f"[!] File not found: {path}. Waiting...")
            while not os.path.exists(path) and not self.stop_event.is_set():
                time.sleep(2)
        
        with open(path, 'r', errors='ignore') as f:
            # Move to the end of file
            f.seek(0, os.SEEK_END)
            
            while not self.stop_event.is_set():
                line = f.readline()
                if not line:
                    time.sleep(0.1)
                    continue
                
                line = line.strip()
                if line:
                    self.buffers[path].append(line)
                    
                    if len(self.buffers[path]) >= self.window_size:
                        # Send window for analysis
                        self.callback(list(self.buffers[path]), path)

    def stop(self):
        self.stop_event.set()
        self.running = False
