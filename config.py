import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Sub-directories for uploads and data
UPLOADS_DIR = DATA_DIR / "uploads"
PROFILE_PHOTOS_DIR = UPLOADS_DIR / "profile-photos"
PROGRESS_PHOTOS_DIR = UPLOADS_DIR / "progress-photos"
EXERCISE_MEDIA_DIR = UPLOADS_DIR / "exercise-media"
PDF_EXPORTS_DIR = DATA_DIR / "pdf"
BACKUPS_DIR = DATA_DIR / "backups"

for folder in [UPLOADS_DIR, PROFILE_PHOTOS_DIR, PROGRESS_PHOTOS_DIR, EXERCISE_MEDIA_DIR, PDF_EXPORTS_DIR, BACKUPS_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

# Database URI
DB_PATH = DATA_DIR / "yalda.db"
DATABASE_URI = f"sqlite:///{DB_PATH}"

# App Details
APP_NAME = "یلدا"
APP_ENGLISH_NAME = "Yalda Gym"
APP_VERSION = "1.0.0"

# Styling & Colors (Dark Red & Black Theme)
COLOR_BACKGROUND = "#121212"
COLOR_SURFACE = "#1E1E1E"
COLOR_SURFACE_LIGHT = "#2D2D2D"
COLOR_PRIMARY_ACCENT = "#8B0000"      # Dark Red
COLOR_PRIMARY_ACCENT_HOVER = "#A91D22" # Lighter Dark Red
COLOR_TEXT_PRIMARY = "#FFFFFF"
COLOR_TEXT_SECONDARY = "#B0B0B0"
COLOR_SUCCESS = "#2E7D32"
COLOR_WARNING = "#F57C00"
COLOR_ERROR = "#D32F2F"
COLOR_BORDER = "#333333"

# Fonts
FONT_FAMILY = "Vazirmatn"
