import sys
import os
import threading
import tkinter as tk

# ── Шляхи до модулів ──────────────────────────────────────────
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, 'audioProces'))
sys.path.insert(0, os.path.join(ROOT, 'interface'))

# Імпортуємо клас вікна (уся логіка кнопок та дизайну всередині нього)
from interface.tray_window import BanduraWindow

try:
    import pystray
    from PIL import Image, ImageDraw
    TRAY_OK = True
except ImportError:
    TRAY_OK = False
    print("[WARN] pystray або Pillow не встановлено — трей недоступний.")
    print("       pip install pystray pillow")


# ── Іконка для трею ───────────────────────────────────────────
def make_icon() -> "Image.Image":
    img_path = os.path.join(ROOT, 'img', 'icon.png')
    if os.path.exists(img_path):
        from PIL import Image
        return Image.open(img_path)
    # Генеруємо просту іконку, якщо файлу немає на диску
    from PIL import Image, ImageDraw
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([4, 4, 60, 60],  fill="#E8FF47")
    d.ellipse([18, 18, 46, 46], fill="#0D0D0D")
    return img


# Tk root (прихований)
root = tk.Tk()
root.withdraw() # Ховаємо дефолтне порожнє вікно Tkinter

popup: BanduraWindow | None = None


def get_window() -> BanduraWindow:
    """Повертає існуюче вікно або створює нове інтерфейсне вікно."""
    global popup
    if popup is None or not popup.winfo_exists():
        # Створюється ТІЛЬКИ об'єкт вікна інтерфейсу
        popup = BanduraWindow(root)
    return popup


def toggle_window(icon=None, item=None):
    """Відкриває або ховає вікно за кліком на іконку трею."""
    win = get_window()
    if win.state() == "withdrawn":
        win.deiconify()
        win.lift()
        win.focus_force()
    else:
        win.withdraw()


def quit_app(icon=None, item=None):
    """Повне закриття програми."""
    if TRAY_OK and icon:
        icon.stop()
    root.quit()


# ── Запуск програми ───────────────────────────────────────────
if TRAY_OK:
    # Описуємо меню для іконки біля годинника
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

    # Запускаємо іконку трею в окремому фоновому потоці
    threading.Thread(target=tray_icon.run, daemon=True).start()

    # Через 200 мс просто створюємо та показуємо вікно візуалу
    root.after(200, get_window)

else:
    # Якщо бібліотеки трею немає — просто відкриваємо вікно інтерфейсу
    get_window()

# Головний цикл Tkinter, який утримує вікна активними
root.mainloop()