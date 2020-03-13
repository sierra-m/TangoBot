import tkinter
from input import networkgui


HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 9090        # Port to listen on (non-privileged ports are > 1023)


input_handler = networkgui.NetworkControl(HOST, PORT)

input_handler.start()
