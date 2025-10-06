import socket
import os
import sys
import ctypes
import threading
import selectors
from colorama import init, Fore, Style
import tkinter as objTK
from tkinter import ttk as objTTK
from tkinter import messagebox as objMessageBox
from tkextrafont import Font
import sv_ttk as objTheme
import ctypes
import hashlib as HASH
from PIL import Image, ImageTk, UnidentifiedImageError
import io
import zstandard as objCompressor
import numpy
from queue import Queue
import time

init()


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def elevate():
    if not is_admin():
        params = " ".join([f'"{arg}"' for arg in sys.argv])
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, params, None, 1
        )
        sys.exit()


GLOBAL_MAX_CLIENTS = 500


class TransferRateTracker:
    def __init__(self):
        self.bytes = 0
        self.start = time.time()

    def add_bytes(self, n):
        self.bytes += n

    def get_rate(self):
        elapsed = time.time() - self.start
        return int(self.bytes / elapsed) if elapsed > 0 else 0

    def reset(self):
        self.bytes = 0
        self.start = time.time()


transfer_rate = TransferRateTracker()


class SocketManager:
    def __init__(self, host="127.0.0.1", port=5001, max_clients=GLOBAL_MAX_CLIENTS):
        # Socket Crap
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        self.server_socket.setblocking(False)
        self.server_socket.bind((host, port))
        self.server_socket.listen()
        # Variable Crap
        self.clients = [None] * max_clients
        self.client_sockets = [None] * max_clients
        self.client_labels = [None] * max_clients
        self.logsClient = [""] * max_clients
        self.connectionsNum = 0
        self.connectionNumThing = str(self.connectionsNum) + " Connections!"
        self.current_client = 0
        self.client_infos = [{}] * max_clients
        self.current_info_index = 0
        self.logIndex = 0
        self.prev_frame = [{}] * max_clients
        self.image_queue = Queue()
        self.rate_per_client = [0] * max_clients
        self.image_buffer = [[] for _ in range(max_clients)]
        self.buffer_history = [[] for _ in range(max_clients)]
        # UI Elements
        self.canvas = objTK.Canvas(root, bg="black")
        self.canvas.pack(fill=objTK.BOTH, expand=True)
        # Select Thingy idk gfys
        self.sel = selectors.DefaultSelector()
        # HAVE AT THEM LADSSSSS
        threading.Thread(target=self.start, daemon=True).start()
        threading.Thread(target=self.worker, daemon=True).start()

    def worker(self):
        while True:
            args = self.image_queue.get()
            self.update_image(*args)
            # doing shit
            self.image_queue.task_done()

    def start(self):
        print(Fore.BLUE + "[*] Server listening [*]" + Style.RESET_ALL)
        self.sel.register(self.server_socket, selectors.EVENT_READ, data=None)
        while True:
            events = self.sel.select(timeout=None)
            for key, mask in events:
                sock = key.fileobj
                if mask & selectors.EVENT_READ:
                    try:
                        global client_socket, address
                        client_socket, address = self.server_socket.accept()
                        print(
                            Fore.GREEN
                            + f"[!] Connection from {address} has been established [!]"
                            + Style.RESET_ALL
                        )
                        empty_slot = None
                        for i in range(GLOBAL_MAX_CLIENTS):
                            if (
                                self.client_sockets[i] is None
                                or self.clients[i] == "No Client Connected"
                            ):
                                empty_slot = i
                                break
                        client_socket.setblocking(False)
                        if empty_slot is not None:
                            self.clients[empty_slot] = address[0]
                            self.client_sockets[empty_slot] = client_socket
                            self.connectionsNum += 1
                            #                    self.update_client_labels(
                            #                        empty_slot, address[0], "No IPv6", self.connectionsNum
                            #                    )
                            print(
                                Fore.BLUE
                                + f"[*] Verifying Client [*]"
                                + Style.RESET_ALL
                            )
                            try:
                                if (
                                    self.recv_exact(
                                        client_socket, empty_slot, 11
                                    ).decode("utf-8")
                                    != "CLIENT_REAL"
                                ):
                                    print(
                                        Fore.MAGENTA
                                        + "[+] Client Failed Verification - Client Handshake Failed [+]"
                                        + Style.RESET_ALL
                                    )
                                    self.handle_client_disconnection(
                                        empty_slot, "start() - real client verifier"
                                    )
                                else:
                                    print(
                                        Fore.GREEN
                                        + "[!] Client Verified [!]"
                                        + Style.RESET_ALL
                                    )
                                    threading.Thread(
                                        target=self.client_data_manager,
                                        args=(client_socket, empty_slot),
                                        daemon=True,
                                    ).start()
                                    print(
                                        Fore.YELLOW
                                        + "-// CLIENT RAID IN PROGRESS //-"
                                        + Style.RESET_ALL
                                    )
                                    try:
                                        self.sel.register(
                                            client_socket,
                                            selectors.EVENT_READ
                                            | selectors.EVENT_WRITE,
                                            data=None,
                                        )
                                    except KeyError:
                                        self.sel.modify(
                                            client_socket,
                                            selectors.EVENT_READ
                                            | selectors.EVENT_WRITE,
                                            data=None,
                                        )
                            except UnicodeDecodeError:
                                print(
                                    Fore.MAGENTA
                                    + "[+] Client Failed Verification - Client Handshake Failed [+]"
                                    + Style.RESET_ALL
                                )
                                self.handle_client_disconnection(
                                    empty_slot, "start() - real client verifier"
                                )
                        else:
                            print(
                                Fore.RED
                                + "[ERR] No new slots available [ERR]"
                                + Style.RESET_ALL
                            )
                    except BlockingIOError:
                        continue
                    except OSError as e:
                        print(Fore.RED + f"[ERR] {e} [ERR]" + Style.RESET_ALL)
                        self.stop()
                        break
            # if self.server_socket in readable:

    def recv_exact(self, sock, index: int, num_bytes):
        try:
            if isinstance(sock, socket.socket) and sock.fileno() >= 0:
                buf = b""
                while True:
                    try:
                        while len(buf) < num_bytes:
                            part = sock.recv(num_bytes - len(buf))
                            if not part:
                                self.handle_client_disconnection(index, "recv_exact()")
                            buf += part
                    except BlockingIOError:
                        continue  # Just in case yk?
                    break
                try:
                    return buf
                except UnicodeDecodeError:
                    return None
                except OSError:
                    self.handle_client_disconnection(index, "recv_exact()")
        except Exception:
            return None

    def send_with_tag(
        self,
        headerSEND,
        dataclassSEND,
        sizeSEND: int,
        dataSEND,
        sockSEND,
        indexSEND: int,
        filenameLengthSEND: int = 0,
        filenameSEND="",
        locationLengthSEND: int = 0,
        locationSEND="",
    ):
        try:
            if not headerSEND or not dataclassSEND or not sizeSEND or not dataSEND:
                print(
                    Fore.RED
                    + f"[ERR] send_with_tag() - Insufficient Parameters [ERR]"
                    + Style.RESET_ALL
                )
            else:
                if (
                    headerSEND == "F"
                    or headerSEND == "C"
                    or headerSEND == "I"
                    or headerSEND == "L"
                ):
                    if headerSEND == "F":
                        if (
                            filenameSEND
                            and filenameLengthSEND
                            and locationLengthSEND
                            and locationSEND
                        ):
                            sockSEND.sendall(headerSEND.encode("utf-8"))
                            sockSEND.sendall(
                                f"{dataclassSEND}{sizeSEND:020}{dataSEND}{filenameLengthSEND:020}{filenameSEND}{locationLengthSEND:020}{locationSEND}".encode(
                                    "utf-8"
                                )
                            )
                        else:
                            print(
                                Fore.RED
                                + f"[ERR] send_with_tag() - Insufficient Parameters [ERR]"
                                + Style.RESET_ALL
                            )
                    else:
                        sockSEND.sendall(headerSEND.encode("utf-8"))
                        sockSEND.sendall(
                            f"{dataclassSEND}{sizeSEND:020}{dataSEND}".encode("utf-8")
                        )
                else:
                    print(
                        Fore.RED
                        + f"[ERR] send_with_tag() - Invalid Header [ERR]"
                        + Style.RESET_ALL
                    )
        except (ConnectionError, OSError):
            self.handle_client_disconnection(indexSEND, "send_with_tag()")

    def buffer_algorithm(self, data, buffer_size, index, header):
        buffer = self.image_buffer[index]
        buffer.append(data)
        if len(buffer) >= buffer_size:
            while len(buffer) >= buffer_size:
                oldest_frame = buffer.pop(0)
                self.image_queue.put((index, oldest_frame, header))

    def client_data_manager(self, sock, index: int):
        while True:
            try:
                buf = self.recv_exact(sock, index, 28)
                if buf:
                    try:
                        header = buf[:1].decode("utf-8")
                        dataclass = buf[1:8].decode("utf-8")
                        sizeR = buf[8:29].decode("utf-8")
                        size = int(sizeR.lstrip("0") or "0")
                        recv_data = self.recv_exact(sock, index, size)
                        data = b""
                        transfer_rate.add_bytes(size + 28)
                        if recv_data is None:
                            self.handle_client_disconnection(
                                index, "client_data_manager() - recv_data is None"
                            )
                            break
                        try:
                            if recv_data[:1].decode("utf-8") == ">":
                                recv_data = recv_data[1:]
                                currChunk = int(
                                    recv_data[:20].decode("utf-8").lstrip("0") or "0"
                                )
                                recv_data = recv_data[20:]
                                totalChunks = int(
                                    recv_data[:20].decode("utf-8").lstrip("0") or "0"
                                )
                                recv_data = recv_data[21:]
                                data = data + recv_data
                                while currChunk != totalChunks:
                                    buf = self.recv_exact(sock, index, 28)
                                    header = buf[:1].decode("utf-8")
                                    dataclass = buf[1:8].decode("utf-8")
                                    sizeR = buf[8:29].decode("utf-8")
                                    size = int(sizeR.lstrip("0") or "0")
                                    recv_data = self.recv_exact(sock, index, size)
                                    if recv_data[:1].decode("utf-8") == ">":
                                        recv_data = recv_data[1:]
                                        currChunk = int(
                                            recv_data[:20].decode("utf-8").lstrip("0")
                                            or "0"
                                        )
                                        recv_data = recv_data[20:]
                                        totalChunks = int(
                                            recv_data[:20].decode("utf-8").lstrip("0")
                                            or "0"
                                        )
                                        recv_data = recv_data[21:]
                                        data = data + recv_data
                                    else:
                                        break
                                    print(
                                        Fore.LIGHTBLUE_EX
                                        + f"Client: {index+1}, Header Type: {header}, Data Class: {dataclass}, Size: {size}, Current Chunk: {currChunk}, Total Chunks: {totalChunks}, Transfer  Rate: {self.rate_per_client[index]}KB/s"
                                    )
                            if header == "C":
                                data = data.decode("utf-8")
                        except UnicodeDecodeError:
                            print(
                                Fore.LIGHTBLUE_EX
                                + f"Client: {index+1}, Header Type: {header}, Data Class: {dataclass}, Size: {size}"
                            )
                            data = recv_data
                        except TypeError:
                            continue
                        if self.rate_per_client[index] != 0 and data:
                            frames_received_per_sec = self.rate_per_client[index] / (
                                300 * 1024
                            )
                            buffer_size = int((1 / frames_received_per_sec))
                            self.buffer_history[index].append(buffer_size)
                            if len(self.buffer_history[index]) > 10:
                                self.buffer_history[index].pop(0)
                            # Use average
                            avg_buffer_size = int(
                                sum(self.buffer_history[index])
                                / len(self.buffer_history[index])
                            )
                            if dataclass == "screenV":
                                self.buffer_algorithm(
                                    data, avg_buffer_size, index, header
                                )
                        if dataclass == "deltaWH":
                            print(HASH.sha256(data.encode()).hexdigest())
                        self.rate_per_client[index] = transfer_rate.get_rate()
                        transfer_rate.reset()
                    except BlockingIOError:
                        continue
                    except (ConnectionError, OSError):
                        self.handle_client_disconnection(index, "client_data_manager()")
                        break
                    except ValueError as e:
                        print(
                            Fore.RED
                            + f"[ERR] Value Error - {e} [ERR]"
                            + Style.RESET_ALL
                        )
                        continue
                else:
                    break
            except BlockingIOError:
                continue

    def handle_client_disconnection(self, index: int, func):
        print(
            Fore.RED
            + f"[ERR] Client {index + 1} has disconnected - reported by {func} [ERR]"
            + Style.RESET_ALL
        )
        global connectionsNum, clients, client_sockets
        if self.client_sockets[index]:
            try:
                self.sel.unregister(self.client_sockets[index])
            except KeyError:
                pass
            self.client_sockets[index].close()
            self.client_sockets[index] = None
        count = 0
        for idx, i in enumerate(self.client_sockets):
            if not i:
                count += 1
            else:
                self.clients[idx] = "No Client Connected"

        self.connectionsNum = count

    def stop(self):
        for sock in self.client_sockets:
            if sock:
                try:
                    self.sel.unregister(sock)
                except KeyError:
                    pass
                sock.close()

    def update_image(self, index: int, image, type):
        decompressor = objCompressor.ZstdDecompressor()
        try:
            adjusted = Image.open(io.BytesIO(decompressor.decompress(image)))
            original_width, original_height = adjusted.size
            aspect_ratio = original_height / original_width

            new_height = int(self.canvas.winfo_width() * aspect_ratio)
            new_size = (self.canvas.winfo_width(), new_height)
            photo = ImageTk.PhotoImage(
                adjusted.resize(
                    new_size,
                    Image.Resampling.LANCZOS,
                )
            )
            self.canvas.create_image(0, 0, anchor="nw", image=photo)
            self.canvas.img_ref = photo
            self.prev_frame[index] = adjusted
        except (OSError, ConnectionError):
            self.handle_client_disconnection(index, "update_image()")


# Tkinter crap
root = objTK.Tk()
root.title("Server Side Control Panel")
root.geometry("800x450")
# root.resizable(width=False, height=False)
if sys.platform == "win32":
    root.iconbitmap("Images/icon.ico")
path = "Fonts/font.ttf"
path2 = "Fonts/font2.ttf"
path3 = "Fonts/font3.otf"
# Fonts
normalFont = Font(file=path, family="Montserrat", size=10)
smallFont = Font(file=path3, family="Cascadia Mono Light", size=8)
terminalFont = Font(family="Cascadia Mono Light", size=8)
boldFont = Font(family="Montserrat Semibold", size=20)
lightFont = Font(family="Montserrat Light", size=10)


def set_dpi_aware():
    try:
        if sys.platform == "win32":
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
            ctypes.windll.user32.SetProcessDPIAware()
        monitor_dpi = root.winfo_fpixels("1i")
        scaling_factor = max(1.0, monitor_dpi / 96.0) * 1.7
        root.tk.call("tk", "scaling", scaling_factor)
    except Exception as e:
        print(f"Failed to set DPI awareness: {e}")


set_dpi_aware()

objTheme.set_theme("dark")

SocketManager()
root.mainloop()
