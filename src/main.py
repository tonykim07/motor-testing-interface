from argparse import ArgumentParser, BooleanOptionalAction
from datetime import datetime
from os import _exit

from motor import Motor
from time_loop import TimeLoop
from motor_ui import MotorControlUI
from data import SharedData
from data_manager import DataManager
from serial import Serial

def main(): 
    try:
        data_manager = DataManager(SharedData())

        serial_port = Serial(port="COM4", baudrate=115200, timeout=1) 

        motor_interface = Motor(serial_port, data_manager)
        # serial_rx = TimeLoop(0.1, motor_interface.receive_data, False)
        serial_tx = TimeLoop(0.5, motor_interface.send_data)

        ui = MotorControlUI(data_manager)
        ui.mainloop()

    finally:
        # This code will always run after the mainloop, even if the window is closed
        # motor_interface.motor_target_power = 0
        # motor_interface.write_to_csv()
        # print("logged data to csv")
        serial_tx.stop_loop()
        print("stopped serial tx loop")
        print("shutting down motor")
        motor_interface.shut_down_motor()
        _exit(1)

if __name__ == '__main__':
    main()