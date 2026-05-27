import sys
from pathlib import Path


APP_VERSION = "1.2.1"
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

if getattr(sys, "frozen", False):
    RESOURCE_ROOT = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
else:
    RESOURCE_ROOT = PROJECT_ROOT

APP_ICO = RESOURCE_ROOT / "assets" / "app_logo.ico"
LOGO_PATH = RESOURCE_ROOT / "assets" / "logo.png"

DEFAULT_CATEGORIES = {
    "Images": ".png, .jpg, .jpeg, .gif, .webp, .bmp, .svg",
    "Documents": ".txt, .pdf, .doc, .docx, .xls, .xlsx, .ppt, .pptx",
    "Audio": ".mp3, .wav, .ogg, .flac, .m4a",
    "Video": ".mp4, .mov, .avi, .mkv, .webm",
    "Archives": ".zip, .rar, .7z, .tar, .gz",
    "Executables": ".exe, .msi, .bat, .cmd",
}

CATEGORY_FOLDER_ALIASES = {
    "Images": ("Images", "Imagenes", "Imágenes", "Fotos", "Photos", "Pictures"),
    "Documents": ("Documents", "Documentos", "Docs", "PDF", "PDFs"),
    "Audio": ("Audio", "Audios", "Musica", "Música", "Music"),
    "Video": ("Video", "Videos", "Vídeos", "Movies", "Peliculas", "Películas"),
    "Archives": ("Archives", "Comprimidos", "Compressed", "ZIP", "ZIPs", "RAR", "7Z"),
    "Executables": ("Executables", "Ejecutables", "Instaladores", "Installers", "Programs", "Programas"),
    "Other": ("Other", "Otros", "Misc", "Varios"),
}
