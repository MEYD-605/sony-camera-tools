import os
import sys
import time
import shutil
import datetime
import logging
import exifread
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

# Base Storage Paths (configurable via environment variables)
NAS_DIR = os.getenv("NAS_STORAGE_DIR", "/Volumes/Club S/NAS_Photo_Hub")
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
SESSION_GAP_SECONDS = int(os.getenv("SESSION_GAP_MINUTES", "30")) * 60

def get_camera_model_from_file(file_path):
    """Extract camera model name (e.g. ILCE-7C, ILCE-7M3) from RAW/JPEG metadata"""
    try:
        with open(file_path, "rb") as f:
            tags = exifread.process_file(f, stop_tag="Image Model", details=False)
            model_tag = tags.get("Image Model")
            if model_tag:
                model_str = str(model_tag.values).strip().replace(" ", "_")
                # Friendly aliases
                if "ILCE-7C" in model_str:
                    return "Sony_A7C"
                elif "ILCE-7M3" in model_str or "ILCE-7RM3" in model_str:
                    return "Sony_A7III"
                elif "ILCE-7M4" in model_str or "ILCE-7RM4" in model_str:
                    return "Sony_A7IV"
                return model_str
    except Exception as e:
        pass
    return "Camera_Unsorted"

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

class SonyMultiCamHandler(FTPHandler):
    def on_file_received(self, file_path):
        filename = os.path.basename(file_path)
        if filename.startswith("."):
            return

        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        event_base_folder = get_or_create_event_folder()

        # Detect Camera Model from RAW/JPEG Exif header (e.g. Sony_A7C / Sony_A7III)
        cam_model = get_camera_model_from_file(file_path)
        camera_folder = os.path.join(event_base_folder, cam_model)
        os.makedirs(camera_folder, exist_ok=True)

        dest_path = os.path.join(camera_folder, filename)

        # Move file from Incoming to sorted Camera folder inside Event
        shutil.move(file_path, dest_path)

        now_str = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"📸 [{now_str}] [{cam_model}] Moved: {filename} ({size_mb:.2f} MB) ➔ 📁 {os.path.basename(event_base_folder)}/{cam_model}/")
        sys.stdout.flush()

def start_server():
    authorizer = DummyAuthorizer()
    
    admin_user = os.getenv("FTP_ADMIN_USER", "clubs")
    admin_pass = os.getenv("FTP_ADMIN_PASSWORD", "clubs2026")
    ingest_user = os.getenv("FTP_INGEST_USER", "sony")
    ingest_pass = os.getenv("FTP_INGEST_PASSWORD", "clubsxai")

    # 1. Full Access to Whole SSD NAS for Cx File Explorer & Browsing
    authorizer.add_user(admin_user, admin_pass, NAS_DIR, perm="elradfmwMT")
    
    # 2. Camera Ingest Users
    authorizer.add_user(ingest_user, ingest_pass, INCOMING_DIR, perm="elradfmwMT")
    authorizer.add_anonymous(NAS_DIR, perm="elradfmwMT")

    handler = SonyMultiCamHandler
    handler.authorizer = authorizer
    handler.banner = "=== SONY ALPHA LIVE INGESTION HUB READY ==="
    handler.passive_ports = range(60000, 60050)

    port = int(os.getenv("FTP_PORT", "2121"))
    host = os.getenv("FTP_HOST", "0.0.0.0")

    server = FTPServer((host, port), handler)
    server.max_cons = 30
    server.max_cons_per_ip = 10

    print(f"🚀 NAS Photo Hub Server Started on {host}:{port}!")
    print(f"📁 Storage Root: {NAS_DIR}")
    print(f"📂 Event Archive: {EVENTS_DIR}/<YYYY-MM-DD>/<งานที่ N>/<Sony_A7C | Sony_A7III>/")
    print(f"🔑 Admin User: {admin_user} | Ingest User: {ingest_user}")
    sys.stdout.flush()

    server.serve_forever()

if __name__ == "__main__":
    start_server()
