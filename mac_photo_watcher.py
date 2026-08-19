import os
import sys
import time
import shutil
import datetime
import exifread

NAS_DIR = "/Volumes/Club S/NAS_Photo_Hub"
RAW_FILES_DIR = os.path.join(NAS_DIR, "Raw file")
os.makedirs(RAW_FILES_DIR, exist_ok=True)

SESSION_STATE = {
    "last_photo_time": 0,
    "current_event_dir": None,
    "session_index": 0,
    "current_date": None
}

SESSION_GAP_SECONDS = 30 * 60

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

def get_or_create_event_folder():
    now = datetime.datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    current_timestamp = time.time()

    if SESSION_STATE["current_date"] != today_str:
        SESSION_STATE["current_date"] = today_str
        SESSION_STATE["session_index"] = 0
        SESSION_STATE["last_photo_time"] = 0

    if (current_timestamp - SESSION_STATE["last_photo_time"]) > SESSION_GAP_SECONDS:
        SESSION_STATE["session_index"] += 1
        time_tag = now.strftime("%H%M")
        folder_name = f"{today_str}_งานที่{SESSION_STATE['session_index']}_{time_tag}"
        target_dir = os.path.join(RAW_FILES_DIR, today_str, folder_name)
        os.makedirs(target_dir, exist_ok=True)
        SESSION_STATE["current_event_dir"] = target_dir

    SESSION_STATE["last_photo_time"] = current_timestamp
    return SESSION_STATE["current_event_dir"]

def watch_and_organize():
    print("👀 Mac Watcher Active: Organizing files into Raw file/<Date>/<Job>/<Model>/")
    while True:
        try:
            for item in os.listdir(NAS_DIR):
                item_path = os.path.join(NAS_DIR, item)
                if os.path.isfile(item_path) and item.upper().endswith((".ARW", ".JPG", ".JPEG", ".PNG")):
                    # Check if file size is stable (finished writing)
                    size1 = os.path.getsize(item_path)
                    time.sleep(1.0)
                    size2 = os.path.getsize(item_path)
                    if size1 != size2 or size2 == 0:
                        continue # still transferring, wait next round
                    
                    event_base_folder = get_or_create_event_folder()
                    cam_model = get_camera_model_from_file(item_path)
                    camera_folder = os.path.join(event_base_folder, cam_model)
                    os.makedirs(camera_folder, exist_ok=True)
                    
                    dest_path = os.path.join(camera_folder, item)
                    shutil.move(item_path, dest_path)
                    size_mb = size2 / (1024 * 1024)
                    print(f"📸 Sorted: {item} ({size_mb:.2f} MB) ➔ 📁 {os.path.basename(event_base_folder)}/{cam_model}/")
                    sys.stdout.flush()
        except Exception as e:
            pass
        time.sleep(1)

if __name__ == "__main__":
    watch_and_organize()
