import tkinter as tk
from tkinter import filedialog
import threading
import asyncio
import sys
import os
import urllib.request
import io
from audioProces.shazamioFinder import shazamio_finder

try:
    from PIL import Image, ImageTk
    PIL_OK = True
except ImportError:
    PIL_OK = False

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'audioProces'))

from audioProces.musicFinder import music_finder

BG        = "#0D0D0D"
BG2       = "#161616"
BG3       = "#1E1E1E"
ACCENT    = "#E8FF47"
ACCENT_DIM= "#9AAA1A"
TEXT      = "#F0EDE6"
TEXT_MUT  = "#666560"
BORDER    = "#2A2A28"
SUCCESS   = "#3BBA6E"
ERROR     = "#E24B4A"
FONT_HEAD = ("JetBrains Mono", 13, "bold")
FONT_BODY = ("JetBrains Mono", 11)
FONT_SMALL= ("JetBrains Mono", 9)
FONT_BIG  = ("JetBrains Mono", 20, "bold")

WIN_W, WIN_H = 360, 560


class BanduraWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("BANDURA")
        self.geometry(f"{WIN_W}x{WIN_H}")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.overrideredirect(True)
        self._center()
        self._state = "idle"
        self._album_photo = None
        self._build()

    def _center(self):
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = sw - WIN_W - 20
        y = sh - WIN_H - 60
        self.geometry(f"+{x}+{y}")

    def _build(self):
        self._drag_x = self._drag_y = 0
        self.bind("<ButtonPress-1>", self._drag_start)
        self.bind("<B1-Motion>",     self._drag_move)

        outer = tk.Frame(self, bg=BORDER, padx=1, pady=1)
        outer.pack(fill="both", expand=True)

        self._inner = tk.Frame(outer, bg=BG)
        self._inner.pack(fill="both", expand=True)

        # ── Заголовок ──
        header = tk.Frame(self._inner, bg=BG2, pady=12)
        header.pack(fill="x")

        tk.Label(header, text="◈  BANDURA", font=FONT_HEAD,
                 fg=ACCENT, bg=BG2).pack(side="left", padx=16)

        # Кнопка закриття (✕) — пакується першою праворуч, тому стає крайньою
        btn_close = tk.Label(header, text="✕", font=FONT_BODY,
                             fg=TEXT_MUT, bg=BG2, cursor="hand2")
        btn_close.pack(side="right", padx=(6, 16))
        btn_close.bind("<Button-1>", lambda e: self.withdraw())
        btn_close.bind("<Enter>", lambda e: btn_close.configure(fg=ERROR))
        btn_close.bind("<Leave>", lambda e: btn_close.configure(fg=TEXT_MUT))

        # Кнопка згортання (─) — пакується другою праворуч, стає поруч із хрестиком
        btn_min = tk.Label(header, text="─", font=FONT_BODY,
                           fg=TEXT_MUT, bg=BG2, cursor="hand2")
        btn_min.pack(side="right", padx=(6, 6))
        btn_min.bind("<Button-1>", lambda e: self._minimize())
        btn_min.bind("<Enter>", lambda e: btn_min.configure(fg=TEXT))
        btn_min.bind("<Leave>", lambda e: btn_min.configure(fg=TEXT_MUT))

        sep(self._inner, BG3)

        # ── Джерело ──
        src_frame = tk.Frame(self._inner, bg=BG, pady=12, padx=16)
        src_frame.pack(fill="x")
        tk.Label(src_frame, text="SOURCE", font=FONT_SMALL,
                 fg=TEXT_MUT, bg=BG).pack(anchor="w")
        self._src_var = tk.StringVar(value="HyperX")
        tk.Entry(src_frame, textvariable=self._src_var,
                 font=FONT_BODY, bg=BG3, fg=TEXT,
                 insertbackground=ACCENT, relief="flat", bd=0,
                 highlightthickness=1, highlightbackground=BORDER,
                 highlightcolor=ACCENT).pack(
                     fill="x", pady=(4, 0), ipady=6, ipadx=8)

        sep(self._inner, BG3)

        # ── Режим ──
        mode_frame = tk.Frame(self._inner, bg=BG, pady=12, padx=16)
        mode_frame.pack(fill="x")
        tk.Label(mode_frame, text="MODE", font=FONT_SMALL,
                 fg=TEXT_MUT, bg=BG).pack(anchor="w")

        self._mode_var = tk.StringVar(value="chunk")
        btn_row = tk.Frame(mode_frame, bg=BG)
        btn_row.pack(fill="x", pady=(6, 0))
        for label, val in [("CHUNK", "chunk"), ("FULL", "full")]:
            self._mode_btn(btn_row, label, val)

        params_row = tk.Frame(mode_frame, bg=BG)
        params_row.pack(fill="x", pady=(10, 0))
        self._dur_var  = tk.IntVar(value=10)
        self._iter_var = tk.IntVar(value=5)
        self._spin_field(params_row, "DURATION (s)", self._dur_var,  3, 60)
        self._spin_field(params_row, "ITERATIONS",   self._iter_var, 1, 20)

        sep(self._inner, BG3)

        # ── Результат ──
        self._result_frame = tk.Frame(self._inner, bg=BG)
        self._result_frame.pack(fill="both", expand=True)
        self._draw_idle()

        sep(self._inner, BG3)

        # ── Кнопки ──
        btn_area = tk.Frame(self._inner, bg=BG2, pady=14, padx=16)
        btn_area.pack(fill="x")
        self._btn_listen = self._action_btn(
            btn_area, "⏺  LISTEN", ACCENT, BG, self._on_listen)
        self._btn_listen.pack(fill="x", pady=(0, 8))
        self._btn_file = self._action_btn(
            btn_area, "📂  LOAD FILE", BG3, TEXT, self._on_file)
        self._btn_file.pack(fill="x")

    # ── Допоміжні компоненти ───────────────────────────────────
    def _mode_btn(self, parent, label, val):
        btn = tk.Label(parent, text=label, font=FONT_SMALL,
                       bg=BG3, fg=TEXT_MUT, cursor="hand2",
                       padx=14, pady=5)
        btn.pack(side="left", padx=(0, 6))

        def update(*_):
            active = self._mode_var.get() == val
            btn.configure(bg=ACCENT if active else BG3,
                          fg=BG    if active else TEXT_MUT)

        btn.bind("<Button-1>", lambda e: (self._mode_var.set(val), update()))
        self._mode_var.trace_add("write", update)
        update()

    def _spin_field(self, parent, label, var, mn, mx):
        f = tk.Frame(parent, bg=BG)
        f.pack(side="left", expand=True, fill="x", padx=(0, 12))
        tk.Label(f, text=label, font=FONT_SMALL,
                 fg=TEXT_MUT, bg=BG).pack(anchor="w")
        tk.Spinbox(f, from_=mn, to=mx, textvariable=var,
                   font=FONT_BODY, bg=BG3, fg=TEXT,
                   buttonbackground=BG3, relief="flat", bd=0,
                   highlightthickness=1, highlightbackground=BORDER,
                   highlightcolor=ACCENT, width=5).pack(
                       anchor="w", ipady=4, pady=(2, 0))

    def _action_btn(self, parent, text, bg, fg, cmd):
        btn = tk.Label(parent, text=text, font=FONT_BODY,
                       bg=bg, fg=fg, cursor="hand2", pady=10)
        btn.bind("<Button-1>", lambda e: cmd())
        btn.bind("<Enter>",    lambda e: btn.configure(
            bg=ACCENT_DIM if bg == ACCENT else BORDER))
        btn.bind("<Leave>",    lambda e: btn.configure(bg=bg))
        return btn

    # ── Згортання у панель завдань ─────────────────────────────
    def _minimize(self):
        self.update_idletasks()
        self.overrideredirect(False)
        self.iconify()
        self.bind("<Map>", self._on_restore)

    def _on_restore(self, event):
        self.unbind("<Map>")
        self.overrideredirect(True)

    # ── Стани ─────────────────────────────────────────────────
    def _clear_result(self):
        for w in self._result_frame.winfo_children():
            w.destroy()
        self._album_photo = None

    def _draw_idle(self):
        self._clear_result()
        tk.Label(self._result_frame, text="—", font=FONT_BIG,
                 fg=BORDER, bg=BG).pack(expand=True)
        tk.Label(self._result_frame,
                 text="press listen or load a file",
                 font=FONT_SMALL, fg=TEXT_MUT, bg=BG).pack(pady=(0, 8))

    def _draw_recording(self):
        self._clear_result()
        self._pulse_label = tk.Label(
            self._result_frame, text="◉  LISTENING",
            font=FONT_HEAD, fg=ACCENT, bg=BG)
        self._pulse_label.pack(expand=True)
        tk.Label(self._result_frame, text="analyzing audio stream…",
                 font=FONT_SMALL, fg=TEXT_MUT, bg=BG).pack(pady=(0, 8))
        self._animate_pulse()

    def _animate_pulse(self, on=True):
        if self._state != "recording":
            return
        if hasattr(self, "_pulse_label"):
            self._pulse_label.configure(fg=ACCENT if on else ACCENT_DIM)
        self.after(500, self._animate_pulse, not on)

    def _draw_found(self, title, artist, cover_url=None):
        self._clear_result()

        # Контейнер обкладинки
        cover_frame = tk.Frame(self._result_frame, bg=BG,
                               width=120, height=120)
        cover_frame.pack(pady=(14, 0))
        cover_frame.pack_propagate(False)

        # Плейсхолдер (замінюється після завантаження)
        self._cover_placeholder = tk.Label(
            cover_frame, text="♪",
            font=("JetBrains Mono", 36), fg=BORDER, bg=BG3)
        self._cover_placeholder.place(relx=.5, rely=.5, anchor="center")

        if cover_url and PIL_OK:
            threading.Thread(
                target=self._load_cover,
                args=(cover_url, cover_frame),
                daemon=True
            ).start()

        tk.Label(self._result_frame, text="✓  FOUND",
                 font=FONT_SMALL, fg=SUCCESS, bg=BG).pack(pady=(10, 2))
        tk.Label(self._result_frame, text=title,
                 font=FONT_BIG, fg=TEXT, bg=BG,
                 wraplength=WIN_W - 32).pack()
        tk.Label(self._result_frame, text=artist,
                 font=FONT_BODY, fg=ACCENT, bg=BG).pack(pady=(2, 0))

        copy_btn = tk.Label(self._result_frame, text="[ copy ]",
                            font=FONT_SMALL, fg=TEXT_MUT,
                            bg=BG, cursor="hand2")
        copy_btn.pack(pady=(8, 8))
        copy_btn.bind("<Button-1>",
                      lambda e: self._copy(f"{artist} — {title}"))

    def _load_cover(self, url, frame):
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = resp.read()
            img = Image.open(io.BytesIO(data)).convert("RGB")
            img = img.resize((120, 120), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.after(0, self._show_cover, photo, frame)
        except Exception:
            pass

    def _show_cover(self, photo, frame):
        self._album_photo = photo   # зберігаємо від GC
        for w in frame.winfo_children():
            w.destroy()
        tk.Label(frame, image=photo, bg=BG).place(
            relx=0, rely=0, relwidth=1, relheight=1)

    def _draw_error(self, msg="track not found"):
        self._clear_result()
        tk.Label(self._result_frame, text="✕  NOT FOUND",
                 font=FONT_SMALL, fg=ERROR, bg=BG).pack(expand=True)
        tk.Label(self._result_frame, text=msg,
                 font=FONT_SMALL, fg=TEXT_MUT, bg=BG).pack(pady=(0, 8))

    # ── Дії ────────────────────────────────────────────────────
    def _on_listen(self):
        if self._state == "recording":
            return
        self._state = "recording"
        self._draw_recording()

        speaker  = self._src_var.get()
        duration = self._dur_var.get()
        mode     = self._mode_var.get()
        iters    = self._iter_var.get()

        def run():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(
                    music_finder(speaker, duration, mode, iters))
                if result:
                    parts = list(result)
                    title  = parts[0] if len(parts) > 0 else "?"
                    artist = parts[1] if len(parts) > 1 else "?"
                    self.after(0, self._on_result, title, artist, None)
                else:
                    self.after(0, self._on_not_found)
            except Exception as e:
                self.after(0, self._on_error, str(e))
            finally:
                loop.close()

        threading.Thread(target=run, daemon=True).start()

    def _on_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")])
        if not path:
            return
        self._state = "recording"
        self._draw_recording()

        def run():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:

                result = loop.run_until_complete(shazamio_finder(path))
                track = result.get("track", {}) if result else {}
                if track:
                    title     = track.get("title", "?")
                    artist    = track.get("subtitle", "?")
                    cover_url = _extract_cover(track)
                    self.after(0, self._on_result, title, artist, cover_url)
                else:
                    self.after(0, self._on_not_found)
            except Exception as e:
                self.after(0, self._on_error, str(e))
            finally:
                loop.close()

        threading.Thread(target=run, daemon=True).start()

    def _on_result(self, title, artist, cover_url):
        self._state = "found"
        self._draw_found(title, artist, cover_url)

    def _on_not_found(self):
        self._state = "error"
        self._draw_error("track not found in database")

    def _on_error(self, msg):
        self._state = "error"
        self._draw_error(msg[:60])

    def _copy(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)

    # ── Drag ───────────────────────────────────────────────────
    def _drag_start(self, e):
        self._drag_x = e.x
        self._drag_y = e.y

    def _drag_move(self, e):
        x = self.winfo_x() + (e.x - self._drag_x)
        y = self.winfo_y() + (e.y - self._drag_y)
        self.geometry(f"+{x}+{y}")


# ── Утиліти ────────────────────────────────────────────────────
def sep(parent, color):
    tk.Frame(parent, bg=color, height=1).pack(fill="x")


def _extract_cover(track: dict) -> str | None:
    """Витягує URL обкладинки з відповіді Shazam у порядку пріоритету."""
    images = track.get("images", {})
    for key in ("coverarthq", "coverart", "background"):
        url = images.get(key)
        if url:
            return url
    share = track.get("share", {})
    if share.get("image"):
        return share["image"]
    return None


# ── Тест без трею ─────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    win = BanduraWindow(root)
    root.mainloop()