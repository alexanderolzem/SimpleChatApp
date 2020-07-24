import socket
# import select
import errno
import sys
from tkinter import *
import tkinter.scrolledtext as tkscroll

HEADER_LENGTH = 10

# Server
PORT = 9090
s = None

def add_to_chatbox(msg):
    global out_chat
    out_chat['state'] = 'normal'
    out_chat.insert('end', f"{msg}\n")
    out_chat.see(END)
    out_chat['state'] = 'disabled'

def btn_connect_click():
    global s

    IP = txt_ip.get()
    my_username = txt_user.get()

    if IP and my_username:
        txt_ip['state'] = 'disabled'
        txt_user['state'] = 'disabled'
        btn_connect['state'] = 'disabled'

        # Setup Socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((IP, PORT))
        s.setblocking(False)

        # Communicate Username
        username = my_username.encode('utf-8')
        username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
        s.send(username_header + username)

        btn_send['state'] = 'normal'
        txt_message['state'] = 'normal'
    else:
        s = None

def btn_send_click(event=None):
    global s
    if not s:
        pass
    message = txt_message.get()
    if message:
        msg = message.encode('utf-8')
        msg_header = f"{len(msg):<{HEADER_LENGTH}}".encode('utf-8')
        s.send(msg_header + msg)
        add_to_chatbox(f"You > {message}")
        txt_message.delete(0, 'end')


root = Tk()
root.title("Simple Chat App")
root.bind('<Return>', btn_send_click)

lbl_ip = Label(root, text="IP:")
lbl_user = Label(root, text="Username:")
txt_ip = Entry(root, width=25)
txt_user = Entry(root, width=25)
txt_message = Entry(root, width=64, state=DISABLED)
btn_connect = Button(root, text="Connect", command=btn_connect_click)
btn_send = Button(root, text="Send", command=btn_send_click, state=DISABLED)
lbl_chat = Label(root, text="Chat:")
out_chat = tkscroll.ScrolledText(root)

lbl_ip.grid(row=0, column=0)
txt_ip.grid(row=0, column=1)
txt_ip.insert(0, "192.168.178.28")

lbl_user.grid(row=0, column=2)
txt_user.grid(row=0, column=3)
txt_user.insert(0, "alex")

btn_connect.grid(row=0, column=5)

lbl_chat.grid(row=1, column=0)
out_chat.grid(row=2, column=0, columnspan=6)
out_chat.config(state=DISABLED)

txt_message.grid(row=3, column=0, columnspan=5)
btn_send.grid(row=3, column=5)

# Main Loop
while True:
    root.update()
    if not s:
        continue
    # Update the chat
    try:
        while True:
            # receive things
            username_header = s.recv(HEADER_LENGTH)
            if not len(username_header):
                print("Connection closed by Server")
                sys.exit()
            username_length = int(username_header.decode('utf-8').strip())
            username = s.recv(username_length).decode('utf-8')

            message_header = s.recv(HEADER_LENGTH)
            message_length = int(message_header.decode('utf-8').strip())
            message = s.recv(message_length).decode('utf-8')

            add_to_chatbox(f"{username} > {message}")

    except IOError as e:
        if e.errno != errno.EAGAIN or e.errno != errno.EWOULDBLOCK:
            print("Reading Error", str(e))
            sys.exit()
        continue

    except Exception as e:
        print("General error", str(e))
        sys.exit()
