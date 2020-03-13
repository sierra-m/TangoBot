import tkinter
from input import network


HOST = '10.200.26.39'  # Standard loopback interface address (localhost)
PORT = 9090        # Port to listen on (non-privileged ports are > 1023)


window = tkinter.Tk()
input_handler = network.NetworkControl(window, HOST, PORT)

window.mainloop()
