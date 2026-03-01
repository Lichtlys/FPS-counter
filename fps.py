import tkinter as tk
import time
import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32

# --------- MONITOR ENUM ----------
MONITORENUMPROC = ctypes.WINFUNCTYPE(
    wintypes.BOOL,
    wintypes.HMONITOR,
    wintypes.HDC,
    ctypes.POINTER(wintypes.RECT),
    wintypes.LPARAM
)

def get_monitors():
    monitors = []

    def _callback(hMonitor, hdc, lprcMonitor, lParam):
        r = lprcMonitor.contents
        monitors.append((r.left, r.top, r.right, r.bottom))
        return True

    cb = MONITORENUMPROC(_callback)
    user32.EnumDisplayMonitors(0, 0, cb, 0)
    return monitors

# --------- WINDOW STYLE ----------
GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x80000
WS_EX_TRANSPARENT = 0x20

TRANSPARENT_KEY = "magenta"
FONT = ("Arial", 16, "bold")

class FpsOverlay:
    def __init__(self, root, mon_rect):
        self.l, self.t, self.r, self.b = mon_rect
        self.margin = 10

        self.win = tk.Toplevel(root)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.config(bg=TRANSPARENT_KEY)
        self.win.wm_attributes("-transparentcolor", TRANSPARENT_KEY)

        # click-through
        self.win.update_idletasks()
        hwnd = user32.GetParent(self.win.winfo_id())
        style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_LAYERED | WS_EX_TRANSPARENT)

        # outlined text
        self.outline = []
        offsets = [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)]

        for dx, dy in offsets:
            lbl = tk.Label(self.win, font=FONT, fg="black", bg=TRANSPARENT_KEY)
            lbl.place(x=dx, y=dy)
            self.outline.append(lbl)

        self.main = tk.Label(self.win, font=FONT, fg="white", bg=TRANSPARENT_KEY)
        self.main.place(x=0, y=0)

        self.times = []

        self.keep_on_top()
        self.tick()

    def set_text(self, s):
        self.main.config(text=s)
        for lbl in self.outline:
            lbl.config(text=s)

    def place_top_left(self):
        self.win.update_idletasks()
        x = self.l + self.margin
        y = self.t + self.margin
        self.win.geometry(f"+{x}+{y}")

    def tick(self):
        now = time.perf_counter()
        self.times.append(now)

        cutoff = now - 1.0
        while self.times and self.times[0] < cutoff:
            self.times.pop(0)

        fps = len(self.times)
        self.set_text(f"FPS: {fps}")

        self.place_top_left()
        self.win.after(1, self.tick)

    def keep_on_top(self):
        self.win.attributes("-topmost", True)
        self.win.after(500, self.keep_on_top)

# --------- MAIN ----------
def main():
    monitors = get_monitors()

    root = tk.Tk()
    root.withdraw()

    overlays = []
    for rect in monitors:
        overlays.append(FpsOverlay(root, rect))

    root.mainloop()

main()