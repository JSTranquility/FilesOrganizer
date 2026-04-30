import os
import shutil
import threading
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk


APP_VERSION = "1.1.0"

DEFAULT_CATEGORIES = {
    "Images": ".png, .jpg, .jpeg, .gif, .webp, .bmp, .svg",
    "Documents": ".txt, .pdf, .doc, .docx, .xls, .xlsx, .ppt, .pptx",
    "Audio": ".mp3, .wav, .ogg, .flac, .m4a",
    "Video": ".mp4, .mov, .avi, .mkv, .webm",
    "Archives": ".zip, .rar, .7z, .tar, .gz",
    "Executables": ".exe, .msi, .bat, .cmd",
}


@dataclass
class PlannedMove:
    source: Path
    destination: Path
    category: str


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class FileOrganizerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(f"File Organizer {APP_VERSION}")
        self.geometry("920x720")
        self.minsize(820, 640)

        try:
            self.iconbitmap("icon.ico")
        except Exception:
            pass

        self.selected_folder: Path | None = None
        self.preview_plan: list[PlannedMove] = []
        self.last_moves: list[tuple[Path, Path]] = []
        self.category_entries: dict[str, ctk.CTkEntry] = {}

        self._build_ui()
        self._set_status("Select a folder to begin.")

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        root = ctk.CTkFrame(self, corner_radius=22)
        root.grid(row=0, column=0, sticky="nsew", padx=18, pady=18)
        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=1)
        root.grid_rowconfigure(4, weight=1)

        header = ctk.CTkFrame(root, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=18, pady=(16, 8))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="File Organizer",
            font=ctk.CTkFont(family="Segoe UI", size=34, weight="bold"),
            text_color="#43E8D8",
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header,
            text=f"v{APP_VERSION} - preview, undo, exclusions and editable categories",
            font=ctk.CTkFont(size=13),
            text_color="#B7C4C9",
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

        folder_card = ctk.CTkFrame(root, corner_radius=16, fg_color="#11181C")
        folder_card.grid(row=1, column=0, columnspan=2, sticky="ew", padx=18, pady=10)
        folder_card.grid_columnconfigure(0, weight=1)

        self.folder_label = ctk.CTkLabel(
            folder_card,
            text="No folder selected",
            font=ctk.CTkFont(size=13),
            text_color="#DCE9ED",
            anchor="w",
        )
        self.folder_label.grid(row=0, column=0, sticky="ew", padx=14, pady=12)

        controls = ctk.CTkFrame(root, fg_color="transparent")
        controls.grid(row=2, column=0, columnspan=2, sticky="ew", padx=18, pady=(2, 12))
        controls.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.preview_button = self._button(controls, "Select Folder", self.select_folder, "#43E8D8")
        self.preview_button.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.scan_button = self._button(controls, "Preview", self.preview_files, "#F7C948")
        self.scan_button.grid(row=0, column=1, sticky="ew", padx=8)

        self.organize_button = self._button(controls, "Organize", self.start_organizing, "#52D273")
        self.organize_button.grid(row=0, column=2, sticky="ew", padx=8)

        self.undo_button = self._button(controls, "Undo Last Move", self.undo_last_move, "#FF8A65")
        self.undo_button.grid(row=0, column=3, sticky="ew", padx=(8, 0))

        options = ctk.CTkFrame(root, corner_radius=16, fg_color="#11181C")
        options.grid(row=3, column=0, sticky="nsew", padx=(18, 9), pady=(0, 12))
        options.grid_columnconfigure(0, weight=1)
        options.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            options,
            text="Editable categories",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#43E8D8",
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(14, 8))

        for index, (category, extensions) in enumerate(DEFAULT_CATEGORIES.items()):
            column = index % 2
            row = (index // 2) * 2 + 1
            ctk.CTkLabel(options, text=category, text_color="#DCE9ED").grid(
                row=row, column=column, sticky="w", padx=14, pady=(6, 0)
            )
            entry = ctk.CTkEntry(options)
            entry.insert(0, extensions)
            entry.grid(row=row + 1, column=column, sticky="ew", padx=14, pady=(2, 4))
            self.category_entries[category] = entry

        exclusions = ctk.CTkFrame(root, corner_radius=16, fg_color="#11181C")
        exclusions.grid(row=3, column=1, sticky="nsew", padx=(9, 18), pady=(0, 12))
        exclusions.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            exclusions,
            text="Exclusions and safety",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#43E8D8",
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(14, 8))

        ctk.CTkLabel(
            exclusions,
            text="Ignore extensions (comma-separated)",
            text_color="#DCE9ED",
        ).grid(row=1, column=0, sticky="w", padx=14, pady=(6, 0))
        self.ignore_extensions_entry = ctk.CTkEntry(exclusions)
        self.ignore_extensions_entry.insert(0, ".tmp, .log")
        self.ignore_extensions_entry.grid(row=2, column=0, sticky="ew", padx=14, pady=(2, 10))

        ctk.CTkLabel(
            exclusions,
            text="Ignore filenames (comma-separated)",
            text_color="#DCE9ED",
        ).grid(row=3, column=0, sticky="w", padx=14, pady=(6, 0))
        self.ignore_names_entry = ctk.CTkEntry(exclusions)
        self.ignore_names_entry.insert(0, "desktop.ini, thumbs.db")
        self.ignore_names_entry.grid(row=4, column=0, sticky="ew", padx=14, pady=(2, 10))

        self.skip_hidden_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            exclusions,
            text="Skip hidden files",
            variable=self.skip_hidden_var,
            text_color="#DCE9ED",
        ).grid(row=5, column=0, sticky="w", padx=14, pady=8)

        self.status_label = ctk.CTkLabel(
            exclusions,
            text="",
            text_color="#B7C4C9",
            wraplength=360,
            justify="left",
        )
        self.status_label.grid(row=6, column=0, sticky="ew", padx=14, pady=(18, 14))

        output = ctk.CTkFrame(root, corner_radius=16, fg_color="#0B1114")
        output.grid(row=4, column=0, columnspan=2, sticky="nsew", padx=18, pady=(0, 18))
        output.grid_columnconfigure(0, weight=1)
        output.grid_rowconfigure(1, weight=1)
        output.configure(height=260)
        output.grid_propagate(False)

        ctk.CTkLabel(
            output,
            text="Preview and activity log",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#43E8D8",
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(12, 6))

        self.log_box = ctk.CTkTextbox(output, height=220, corner_radius=12, fg_color="#071013")
        self.log_box.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 14))
        self.log_box.insert("end", "Choose a folder, then click Preview.\n")
        self.log_box.configure(state="disabled")

    def _button(self, parent, text, command, color):
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            height=46,
            corner_radius=12,
            fg_color=color,
            hover_color=self._darken(color),
            text_color="#071013",
            font=ctk.CTkFont(size=13, weight="bold"),
        )

    @staticmethod
    def _darken(hex_color: str):
        value = hex_color.lstrip("#")
        red, green, blue = (int(value[i : i + 2], 16) for i in (0, 2, 4))
        return f"#{int(red * 0.78):02x}{int(green * 0.78):02x}{int(blue * 0.78):02x}"

    def select_folder(self):
        selected = filedialog.askdirectory(title="Select a folder to organize")
        if not selected:
            return

        self.selected_folder = Path(selected)
        self.preview_plan = []
        self.folder_label.configure(text=str(self.selected_folder))
        self._write_log("Folder selected. Click Preview to inspect planned moves.")
        self._set_status("Folder ready.")

    def preview_files(self):
        if not self._ensure_folder():
            return

        try:
            self.preview_plan = self._build_plan()
        except OSError as exc:
            messagebox.showerror("Preview failed", str(exc))
            return

        if not self.preview_plan:
            self._write_log("No movable files found with the current settings.")
            self._set_status("Nothing to organize.")
            return

        summary = self._summarize_plan(self.preview_plan)
        lines = ["Preview:", "", summary, "", "Planned moves:"]
        for move in self.preview_plan[:250]:
            lines.append(f"- {move.source.name} -> {move.category}\\{move.destination.name}")
        if len(self.preview_plan) > 250:
            lines.append(f"...and {len(self.preview_plan) - 250} more files.")

        self._write_log("\n".join(lines))
        self._set_status(f"{len(self.preview_plan)} files ready to organize.")

    def start_organizing(self):
        if not self._ensure_folder():
            return

        if not self.preview_plan:
            self.preview_files()

        if not self.preview_plan:
            return

        answer = messagebox.askyesno(
            "Confirm organization",
            f"Move {len(self.preview_plan)} files according to the preview?",
        )
        if not answer:
            return

        self._toggle_actions(False)
        self._set_status("Organizing files...")
        thread = threading.Thread(target=self._organize_files, args=(list(self.preview_plan),), daemon=True)
        thread.start()

    def undo_last_move(self):
        if not self.last_moves:
            messagebox.showinfo("Nothing to undo", "There is no previous organization to undo.")
            return

        answer = messagebox.askyesno(
            "Undo last move",
            f"Move {len(self.last_moves)} files back to their original locations?",
        )
        if not answer:
            return

        self._toggle_actions(False)
        self._set_status("Undoing last organization...")
        thread = threading.Thread(target=self._undo_moves, daemon=True)
        thread.start()

    def _build_plan(self) -> list[PlannedMove]:
        assert self.selected_folder is not None

        extension_map = self._extension_map()
        ignored_extensions = self._parse_extensions(self.ignore_extensions_entry.get())
        ignored_names = {name.strip().lower() for name in self.ignore_names_entry.get().split(",") if name.strip()}

        plan: list[PlannedMove] = []
        for item in self.selected_folder.iterdir():
            if not item.is_file():
                continue
            if item.name.lower() in ignored_names:
                continue
            if self.skip_hidden_var.get() and self._is_hidden(item):
                continue
            if item.suffix.lower() in ignored_extensions:
                continue
            category = extension_map.get(item.suffix.lower(), "Other")
            destination_folder = self.selected_folder / category
            destination = self._unique_destination(destination_folder / item.name, item)
            if destination.resolve() == item.resolve():
                continue
            plan.append(PlannedMove(source=item, destination=destination, category=category))

        return plan

    def _organize_files(self, plan: list[PlannedMove]):
        completed: list[tuple[Path, Path]] = []
        errors: list[str] = []

        for move in plan:
            try:
                move.destination.parent.mkdir(exist_ok=True)
                shutil.move(str(move.source), str(move.destination))
                completed.append((move.source, move.destination))
            except OSError as exc:
                errors.append(f"{move.source.name}: {exc}")

        self.after(0, self._finish_organizing, completed, errors)

    def _finish_organizing(self, completed: list[tuple[Path, Path]], errors: list[str]):
        self.last_moves = completed
        self.preview_plan = []
        self._toggle_actions(True)

        moved_summary = Counter(destination.parent.name for _, destination in completed)
        lines = [
            "Organization complete.",
            "",
            f"Moved files: {len(completed)}",
        ]
        for category, count in sorted(moved_summary.items()):
            lines.append(f"- {category}: {count}")
        if errors:
            lines.extend(["", "Errors:"])
            lines.extend(f"- {error}" for error in errors)

        self._write_log("\n".join(lines))
        self._set_status("Organization complete. Undo is available.")
        messagebox.showinfo("Organization complete", f"Moved {len(completed)} files.")

    def _undo_moves(self):
        undone = 0
        errors: list[str] = []

        for original, current in reversed(self.last_moves):
            try:
                if not current.exists():
                    errors.append(f"Missing moved file: {current.name}")
                    continue
                restore_path = self._unique_destination(original, current)
                restore_path.parent.mkdir(exist_ok=True)
                shutil.move(str(current), str(restore_path))
                undone += 1
            except OSError as exc:
                errors.append(f"{current.name}: {exc}")

        self.after(0, self._finish_undo, undone, errors)

    def _finish_undo(self, undone: int, errors: list[str]):
        if not errors:
            self.last_moves = []
        self._toggle_actions(True)

        lines = ["Undo complete.", "", f"Restored files: {undone}"]
        if errors:
            lines.extend(["", "Errors:"])
            lines.extend(f"- {error}" for error in errors)

        self._write_log("\n".join(lines))
        self._set_status("Undo complete." if not errors else "Undo finished with errors.")
        messagebox.showinfo("Undo complete", f"Restored {undone} files.")

    def _extension_map(self) -> dict[str, str]:
        mapping: dict[str, str] = {}
        for category, entry in self.category_entries.items():
            for extension in self._parse_extensions(entry.get()):
                mapping[extension] = category
        return mapping

    @staticmethod
    def _parse_extensions(raw_text: str) -> set[str]:
        extensions = set()
        for part in raw_text.split(","):
            value = part.strip().lower()
            if not value:
                continue
            if not value.startswith("."):
                value = f".{value}"
            extensions.add(value)
        return extensions

    @staticmethod
    def _is_hidden(path: Path) -> bool:
        if path.name.startswith("."):
            return True
        try:
            return bool(os.stat(path).st_file_attributes & 2)
        except (AttributeError, OSError):
            return False

    @staticmethod
    def _unique_destination(destination: Path, source: Path) -> Path:
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

    @staticmethod
    def _summarize_plan(plan: list[PlannedMove]) -> str:
        summary = Counter(move.category for move in plan)
        return "\n".join(f"- {category}: {count}" for category, count in sorted(summary.items()))

    def _ensure_folder(self) -> bool:
        if self.selected_folder and self.selected_folder.exists():
            return True
        messagebox.showerror("No folder selected", "Please select a folder first.")
        return False

    def _write_log(self, text: str):
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.insert("end", text)
        self.log_box.configure(state="disabled")

    def _set_status(self, text: str):
        self.status_label.configure(text=text)

    def _toggle_actions(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        for button in (self.preview_button, self.scan_button, self.organize_button, self.undo_button):
            button.configure(state=state)


if __name__ == "__main__":
    app = FileOrganizerApp()
    app.mainloop()
