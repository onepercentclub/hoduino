#!/usr/bin/env python
import time
from DDPClient import DDPClient
from pyfirmata import Arduino, util

SERVER_URL = 'ws://127.0.0.1:3000/websocket'
ARDUINO_PORT = '/dev/tty.usbmodem1431'
DEBUG = False


class Hoduino():
    def __init__(self, server_url, debug=False):        
        # Connect to the Arduino board
        self.board = Arduino(ARDUINO_PORT)

        # Arduino pin for LED
        self.led_pin = self.board.get_pin('d:11:o')

        # Setup connection to the DDP server
        self.client = DDPClient(server_url)
        self.client.debug = debug

        # Some events to handle from DDP
        self.client.on('added', self.added)
        self.client.on('connected', self.connected)
        self.client.on('socket_closed', self.closed)
        self.client.on('failed', self.failed)

        # Connect to DDP server
        self.client.connect()

    def exit(self):
        # Close connect to Arduino
        self.board.exit()

        # Close connection to 
        self.client.close()

    def connected(self):
        print '* CONNECTED'

        # Subscribe to messages stream. Limit messages to 1 as we 
        # only want the latest message.
        sub_id = self.client.subscribe('messages', [{'limit': 1}])

    def closed(self, code, reason):
        print '* CONNECTION CLOSED {} {}'.format(code, reason)

    def failed(self, data):
        print '* FAILED - data: {}'.format(str(data))

    def added(self, collection, id, fields):
        print '* ADDED {} {}'.format(collection, id)
        for key, value in fields.items():
            print '  - FIELD {} {}'.format(key, value)

        # Light the LED when a message is added
        self._flash_led()

    def _flash_led(self):
        self.led_pin.write(1)
        time.sleep(2)
        self.led_pin.write(0)

def main():
    # Connect to server
    hoduino = Hoduino(SERVER_URL, DEBUG)

    print "Press Enter to quit ..." 
    raw_input()

    print "Exiting hoduino ..." 
    hoduino.exit()

if __name__ == "__main__":
    try:
        main()
    except:
        import sys
        print sys.exc_info()[0]
        import traceback
        print traceback.format_exc()
