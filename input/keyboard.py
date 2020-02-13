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
from ..tango import TangoBot


class KeyboardControl:
    def __init__(self, window: tkinter.Tk):
        self.root = window
        self.bot = TangoBot()

        self.velocity = 0  # driving
        self.rotational = 0  # steering
        self.head_swivel = 0
        self.head_tilt = 0
        self.waist_turn = 0

        self.root.bind('<Up>', self.drive_event)
        self.root.bind('<Down>', self.drive_event)

        self.root.bind('<Left>', self.steer_event)
        self.root.bind('<Right>', self.steer_event)

        self.root.bind('<Space>', self.stop_event)

        self.root.bind('q', self.head_swivel_event)
        self.root.bind('e', self.head_swivel_event)

        self.root.bind('r', self.head_tilt_event)
        self.root.bind('f', self.head_tilt_event)

        self.root.bind('a', self.waist_turn_event)
        self.root.bind('s', self.waist_turn_event)
        self.root.bind('d', self.waist_turn_event)

    # Seven speeds total
    def drive_event(self, event):
        if event.keysym == 'Up':
            self.velocity += 0.2
        elif event.keysym == 'Down':
            self.velocity -= 0.2

        if self.velocity > 0.6:
            self.velocity = 0.6
        elif self.velocity < -0.6:
            self.velocity = -0.6

        self.bot.drive(self.velocity)

    def steer_event(self, event):
        pass

    def stop_event(self, event):
        self.velocity = 0
        self.bot.drive(self.velocity)

    # Five degrees of freedom
    def head_swivel_event(self, event):
        if event.char == 'q':
            self.head_swivel += 0.5
        elif event.char == 'e':
            self.head_swivel -= 0.5

        if self.head_swivel > 1:
            self.head_swivel = 1
        elif self.head_swivel < -1:
            self.head_swivel = -1

        self.bot.swivel_head(self.head_swivel)

    def head_tilt_event(self, event):
        pass

    def waist_turn_event(self, event):
        pass
