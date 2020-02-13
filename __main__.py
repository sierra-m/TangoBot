import tkinter
from input import keyboard


window = tkinter.Tk()
input_handler = keyboard.KeyboardControl(window)

window.mainloop()
