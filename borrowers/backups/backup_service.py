import os
import shutil
import zipfile
import subprocess
from pathlib import Path

from django.conf import settings
from django.utils import timezone


class BackupService:

    BACKUP_FOLDER = Path(settings.MEDIA_ROOT) / "backups"

    EXCLUDED_FOLDERS = {
        "venv",
        "__pycache__",
        ".git",
        ".idea",
        ".vscode",
        "staticfiles",
        "backups",
    }

    EXCLUDED_FILES = {
        "db.sqlite3-journal",
    }

    @classmethod
    def ensure_backup_folder(cls):
        cls.BACKUP_FOLDER.mkdir(parents=True, exist_ok=True)
        return cls.BACKUP_FOLDER

    @classmethod
    def timestamp(cls):
        return timezone.now().strftime("%Y%m%d_%H%M%S")

    @classmethod
    def file_size(cls, filename):
        return os.path.getsize(filename)

    @classmethod
    def cleanup_old_backups(cls, keep=30):

        cls.ensure_backup_folder()

        files = sorted(
            cls.BACKUP_FOLDER.glob("*"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )

        for file in files[keep:]:
            try:
                file.unlink()
            except Exception:
                pass

    #######################################################################
    # SQLITE DATABASE
    #######################################################################

    @classmethod
    def create_database_backup(cls):

        cls.ensure_backup_folder()

        filename = (
            cls.BACKUP_FOLDER /
            f"database_{cls.timestamp()}.sqlite3"
        )

        shutil.copy2(
            settings.BASE_DIR / "db.sqlite3",
            filename
        )

        cls.cleanup_old_backups()

        return str(filename)

    #######################################################################
    # MYSQL DATABASE (TRUEHOST)
    #######################################################################

    @classmethod
    def create_mysql_backup(cls):

        cls.ensure_backup_folder()

        filename = (
            cls.BACKUP_FOLDER /
            f"mysql_{cls.timestamp()}.sql"
        )

        db = settings.DATABASES["default"]

        command = [
            "mysqldump",
            "-h", db["HOST"],
            "-u", db["USER"],
            f"-p{db['PASSWORD']}",
            db["NAME"],
        ]

        with open(filename, "w", encoding="utf-8") as outfile:
            subprocess.run(command, stdout=outfile)

        cls.cleanup_old_backups()

        return str(filename)

    #######################################################################
    # MEDIA
    #######################################################################

    @classmethod
    def create_media_backup(cls):

        cls.ensure_backup_folder()

        filename = (
            cls.BACKUP_FOLDER /
            f"media_{cls.timestamp()}.zip"
        )

        with zipfile.ZipFile(
            filename,
            "w",
            zipfile.ZIP_DEFLATED
        ) as archive:

            media_root = Path(settings.MEDIA_ROOT)

            if media_root.exists():

                for root, dirs, files in os.walk(media_root):

                    for file in files:

                        full_path = Path(root) / file

                        archive.write(
                            full_path,
                            full_path.relative_to(media_root)
                        )

        cls.cleanup_old_backups()

        return str(filename)

    #######################################################################
    # FULL PROJECT
    #######################################################################

    @classmethod
    def create_full_backup(cls):

        cls.ensure_backup_folder()

        filename = (
            cls.BACKUP_FOLDER /
            f"project_{cls.timestamp()}.zip"
        )

        project_root = Path(settings.BASE_DIR)

        with zipfile.ZipFile(
            filename,
            "w",
            zipfile.ZIP_DEFLATED
        ) as archive:

            for root, dirs, files in os.walk(project_root):

                dirs[:] = [
                    d for d in dirs
                    if d not in cls.EXCLUDED_FOLDERS
                ]

                for file in files:

                    if file in cls.EXCLUDED_FILES:
                        continue

                    full_path = Path(root) / file

                    archive.write(
                        full_path,
                        full_path.relative_to(project_root)
                    )

        cls.cleanup_old_backups()

        return str(filename)

    #######################################################################
    # EMERGENCY
    #######################################################################

    @classmethod
    def emergency_backup(cls):
        return cls.create_database_backup()

    #######################################################################
    # AUTO
    #######################################################################

    @classmethod
    def auto_backup(cls):

        engine = settings.DATABASES["default"]["ENGINE"]

        if "sqlite" in engine:

            return cls.create_database_backup()

        return cls.create_mysql_backup()