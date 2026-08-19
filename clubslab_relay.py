#!/usr/bin/env python3
import os
import sys
import time
import shutil
import datetime
import subprocess
import logging
import exifread
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

# Local Relay Storage on VPS
RELAY_DIR = "/var/photo_relay"
INCOMING_DIR = os.path.join(RELAY_DIR, "Incoming")
os.makedirs(INCOMING_DIR, exist_ok=True)

# Maclab Destination over Tailscale
MACLAB_IP = "100.83.0.1"
MACLAB_PORT = 2121

def get_camera_model_from_file(file_path):
    try:
        with open(file_path, "rb") as f:
            tags = exifread.process_file(f, stop_tag="Image Model", details=False)
            model_tag = tags.get("Image Model")
            if model_tag:
                model_str = str(model_tag.values).strip().replace(" ", "_")
                if "ILCE-7C" in model_str:
                    return "Sony_A7C"
                elif "ILCE-7M3" in model_str or "ILCE-7RM3" in model_str:
                    return "Sony_A7III"
                elif "ILCE-7M4" in model_str or "ILCE-7RM4" in model_str:
                    return "Sony_A7IV"
                return model_str
    except Exception:
        pass
    return "Camera_Unsorted"

def forward_to_maclab(file_path):
    filename = os.path.basename(file_path)
    size_mb = os.path.getsize(file_path) / (1024 * 1024)
    now_str = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"📸 [{now_str}] Relaying {filename} ({size_mb:.2f} MB) to Maclab SSD...")
    sys.stdout.flush()
    
    # Send via FTP directly to Maclab SSD NAS
    import ftplib
    try:
        ftp = ftplib.FTP()
        ftp.connect(MACLAB_IP, MACLAB_PORT, timeout=15)
        ftp.login("sony", "clubsxai")
        with open(file_path, "rb") as f:
            ftp.storbinary(f"STOR {filename}", f)
        ftp.quit()
        print(f"✅ [{now_str}] {filename} Successfully arrived on Maclab SSD!")
        os.remove(file_path)
    except Exception as e:
        print(f"⚠️ [{now_str}] Forwarding error: {e}")
    sys.stdout.flush()

class RelayFTPHandler(FTPHandler):
    def on_file_received(self, file_path):
        if os.path.basename(file_path).startswith("."):
            return
        forward_to_maclab(file_path)

def main():
    authorizer = DummyAuthorizer()
    authorizer.add_user("sony", "clubsxai", INCOMING_DIR, perm="elradfmwMT")
    authorizer.add_user("clubs", "clubs2026", INCOMING_DIR, perm="elradfmwMT")
    authorizer.add_anonymous(INCOMING_DIR, perm="elradfmwMT")

    handler = RelayFTPHandler
    handler.authorizer = authorizer
    handler.banner = "=== CLUBSLAB PHOTO RELAY SERVER READY ==="
    handler.masquerade_address = "103.208.27.171"
    handler.passive_ports = range(50000, 50050)

    server = FTPServer(("0.0.0.0", 2121), handler)
    server.max_cons = 30
    server.max_cons_per_ip = 10

    print("🚀 Clubslab Photo Cloud Relay is LIVE on 103.208.27.171:2121!")
    print(f"🔒 Connected to Maclab SSD via Tailscale: {MACLAB_IP}:{MACLAB_PORT}")
    sys.stdout.flush()
    server.serve_forever()

if __name__ == "__main__":
    main()
