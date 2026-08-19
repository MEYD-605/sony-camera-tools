# Sony A7C (ILCE-7C) Remote Control — Deep Research Report
Date: 2026-08-19 · Machine: maclab (iMac Pro, macOS 15.7.9)

## 1. Official Sony Camera Remote SDK (CrSDK) — verified from support.d-imaging.sony.co.jp

- **Latest: Ver 2.02.00 (2026-Jun-10)**. Lineage: 1.03.00 (Oct 2020, **first macOS support** + multi-camera) → … → 2.00.00 (2025-Jun-23: delete-on-camera, background file transfer) → 2.01.00 (Feb 2026) → 2.02.00.
- **ILCE-7C is officially supported** (listed in "Supported device" on the SDK page). Latest firmware required.
- **Interfaces:** USB, Wired LAN, Wi-Fi. **OS:** macOS 14.1+ / 15.1+ / 26.0+, Win11 (x86 only), Linux x64/ARM64/ARM32.
- **Capabilities:** live view monitoring, shutter release, all camera settings, file transfer, multi-cam, remote firmware update (newer bodies), background transfer + delete (2.x, not A7C).
- **License:** free, but requires regional application (pro.sony/ue_US/digital-imaging/sdk-download). Sony page notes some functions/APIs need a license installed on camera (paid "Remote Control" license for pro bodies — A7C generally not affected).
- **C++ (primary) + C# bindings**; no official Python.

### GitHub bindings/tools for CrSDK
| Repo | What |
|---|---|
| https://github.com/olkham/pysonycam | Pure-Python PTP/SDIO control (from Camera Remote Command docs) — best macOS/Python path |
| https://github.com/jakkuh/sony-alpha-python | Minimal PTP skeleton for Alpha |
| https://pypi.org/project/sonyalphapy/ | ctypes bindings to **CrSDK v1** (.dylib) — tested macOS + a7IV, Python ≥3.10, "fragile" per author |
| https://github.com/Jeffxcao/sony-camera-remote-sdk-console-mac | C++ console app, CrSDK v2.00.00, macOS + Wi-Fi (cloned locally) |
| https://github.com/mofu-ken/scp (local `scp/`) | Python wrapper around CrSDK C++ w/ uv packaging |
| sonshell (local) | Linux "ssh into camera" shell on CrSDK: auto-download new captures, hooks |
| ofxSonyCameraRemote / expo-sony-camera / SonyCameraRemoteWin (local) | openFrameworks addon / Expo RN module / Windows CLI (CrSDK 1.05, explicitly mentions A7C) |

## 2. Camera Remote Command (PTP over USB / PTP-IP) — verified from official page + pysonycam source

- Sony's **free** proprietary extension of ISO 15740 (PTP). Note: **corporate customers only** per FAQ (individuals officially can't download; community reimplementations exist).
- **ILCE-7C supported** (listed; USB + Wi-Fi + PTP-IP since 2024.1.0). Warning in v2.02.00 notes: *"Camera Control PTP 2 commands may become unusable on some models from 2027"* — prefer v3 opcodes / CrSDK for longevity.
- pysonycam embeds the full Sony PTP2/PTP3 command reference (750 pages, `docs/sdk/` markdown) — cloned at `/Users/admin/Code/sony-camera-tools/pysonycam`.

### Key opcodes (extracted from pysonycam/pysonycam/constants.py)
**Standard PTP ops:** OpenSession 0x1002 · GetObjectHandles 0x1007 · GetObjectInfo 0x1008 · GetObject 0x1009 · GetThumb 0x100A · DeleteObject 0x100B · GetPartialObject 0x101B

**Sony SDIO vendor ops (0x92xx):** CONNECT 0x9201 · GetExtDeviceInfo 0x9202 · SetExtDevicePropValue 0x9205 · ControlDevice 0x9207 · SDIO_OpenSession 0x9210 · SetContentsTransferMode 0x9212 · **GetContentData 0x923D** (file download) · DeleteContent 0x9250 · GetContentInfoList 0x923C

**Device properties (Set/Get 0x9205/0x9202):**
| Function | Code | Notes |
|---|---|---|
| Shutter speed | 0xD20D | |
| ISO | 0xD21E | |
| F-number (aperture) | standard 0x5007 via pysonycam F_NUMBER_TABLE | |
| Exposure mode | 0x500E | M/A/S/P |
| Exposure comp | 0x5010 | |
| LiveView status/mode | 0xD221 / 0xD26A | frames via LiveView object 0xFFFFC002 |
| Focus mode | 0x500A | |
| Movie rec | 0xD2C8 | |
| AE/AF lock | 0xD2C3 / 0xD2C9 | |
| Focus step near/far | 0xD2D7 / 0xD2D8 | |
| Still capture | ControlDevice 0x9207 prop 0xD2C2 (S2 button half/full press) | |

