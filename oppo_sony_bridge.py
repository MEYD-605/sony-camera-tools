#!/usr/bin/env python3
import os
import sys
import time
import subprocess
import threading
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

PHONE_STORAGE_DIR = "/sdcard/Pictures/SonyRaw"
os.makedirs(PHONE_STORAGE_DIR, exist_ok=True)

MACLAB_TARGET = "admin@100.83.0.1:/Users/admin/NAS_Photo_Hub/"

def sync_file_to_mac(file_path):
    filename = os.path.basename(file_path)
    if filename.startswith("."):
        return
    
    cmd = [
        "rsync", "-avz",
        "-e", "ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10",
        file_path,
        MACLAB_TARGET
    ]
    try:
        subprocess.run(cmd, check=True)
        print(f"✅ Fast Rsync {filename} to Maclab SSD complete!")
    except Exception as e:
        print(f"⚠️ Rsync error for {filename}: {e}")

class FastBridgeHandler(FTPHandler):
    def on_file_received(self, file_path):
        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        filename = os.path.basename(file_path)
        print(f"📸 [PHONE RECEIVED]: {filename} ({size_mb:.2f} MB)")
        threading.Thread(target=sync_file_to_mac, args=(file_path,), daemon=True).start()

def main():
    authorizer = DummyAuthorizer()
    authorizer.add_user("sony", "clubsxai", PHONE_STORAGE_DIR, perm="elradfmwMT")
    authorizer.add_anonymous(PHONE_STORAGE_DIR, perm="elradfmwMT")

    handler = FastBridgeHandler
    handler.authorizer = authorizer
    handler.banner = "=== OPPO SONY FAST SYNC READY ==="
    handler.passive_ports = range(50000, 50050)

    server = FTPServer(("0.0.0.0", 2121), handler)
    server.max_cons = 20
    server.max_cons_per_ip = 5

    print("🚀 OPPO Fast Sync Service is LIVE on port 2121!")
    print(f"📁 Local Storage: {PHONE_STORAGE_DIR}")
    print(f"🔒 Destination: {MACLAB_TARGET}")
    sys.stdout.flush()

    server.serve_forever()

if __name__ == "__main__":
    main()
