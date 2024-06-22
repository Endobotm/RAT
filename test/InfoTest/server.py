import socket

def run_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_ip = "0.0.0.0"
    port = 8000
    server.bind((server_ip, port))
    server.listen(1)
    print(f"Listening on {server_ip}:{port}")
    
    client_socket, client_address = server.accept()
    print(f"Accepted connection from {client_address[0]}:{client_address[1]}")

    questions = ["IPv4", "IPv6", "IPv4 Public"]
    question_index = 0

    while True:
        request = client_socket.recv(1024).decode("utf-8")
        
        if request.lower() == "close":
            client_socket.send("closed".encode("utf-8"))
            break
        
        if request.lower() == "start":
            client_socket.send(questions[question_index].encode("utf-8"))
            continue

        if request.lower().startswith("ipv4 address:") and question_index == 0:
            print(request)
            question_index += 1
            client_socket.send(questions[question_index].encode("utf-8"))
            continue

        if request.lower().startswith("ipv6 address:") and question_index == 1:
            print(request)
            question_index += 1
            client_socket.send(questions[question_index].encode("utf-8"))
            continue

        if request.lower().startswith("ipv4 public address:") and question_index == 2:
            print(request)
            question_index += 1
            client_socket.send("All questions answered".encode("utf-8"))
            continue

        client_socket.send("unrecognized command".encode("utf-8"))

run_server()
