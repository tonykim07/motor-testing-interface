
import tkinter as tk
from tkinter import ttk
import threading
import serial
from os import path
import time


# details
# upload drive profiles (potentiometer values or if there are ways to target specific speed)
# motor and dyno synchronization
# interface with a bunch of buttons for control 
# slider for accel and regen?
# data logging, plots, etc.
# emergency shut off, etc.
# also add controls via the terminal -> have option for it
# class for gui 
# class for data stuff?
# read data from system -> motor power, target power, etc. (all read over uart)

class MotorGUI(tk.TK): 

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.title('Motor Testing Interface')
        self.geometry("300x100")

        main_frame = ttk.Frame(self)
        main_frame.grid(column=0, row=0, sticky='nsew')
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, pad=100)

    def show_frame(): 
        pass


class MainFrame(ttk.Frame): 
    
    def __init__(self, parent, controller) -> None: 
        super().__init__(parent)




