import tkinter as tk
from tkinter import filedialog
import threading
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'audioProces'))

from musicFinder import music_finder

# ── Кольори та шрифти ──────────────────────────────────────────
BG        = "#0D0D0D"
BG2       = "#161616"
BG3       = "#1E1E1E"
ACCENT    = "#E8FF47"      # жовто-зелений акцент
ACCENT_DIM= "#9AAA1A"
TEXT      = "#F0EDE6"
TEXT_MUT  = "#666560"
BORDER    = "#2A2A28"
SUCCESS   = "#3BBA6E"
ERROR     = "#E24B4A"
FONT_HEAD = ("JetBrains Mono", 13, "bold")
FONT_BODY = ("JetBrains Mono", 11)
FONT_SMALL= ("JetBrains Mono", 9)
FONT_BIG  = ("JetBrains Mono", 22, "bold")

WIN_W, WIN_H = 360, 480


class BanduraWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("BANDURA")
        self.geometry(f"{WIN_W}x{WIN_H}")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.overrideredirect(True)          # без системних рамок
        self._center()
        self._state = "idle"                 # idle | recording | found | error
        self._result_title = ""
        self._result_artist = ""
        self._build()

    def _center(self):
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = sw - WIN_W - 20
        y = sh - WIN_H - 60
        self.geometry(f"+{x}+{y}")

    # ── Побудова UI ────────────────────────────────────────────
    def _build(self):
        # Drag support
        self._drag_x = self._drag_y = 0
        self.bind("<ButtonPress-1>",   self._drag_start)
        self.bind("<B1-Motion>",       self._drag_move)

        # Зовнішня рамка
        outer = tk.Frame(self, bg=BORDER, padx=1, pady=1)
        outer.pack(fill="both", expand=True)

        inner = tk.Frame(outer, bg=BG)
        inner.pack(fill="both", expand=True)

        # ── Заголовок ──
        header = tk.Frame(inner, bg=BG2, pady=12)
        header.pack(fill="x")

        tk.Label(header, text="◈  BANDURA", font=FONT_HEAD,
                 fg=ACCENT, bg=BG2).pack(side="left", padx=16)

        btn_close = tk.Label(header, text="✕", font=FONT_BODY,
                             fg=TEXT_MUT, bg=BG2, cursor="hand2")
        btn_close.pack(side="right", padx=16)
        btn_close.bind("<Button-1>", lambda e: self.withdraw())

        sep(inner, BG3)

        # ── Джерело звуку ──
        src_frame = tk.Frame(inner, bg=BG, pady=12, padx=16)
        src_frame.pack(fill="x")

        tk.Label(src_frame, text="SOURCE", font=FONT_SMALL,
                 fg=TEXT_MUT, bg=BG).pack(anchor="w")

        row = tk.Frame(src_frame, bg=BG)
        row.pack(fill="x", pady=(4, 0))

        self._src_var = tk.StringVar(value="HyperX")
        entry = tk.Entry(row, textvariable=self._src_var,
                         font=FONT_BODY, bg=BG3, fg=TEXT,
                         insertbackground=ACCENT, relief="flat",
                         bd=0, highlightthickness=1,
                         highlightbackground=BORDER,
                         highlightcolor=ACCENT)
        entry.pack(side="left", fill="x", expand=True,
                   ipady=6, ipadx=8)

        sep(inner, BG3)

        # ── Режим запису ──
        mode_frame = tk.Frame(inner, bg=BG, pady=12, padx=16)
        mode_frame.pack(fill="x")

        tk.Label(mode_frame, text="MODE", font=FONT_SMALL,
                 fg=TEXT_MUT, bg=BG).pack(anchor="w")

        self._mode_var = tk.StringVar(value="chunk")
        btn_row = tk.Frame(mode_frame, bg=BG)
        btn_row.pack(fill="x", pady=(6, 0))

        for label, val in [("CHUNK", "chunk"), ("FULL", "full")]:
            self._mode_btn(btn_row, label, val)

        # Тривалість + ітерації
        params_row = tk.Frame(mode_frame, bg=BG)
        params_row.pack(fill="x", pady=(10, 0))

        self._dur_var  = tk.IntVar(value=10)
        self._iter_var = tk.IntVar(value=5)

        self._spin_field(params_row, "DURATION (s)", self._dur_var,  3, 60)
        self._spin_field(params_row, "ITERATIONS",   self._iter_var, 1, 20)

        sep(inner, BG3)

        # ── Область результату ──
        self._result_frame = tk.Frame(inner, bg=BG, pady=0, padx=16)
        self._result_frame.pack(fill="both", expand=True)
        self._draw_idle()

        sep(inner, BG3)

        # ── Кнопки дій ──
        btn_area = tk.Frame(inner, bg=BG2, pady=14, padx=16)
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

        spin = tk.Spinbox(f, from_=mn, to=mx, textvariable=var,
                          font=FONT_BODY, bg=BG3, fg=TEXT,
                          buttonbackground=BG3, relief="flat",
                          bd=0, highlightthickness=1,
                          highlightbackground=BORDER,
                          highlightcolor=ACCENT, width=5)
        spin.pack(anchor="w", ipady=4, pady=(2, 0))

    def _action_btn(self, parent, text, bg, fg, cmd):
        btn = tk.Label(parent, text=text, font=FONT_BODY,
                       bg=bg, fg=fg, cursor="hand2",
                       pady=10)
        btn.bind("<Button-1>", lambda e: cmd())
        btn.bind("<Enter>",    lambda e: btn.configure(bg=ACCENT_DIM if bg == ACCENT else BORDER))
        btn.bind("<Leave>",    lambda e: btn.configure(bg=bg))
        return btn

    # ── Стани результату ───────────────────────────────────────
    def _clear_result(self):
        for w in self._result_frame.winfo_children():
            w.destroy()

    def _draw_idle(self):
        self._clear_result()
        tk.Label(self._result_frame, text="—", font=FONT_BIG,
                 fg=BORDER, bg=BG).pack(expand=True)
        tk.Label(self._result_frame,
                 text="press listen or load a file",
                 font=FONT_SMALL, fg=TEXT_MUT, bg=BG).pack()

    def _draw_recording(self):
        self._clear_result()
        self._pulse_label = tk.Label(
            self._result_frame, text="◉  LISTENING",
            font=FONT_HEAD, fg=ACCENT, bg=BG)
        self._pulse_label.pack(expand=True)
        tk.Label(self._result_frame,
                 text="analyzing audio stream…",
                 font=FONT_SMALL, fg=TEXT_MUT, bg=BG).pack()
        self._animate_pulse()

    def _animate_pulse(self, on=True):
        if self._state != "recording":
            return
        color = ACCENT if on else ACCENT_DIM
        if hasattr(self, "_pulse_label"):
            self._pulse_label.configure(fg=color)
        self.after(500, self._animate_pulse, not on)

    def _draw_found(self, title, artist):
        self._clear_result()
        tk.Label(self._result_frame, text="✓  FOUND",
                 font=FONT_SMALL, fg=SUCCESS, bg=BG).pack(pady=(16, 4))
        tk.Label(self._result_frame, text=title,
                 font=FONT_BIG, fg=TEXT, bg=BG,
                 wraplength=WIN_W - 32).pack()
        tk.Label(self._result_frame, text=artist,
                 font=FONT_BODY, fg=ACCENT, bg=BG).pack(pady=(4, 0))

        copy_btn = tk.Label(self._result_frame,
                            text="[ copy ]", font=FONT_SMALL,
                            fg=TEXT_MUT, bg=BG, cursor="hand2")
        copy_btn.pack(pady=(12, 0))
        copy_btn.bind("<Button-1>", lambda e: self._copy(f"{artist} — {title}"))

    def _draw_error(self, msg="track not found"):
        self._clear_result()
        tk.Label(self._result_frame, text="✕  NOT FOUND",
                 font=FONT_SMALL, fg=ERROR, bg=BG).pack(expand=True)
        tk.Label(self._result_frame, text=msg,
                 font=FONT_SMALL, fg=TEXT_MUT, bg=BG).pack()

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
                    self.after(0, self._on_result, title, artist)
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
                from shazamioFinder import shazamio_finder
                result = loop.run_until_complete(shazamio_finder(path))
                track = result.get("track", {}) if result else {}
                if track:
                    self.after(0, self._on_result,
                               track.get("title", "?"),
                               track.get("subtitle", "?"))
                else:
                    self.after(0, self._on_not_found)
            except Exception as e:
                self.after(0, self._on_error, str(e))
            finally:
                loop.close()

        threading.Thread(target=run, daemon=True).start()

    def _on_result(self, title, artist):
        self._state = "found"
        self._draw_found(title, artist)

    def _on_not_found(self):
        self._state = "error"
        self._draw_error("track not found in database")

    def _on_error(self, msg):
        self._state = "error"
        self._draw_error(msg[:60])

    def _copy(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)

    # ── Перетягування ──────────────────────────────────────────
    def _drag_start(self, e):
        self._drag_x = e.x
        self._drag_y = e.y

    def _drag_move(self, e):
        x = self.winfo_x() + (e.x - self._drag_x)
        y = self.winfo_y() + (e.y - self._drag_y)
        self.geometry(f"+{x}+{y}")


def sep(parent, color):
    tk.Frame(parent, bg=color, height=1).pack(fill="x")


# ── Запуск без трею (для тесту) ────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    win = BanduraWindow(root)
    root.mainloop()
