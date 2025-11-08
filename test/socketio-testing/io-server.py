import socketio
import eventlet
import eventlet.wsgi

sio = socketio.Server(async_mode="threading")
app = socketio.WSGIApp(sio)


@sio.event
def connect(sid, environ):
    print(f"[+] Client connected: {sid}")


@sio.event
def disconnect(sid):
    print(f"[-] Client disconnected: {sid}")


@sio.event
def message(sid, data):
    print(f"Client says: {data}")
    reply = input("You: ")
    sio.emit("message", reply, to=sid)


if __name__ == "__main__":
    from pyfiglet import Figlet

    f = Figlet(font="poison")
    print(
        "\033[1;31m"
        + f.renderText("The Superheated Nutsack of Doom and Despair")
        + "\033[0m"
    )
    eventlet.wsgi.server(eventlet.listen(("localhost", 5000)), app)
