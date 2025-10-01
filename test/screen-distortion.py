import numpy as np
import tkinter as tk
import sys
import ctypes
import cv2
from mss import mss
from PIL import Image, ImageTk

root = tk.Tk()
root.title("Server Side Control Panel")
root.resizable(width=False, height=False)

canvas = tk.Canvas(root, width=1200, height=800)
canvas.pack(fill=tk.BOTH, expand=True)
sct = mss()

# Precompute LUT for gamma correction
lut = np.array([((i / 255.0) ** 0.8) * 255 for i in range(256)]).astype("uint8")


def distorter():
    img = np.array(sct.grab(sct.monitors[1]))[..., :3]
    factors = np.random.randint(0, 3, size=(3,))
    img = img * factors
    img = cv2.LUT(img.astype("uint8"), lut)
    noise = np.random.normal(0, 20, img.shape).astype("int16")
    img = cv2.add(img, noise, dtype=cv2.CV_8U)
    offsets = np.random.randint(-10, 10, size=(img.shape[0],))
    for y, off in enumerate(offsets):
        M = np.float32([[1, 0, off], [0, 1, 0]])
        img[y : y + 1] = cv2.warpAffine(img[y : y + 1], M, (img.shape[1], 1))
    img = cv2.resize(
        img,
        (canvas.winfo_width(), canvas.winfo_height()),
        interpolation=cv2.INTER_LANCZOS4,
    )
    img = ImageTk.PhotoImage(Image.fromarray(img))
    canvas.create_image(0, 0, anchor="nw", image=img)
    canvas.img_ref = img


def set_dpi_aware(root):
    try:
        if sys.platform == "win32":
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
            ctypes.windll.user32.SetProcessDPIAware()
        monitor_dpi = root.winfo_fpixels("1i")
        scaling_factor = max(1.0, monitor_dpi / 96.0) * 1.7
        root.tk.call("tk", "scaling", scaling_factor)
    except Exception as e:
        print(f"Failed to set DPI awareness: {e}")


set_dpi_aware(root)


def update():
    distorter()
    root.after(1, update)


update()

root.mainloop()
