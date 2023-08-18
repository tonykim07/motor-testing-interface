from dataclasses import dataclass, field
from enum import Enum
from data_manager import DataManager

class MotorStates(Enum):
	OFF = 0
	PEDAL = 1
	CRUISE = 2
	REGEN = 3
	STANDBY = 4
        
class MotorDirection(Enum):
    FWD = 0
    REV = 1

class EcoPowerState(Enum):
    ECO = 0
    POWER = 1

@dataclass
class SharedData:
    motor_target_power: int = 0
    motor_state: int = MotorStates.OFF.value
    motor_target_speed: int = 0
    motor_direction: int = MotorDirection.FWD.value
    motor_vfm_position: int = 0
    motor_eco_power_state: int = EcoPowerState.ECO.value



