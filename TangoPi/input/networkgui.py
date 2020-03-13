"""
MIT License

Copyright (c) 2020 Sierra MacLeod and Conner Cross

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


import socket
import threading
from tango import TangoBot
from util.enums import Direction


class NetworkControl:
    def __init__(self, host, port):
        self.bot = TangoBot()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((host, port))
        self.sock.listen(5)

        self.thread = threading.Thread(target=self.start)
        self.thread.start()

    def __del__(self):
        self.sock.close()

    def start(self):
        try:
            print('Entering network control')
            client, address = self.sock.accept()
            while True:
                command = client.recv(1024)

                if command:
                    command = command.decode()

                    print(command)

        except KeyboardInterrupt:
            print('Exiting network control')
        except socket.timeout:
            print('Server closed connection')


