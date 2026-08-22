import os
import shutil
import zipfile
import socket
import json
import urllib.request
import urllib.error
import ssl
from pathlib import Path
from datetime import datetime
import config
from yalda.database.connection import SessionLocal
from yalda.models.database_models import BackupRecord
from yalda.utils.jalali_date import gregorian_to_shamsi


def create_local_backup() -> Path:
    """Always updates and overwrites the single local backup in data/backups/latest_backup.db and AppData."""
    if not config.DB_PATH.exists():
        return None
        
    config.BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    local_backup_file = config.BACKUPS_DIR / "latest_backup.db"
    
    try:
        shutil.copy2(config.DB_PATH, local_backup_file)
    except Exception as e:
        print(f"Error saving local backup: {e}")
        
    # Sync to persistent AppData
    try:
        config.APPDATA_DATA_DIR.mkdir(parents=True, exist_ok=True)
        appdata_db = config.APPDATA_DATA_DIR / "yalda.db"
        shutil.copy2(config.DB_PATH, appdata_db)
    except Exception as e:
        print(f"Error syncing to AppData: {e}")
        
    return local_backup_file


def export_offline_backup(target_file_path: str) -> bool:
    """Exports a copy of the database to the specified custom path and refreshes local backup."""
    if not config.DB_PATH.exists():
        return False
    try:
        target_p = Path(target_file_path)
        target_p.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(config.DB_PATH, target_p)
        create_local_backup()
        return True
    except Exception as e:
        print(f"Error exporting offline backup: {e}")
        return False


def is_internet_connected(timeout: float = 2.5) -> bool:
    """Checks if active internet connection is available."""
    hosts = [
        ("8.8.8.8", 53),
        ("1.1.1.1", 53),
        ("google.com", 80)
    ]
    for host, port in hosts:
        try:
            s = socket.create_connection((host, port), timeout=timeout)
            s.close()
            return True
        except (socket.timeout, OSError):
            continue
    return False


def upload_cloud_backup(trainer_phone: str, trainer_name: str = "", server_url: str = None) -> tuple[bool, str]:
    """Uploads the database to the Yalda Cloud Backup Server."""
    if not config.DB_PATH.exists():
        return False, "فایل پایگاه‌داده یافت نشد."
        
    # 1. Verify Internet Connection
    if not is_internet_connected():
        return False, "اتصال اینترنت برقرار نیست. لطفاً سیستم خود را به اینترنت متصل کنید و دوباره تلاش نمایید."
        
    url = server_url or config.DEFAULT_CLOUD_BACKUP_URL
    if not url.endswith("/"):
        upload_endpoint = f"{url}/api/backup/upload"
    else:
        upload_endpoint = f"{url}api/backup/upload"
        
    # Always refresh local backup
    create_local_backup()
    
    # 2. Prepare Multipart Form Data
    try:
        boundary = "----WebKitFormBoundaryYaldaGym" + os.urandom(8).hex()
        
        with open(config.DB_PATH, "rb") as f:
            db_bytes = f.read()
            
        body = bytearray()
        
        # Field: phone
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(f'Content-Disposition: form-data; name="phone"\r\n\r\n'.encode("utf-8"))
        body.extend(f"{trainer_phone}\r\n".encode("utf-8"))
        
        # Field: trainer_name
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(f'Content-Disposition: form-data; name="trainer_name"\r\n\r\n'.encode("utf-8"))
        body.extend(f"{trainer_name}\r\n".encode("utf-8"))
        
        # Field: file
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(f'Content-Disposition: form-data; name="file"; filename="yalda.db"\r\n'.encode("utf-8"))
        body.extend(b"Content-Type: application/octet-stream\r\n\r\n")
        body.extend(db_bytes)
        body.extend(b"\r\n")
        
        # Closing boundary
        body.extend(f"--{boundary}--\r\n".encode("utf-8"))
        
        req = urllib.request.Request(upload_endpoint, data=bytes(body), method="POST")
        req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
        req.add_header("X-API-Key", config.CLOUD_BACKUP_SECRET_KEY)
        req.add_header("User-Agent", f"YaldaGymDesktop/{config.APP_VERSION}")
        
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        with urllib.request.urlopen(req, timeout=25, context=ctx) as response:
            resp_data = json.loads(response.read().decode("utf-8"))
            if response.status in (200, 201) and resp_data.get("success", True):
                return True, "نسخه پشتیبان با موفقیت در سرور ابری و حافظه سیستم ذخیره شد."
            else:
                return False, resp_data.get("message", "خطا در ثبت بک‌آپ روی سرور.")
                
    except urllib.error.HTTPError as e:
        try:
            err_body = json.loads(e.read().decode("utf-8"))
            return False, err_body.get("detail", err_body.get("message", f"خطای سرور: {e.code}"))
        except Exception:
            return False, f"خطای ارتباط با سرور (کد {e.code})"
    except Exception as e:
        return False, f"خطا در ارسال نسخه پشتیبان به سرور ابری: {str(e)}"


class BackupService:
    @staticmethod
    def get_all_backups():
        with SessionLocal() as db:
            return db.query(BackupRecord).order_by(BackupRecord.created_at.desc()).all()

    @staticmethod
    def create_backup() -> str:
        config.BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        filename = f"yalda_backup_{timestamp}.zip"
        filepath = config.BACKUPS_DIR / filename

        with zipfile.ZipFile(filepath, "w", zipfile.ZIP_DEFLATED) as zipf:
            if config.DB_PATH.exists():
                zipf.write(config.DB_PATH, arcname="yalda.db")
            if config.UPLOADS_DIR.exists():
                for root, _, files in os.walk(config.UPLOADS_DIR):
                    for file in files:
                        full_p = Path(root) / file
                        rel_p = full_p.relative_to(config.DATA_DIR)
                        zipf.write(full_p, arcname=str(rel_p))

        file_size_mb = round(os.path.getsize(filepath) / (1024 * 1024), 2)
        shamsi_date = gregorian_to_shamsi(now.date()) + " " + now.strftime("%H:%M")

        with SessionLocal() as db:
            record = BackupRecord(
                file_name=filename,
                file_path=str(filepath),
                backup_size_mb=file_size_mb,
                backup_date_shamsi=shamsi_date,
                created_at=now
            )
            db.add(record)
            db.commit()

        create_local_backup()
        return str(filepath)

    @staticmethod
    def restore_backup(filepath: str):
        if not os.path.exists(filepath):
            raise FileNotFoundError("فایل بک‌آپ یافت نشد.")

        if filepath.endswith(".zip"):
            with zipfile.ZipFile(filepath, "r") as zipf:
                zipf.extractall(config.DATA_DIR)
        elif filepath.endswith(".db"):
            shutil.copy2(filepath, config.DB_PATH)

        create_local_backup()