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


import tkinter
import socket
import threading
from tango import TangoBot
from util.enums import Direction


class NetworkControl:
    def __init__(self, window: tkinter.Tk, host, port):
        self.root = window
        self.bot = TangoBot()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

        self.rotational = 0  # steering
        self.head_swivel = 0
        self.head_tilt = 0
        self.waist_turn = 0

        self.root.bind('f', self.message_one)
        self.root.bind('w', self.message_two)

        self.thread = threading.Thread(target=self.start)
        self.thread.start()

    def __del__(self):
        self.sock.close()

    def message_one(self, event):
        self.sock.sendall(b'fuck you\n')

    def message_two(self, event):
        self.sock.sendall(b'what is my purpose?\n')

    def start(self):
        try:
            print('Entering network control')
            while True:
                command = self.sock.recv(2)

                if command:
                    command = command.decode()

                    if command == 'DF':
                        self.forward()
                    elif command == 'DS':
                        self.stop()
                    elif command == 'DB':
                        self.backward()
                    elif command in ['SL', 'SR']:
                        self.steer(command)
                    elif command in ['HU', 'HD']:
                        self.head_tilt_event(command)
                    elif command in ['HL', 'HR']:
                        self.head_swivel_event(command)
                    elif command in ['WL', 'WR']:
                        self.waist_turn_event(command)

                    print(command)

        except KeyboardInterrupt:
            print('Exiting network control')
        except socket.timeout:
            print('Server closed connection')

    def forward(self):
        self.bot.drive(0.9)

    def backward(self):
        self.bot.drive(-0.9)

    def stop(self):
        self.rotational = 0
        self.bot.drive(0)
        self.bot.steer(Direction.LEFT, 0)

    def steer(self, cmd):
        if cmd == 'SR':
            self.rotational += 0.5
        elif cmd == 'SL':
            self.rotational -= 0.5

        if self.rotational > 0.5:
            self.rotational = 0.5
        elif self.rotational < -0.5:
            self.rotational = -0.5

        direction = Direction.RIGHT if self.rotational > 0 else Direction.LEFT

        self.bot.steer(direction, abs(self.rotational))

    def head_tilt_event(self, cmd):
        if cmd == 'HU':
            self.head_tilt += 0.5
        elif cmd == 'HD':
            self.head_tilt -= 0.5

        if self.head_tilt > 1:
            self.head_tilt = 1
        elif self.head_tilt < -1:
            self.head_tilt = -1

        self.bot.tilt_head(self.head_tilt)

    def head_swivel_event(self, cmd):
        if cmd == 'HL':
            self.head_swivel += 0.5
        elif cmd == 'HR':
            self.head_swivel -= 0.5

        if self.head_swivel > 1:
            self.head_swivel = 1
        elif self.head_swivel < -1:
            self.head_swivel = -1

        self.bot.swivel_head(self.head_swivel)

    def waist_turn_event(self, cmd):
        if cmd == 'WL':
            self.waist_turn += 0.5
        elif cmd == 'WR':
            self.waist_turn -= 0.5

        if self.waist_turn > 0.5:
            self.waist_turn = 0.5
        elif self.waist_turn < -0.5:
            self.waist_turn = -0.5

        self.bot.turn_waist(self.waist_turn)
