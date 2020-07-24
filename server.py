import socket
import select

HEADER_LENGTH = 10
IP = str(socket.gethostbyname(socket.getfqdn()))
PORT = 9090

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

s.bind((IP, PORT))

s.listen()
print(f"Server is running on {IP}")

sockets_list = [s]

clients = {}

def recv_msg(client_socket):
    try:
        msg_header = client_socket.recv(HEADER_LENGTH)
        if not len(msg_header):
            print(f"{client_socket} disconnected")
            return False
        msg_length = int(msg_header.decode("utf-8").strip())
        return {"header": msg_header, "data": client_socket.recv(msg_length)}
    except:
        return False


while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    for notified_socket in read_sockets:
        if notified_socket == s:
            client_socket, client_address = s.accept()

            user = recv_msg(client_socket)
            if user == False:
                continue
            sockets_list.append(client_socket)
            clients[client_socket] = user

            # Inform user that he is connected
            username = "Server"
            reply = f"Connected to {IP}, welcome to the Chat!\n"

            user = {
                "header": f"{len(username):<{HEADER_LENGTH}}".encode('utf-8'),
                "data": str(username).encode('utf-8')
            }
            message = {
                "header": f"{len(reply):<{HEADER_LENGTH}}".encode('utf-8'),
                "data": reply.encode('utf-8')
            }
            client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

            # Logging
            print(f"{user['data'].decode('utf-8')} connected from {client_address[0]}:{client_address[1]}")
        else:
            message = recv_msg(notified_socket)
            if message == False:
                print(f"{clients[notified_socket]['data'].decode('utf-8')} closed Connection")
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue
            user = clients[notified_socket]

            # Broadcast the message
            for client_socket in clients:
                if client_socket != notified_socket:
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

            # Logging
            print(f"Received message from {user['data'].decode('utf-8')}: {message['data'].decode('utf-8')}")

    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients[notified_socket]
