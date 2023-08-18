import tkinter as tk
import serial
import threading
import time
from os import path
from data_manager import DataManager
from data import MotorStates, MotorDirection, SharedData, EcoPowerState


LIGHTBLUE1 = '#8FA5BF'
LIGHTBLUE2 = '#8FB0BF'
WINDOW_WIDTH = 450
WINDOW_HEIGHT = 300
BLUEISH = '#356885'


class MotorControlUI:
    def __init__(self, data_manager: DataManager[SharedData]):
        self.data_manager = data_manager

        self.button_width = 100
        self.label_width = 40
        self.is_motor_on = False
        self.is_forward = True
        self.accel_value = 0
        self.regen_value = 0
        self.is_accel_turn = True
        self.vfm_count = 0
        self.last_button_press_time = time.time()

        root_window = tk.Tk()
        root_window.title('MotorControl')
        root_window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        root_window['background'] = BLUEISH
        file_path = path.dirname(__file__).replace("\\", "/")
        root_window.iconbitmap(path.join(file_path, 'icon.ico'))
        self.root_window = root_window

        
        self._init_ui_elements()
        self._layout_ui_elements()

    def mainloop(self):
        self.root_window.mainloop()

    def _init_ui_elements(self):
        self.main_button = self._create_button("MAIN", self._toggle_motor)
        self.main_label = self._create_label("OFF")
        
        self.direction_button = self._create_button("FwdRev", self._toggle_direction)
        self.direction_label = self._create_label("FWD")

        self.accel_slider = self._create_slider(self._accel_slider_callback)
        self.accel_label = self._create_label("Accel")
        # self.accel_send_button = self._create_button("Send", self._send_accel_value)

        self.regen_slider = self._create_slider(self._regen_slider_callback)
        self.regen_label = self._create_label("Regen")
        # self.regen_send_button = self._create_button("Send", self._send_regen_value)

        self.vfm_up_button = self._create_button("VFM \n\nUP", self._increment_vfm)
        self.vfm_down_button = self._create_button("VFM \n\nDOWN", self._decrement_vfm)
        self.vfm_label = self._create_label(str(self.vfm_count))

        # create eco power button under vfm buttons. Make it the same type as main button
        self.eco_power_button = self._create_button("ECO POWER", self._toggle_eco_power)
        self.eco_power_label = self._create_label("ECO")


    def _create_button(self, text, callback):
        return tk.Button(self.root_window, text=text, command=callback, 
                        background=LIGHTBLUE2, foreground='white', 
                        font=('Fixedsys', 12), borderwidth=3)

    def _create_label(self, text):
        return tk.Label(self.root_window, text=text, font=('Fixedsys', 12), 
                        bg='black', foreground='yellow')

    def _create_slider(self, callback):
        return tk.Scale(self.root_window, from_=255, to=0, bg=LIGHTBLUE1, 
                        foreground='black', command=callback)

    def _layout_ui_elements(self):
        left_column = 40
        right_column = left_column + self.button_width + 10
        slider_column = 250
        slider_width = 45

        self.main_button.place(x=left_column, y=50, width=self.button_width)
        self.main_label.place(x=right_column, y=50, width=self.label_width+5)

        self.direction_button.place(x=left_column, y=100, width=self.button_width)
        self.direction_label.place(x=right_column, y=100, width=self.label_width+5)

        self.accel_slider.place(x=slider_column, y=50, width=slider_width)
        # self.accel_send_button.place(x=slider_column, y=170, width=slider_width)
        self.accel_label.place(x=slider_column, y=200)

        slider_column2 = 340
        self.regen_slider.place(x=slider_column2, y=50, width=slider_width)
        # self.regen_send_button.place(x=slider_column2, y=170, width=slider_width)
        self.regen_label.place(x=slider_column2, y=200)

        self.vfm_down_button.place(x=left_column, y=155)
        self.vfm_label.place(x=(right_column - left_column), y=165)
        self.vfm_up_button.place(x=right_column, y=155)

        self.eco_power_button.place(x=left_column, y=245, width=self.button_width)
        self.eco_power_label.place(x=right_column, y=245, width=self.label_width+5)

    def _toggle_motor(self):
        if time.time() - self.last_button_press_time < 1:
            return
        self.last_button_press_time = time.time()
        if not self.is_motor_on:
            self.is_motor_on = True
            self.main_label.config(text="ON")
            with self.data_manager.write() as data:
                data.motor_state = MotorStates.STANDBY.value
        else:
            self.is_motor_on = False
            self.main_label.config(text="OFF")
            with self.data_manager.write() as data:
                data.motor_state = MotorStates.OFF.value

    def _toggle_direction(self):
        if self.is_forward:
            self.direction_label.config(text="REV")
            self.is_forward = False
            with self.data_manager.write() as data:
                data.motor_direction = MotorDirection.REV.value
        else:
            self.direction_label.config(text="FWD")
            self.is_forward = True
            with self.data_manager.write() as data:
                data.motor_direction = MotorDirection.FWD.value

    def _accel_slider_callback(self, value):
        self.accel_value = int(value)
        if self.regen_value > 0:
            self.regen_value = 0
            self.regen_slider.set(0)
        with self.data_manager.write() as data:
            if self.accel_value > 0:
                data.motor_state = MotorStates.PEDAL.value
            else:
                data.motor_state = MotorStates.STANDBY.value
            data.motor_target_power = self.accel_value

    def _send_accel_value(self): # not used
        pass

    def _regen_slider_callback(self, value):
        self.regen_value = int(value)
        if self.accel_value > 0:
            self.accel_value = 0
            self.accel_slider.set(0)
        with self.data_manager.write() as data:
            if self.regen_value > 0 and self.accel_value == 0:
                data.motor_state = MotorStates.REGEN.value
            else:
                data.motor_state = MotorStates.STANDBY.value
            data.motor_target_power = self.regen_value

    def _send_regen_value(self): # not used
        pass

    def _increment_vfm(self):
        if self.vfm_count < 8:
            self.vfm_count += 1
            self.vfm_label.config(text=str(self.vfm_count))
            with self.data_manager.write() as data:
                data.motor_vfm_position = self.vfm_count

    def _decrement_vfm(self):
        if self.vfm_count > 0:
            self.vfm_count -= 1
            self.vfm_label.config(text=str(self.vfm_count))
            with self.data_manager.write() as data:
                data.motor_vfm_position = self.vfm_count
    
    def _toggle_eco_power(self):
        if time.time() - self.last_button_press_time < 1:
            return
        self.last_button_press_time = time.time()
        if self.eco_power_label.cget('text') == "POWER":
            self.eco_power_label.config(text="ECO")
            with self.data_manager.write() as data:
                data.motor_eco_power_state = EcoPowerState.ECO.value
        else:
            self.eco_power_label.config(text="POWER")
            with self.data_manager.write() as data:
                data.motor_eco_power_state = EcoPowerState.POWER.value

