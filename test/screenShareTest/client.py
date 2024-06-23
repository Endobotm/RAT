import socket
import pyautogui
from PIL import Image
import io
import threading
import time
import platform

class ScreenSharingClient:
    def __init__(self, server_ip='ENDOSPC', server_port=5001):
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.is_screen_sharing = False  # Flag to control screen sharing
        self.connect_to_server()

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
                print("Server received system info")
                self.start_screen_share()  # Start screen sharing upon receiving acknowledgment
        except Exception as e:
            print(f"Error sending system info: {e}")
            self.client_socket.close()

    def get_system_info(self):
        system_info = {
            'hostname': platform.node(),
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor()
        }
        return str(system_info)

    def receive_commands(self):
        try:
            while True:
                command = self.client_socket.recv(1024).decode('utf-8')
        except Exception as e:
            print(f"Error receiving commands: {e}")
            self.client_socket.close()

    def start_screen_share(self):
        self.is_screen_sharing = True
        self.start_screenshot_thread()

    def start_screenshot_thread(self):
        self.screenshot_thread = threading.Thread(target=self.send_screenshot)
        self.screenshot_thread.start()

    def send_screenshot(self):
        try:
            if self.is_screen_sharing:
                while self.is_screen_sharing:
                    screenshot = pyautogui.screenshot()
                    buffer = io.BytesIO()
                    screenshot.save(buffer, format='JPEG', quality=85)
                    data = buffer.getvalue()
                    size = len(data)
                    
                    self.client_socket.sendall(size.to_bytes(4, 'big'))
                    self.client_socket.sendall(data)
            else:
                self.send_screenshot()
                time.sleep(0.1)  # Reduce CPU usage by adding a small delay
        except Exception as e:
            print(f"Error sending screenshot: {e}")

if __name__ == "__main__":
    client = ScreenSharingClient()
