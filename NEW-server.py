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


GLOBAL_MAX_CLIENTS = 5


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
        self.nuclearFailSafeAkaDeltaWarhead = False
        self.logIndex = 0
        # Select Thingy idk gfys
        self.sel = selectors.DefaultSelector()
        # HAVE AT THEM LADSSSSS
        threading.Thread(target=self.start).start()

    def start(self):
        print(Fore.BLUE + "[*] Server listening [*]" + Style.RESET_ALL)
        self.sel.register(self.server_socket, selectors.EVENT_READ, data=None)
        while True:
            events = self.sel.select(timeout=None)
            # readable, _, _ = select.select([self.server_socket], [], [], 0.1)
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
                            if (
                                self.recv_exact(client_socket, empty_slot, 11).decode(
                                    "utf-8"
                                )
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
                                        selectors.EVENT_READ | selectors.EVENT_WRITE,
                                        data=None,
                                    )
                                except KeyError:
                                    self.sel.modify(
                                        client_socket,
                                        selectors.EVENT_READ | selectors.EVENT_WRITE,
                                        data=None,
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

    def client_data_manager(self, sock, index: int):
        while True:
            try:
                buf = self.recv_exact(sock, index, 28)
                if buf:
                    try:
                        if buf:
                            header = buf[:1].decode("utf-8")
                            dataclass = buf[1:8].decode("utf-8")
                            sizeR = buf[8:29].decode("utf-8")
                            size = int(sizeR.lstrip("0") or "0")
                            data = self.recv_exact(sock, index, size)
                            if dataclass != "deltaWH":
                                print(
                                    Fore.LIGHTBLUE_EX
                                    + f"Client: {index+1}, Header Type: {header}, Data Class: {dataclass}, Size: {size}"
                                )
                            else:
                                print(HASH.sha256(data.encode()).hexdigest())
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


# Tkinter crap
root = objTK.Tk()
root.title("Server Side Control Panel")
root.geometry("905x610")
root.resizable(width=False, height=False)
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
