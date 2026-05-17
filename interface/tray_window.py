import tkinter as tk
from tkinter import filedialog
import threading
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'audioProces'))

from musicFinder import music_finder


# ── Запуск без трею (для тесту) ────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    win = BanduraWindow(root)
    root.mainloop()
