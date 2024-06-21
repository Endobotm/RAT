import socket
import pyautogui
from PIL import Image
import io
import threading
import time

class ScreenSharingClient:
    def __init__(self, server_ip='ENDOSPC', server_port=5001):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((server_ip, server_port))
        self.is_screen_sharing = False

    def start_screen_share(self):
        self.is_screen_sharing = True
        threading.Thread(target=self.send_screenshot).start()

    def stop_screen_share(self):
        self.is_screen_sharing = False

    def send_screenshot(self):
        try:
            while self.is_screen_sharing:
                screenshot = pyautogui.screenshot()
                buffer = io.BytesIO()
                screenshot.save(buffer, format='JPEG', quality=85)
                data = buffer.getvalue()
                size = len(data)
                
                try:
                    self.client_socket.sendall(size.to_bytes(4, 'big'))
                    self.client_socket.sendall(data)
                except BlockingIOError:
                    continue

                time.sleep(0.1)  # Reduce CPU usage by adding a small delay
        except Exception as e:
            print(f"Error: {e}")
            self.client_socket.close()

if __name__ == "__main__":
    client = ScreenSharingClient()
    
    
client.start_screen_share()
