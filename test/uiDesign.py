import tkinter as objTK
from tkinter import ttk as objTTK
from tkinter import messagebox as objMessageBox
import tkinter.font as tkFont
import sv_ttk
import ctypes
from pathlib import Path
from PIL import Image, ImageTk, UnidentifiedImageError
import io
import threading
import socket
import ast

connectionsNum = 0
clients = ["No Client Connected"] * 5
client_labels = [None] * 5
connectionNumThing = str(connectionsNum) + " Connections!"
client_sockets = [None] * 5

class ScreenSharingServer:
    def __init__(self, master, host='0.0.0.0', port=5001):
        self.master = master
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)
        
        self.clients = [None] * 5
        self.client_sockets = [None] * 5
        self.client_labels = [None] * 5  # List to hold references to client labels
        self.connectionNumThing = str(connectionsNum) + " Connections!"
        self.current_client = 0
        self.is_screen_sharing = True  # Initialize the attribute

        self.canvas = objTK.Canvas(master, bg='black')
        self.canvas.pack(fill=objTK.BOTH, expand=True)

        self.prev_button = objTTK.Button(master, text="Previous", command=self.prev_client, width=20, state=objTK.DISABLED)
        self.prev_button.pack(padx=5, pady=5, side=objTK.LEFT)
        
        self.next_button = objTTK.Button(master, text="Next", command=self.next_client, width=20, state=objTK.DISABLED)
        self.next_button.pack(padx=5, pady=5, side=objTK.RIGHT)

        self.wait_for_connection()

    def wait_for_connection(self):
        threading.Thread(target=self.accept_connection).start()

    def accept_connection(self):
        global connectionsNum  # Assuming connectionsNum is defined globally somewhere
        print("Waiting for a connection...")
        try:
            while True:
                client_socket, address = self.server_socket.accept()
                print(f"Connection from {address} has been established!")
                
                # Receive client info
                client_info = client_socket.recv(1024).decode('utf-8')
                client_info = ast.literal_eval(client_info)
                for key, value in client_info.items():
                    clientInfoFrameText.config(state="normal")
                    clientInfoFrameText.insert(objTK.END, f"{key}: {value}\n")
                    clientInfoFrameText.config(state="disabled")
                client_socket.send("received".encode('utf-8'))
                
                # Find an empty slot for the client
                empty_slot = None
                ipv6 = "wtf no ipv6?"
                for addr_info in socket.getaddrinfo(address[0], None):
                    if addr_info[0] == socket.AF_INET6:
                        ipv6 = addr_info[4][0]
                        break
                for i in range(5):
                    if self.client_sockets[i] is None or self.clients[i] == "Client Disconnected":
                        empty_slot = i
                        break
                if empty_slot is not None:
                    self.clients[empty_slot] = address[0]
                    self.client_sockets[empty_slot] = client_socket
                    connectionsNum += 1
                    self.update_client_labels(empty_slot, address[0], ipv6, connectionsNum)  # Update client labe
                    if connectionsNum > 1:
                        self.next_button.config(state=objTK.NORMAL)
                        self.prev_button.config(state=objTK.NORMAL)
                    threading.Thread(target=self.receive_images, args=(client_socket, empty_slot)).start()
                else:
                    print("No available slots for new connections.")
        except OSError as e:
            if str(e) != "[WinError 10038] An operation was attempted on something that is not a socket":
                print(f"Error: {e}")
                self.disconnect()

    def receive_images(self, client_socket, index):
        try:
            while True:
                if not self.is_screen_sharing:
                    continue

                size_data = client_socket.recv(4)
                if not size_data:
                    raise ConnectionError("Client disconnected")
                size = int.from_bytes(size_data, 'big')

                data = b''
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

            self.canvas.create_image((canvas_width - new_width) // 2, (canvas_height - new_height) // 2, anchor=objTK.NW, image=photo)
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
        connectionsNum -= 1
        self.update_client_labels(index, "Client Disconnected", "Client Disconnected", connectionsNum)  # Update label to indicate disconnection
        if connectionsNum <= 1:
            self.next_button.config(state=objTK.DISABLED)
            self.prev_button.config(state=objTK.DISABLED)

    def disconnect(self):
        for sock in self.client_sockets:
            if sock:
                sock.close()
        self.is_screen_sharing = False

    def update_client_labels(self, index, ipv4, ipv6, num):
        # Example implementation, adjust as per your GUI structure
        connectionNumThing.config(text=f"{num} Connections!")
        if ipv4 != "Client Disconnected":
            client_labels[index].config(text=f"IPv4: {ipv4} | IPv6: {ipv6}")
        else:
            client_labels[index].config(text="Client Disconnected")

# Enable high DPI scaling on Windows
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception as e:
    print(f"Failed to set DPI awareness: {e}")

# Path to the font file
font_path = Path('font.ttf')

# Verify that the font file exists
if not font_path.is_file():
    print(f"Font file '{font_path}' does not exist.")
    exit(1)

# Load the font
ctypes.windll.gdi32.AddFontResourceW(str(font_path))

root = objTK.Tk()
root.title("Server Side Control Panel")
root.geometry("905x610")
root.resizable(width=False, height=False)

# Specify the font family name
family = "Josefin Slab"

# Define fonts with different weights using bold and normal
smallFont = tkFont.Font(family=family, size=10)
lightFont = tkFont.Font(family=family, size=12)  # Light equivalent (use NORMAL)
normalFont = tkFont.Font(family=family, size=12, weight=tkFont.NORMAL)  # Normal
boldFont = tkFont.Font(family=family, size=12, weight=tkFont.BOLD)  # Bold
bigGlobalFont = tkFont.Font(family=family, size=20, weight=tkFont.BOLD)  # Big Bold

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
        focus_bg = "#333333"  # Dark theme background
    else:
        focus_bg = "#FFFFFF"  # Light theme background
    
    style.map("TNotebook.Tab", focuscolor=[('!focus', focus_bg), ('focus', focus_bg)])
    style.configure("TNotebook.Tab", font=normalFont)  # Set the font for tabs

sv_ttk.set_theme("dark")
style = objTTK.Style()

style.configure("TButton", font=normalFont)
style.map('TButton', font=[('disabled', (family, 12, 'bold'))])
style.layout('TNotebook.Tab', [
    ('Notebook.tab', {
        'sticky': 'nswe',
        'children': [
            ('Notebook.padding', {
                'side': 'top',
                'sticky': 'nswe',
                'children': [
                    ('Notebook.label', {'sticky': 'nswe'})
                ]
            })
        ]
    })
])

apply_focus_style()

tabControl = objTTK.Notebook(root, width=887, height=547)

objHomeTab = objTTK.Frame(tabControl)
objSettingsTab1 = objTTK.Frame(tabControl)
objSettingsTab2 = objTTK.Frame(tabControl)
objSettingsTab3 = objTTK.Frame(tabControl)
objSettingsTab4 = objTTK.Frame(tabControl)

tabControl.add(objHomeTab, text='Home')
tabControl.add(objSettingsTab1, text='Remote CMD')
tabControl.add(objSettingsTab2, text='Screen View')
tabControl.add(objSettingsTab3, text='File Uploader')
tabControl.add(objSettingsTab4, text='File Downloader')

# Home Tab
themeLabel = objTTK.Label(objHomeTab, text="Toggle between Light and Dark theme:", font=normalFont)
themeLabel.place(x=20, y=20)
themeToggle = objTTK.Button(objHomeTab, text="Toggle theme", command=toggle_theme)
themeToggle.place(x=30, y=50)

# Connections
heading = objTTK.Label(objHomeTab, text="Connections", font=bigGlobalFont)
heading.place(x=20, y=100)

connections = objTTK.Label(objHomeTab, text=str(connectionsNum) + " Connections!", font=normalFont)
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

clientInfoFrame = objTK.Frame(objHomeTab, bg="#252525", bd=2, highlightthickness=0, borderwidth=0)
clientInfoFrame.place(x=382,y=5, width=500, height=170)

clientInfoFrameText = objTK.Text(clientInfoFrame, font=smallFont, bg="#252525", fg="#fff", state="disabled", highlightthickness=0, borderwidth=0, padx=5, pady=5)
clientInfoFrameText.place(x=0,y=0, width=500, height=170)
# Remote CMD tab
class CustomCommandPrompt:
    def __init__(self, master):
        self.frame = objTK.Frame(master, bg="#252525", bd=2, highlightthickness=0, borderwidth=0)
        self.frame.place(relx=0.5, rely=0.5, anchor=objTK.CENTER, width=870, height=525)

        self.output_text = objTK.Text(self.frame, font=normalFont, bg="#252525", fg="#fff", state="disabled", highlightthickness=0, borderwidth=0, padx=15, pady=15)
        self.output_text.place(relwidth=1, relheight=0.929)
        
        self.command_entry = objTTK.Entry(self.frame, font=normalFont)
        self.command_entry.place(relx=0, rely=0.91, relwidth=1, relheight=0.08)
        self.command_entry.bind("<Return>", self.display_command)

    def display_command(self, event):
        command = self.command_entry.get()
        if command != "":
            self.output_text.config(state="normal")
            self.output_text.insert(objTK.END, f"$ {command}\n")
            self.output_text.insert(objTK.END, f"$ No Client Response\n")
            self.command_entry.delete(0, objTK.END)
            self.output_text.config(state="disabled")
            self.output_text.yview_moveto(1.0)
        else:
            print("fuck you")

# Instantiate the CustomCommandPrompt class
terminal = CustomCommandPrompt(objSettingsTab1)

# Screen View tab
tabControl.add(objSettingsTab2, text='Screen View')
server = ScreenSharingServer(objSettingsTab2)


# File Uploader tab
lb4 = objTTK.Label(objSettingsTab3, text="Placeholder 3", font=normalFont)
lb4.place(x=5, y=5)

# File Downloader tab
lb5 = objTTK.Label(objSettingsTab4, text="Placeholder 4", font=normalFont)
lb5.place(x=5, y=5)

def center_widget(widget):
    widget.place(relx=0.5, rely=0.5, anchor="center")

def shutDown():
    if objMessageBox.askyesno(title="WARNING", message="Are you sure you want to shut down? This will close the connection between the client and the server. You will not be able to reconnect unless the client program is opened manually along with the server."):
        if objMessageBox.askyesno(title="LAST WARNING", message="Are you really sure?!"):
            if server.server_socket is not None:
                server.server_socket.close()
            if server.is_screen_sharing:
                server.is_screen_sharing = False
            if server.client_sockets != [None]:
                try:
                    for sock in server.client_sockets:
                        if sock is not None:
                            sock.close()
                except Exception as e:
                    print(f"Error while closing client sockets: {e}")
            server.disconnect()
            stop_all_threads()
            root.destroy()

def stop_all_threads():
    for thread in threading.enumerate():
        if thread.name != "MainThread":
            try:
                ctypes.pythonapi.PyThreadState_SetAsyncExc(
                    ctypes.c_long(thread.ident),
                    ctypes.py_object(SystemExit)
                )
            except Exception as e:
                print(f"Error while stopping thread {thread.name}: {e}")

center_widget(tabControl)

root.protocol("WM_DELETE_WINDOW", shutDown)
root.mainloop()
