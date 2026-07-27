import shutil
import zipfile
import os
from datetime import datetime
from pathlib import Path
import config
from yalda.database.connection import get_session, engine
from yalda.models.database_models import BackupRecord
from yalda.utils.jalali_date import get_today_shamsi

class BackupService:
    @staticmethod
    def create_backup(backup_type: str = "manual") -> str:
        """Creates a ZIP backup of database and uploaded files."""
        session = get_session()
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"yalda_backup_{timestamp}.zip"
            backup_filepath = config.BACKUPS_DIR / backup_filename

            with zipfile.ZipFile(backup_filepath, "w", zipfile.ZIP_DEFLATED) as zipf:
                # Add database file if exists
                if config.DB_PATH.exists():
                    zipf.write(config.DB_PATH, arcname="yalda.db")

                # Add uploads folder if exists
                if config.UPLOADS_DIR.exists():
                    for root, dirs, files in os.walk(config.UPLOADS_DIR):
                        for file in files:
                            full_path = Path(root) / file
                            arc_name = full_path.relative_to(config.DATA_DIR)
                            zipf.write(full_path, arcname=str(arc_name))

            size_mb = round(os.path.getsize(backup_filepath) / (1024 * 1024), 2)
            today_str = get_today_shamsi()

            record = BackupRecord(
                file_name=backup_filename,
                file_path=str(backup_filepath),
                backup_date_shamsi=today_str,
                backup_size_mb=size_mb
            )
            session.add(record)
            session.commit()
            return str(backup_filepath)
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @staticmethod
    def get_all_backups():
        session = get_session()
        try:
            return session.query(BackupRecord).order_by(BackupRecord.id.desc()).all()
        finally:
            session.close()

    @staticmethod
    def restore_backup(backup_filepath: str):
        """Restores database and uploads from a backup ZIP file."""
        if not os.path.exists(backup_filepath):
            raise FileNotFoundError("فایل پشتیبان پیدا نشد.")

        # Close active database connections
        engine.dispose()

        temp_extract_dir = config.DATA_DIR / "temp_restore"
        if temp_extract_dir.exists():
            shutil.rmtree(temp_extract_dir)
        temp_extract_dir.mkdir(parents=True, exist_ok=True)

        try:
            with zipfile.ZipFile(backup_filepath, "r") as zipf:
                zipf.extractall(temp_extract_dir)

            # Overwrite yalda.db
            extracted_db = temp_extract_dir / "yalda.db"
            if extracted_db.exists():
                shutil.copy2(extracted_db, config.DB_PATH)

            # Overwrite uploads directory
            extracted_uploads = temp_extract_dir / "uploads"
            if extracted_uploads.exists():
                if config.UPLOADS_DIR.exists():
                    shutil.rmtree(config.UPLOADS_DIR)
                shutil.copytree(extracted_uploads, config.UPLOADS_DIR)

        finally:
            if temp_extract_dir.exists():
                shutil.rmtree(temp_extract_dir)
