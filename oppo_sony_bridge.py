#!/usr/bin/env python3
import os
import sys
import time
import datetime
import ftplib
import threading
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

# Folder on OPPO Phone Storage
LOCAL_FOLDER = "/sdcard/Pictures/SonyRaw"
os.makedirs(LOCAL_FOLDER, exist_ok=True)

# Maclab SSD NAS over Tailscale
MACLAB_IP = "100.83.0.1"
MACLAB_PORT = 2121

def do_upload(file_path):
    filename = os.path.basename(file_path)
    if filename.startswith("."):
        return
    
    # Wait briefly for file write to complete
    time.sleep(0.5)
    
    size_mb = os.path.getsize(file_path) / (1024 * 1024)
    now_str = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"📸 [{now_str}] Received on OPPO: {filename} ({size_mb:.2f} MB)")
    print(f"🚀 [{now_str}] Syncing {filename} to Maclab SSD NAS...")
    sys.stdout.flush()

    try:
        ftp = ftplib.FTP()
        ftp.connect(MACLAB_IP, MACLAB_PORT, timeout=20)
        ftp.login("sony", "clubsxai")
        with open(file_path, "rb") as f:
            ftp.storbinary(f"STOR {filename}", f)
        ftp.quit()
        print(f"✅ [{now_str}] {filename} Synced to Maclab SSD NAS Successfully!")
    except Exception as e:
        print(f"⚠️ [{now_str}] Sync error to Maclab: {e}")
    sys.stdout.flush()

class DirectPhoneHandler(FTPHandler):
    def on_file_received(self, file_path):
        threading.Thread(target=do_upload, args=(file_path,), daemon=True).start()

def main():
    authorizer = DummyAuthorizer()
    authorizer.add_user("sony", "clubsxai", LOCAL_FOLDER, perm="elradfmwMT")
    authorizer.add_anonymous(LOCAL_FOLDER, perm="elradfmwMT")

    handler = DirectPhoneHandler
    handler.authorizer = authorizer
    handler.banner = "=== OPPO SONY DIRECT SYNC HUB READY ==="
    handler.passive_ports = range(50000, 50050)

    server = FTPServer(("0.0.0.0", 2121), handler)
    server.max_cons = 20
    server.max_cons_per_ip = 5

    print("🚀 OPPO Sony Bridge Service is LIVE on port 2121!")
    print(f"📁 Local Phone Folder: {LOCAL_FOLDER}")
    print(f"🔒 Auto-Sync Destination: ftp://{MACLAB_IP}:{MACLAB_PORT} (Maclab SSD)")
    sys.stdout.flush()
    server.serve_forever()

if __name__ == "__main__":
    main()
