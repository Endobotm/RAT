import socket
import tkinter as tk
from PIL import Image, ImageTk, UnidentifiedImageError
import io
import threading

class ScreenSharingServer:
    def __init__(self, host='0.0.0.0', port=5000):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen(1)
        self.client_socket = None
        self.address = None
        self.is_screen_sharing = False

        self.root = tk.Tk()
        self.canvas = tk.Canvas(self.root, bg='black')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.start_button = tk.Button(self.root, text="Start Screen Share", command=self.start_screen_share)
        self.start_button.pack()

        self.stop_button = tk.Button(self.root, text="Stop Screen Share", command=self.stop_screen_share, state=tk.DISABLED)
        self.stop_button.pack()

        self.wait_for_connection()

    def wait_for_connection(self):
        threading.Thread(target=self.accept_connection).start()

    def accept_connection(self):
        print("Waiting for a connection...")
        self.client_socket, self.address = self.server_socket.accept()
        print(f"Connection from {self.address} has been established!")
        self.receive_images()

    def receive_images(self):
        try:
            while True:
                if not self.is_screen_sharing:
                    continue

                size_data = self.client_socket.recv(4)
                if not size_data:
                    raise ConnectionError("Client disconnected")
                size = int.from_bytes(size_data, 'big')

                data = b''
                while len(data) < size:
                    packet = self.client_socket.recv(min(4096, size - len(data)))
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
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        img_width, img_height = image.size
        img_ratio = img_width / img_height
        canvas_ratio = canvas_width / canvas_height

        if img_ratio > canvas_ratio:
            new_width = canvas_width
            new_height = int(canvas_width / img_ratio)
        else:
            new_height = canvas_height
            new_width = int(canvas_height * img_ratio)

        resized_image = image.resize((new_width, new_height), Image.LANCZOS)
        photo = ImageTk.PhotoImage(resized_image)

        self.canvas.create_image((canvas_width - new_width) // 2, (canvas_height - new_height) // 2, anchor=tk.NW, image=photo)
        self.canvas.image = photo

    def start_screen_share(self):
        self.is_screen_sharing = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

    def stop_screen_share(self):
        self.is_screen_sharing = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    server = ScreenSharingServer()
    server.run()
