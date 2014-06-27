#!/usr/bin/env python

import time
import random
from pyfirmata import Arduino, util
from pyfirmata import SERVO as SERVO_MODE
from utils import Singleton

ARDUINO_PORT = '/dev/tty.usbmodem1421'
UPPER_BOUND_DEGREES = 179
LOWER_BOUND_DEGREES = 0
SLEEP_TIME = 0.5


class PinManager():
    """
        This class is responsible for the pins on the board
    """
    dig_pin_output_format = 'd:{0}:o'
    dig_pin_input_format = 'd:{0}:i'

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

        print pin_number
        if (not pin_number or (pin_number not in self.digital_pins_available)):
            pin_number = self.digital_pins_available.pop()

        print pin_number
        self.digital_pins_allocated.append(pin_number)

        return self.board.get_pin(self.dig_pin_output_format.format(pin_number))

    def set_pin_mode(self, pin, mode):
        if mode == "Servo":
            pin.mode = SERVO_MODE

class HoduinoBoardInterface():
    """
        This is the Arduino Board Interface.
        This class initialize the Board and provides all the methods
        for the interaction with it.
    """
    __metaclass__ = Singleton

    def __init__(self, port=ARDUINO_PORT):

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

    def _spin(self, degrees):
        # spin the weel
        self.motor_pin.write(degrees)
        time.sleep(SLEEP_TIME)

    def donationReaction(self):
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