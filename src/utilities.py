from argparse import ArgumentParser, BooleanOptionalAction
from datetime import datetime
from os import _exit

from motor_interface import MotorInterface
from time_loop import TimeLoop

def main(): 

    motor = MotorInterface('COM5', 500000, 1)
    serial_rx = TimeLoop(0.1, motor.receive_data, False)
    serial_tx = TimeLoop(0.02, motor.send_data)
    logger = TimeLoop(0.02, motor.logger)

    while True: 
        try:
            motor.motor_loop()
        except KeyboardInterrupt: 
            motor.motor_target_power = 0
            motor.write_to_csv()
            print("logged data to csv")
            _exit(1)
