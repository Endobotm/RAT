import socketio

sio = socketio.Client()


@sio.event
def connect():
    print("[+] Connected to server")


@sio.event
def disconnect():
    print("[-] Disconnected from server")


@sio.event
def message(data):
    print(f"Server: {data}")
    send_message()


def send_message():
    msg = input("You: ")
    sio.emit("message", msg)


if __name__ == "__main__":
    sio.connect("http://localhost:5000")
    send_message()
    sio.wait()
