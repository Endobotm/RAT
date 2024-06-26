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

connectionsNum = 0
client1IP = "No Client Connected"
client2IP = "No Client Connected"
client3IP = "No Client Connected"
client4IP = "No Client Connected"
client5IP = "No Client Connected"

# Global variables for label widgets in the Home tab
connections = None
connections1_label = None
connections2_label = None
connections3_label = None
connections4_label = None
connections5_label = None

class ScreenSharingServer:
    def __init__(self, master, host='0.0.0.0', port=5001):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((host, port))
        self.server_socket.listen(1)
        self.client_sockets = [None] * 5  # List to hold client sockets
        self.client_addresses = [None] * 5  # List to hold client addresses
        self.current_client_index = 0  # Index to keep track of current client
        self.is_screen_sharing = True
        self.canvas = objTK.Canvas(master, bg='black')
        self.canvas.pack(fill=objTK.BOTH, expand=True)

        self.start_button = objTTK.Button(master, text="Start Screen Share", command=self.start_screen_share, state=objTK.DISABLED)
        self.start_button.pack(padx=5, pady=5)

        self.stop_button = objTTK.Button(master, text="Stop Screen Share", command=self.stop_screen_share)
        self.stop_button.pack(padx=5, pady=5)

        self.client_label = objTTK.Label(master, text="", font=normalFont)
        self.client_label.pack(padx=5, pady=5)

        self.prev_client_button = objTTK.Button(master, text="Previous Client", command=self.switch_to_prev_client)
        self.prev_client_button.pack(padx=5, pady=5)

        self.next_client_button = objTTK.Button(master, text="Next Client", command=self.switch_to_next_client)
        self.next_client_button.pack(padx=5, pady=5)

        self.wait_for_connection()

    def wait_for_connection(self):
        threading.Thread(target=self.accept_connection).start()

    def accept_connection(self):
        try:
            while True:
                for i in range(5):
                    if self.client_sockets[i] is None:
                        self.client_sockets[i], self.client_addresses[i] = self.server_socket.accept()
                        break
                else:
                    objMessageBox.WARNING("Out of Sockets!")

                # Update client label to display current client's IP
                self.current_client_ip = self.client_addresses[self.current_client_index][0]
                self.client_label.config(text="Current Client: " + self.current_client_ip)

                self.receive_images()
        except OSError as e:
            if str(e) != "[WinError 10038] An operation was attempted on something that is not a socket":
                print(f"Error: {e}")
                self.disconnect()

    def receive_images(self):
        try:
            while True:
                if not self.is_screen_sharing:
                    continue

                size_data = self.client_sockets[self.current_client_index].recv(4)
                if not size_data:
                    raise ConnectionError("Client disconnected")
                size = int.from_bytes(size_data, 'big')

                data = b''
                while len(data) < size:
                    packet = self.client_sockets[self.current_client_index].recv(min(4096, size - len(data)))
                    if not packet:
                        raise ConnectionError("Client disconnected")
                    data += packet

                if len(data) < size:
                    raise ConnectionError("Incomplete data received")

                try:
                    image = Image.open(io.BytesIO(data))
                    self.update_image(image)
                except UnidentifiedImageError:
                    print("Received data is not a valid image")
        except (ConnectionError, OSError) as e:
            print(f"Error: {e}")
            self.disconnect()

    def update_image(self, image):
        try:
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            if canvas_width <= 0 or canvas_height <= 0:
                print("Canvas width or height is not valid")
                return  # Don't attempt to resize if canvas size is not valid

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
                print("New width or height after resizing is not valid")
                return  # Don't attempt to resize if calculated size is not valid

            resized_image = image.resize((new_width, new_height), Image.LANCZOS)
            photo = ImageTk.PhotoImage(resized_image)

            self.canvas.create_image((canvas_width - new_width) // 2, (canvas_height - new_height) // 2, anchor=objTK.NW, image=photo)
            self.canvas.image = photo
        except Exception as e:
            print(f"Error in updating image: {e}")

    def start_screen_share(self):
        self.is_screen_sharing = True
        self.start_button.config(state=objTK.DISABLED)
        self.stop_button.config(state=objTK.NORMAL)

    def stop_screen_share(self):
        self.is_screen_sharing = False
        self.start_button.config(state=objTK.NORMAL)
        self.stop_button.config(state=objTK.DISABLED)

    def disconnect(self):
        for i in range(5):
            if self.client_sockets[i]:
                self.client_sockets[i].close()
                self.client_sockets[i] = None
        self.is_screen_sharing = False

    def switch_to_prev_client(self):
        if self.current_client_index > 0:
            self.current_client_index -= 1
            self.current_client_ip = self.client_addresses[self.current_client_index][0]
            self.client_label.config(text="Current Client: " + self.current_client_ip)
            self.receive_images()

    def switch_to_next_client(self):
        if self.current_client_index < 4:  # Assuming there are only 5 clients
            self.current_client_index += 1
            self.current_client_ip = self.client_addresses[self.current_client_index][0]
            self.client_label.config(text="Current Client: " + self.current_client_ip)
            self.receive_images()


def update_client_labels():
    global connections1_label, connections2_label, connections3_label, connections4_label, connections5_label, connections
    connections.config(text = str(connectionsNum) + " Connections!")
    if connectionsNum >= 1:
        connections1_label.config(text=client1IP)
    if connectionsNum >= 2:
        connections2_label.config(text=client2IP)
    if connectionsNum >= 3:
        connections3_label.config(text=client3IP)
    if connectionsNum >= 4:
        connections4_label.config(text=client4IP)
    if connectionsNum >= 5:
        connections5_label.config(text=client5IP)

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

connections1_label = objTTK.Label(objHomeTab, text=client1IP, font=normalFont)
connections1_label.place(x=40, y=170)

connections2_label = objTTK.Label(objHomeTab, text=client2IP, font=normalFont)
connections2_label.place(x=40, y=200)

connections3_label = objTTK.Label(objHomeTab, text=client3IP, font=normalFont)
connections3_label.place(x=40, y=230)

connections4_label = objTTK.Label(objHomeTab, text=client4IP, font=normalFont)
connections4_label.place(x=40, y=260)

connections5_label = objTTK.Label(objHomeTab, text=client5IP, font=normalFont)
connections5_label.place(x=40, y=290)

# Remote CMD tab
class CustomCommandPrompt:
    def __init__(self, master):
        self.frame = objTK.Frame(master, bg="#222", bd=2, relief="solid", highlightthickness=0, borderwidth=0)
        self.frame.place(relx=0.5, rely=0.5, anchor=objTK.CENTER, width=850, height=400)
        smallFont = tkFont.Font(family=family, size=10, weight=tkFont.NORMAL)
        self.output_text = objTK.Text(self.frame, wrap=objTK.WORD, state="disabled", bg="#111", fg="white", highlightthickness=0, borderwidth=0, spacing1=0, spacing2=0, spacing3=0, font=smallFont)
        self.output_text.place(relwidth=1, relheight=0.9)
        self.command_entry = objTTK.Entry(self.frame, font=normalFont)
        self.command_entry.place(relx=0, rely=0.9, relwidth=1, relheight=0.1)
        self.command_entry.bind("<Return>", self.execute_command)

    def execute_command(self, event):
        command = self.command_entry.get()
        self.output_text.config(state="normal")
        self.output_text.insert(objTK.END, f"\n$ {command}\n")
        # insert output logic self.output_text.insert(objTK.END, f"Directory changed to: {new_dir}\n")
        self.command_entry.delete(0, objTK.END)
        self.output_text.config(state="disabled")
        self.output_text.yview_moveto(1.0)

# Instantiate the CustomCommandPrompt class
terminal = CustomCommandPrompt(objSettingsTab1)

# Screen View tab
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
    global server
    if objMessageBox.askyesno(title="WARNING", message="Are you sure you want to shut down? This will close the connection between client and the server? YOU WILL NOT BE ABLE TO CONNECT TO THE CLIENT AGAIN UNLESS THE CLIENT PROGRAM IS OPENED MANUALLY ALONG WITH THE SERVER"):
        if objMessageBox.askyesno(title="LAST WARNING", message="REALLY SURE?!"):
            if server.server_socket is not None:
                server.server_socket.close()
            if server.client_socket is not None:
                server.client_socket.close()
            root.destroy()
            


root.bind("<Escape>", lambda _: root.destroy())

center_widget(tabControl)

root.protocol("WM_DELETE_WINDOW", shutDown)
root.mainloop()
