import socket
import subprocess

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = "ENDOSPC"
port = 5425

client_socket.connect((host, port))

while True:
    command = client_socket.recv(1024)
    command = command.decode("utf-8")
    if command == "message":
        client_socket.send("Fuck you from the client".encode("utf-8"))
    if command == "quit":
        client_socket.close()
        break