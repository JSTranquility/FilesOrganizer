import shutil
import threading
from collections import Counter
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk
from PIL import Image

from config import APP_VERSION, DEFAULT_CATEGORIES, APP_ICO, LOGO_PATH

try:
    import ctypes
    _user32 = ctypes.windll.user32
    _has_ctypes = True
except Exception:
    _has_ctypes = False
from file_utils import (
    build_extension_map,
    build_plan,
    parse_extensions,
    summarize_plan,
    unique_destination,
)
from models import PlannedMove


class Clr:
    bg = "#0a0f1a"
    surface = "#121b2e"
    surface2 = "#1a2740"
    input_bg = "#0c1425"
    blue = "#3b82f6"
    cyan = "#06b6d4"
    green = "#22c55e"
    purple = "#8b5cf6"
    orange = "#f59e0b"
    rose = "#ef4444"
    text = "#e2e8f0"
    text2 = "#94a3b8"
    text3 = "#556580"
    border = "#1e293b"


F = "Segoe UI"
FM = "Consolas"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def _dim(c: str, f: float = 0.7) -> str:
    v = c.lstrip("#")
    r, g, b = (int(v[i:i+2], 16) for i in (0, 2, 4))
    return f"#{int(r*f):02x}{int(g*f):02x}{int(b*f):02x}"


class FileOrganizerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"File Organizer {APP_VERSION}")
        self.geometry("1060x720")
        self.minsize(900, 640)

        self._logo_img = None
        try:
            if LOGO_PATH and LOGO_PATH.exists():
                img = Image.open(LOGO_PATH)
                self._logo_img = ctk.CTkImage(img.copy(), size=(18, 18))
            if APP_ICO and APP_ICO.exists() and _has_ctypes:
                ico = str(APP_ICO.resolve())
                self.iconbitmap(default=ico)
                hwnd = _user32.GetParent(self.winfo_id())
                hicon = _user32.LoadImageW(
                    0, ico, 1, 0, 0, 0x00000010 | 0x00008000
                )
                if hicon:
                    _user32.SendMessageW(hwnd, 0x0080, 0, hicon)
                    _user32.SendMessageW(hwnd, 0x0080, 1, hicon)
        except Exception:
            pass

        self.sel: Path | None = None
        self.plan: list[PlannedMove] = []
        self.last: list[tuple[Path, Path]] = []
        self.ext_entries: dict[str, ctk.CTkEntry] = {}
        self.dst_entries: dict[str, ctk.CTkEntry] = {}
        self.dst_paths: dict[str, Path | None] = {c: None for c in DEFAULT_CATEGORIES}

        self._ui()
        self._st("Ready")
        self._fps_loop()


    # ── UI ──────────────────────────────────────────────────────────────────

    def _ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        w = ctk.CTkFrame(self, fg_color=Clr.bg, corner_radius=0)
        w.grid(row=0, column=0, sticky="nsew")
        w.grid_columnconfigure(0, weight=1)
        w.grid_rowconfigure(4, weight=1)

        self._top(w, row=0)          # source bar
        self._cats(w, row=2)         # category list
        self._opts(w, row=3)         # settings strip
        self._log(w, row=4)          # activity log  (expandable)
        self._bar(w, row=5)          # action bar
        self._bot(w, row=6)          # status bar

    # ── Top bar: source folder ──────────────────────────────────────────────

    def _top(self, parent, row):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.grid(row=row, column=0, sticky="ew", padx=30, pady=(14, 6))
        f.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(f, text="File Organizer", font=ctk.CTkFont(F, 20, "bold"),
                      text_color=Clr.text).grid(row=0, column=0, padx=(0, 20))

        ctk.CTkLabel(f, text="\U0001f4c1", font=ctk.CTkFont(size=14)).grid(row=0, column=1, padx=(0, 6))

        self.fol_lbl = ctk.CTkLabel(
            f, text="No folder selected", anchor="w",
            font=ctk.CTkFont(F, 12), text_color=Clr.text2,
        )
        self.fol_lbl.grid(row=0, column=2, sticky="ew")

        self.fol_btn = ctk.CTkButton(
            f, text="\U0001f4c2 Browse", command=self.pick,
            height=32, corner_radius=6,
            fg_color=Clr.blue, hover_color=_dim(Clr.blue),
            text_color=Clr.bg, font=ctk.CTkFont(F, 12, "bold"),
        )
        self.fol_btn.grid(row=0, column=3, padx=(12, 0))

    # ── Category list ───────────────────────────────────────────────────────

    def _cats(self, parent, row):
        f = ctk.CTkFrame(parent, fg_color=Clr.surface, corner_radius=10,
                          border_width=1, border_color=Clr.border)
        f.grid(row=row, column=0, sticky="nsew", padx=30, pady=(10, 10))
        f.grid_columnconfigure(0, weight=1)
        f.grid_rowconfigure(1, weight=1)

        hdr = ctk.CTkFrame(f, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", padx=16, pady=(10, 2))
        hdr.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(hdr, text="Categories", font=ctk.CTkFont(F, 14, "bold"),
                      text_color=Clr.blue).grid(row=0, column=0, sticky="w")

        scroll = ctk.CTkScrollableFrame(
            f, fg_color="transparent", corner_radius=0,
            scrollbar_button_color=Clr.surface2,
            scrollbar_button_hover_color=Clr.text3,
        )
        scroll.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0, 2))
        scroll.grid_columnconfigure(0, weight=1)

        icons = ["\U0001f5bc", "\U0001f4c4", "\U0001f3b5", "\U0001f3ac", "\U0001f4e6", "\u2699", "\U0001f4c2"]
        for i, (cat, exts) in enumerate(DEFAULT_CATEGORIES.items()):
            self._cat_row(scroll, i, icons[i], cat, exts)

        hint = ctk.CTkFrame(f, fg_color="transparent")
        hint.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 8))
        hint.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            hint,
            text="\u2139 Each category sends files to a folder. Click \u2026 to pick a custom folder, \u2716 to reset to default.",
            font=ctk.CTkFont(F, 10), text_color=Clr.text3, justify="left", wraplength=600,
        ).grid(row=0, column=0, sticky="w")

    def _cat_row(self, parent, i, icon, cat, exts):
        # ┌──────────────────────────────────────────────────────────────────┐
        # │ 🖼  Images   [.png, .jpg, .jpeg...        ]  📁 Default    […] ✕│
        # └──────────────────────────────────────────────────────────────────┘

        row = ctk.CTkFrame(parent, fg_color=Clr.surface2, corner_radius=8)
        row.grid(row=i, column=0, sticky="ew", pady=5)
        row.grid_columnconfigure(2, weight=2)
        row.grid_columnconfigure(4, weight=1)

        ctk.CTkLabel(row, text=icon, font=ctk.CTkFont(size=15)).grid(
            row=0, column=0, padx=(10, 4))

        ctk.CTkLabel(row, text=cat, font=ctk.CTkFont(F, 12, "bold"),
                      text_color=Clr.text, width=80, anchor="w").grid(
            row=0, column=1, padx=(0, 6))

        ext = ctk.CTkEntry(
            row, fg_color=Clr.input_bg, border_color=Clr.border,
            border_width=1, corner_radius=6, height=30,
            text_color=Clr.text2, font=ctk.CTkFont(size=11),
        )
        ext.insert(0, exts)
        ext.grid(row=0, column=2, sticky="ew", padx=(0, 6))
        self.ext_entries[cat] = ext

        dst = ctk.CTkEntry(
            row, fg_color=Clr.input_bg, border_color=Clr.border,
            border_width=1, corner_radius=6, height=30,
            text_color=Clr.text3, font=ctk.CTkFont(size=11),
        )
        dst.insert(0, "Default")
        dst.configure(state="readonly")
        dst.grid(row=0, column=3, columnspan=1, sticky="ew", padx=(0, 4))
        self.dst_entries[cat] = dst

        ctk.CTkButton(
            row, text="\u2026", width=30, height=28, corner_radius=5,
            fg_color=Clr.surface, hover_color=Clr.blue,
            text_color=Clr.text2, font=ctk.CTkFont(size=14, weight="bold"),
            command=lambda c=cat: self._pick(c),
        ).grid(row=0, column=5, padx=(0, 2))

        ctk.CTkButton(
            row, text="\u2716", width=26, height=28, corner_radius=5,
            fg_color=Clr.surface, hover_color=Clr.rose,
            text_color=Clr.text3, font=ctk.CTkFont(size=9),
            command=lambda c=cat: self._clr(c),
        ).grid(row=0, column=6, padx=(0, 8))

    # ── Settings strip ──────────────────────────────────────────────────────

    def _opts(self, parent, row):
        f = ctk.CTkFrame(parent, fg_color=Clr.surface2, corner_radius=8,
                          border_width=1, border_color=Clr.border)
        f.grid(row=row, column=0, sticky="ew", padx=30, pady=4)
        f.grid_columnconfigure((1, 3), weight=1)

        ctk.CTkLabel(f, text="\u2699", font=ctk.CTkFont(size=12)).grid(
            row=0, column=0, padx=(10, 4), pady=8)

        self.ig_ext = ctk.CTkEntry(
            f, fg_color=Clr.input_bg, border_color=Clr.border,
            border_width=1, corner_radius=5, height=28,
            text_color=Clr.text2, font=ctk.CTkFont(size=11),
        )
        self.ig_ext.insert(0, ".tmp, .log")
        self.ig_ext.grid(row=0, column=1, sticky="ew", padx=(0, 12))

        self.ig_nam = ctk.CTkEntry(
            f, fg_color=Clr.input_bg, border_color=Clr.border,
            border_width=1, corner_radius=5, height=28,
            text_color=Clr.text2, font=ctk.CTkFont(size=11),
        )
        self.ig_nam.insert(0, "desktop.ini, thumbs.db")
        self.ig_nam.grid(row=0, column=2, sticky="ew", padx=(0, 12))

        self.hid_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            f, text="Hidden", variable=self.hid_var,
            text_color=Clr.text2, font=ctk.CTkFont(F, 11),
            fg_color=Clr.blue, corner_radius=4, checkmark_color=Clr.bg,
        ).grid(row=0, column=3, padx=(0, 10))

    # ── Activity log ────────────────────────────────────────────────────────

    def _log(self, parent, row):
        f = ctk.CTkFrame(parent, fg_color=Clr.surface, corner_radius=8,
                          border_width=1, border_color=Clr.border)
        f.grid(row=row, column=0, sticky="nsew", padx=30, pady=(2, 4))
        f.grid_columnconfigure(0, weight=1)
        f.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            f, text="\U0001f4cb Log",
            font=ctk.CTkFont(F, 12, "bold"), text_color=Clr.cyan,
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(6, 2))

        self.log = ctk.CTkTextbox(
            f, corner_radius=6, height=80,
            fg_color=Clr.bg, border_color=Clr.border, border_width=1,
            text_color=Clr.text2, font=ctk.CTkFont(FM, 11),
        )
        self.log.grid(row=1, column=0, sticky="nsew", padx=12, pady=(2, 10))
        self.log.insert("end", "Select a folder and press Preview.\n")
        self.log.configure(state="disabled")

    # ── Action bar ──────────────────────────────────────────────────────────

    def _bar(self, parent, row):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.grid(row=row, column=0, sticky="ew", padx=30, pady=(4, 8))

        self._btns = []
        for txt, cmd, clr in [
            ("\U0001f50d  Preview", self.preview, Clr.cyan),
            ("\U0001f680  Organize", self.organize, Clr.green),
            ("\u21a9  Undo", self.undo, Clr.orange),
            ("\U0001f504  Refresh", self.preview, Clr.purple),
        ]:
            b = ctk.CTkButton(
                f, text=txt, command=cmd,
                height=38, corner_radius=8,
                fg_color=clr, hover_color=_dim(clr),
                text_color=Clr.bg, font=ctk.CTkFont(F, 12, "bold"),
            )
            b.pack(side="left", padx=4, fill="x", expand=True)
            self._btns.append(b)

        self.st_lbl = ctk.CTkLabel(
            f, text="", font=ctk.CTkFont(F, 11), text_color=Clr.text3,
        )
        self.st_lbl.pack(side="right", padx=(12, 0))

    # ── Status bar ──────────────────────────────────────────────────────────

    def _bot(self, parent, row):
        b = ctk.CTkFrame(parent, fg_color=Clr.surface2, height=28, corner_radius=0)
        b.grid(row=row, column=0, sticky="ew")
        b.grid_columnconfigure(1, weight=1)
        b.grid_propagate(False)

        if self._logo_img:
            ctk.CTkLabel(b, text="", image=self._logo_img,
            ).grid(row=0, column=0, padx=(12, 4))

        ctk.CTkLabel(b, text="File Organizer",
                      font=ctk.CTkFont(F, 10), text_color=Clr.text3,
        ).grid(row=0, column=1, sticky="w")

        ctk.CTkLabel(b, text="120 FPS",
                      font=ctk.CTkFont(FM, 9), text_color=Clr.text3,
        ).grid(row=0, column=2, padx=(0, 4))

        ctk.CTkLabel(b, text=f"v{APP_VERSION}",
                      font=ctk.CTkFont(F, 10), text_color=Clr.text3,
        ).grid(row=0, column=3, sticky="e", padx=(0, 16))

    # ── Destination helpers ─────────────────────────────────────────────────

    def _pick(self, cat):
        d = filedialog.askdirectory(title=f"Destination: {cat}")
        if not d:
            return
        p = Path(d)
        self.dst_paths[cat] = p
        e = self.dst_entries[cat]
        e.configure(state="normal")
        e.delete(0, "end")
        e.insert(0, str(p))
        e.configure(state="readonly")

    def _clr(self, cat):
        self.dst_paths[cat] = None
        e = self.dst_entries[cat]
        e.configure(state="normal")
        e.delete(0, "end")
        e.insert(0, "Default")
        e.configure(state="readonly")

    # ── Actions ─────────────────────────────────────────────────────────────

    def pick(self):
        d = filedialog.askdirectory(title="Select folder to organize")
        if not d:
            return
        self.sel = Path(d)
        self.plan = []
        self.fol_lbl.configure(text=str(self.sel))
        self._wr("Folder selected. Press Preview.")
        self._st("Ready")

    def preview(self):
        if not self._ok():
            return
        try:
            self.plan = self._plan()
        except OSError as e:
            messagebox.showerror("Error", str(e))
            return
        if not self.plan:
            self._wr("Nothing to move.")
            self._st("Empty")
            return
        s = summarize_plan(self.plan)
        lines = ["Preview:", "", s, "", "Moves:"]
        for m in self.plan[:250]:
            lines.append(f"  {m.source.name} \u2192 {m.category}/{m.destination.name}")
        if len(self.plan) > 250:
            lines.append(f"  ... +{len(self.plan)-250} more")
        self._wr("\n".join(lines))
        self._st(f"{len(self.plan)} files ready")

    def organize(self):
        if not self._ok():
            return
        if not self.plan:
            self.preview()
        if not self.plan:
            return
        if not messagebox.askyesno("Confirm", f"Move {len(self.plan)} files?"):
            return
        self._toggle(False)
        self._st("Organizing\u2026")
        threading.Thread(target=self._run, args=(list(self.plan),), daemon=True).start()

    def undo(self):
        if not self.last:
            messagebox.showinfo("Undo", "Nothing to undo.")
            return
        if not messagebox.askyesno("Undo", f"Restore {len(self.last)} files?"):
            return
        self._toggle(False)
        self._st("Undoing\u2026")
        threading.Thread(target=self._rev, daemon=True).start()

    def _plan(self) -> list[PlannedMove]:
        assert self.sel is not None
        m = {c: e.get() for c, e in self.ext_entries.items()}
        em = build_extension_map(m)
        ie = parse_extensions(self.ig_ext.get())
        inm = {s.strip().lower() for s in self.ig_nam.get().split(",") if s.strip()}
        cd = {c: p for c, p in self.dst_paths.items() if p is not None}
        return build_plan(self.sel, em, ie, inm, self.hid_var.get(), cd or None)

    def _run(self, plan):
        ok, err = [], []
        folders = {m.destination.parent for m in plan}
        for f in folders:
            try:
                f.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                err.append(f"Cannot create {f.name}: {e}")
        if err:
            self.after(0, self._done, ok, err)
            return
        for m in plan:
            try:
                shutil.move(str(m.source), str(m.destination))
                ok.append((m.source, m.destination))
            except OSError as e:
                err.append(f"{m.source.name}: {e}")
        self.after(0, self._done, ok, err)

    def _done(self, ok, err):
        self.last = ok
        self.plan = []
        self._toggle(True)
        c = Counter(d.parent.name for _, d in ok)
        lines = [f"Moved {len(ok)} files."]
        for cat, n in sorted(c.items()):
            lines.append(f"  {cat}: {n}")
        if err:
            lines += ["", "Errors:"] + [f"  {e}" for e in err]
        self._wr("\n".join(lines))
        self._st("Complete")
        messagebox.showinfo("Done", f"Moved {len(ok)} files.")

    def _rev(self):
        ok, err = 0, []
        for src, dst in reversed(self.last):
            try:
                if not dst.exists():
                    err.append(f"Missing: {dst.name}")
                    continue
                r = unique_destination(src, dst)
                r.parent.mkdir(exist_ok=True)
                shutil.move(str(dst), str(r))
                ok += 1
            except OSError as e:
                err.append(f"{dst.name}: {e}")
        self.after(0, self._undone, ok, err)

    def _undone(self, ok, err):
        if not err:
            self.last = []
        self._toggle(True)
        lines = [f"Restored {ok} files."]
        if err:
            lines += ["Errors:"] + [f"  {e}" for e in err]
        self._wr("\n".join(lines))
        self._st("Undone" if not err else "Errors")
        messagebox.showinfo("Undo", f"Restored {ok} files.")

    def _fps_loop(self):
        self.update_idletasks()
        self.after(8, self._fps_loop)

    def destroy(self):
        super().destroy()

    def _ok(self) -> bool:
        if self.sel and self.sel.exists():
            return True
        messagebox.showerror("Error", "Select a folder first.")
        return False

    def _wr(self, t):
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.insert("end", t)
        self.log.configure(state="disabled")

    def _st(self, t):
        self.st_lbl.configure(text=t)

    def _toggle(self, en):
        s = "normal" if en else "disabled"
        for b in self._btns:
            b.configure(state=s)
        self.fol_btn.configure(state=s)
