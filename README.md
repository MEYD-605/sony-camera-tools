# 📸 Sony Camera Live NAS Ingestion System

Production-tested automated RAW/JPEG live ingest pipeline from Sony Alpha cameras (ILCE-7C / A7 Series) over Cellular 4G/5G Hotspot & Local LAN directly to an external storage volume or NAS.

---

## 🏗️ System Architecture

```text
[📷 Sony Alpha A7C / A7III]
       │ (Wi-Fi 5GHz / 4G-5G Hotspot)
       ▼ [FTP Port 2121 - RAW & JPEG]
[🖥️ Local Ingestion Hub (macOS / Linux)]
       ├─► 💾 External SSD / NAS Storage Target
       ├─► 📁 Smart Auto-Organizer: Events/<YYYY-MM-DD>/<YYYY-MM-DD_งานที่N_HHMM>/<Camera_Model>/
       └─► 🌐 Web UI (FileBrowser / Cx File Explorer)
```

---

## 🚀 Quick Start

### 1. Configure Environment
Copy `.env.example` to `.env` and set your credentials/paths:
```bash
cp .env.example .env
```

### 2. Start Ingest Server
```bash
python3 nas_photo_ftp_server.py
```

---

## 📷 Sony Camera Configuration (A7C / A7 Series)
1. **Network ➔ FTP Transfer Func.:**
   * `FTP Function`: ON
   * `Auto Transfer`: ON
   * `RAW+J Transfer Target`: RAW Only (or RAW & JPEG)
2. **Server Setting ➔ Server 1:**
   * `Display Name`: Studio-NAS
   * `Host Name / IP`: `<Your_Host_IP_or_Tailscale_IP>`
   * `Port`: `2121`
   * `Security`: OFF
   * `User Name`: `<Your_Ingest_User>`
   * `Password`: `<Your_Ingest_Password>`
   * `Directory`: `/`
