# 📸 Sony Camera Live NAS Ingestion System

Production-tested automated RAW/JPEG live ingest pipeline from Sony Alpha cameras (ILCE-7C / A7 Series) over Cellular 4G/5G Hotspot & Local LAN directly to Maclab External SSD NAS.

---

## 🏗️ System Architecture

```text
[📷 Sony Alpha A7C]
       │ (Wi-Fi 5GHz / 4G-5G Hotspot)
       ▼ [FTP Port 2121 - RAW & JPEG]
[🖥️ Maclab NAS Hub (iMac Pro)]
       ├─► 💾 SSD Extreme Storage: /Volumes/Club S/NAS_Photo_Hub/
       ├─► 📁 Smart Auto-Organizer: Events/<YYYY-MM-DD>/<YYYY-MM-DD_งานที่N_HHMM>/
       └─► 🌐 Web UI (FileBrowser): Port 8082 (Preview, Download, Share)
```

---

## 🚀 Quick Start

### 1. Start Ingest Server
```bash
/Users/admin/Code/sony-camera-tools/venv/bin/python /Users/admin/Code/sony-camera-tools/nas_photo_ftp_server.py
```

### 2. Start Web UI (File Browser)
```bash
/Users/admin/bin/filebrowser -r "/Volumes/Club S/NAS_Photo_Hub" -a 0.0.0.0 -p 8082 -d /Users/admin/.filebrowser.db
```

---

## 📷 Sony Camera Configuration (A7C)
1. **Network ➔ FTP Transfer Func.:**
   * `FTP Function`: ON
   * `Auto Transfer`: ON
   * `RAW+J Transfer Target`: RAW Only (or RAW & JPEG)
2. **Server Setting ➔ Server 1:**
   * `Display Name`: iMac-NAS
   * `Host Name / IP`: `10.70.199.95` (LAN) or `100.83.0.1` (Tailscale VPN)
   * `Port`: `2121`
   * `Security`: OFF
   * `User Name`: `sony`
   * `Password`: `clubsxai`
   * `Directory`: `/`

---

## 🔐 Web UI Credentials
* **URL:** `http://100.83.0.1:8082` (Tailscale) or `http://10.70.199.95:8082` (Local)
* **Username:** `admin`
* **Password:** `clubs123121`
