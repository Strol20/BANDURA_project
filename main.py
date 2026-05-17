import sys
import os
import threading
import tkinter as tk
from PIL import Image, ImageDraw
import pystray

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from interface.tray_window import BanduraWindow

# ── Іконка трею (генерується якщо немає файлу) ─────────────────
def make_icon():
    img_path = os.path.join(os.path.dirname(__file__), '..', 'img', 'icon.png')
    if os.path.exists(img_path):
        return Image.open(img_path)
    # Генеруємо просту іконку
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([4, 4, 60, 60], fill="#E8FF47")
    d.ellipse([18, 18, 46, 46], fill="#0D0D0D")
    return img


# ── Головне вікно Tk (прихований root) ─────────────────────────
root = tk.Tk()
root.withdraw()

popup: BanduraWindow | None = None


def toggle_window(icon=None, item=None):
    global popup
    if popup is None or not popup.winfo_exists():
        popup = BanduraWindow(root)
    elif popup.state() == "withdrawn":
        popup.deiconify()
        popup.lift()
    else:
        popup.withdraw()


def quit_app(icon, item):
    icon.stop()
    root.quit()


# ── Меню трею ──────────────────────────────────────────────────
menu = pystray.Menu(
    pystray.MenuItem("Open / Close", toggle_window, default=True),
    pystray.Menu.SEPARATOR,
    pystray.MenuItem("Quit", quit_app),
)

tray_icon = pystray.Icon(
    name="BANDURA",
    icon=make_icon(),
    title="BANDURA — music finder",
    menu=menu,
)

# Запускаємо тrei в окремому потоці, Tk в головному
threading.Thread(
    target=tray_icon.run,
    daemon=True,
).start()

root.mainloop()
