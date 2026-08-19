import os
import sys
import time
import shutil
import datetime
import logging
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

# Base Storage on External SSD
NAS_DIR = "/Volumes/Club S/NAS_Photo_Hub"
INCOMING_DIR = os.path.join(NAS_DIR, "Incoming")
EVENTS_DIR = os.path.join(NAS_DIR, "Events")

os.makedirs(INCOMING_DIR, exist_ok=True)
os.makedirs(EVENTS_DIR, exist_ok=True)

# Tracking session state
SESSION_STATE = {
    "last_photo_time": 0,
    "current_event_dir": None,
    "session_index": 0,
    "current_date": None
}

# Session Gap threshold: 30 minutes between shots = New Session / New Job
SESSION_GAP_SECONDS = 30 * 60

def get_or_create_event_folder():
    now = datetime.datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    current_timestamp = time.time()

    # Reset counter if new day
    if SESSION_STATE["current_date"] != today_str:
        SESSION_STATE["current_date"] = today_str
        SESSION_STATE["session_index"] = 0
        SESSION_STATE["last_photo_time"] = 0

    # If gap between shots > 30 minutes, create a new Event/Job session
    if (current_timestamp - SESSION_STATE["last_photo_time"]) > SESSION_GAP_SECONDS:
        SESSION_STATE["session_index"] += 1
        time_tag = now.strftime("%H%M")
        folder_name = f"{today_str}_งานที่{SESSION_STATE['session_index']}_{time_tag}"
        target_dir = os.path.join(EVENTS_DIR, today_str, folder_name)
        os.makedirs(target_dir, exist_ok=True)
        SESSION_STATE["current_event_dir"] = target_dir
        print(f"\n📁 [NEW EVENT SESSION CREATED]: {folder_name}")

    SESSION_STATE["last_photo_time"] = current_timestamp
    return SESSION_STATE["current_event_dir"]

class SonyAutoSortHandler(FTPHandler):
    def on_file_received(self, file_path):
        filename = os.path.basename(file_path)
        if filename.startswith("."):
            return

        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        event_folder = get_or_create_event_folder()
        dest_path = os.path.join(event_folder, filename)

        # Move file from Incoming to sorted Event folder
        shutil.move(file_path, dest_path)

        now_str = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"📸 [{now_str}] Moved: {filename} ({size_mb:.2f} MB) ➔ 📁 {os.path.basename(event_folder)}")
        sys.stdout.flush()

def start_server():
    authorizer = DummyAuthorizer()
    authorizer.add_user("sony", "clubsxai", INCOMING_DIR, perm="elradfmwMT")
    authorizer.add_anonymous(INCOMING_DIR, perm="elradfmwMT")

    handler = SonyAutoSortHandler
    handler.authorizer = authorizer
    handler.banner = "=== MACLAB SSD NAS PHOTO HUB AUTO-ORGANIZER READY ==="
    handler.passive_ports = range(60000, 60050)

    server = FTPServer(("0.0.0.0", 2121), handler)
    server.max_cons = 20
    server.max_cons_per_ip = 5

    print("🚀 NAS Photo Hub Auto-Organizer Started!")
    print(f"📁 Root Storage: {NAS_DIR}")
    print(f"📂 Event Archive: {EVENTS_DIR}/<YYYY-MM-DD>/<งานที่ N>/")
    print("🌐 LAN IP: ftp://10.70.199.95:2121")
    print("🔒 Tailscale: ftp://100.83.0.1:2121")
    print("🔑 User: sony / Pass: clubsxai")
    sys.stdout.flush()

    server.serve_forever()

if __name__ == "__main__":
    start_server()
