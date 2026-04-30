# File Organizer

Desktop app for organizing files by type with a safe preview-first workflow.

## Download

Download the portable release from GitHub Releases:

[File Organizer v1.1.0](https://github.com/JSTranquility/FilesOrganizer/releases/tag/v1.1.0)

Extract the ZIP and run `File Organizer.exe`.

## Features

- Preview planned moves before changing files.
- Organize files into editable categories.
- Ignore specific extensions or filenames.
- Avoid overwriting files by automatically renaming duplicates.
- Undo the last organization from the app.
- View a summary of moved files by category.

## Run From Source

Requirements:

- Python 3.10+
- pip

Installation:

```bash
git clone https://github.com/JSTranquility/FilesOrganizer.git
cd FilesOrganizer
pip install -r requirements.txt
python main.py
```

## Usage

1. Open the app.
2. Select a folder.
3. Adjust categories or exclusions if needed.
4. Click `Preview`.
5. Click `Organize` when the preview looks right.
6. Use `Undo Last Move` if you want to restore the previous organization.

## Default Categories

| Category | Extensions |
| --- | --- |
| Images | PNG, JPG, JPEG, GIF, WEBP, BMP, SVG |
| Documents | TXT, PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX |
| Audio | MP3, WAV, OGG, FLAC, M4A |
| Video | MP4, MOV, AVI, MKV, WEBM |
| Archives | ZIP, RAR, 7Z, TAR, GZ |
| Executables | EXE, MSI, BAT, CMD |
| Other | Any extension not matched above |

## Project Files

- `main.py` - Main application.
- `requirements.txt` - Runtime dependencies.
- `icon.ico` - Window icon.

## Version

1.1.0
