import os
import unicodedata
from collections import Counter
from pathlib import Path

from config import CATEGORY_FOLDER_ALIASES
from models import PlannedMove


def build_plan(
    selected_folder: Path,
    extension_map: dict[str, str],
    ignored_extensions: set[str],
    ignored_names: set[str],
    skip_hidden: bool,
    custom_destinations: dict[str, Path] | None = None,
) -> list[PlannedMove]:
    category_folders = category_folder_map(selected_folder)
    plan: list[PlannedMove] = []

    for item in selected_folder.iterdir():
        if not item.is_file():
            continue
        if item.name.lower() in ignored_names:
            continue
        if skip_hidden and is_hidden(item):
            continue
        if item.suffix.lower() in ignored_extensions:
            continue

        category = extension_map.get(item.suffix.lower(), "Other")

        if custom_destinations and category in custom_destinations:
            destination_folder = custom_destinations[category]
        else:
            destination_folder = category_folders[category]

        destination = unique_destination(destination_folder / item.name, item)
        if destination.resolve() == item.resolve():
            continue

        plan.append(PlannedMove(source=item, destination=destination, category=destination_folder.name))

    return plan


def build_extension_map(category_extensions: dict[str, str]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for category, extensions_text in category_extensions.items():
        for extension in parse_extensions(extensions_text):
            mapping[extension] = category
    return mapping


def category_folder_map(selected_folder: Path) -> dict[str, Path]:
    existing_folders = {
        normalize_folder_name(path.name): path
        for path in selected_folder.iterdir()
        if path.is_dir()
    }

    category_folders: dict[str, Path] = {}
    for category, aliases in CATEGORY_FOLDER_ALIASES.items():
        found = False
        for alias in aliases:
            folder = existing_folders.get(normalize_folder_name(alias))
            if folder is not None:
                category_folders[category] = folder
                found = True
                break
        if not found:
            category_folders[category] = selected_folder / category
    return category_folders


def normalize_folder_name(name: str) -> str:
    without_accents = "".join(
        character
        for character in unicodedata.normalize("NFKD", name)
        if not unicodedata.combining(character)
    )
    normalized = []
    for character in without_accents.lower():
        normalized.append(character if character.isalnum() else " ")
    return " ".join("".join(normalized).split())


def parse_extensions(raw_text: str) -> set[str]:
    extensions = set()
    for part in raw_text.split(","):
        value = part.strip().lower()
        if not value:
            continue
        if not value.startswith("."):
            value = f".{value}"
        extensions.add(value)
    return extensions


def is_hidden(path: Path) -> bool:
    if path.name.startswith("."):
        return True
    try:
        return bool(os.stat(path).st_file_attributes & 2)
    except (AttributeError, OSError):
        return False


def unique_destination(destination: Path, source: Path) -> Path:
    if not destination.exists() or destination.resolve() == source.resolve():
        return destination

    index = 1
    stem = destination.stem
    suffix = destination.suffix
    parent = destination.parent
    while True:
        candidate = parent / f"{stem}_{index}{suffix}"
        if not candidate.exists():
            return candidate
        index += 1


def summarize_plan(plan: list[PlannedMove]) -> str:
    summary = Counter(move.category for move in plan)
    return "\n".join(f"- {category}: {count}" for category, count in sorted(summary.items()))
