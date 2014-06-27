#!/usr/bin/env python

import time
import random
from pyfirmata import Arduino, util
from pyfirmata import SERVO as SERVO_MODE, PWM as PWM_MODE, OUTPUT as OUTPUT_MODE
from utils import Singleton

UPPER_BOUND_DEGREES = 179
LOWER_BOUND_DEGREES = 0
SLEEP_TIME = 0.5


class PinManager():
    """
        This class is responsible for the pins on the board
    """
    dig_pin_output_format = 'd:{0}:o'
    dig_pin_input_format = 'd:{0}:i'

    analog_pin_output_format = 'a:{0}:o'
    analog_pin_input_format = 'a:{0}:i'

    digital_pins_available = []
    analog_pins_available = []

    digital_pins_allocated = []
    analog_pins_allocated = []

    __metaclass__ = Singleton

    def __init__(self, board):

        self.board = board
        self.digital_pins_available = [x for x in range(2, 13)]
        self.analog_pins_available = [x for x in range(6)]

    def get_digital_pin_out(self, pin_number=None):
        if (not pin_number or (pin_number not in self.digital_pins_available)):
            pin_number = self.digital_pins_available.pop()

        self.digital_pins_allocated.append(pin_number)

        return self.board.get_pin(self.dig_pin_output_format.format(pin_number))

    def get_analog_pin_out(self, pin_number=None):
        if (not pin_number or (pin_number not in self.analog_pins_available)):
            pin_number = self.analog_pins_available.pop()

        self.analog_pins_allocated.append(pin_number)

        return self.board.get_pin(self.analog_pin_output_format.format(pin_number))

    def set_pin_mode(self, pin, mode):
        if mode == "Servo":
            pin.mode = SERVO_MODE
        elif mode == "PWM":
            pin.mode = PWM_MODE
        elif mode == "OUTPUT":
            pin.mode = OUTPUT_MODE

class HoduinoBoardInterface():
    """
        This is the Arduino Board Interface.
        This class initialize the Board and provides all the methods
        for the interaction with it.
    """
    __metaclass__ = Singleton

    def __init__(self, port):

        try:
            self.board = Arduino(port)
        except OSError as e:
            raise Exception("Arduino not found on: {0}".format(port))
        self._setup()

    def _setup(self):
        # Setup the pins
        self.pin_manager = PinManager(self.board)

        self.motor_pin = self.pin_manager.get_digital_pin_out(9)
        self.pin_manager.set_pin_mode(self.motor_pin, "Servo")

        self.buzzer_pin = self.pin_manager.get_digital_pin_out(3)
        self.pin_manager.set_pin_mode(self.buzzer_pin, "PWM")

    def _spin(self, degrees):
        # spin the weel
        self.motor_pin.write(degrees)
        time.sleep(SLEEP_TIME)

    def _buzzer(self, value):
        self.buzzer_pin.write(value)
        time.sleep(SLEEP_TIME)
        self.buzzer_pin.write(0.0)

    def _melody(self):
        notes = {
            'c': 62, 
            'd': 94, 
            'e': 30, 
            'f': 49, 
            'g': 50, 
            'a': 140, 
            'b': 194, 
            'C': 223
          }

        freqs = ['c', 'g', 'a', 'a', 'f', 'e']

        for f in freqs:
            self.buzzer_pin.write(notes[f]/255.0)
            time.sleep(0.2)

        self.buzzer_pin.write(0.0)

    def donation_reaction(self):
        # buzzer
        # self._melody()

        # spin procedure for donation reaction
        self._spin(90)
        self._spin(150)
        self._spin(30)
        self._spin(150)
        self._spin(30)
        self._spin(90)

    def close_arduino(self):
        self._exit()

    def _exit(self):
        try:
            self.board.exit()
            print "Succesfully exit from arduino board"
        except:
            print "Error while exiting arduino board"