**Events (0xC2xx):** ObjectAdded 0xC201 · PropChanged 0xC203 · CapturedEvent 0xC206 …
**SDIO protocol version:** v2 = 0xC8 (200), v3 = 0x12C (300).

## 3. SD-card FTP config automation — VERIFIED FINDINGS

- **A7C HAS built-in FTP transfer.** Official Sony FTP Help Guide (helpguide.sony.net/di/ftp/v1/en/, 145pp, saved /tmp/sony-ftp-helpguide.pdf) covers: ILCE-9/9M2/7M3/7RM3/7RM3A/7RM4/7RM4A/**7C**. Path: `MENU → Network → FTP Transfer Func. → Server Setting → Server 1` (host, port, user, pass, passive on/off, dir "Same as in Camera" → `A/DCIM/100MSDCF/…`).
- **FTPSET01.DAT: format is NOT publicly documented.** Only one SonyAlphaForum thread (Apr 2025, unanswered) + a gated Reddit thread ask for it. No reverse-engineering repo exists. Manual decode would require dumping a card after configuring one server.
- **Official automation path = "Transfer & Tagging add-on" mobile app** (free): inputs Server Settings on phone, **writes them to the camera via Bluetooth** (pair first). This is the supported way to bulk-push FTP config — but it needs a phone, not a Mac. (support.d-imaging.sony.co.jp/app/transfer/en/instruction/51_ftp.php)
- **Mac receiver side is solved:** local clone `sony-camera-ftp-macos/` (github.com/Mifaiyang/sony-camera-ftp-macos) sets up `pyftpdlib` FTP server on macOS w/ launchd autostart: user `sonyftp`, port 2121, passive 50000-50050, inbox `~/Public/Sony-Camera-Inbox`, prints the exact values to type into the camera menu once. Script: `scripts/setup_sony_camera_ftp_macos.py`. Camera-menu entry is the one manual step — FTPSET01.DAT generation would remove it but is not currently feasible.

## 4. Concrete code — verified install on maclab

pysonycam v1.0.0 installed OK into `/Users/admin/Code/sony-camera-tools/venv` (needs only `libusb1`; on macOS: `brew install libusb`). Hardware-tested by author only on RX100M7/Win11 — A7C/macOS is first-try territory. API: `SonyCamera(bus=0, device=0, version=300)`.

```python
# /Users/admin/Code/sony-camera-tools/capture_a7c.py
from pysonycam.camera import SonyCamera

cam = SonyCamera(version=300)          # A7C: try v3 first, fall back 200
cam.connect()
cam.set_property('ISO', 0xD21E_ISO800) # see constants ISO_TABLE / F_NUMBER_TABLE
cam.set_property('SHUTTER_SPEED', ...) # 0xD20D
for i, jpg in enumerate(cam.liveview_stream(count=100)):  # JPEG frames
    open(f'lv_{i:03}.jpg','wb').write(jpg)
cam.capture()                          # ControlDevice/S2 full-press
# download: cam.get_content_data(...) via GetContentData 0x923D
cam.disconnect()
```

C++ path (CrSDK, Wi-Fi or USB, needs Sony license grant):
```cpp
CrLib::Init(); auto camera = CrLibrary::GetCamera(); camera->Connect(USB);
camera->SetImageRotation(...); camera->StartLiveview(); camera->SendCommand(CrCommand::HalfPress, CrFindCondition::ON);
camera->SendCommand(CrCommand::FullPress, ...); camera->GetImageList(...); // download
```
(macOS .dylib ships in the SDK `lib/` — link via CMake, sample: `sony-camera-remote-sdk-console-mac/`.)

## 5. Recommended plan for maclab

1. **USB control from Python (no license):** `brew install libusb`, use local venv + pysonycam against A7C (`version=300`, else `200`). Verify `SonyCamera.connect()`; iterate opcodes from `pysonycam/constants.py`; the full command spec is in `pysonycam/docs/sdk/camera_control_ptp_3_reference/`.
2. **If pysonycam+A7C fails on macOS:** apply for CrSDK (free, pro.sony), build `sony-camera-remote-sdk-console-mac` locally (CMake + brew libusb), or try `sonyalphapy` (pip) which wraps CrSDK v1 dylib.
3. **Image ingestion (no SDK at all):** run `python3 sony-camera-ftp-macos/scripts/setup_sony_camera_ftp_macos.py`; type printed values into camera once (MENU→Network→FTP Transfer Func.). Auto-ingest to `~/Public/Sony-Camera-Inbox`. FTPSET01.DAT generation: not feasible today — undocumented.
4. **Watch item:** Sony's 2027 deprecation note on PTP-2 commands → build on PTP-3 (v3) or CrSDK 2.x.
