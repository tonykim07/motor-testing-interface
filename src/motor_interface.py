
from time import time
from serial import Serial
from csv import writer
from socket import htons
import numpy as np
from enum import Enum
from data import MotorStates, SharedData
from data_manager import DataManager

# Packet Info
START_BYTE = 0xA5
PAYLOAD_LENGTH = 12
DCMB_ID = 0x4
SEQUENCE_NUM = 0
DCMB_MOTOR_CONTROL_STATE_ID = 0x05

# CRC
NUM_BYTES_IN_WORD = 4

class rxPacketIDs(Enum): 
    MCMB_BUS_METRICS_ID = 0
    MCMB_CAR_SPEED = 1
    MCMB_MOTOR_TEMPERATURE_ID = 2
        
class MotorInterface(): 

    def __init__(self, serial_port, data_manager: DataManager[SharedData]):

        self.serial_port = serial_port
        self.data_manager = data_manager

        self.motor_state = MotorStates.OFF.value
        self.motor_target_power = 0
        self.motor_target_speed = 0
        self.direction = 0 
        self.vfm_up_state = 0
        self.vfm_down_state = 0
        self.eco_power_state = 0
        self.digital_buttons = 0

        self.vfm_position = 0
        self.live_voltage = 0
        self.live_current = 0
        self.live_temperature = 0
        self.live_rpm = 0

        self.voltage = []
        self.current = []
        self.temperature = []
        self.rpm = []
        self.timestamps = []

        self.log_data = {
            "voltage": True, 
            "current": True,
            "temperature": True,
            "rpm": True
        }

        self.start_time = time()
        self.start = False
        self.packet = None

    def set_motor_direction(self, direction): 
        self.direction = direction
    
    def set_motor_target_power(self, target): 
        self.motor_target_power = target

    def set_motor_target_speed(self, speed): 
        self.motor_target_speed = speed

    def logger(self): 

        if self.start == True: 
            self.start_time = time()
            self.start = False
        
        if self.log_data["voltage"] == True: 
            self.voltage.append(self.live_voltage)
        if self.log_data["current"] == True:
            self.current.append(self.live_current)
        if self.log_data["temperature"] == True:
            self.temperature.append(self.live_temperature)
        if self.log_data["rpm"] == True:
            self.rpm.append(self.live_rpm)
        
        self.timestamps.append(round((time() - self.start_time), 4))

    def write_to_csv(self):

        with open('motor_test.csv', mode='w', newline='') as file:

            write = writer(file, delimiter=',')
            write.writerow(["Timestamp", "PSM Voltage", "PSM Current", "Motor Temperature", "RPM"])

            for i in range(len(self.timestamps)): 
                row = [self.timestamps[i]]
                if self.log_data["voltage"] == True: 
                    row.append(self.voltage[i])
                else:
                    row.append("N/A")
                if self.log_data["current"] == True:
                    row.append(self.current[i])
                else:
                    row.append("N/A")
                if self.log_data["temperature"] == True:
                    row.append(self.temperature[i])
                else:
                    row.append("N/A")
                if self.log_data["rpm"] == True:
                    row.append(self.rpm[i])
                else:
                    row.append("N/A")

                write.writerow(row)


    def send_data(self):

        # self.motor_target_power = htons(self.motor_target_power)
        with self.data_manager.read() as data:
            self.digital_buttons = (data.motor_direction << 3) | data.motor_eco_power_state


            self.packet = [START_BYTE, PAYLOAD_LENGTH, DCMB_ID, SEQUENCE_NUM, 
                        DCMB_MOTOR_CONTROL_STATE_ID, data.motor_state, self.digital_buttons, data.motor_vfm_position, 
                        data.motor_target_power, 0, 0, 0,
                        self.motor_target_speed, 0, 0, 0]
        
        crc = self.calculate_crc(self.packet, PAYLOAD_LENGTH)
        self.packet += crc
        # print(bytes(self.packet).hex())
        if self.serial_port != None:
            self.serial_port.write(bytearray(self.packet))

    def receive_data(self, print_flag):
        if self.serial_port != None:
            data_buffer = self.serial_port.readline().decode('ascii').strip()

        # read temperature, voltage, current, speed
        if print_flag == True: 
            print(data_buffer)

        # parse the data...

    def crc32(self, crc, data):
        crc = crc ^ data
        for i in range(32):
            if crc & 0x80000000:
                crc = (crc << 1) ^ 0x04C11DB7
            else:
                crc = crc << 1

        return crc
    
    def crc32Block(self, crc, size, data):
        for i in range(size):
            crc = self.crc32(crc, data[i])
            
        return crc
    
    def calculate_crc(self, crc_bytes, payload_length):

        num_elements = len(crc_bytes[0:4+payload_length])
        if (num_elements % NUM_BYTES_IN_WORD != 0):
            return np.zeros(4)

        num_words = int(num_elements / NUM_BYTES_IN_WORD)
        uint32_value = [((crc_bytes[i]) + (crc_bytes[i+1] << 8) + (crc_bytes[i+2] << 16) + (crc_bytes[i+3] << 24)) for i in range(0, num_elements, 4)]

        raw = self.crc32Block(0xFFFFFFFF, num_words, uint32_value)
        raw = raw ^ 0xFFFFFFFF
        
        crc = [(raw >> 24) & 0xFF, (raw >> 16) & 0xFF, (raw >> 8) & 0xFF, raw & 0xFF]
        return crc

    def motor_loop(self): 
        pass
        # user_input = input()
        # parse_message = user_input.split()

        # # example message: motor power 5
        # if "power" in user_input:
        #     if int(parse_message[2]) >= 0 or int(parse_message[2]) < 256:
        #         self.motor_target_power = int(parse_message[2])
        #     else:
        #         print("Value out of range")

        # elif "vfm up" in user_input:     
        #     self.vfm_up_state = 1 
        #     self.vfm_position += 1
        
        # elif "vfm down" in user_input: 
        #     self.vfm_down_state = 1
        #     if self.vfm_position > 0: 
        #         self.vfm_position -= 1
        
        # elif "eco mode" in user_input: 
        #     self.eco_power_state = 1
        
        # elif "normal mode" in user_input:
        #     self.eco_power_state = 0

        # elif "shutdown" in user_input:
        #     self.motor_target_power = 0
        #     self.motor_target_speed = 0
        
        # elif "print tx" in user_input: 
        #     print(self.packet)
        
