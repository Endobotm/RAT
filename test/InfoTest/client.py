import socket

def run_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_ip = "127.0.0.1"  # Replace with the actual server IP
    server_port = 8000
    client.connect((server_ip, server_port))

    client.send("start".encode("utf-8"))

    while True:
        response = client.recv(1024).decode("utf-8")
        print(f"Received: {response}")

        if response.lower() == "closed":
            break
        if response.lower() == "ipv4":
            msg = "ipv4 address: hello"
            client.send(msg.encode("utf-8"))
            continue

        if response.lower() == "ipv6":
            msg = "ipv6 address: hello"
            client.send(msg.encode("utf-8"))
            continue

        if response.lower() == "ipv4 public":
            msg = "ipv4 public address: hello"
            client.send(msg.encode("utf-8"))
            continue
        
        if response.lower() == "all questions answered":
            print("All questions have been answered.")

run_client()
