from argparse import ArgumentParser, BooleanOptionalAction
from datetime import datetime
from os import _exit

from motor_interface import MotorInterface
from time_loop import TimeLoop
from motor_ui import MotorControlUI
from data import SharedData
from data_manager import DataManager

def main(): 
    try:
        # Create a shared data manager
        data_manager = DataManager(SharedData())

        serial_port = None # TODO: add serial port

        motor_interface = MotorInterface(serial_port, data_manager)
        # serial_rx = TimeLoop(0.1, motor_interface.receive_data, False)
        serial_tx = TimeLoop(0.1, motor_interface.send_data)
        # logger = TimeLoop(0.02, motor_interface.logger)

        MotorControlUI(data_manager).mainloop()

    except KeyboardInterrupt: 
        # motor_interface.motor_target_power = 0
        # motor_interface.write_to_csv()
        # print("logged data to csv")
        _exit(1)

if __name__ == '__main__':
    main()