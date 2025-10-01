import ctypes
import time

VK_CAPITAL = 0x14  # Virtual key code for Caps Lock


def is_caps_on():
    return bool(ctypes.WinDLL("User32.dll").GetKeyState(VK_CAPITAL) & 1)


# Toggle Caps Lock
def toggle_caps(timeS):
    ctypes.WinDLL("User32.dll").keybd_event(VK_CAPITAL, 0, 2, 0)
    ctypes.WinDLL("User32.dll").keybd_event(VK_CAPITAL, 0, 0, 0)
    time.sleep(timeS)
    ctypes.WinDLL("User32.dll").keybd_event(VK_CAPITAL, 0, 2, 0)


code = ".-.. . - / -- . / --- ..- -"
for i in code:
    if i == ".":
        toggle_caps(0.1)
    elif i == "-":
        toggle_caps(0.7)
    elif i == " ":
        toggle_caps(0.3)
    elif i == "/":
        toggle_caps(1)
    else:
        pass
ctypes.WinDLL("User32.dll").keybd_event(VK_CAPITAL, 0, 0, 0)
