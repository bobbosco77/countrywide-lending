import os
import shutil
import zipfile
import subprocess
from pathlib import Path

from django.conf import settings

from .backup_service import BackupService


class RestoreService:

    ####################################################################
    # SQLITE DATABASE
    ####################################################################

    @classmethod
    def restore_database(cls, database_file):

        database_file = Path(database_file)

        if not database_file.exists():
            raise FileNotFoundError(database_file)

        BackupService.emergency_backup()

        destination = settings.BASE_DIR / "db.sqlite3"

        shutil.copy2(database_file, destination)

        return True

    ####################################################################
    # MYSQL DATABASE (TRUEHOST)
    ####################################################################

    @classmethod
    def restore_mysql(cls, sql_file):

        sql_file = Path(sql_file)

        if not sql_file.exists():
            raise FileNotFoundError(sql_file)

        BackupService.auto_backup()

        db = settings.DATABASES["default"]

        command = [
            "mysql",
            "-h", db["HOST"],
            "-u", db["USER"],
            f"-p{db['PASSWORD']}",
            db["NAME"],
        ]

        with open(sql_file, "r", encoding="utf-8") as infile:
            subprocess.run(command, stdin=infile, check=True)

        return True

    ####################################################################
    # AUTO DATABASE
    ####################################################################

    @classmethod
    def restore_auto_database(cls, backup_file):

        engine = settings.DATABASES["default"]["ENGINE"]

        if "sqlite" in engine:
            return cls.restore_database(backup_file)

        return cls.restore_mysql(backup_file)

    ####################################################################
    # MEDIA
    ####################################################################

    @classmethod
    def restore_media(cls, zip_file):

        zip_file = Path(zip_file)

        if not zip_file.exists():
            raise FileNotFoundError(zip_file)

        media_root = Path(settings.MEDIA_ROOT)

        if media_root.exists():
            shutil.rmtree(media_root)

        media_root.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(zip_file, "r") as archive:
            archive.extractall(media_root)

        return True

    ####################################################################
    # FULL PROJECT
    ####################################################################

    @classmethod
    def restore_full(cls, zip_file):

        zip_file = Path(zip_file)

        if not zip_file.exists():
            raise FileNotFoundError(zip_file)

        BackupService.auto_backup()

        with zipfile.ZipFile(zip_file, "r") as archive:
            archive.extractall(settings.BASE_DIR)

        return True