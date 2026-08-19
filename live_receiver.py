#!/usr/bin/env python3
"""
Sony Camera Live Auto-Receive & AI Pipeline Hub
1. Runs a high-performance local FTP Server for Sony A7C Auto-Transfer
2. Watches for incoming photos (.JPG / .ARW)
3. Ready to trigger AI Face Detection, Tone Grading, or Sync to Cloud/LINE
"""

import os
import sys
import time
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from threading import Thread

INCOMING_DIR = os.path.expanduser("~/Pictures/SonyLiveShoot")
os.makedirs(INCOMING_DIR, exist_ok=True)

class PhotoHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        filename = event.src_path
        ext = os.path.splitext(filename)[1].lower()
        if ext in ['.jpg', '.jpeg', '.arw', '.png']:
            print(f"\n[📸 NEW PHOTO RECEIVED] -> {os.path.basename(filename)}")
            print(f"   Path: {filename}")
            # Placeholder for AI Face Recognition / Color grading hook
            # e.g., process_image(filename)

def run_watcher():
    event_handler = PhotoHandler()
    observer = Observer()
    observer.schedule(event_handler, INCOMING_DIR, recursive=True)
    observer.start()
    print(f"[👀 WATCHER ACTIVE] Monitoring folder: {INCOMING_DIR}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def run_ftp_server(host="0.0.0.0", port=2121):
    authorizer = DummyAuthorizer()
    # User: sony / Pass: sony1234
    authorizer.add_user("sony", "sony1234", INCOMING_DIR, perm="elradfmwMT")
    authorizer.add_anonymous(INCOMING_DIR)

    handler = FTPHandler
    handler.authorizer = authorizer
    handler.banner = "Sony Alpha Live Receiver Ready."

    server = FTPServer((host, port), handler)
    server.max_cons = 10
    server.max_cons_per_ip = 5

    print(f"\n==========================================")
    print(f"🚀 Sony Alpha FTP Live Receiver Server")
    print(f"📡 Host: {host} | Port: {port}")
    print(f"📁 Storage: {INCOMING_DIR}")
    print(f"🔑 Auth: sony / sony1234 (or anonymous)")
    print(f"==========================================\n")
    server.serve_forever()

if __name__ == "__main__":
    watcher_thread = Thread(target=run_watcher, daemon=True)
    watcher_thread.start()
    run_ftp_server()
