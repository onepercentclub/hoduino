#!/usr/bin/env python
import time, sys
from DDPClient import DDPClient
from pyfirmata import Arduino, util
from daemon import Daemon

SERVER_URL = 'ws://127.0.0.1:3000/websocket'
ARDUINO_PORT = '/dev/tty.usbmodem1431'
DEBUG = True

class HoduinoDaemon(Daemon):
    def run(self):
        # Connect to server
        print "Starting Hoduino!"
        self.hoduino = Hoduino(SERVER_URL, DEBUG)

        while True:
            time.sleep(1)

    def exit(self):
        print "Exiting Hoduino ..." 
        try:
            self.hoduino.exit()
        except AttributeError:
            print "Why no Hoduino? :-("

class Hoduino():
    def __init__(self, server_url, debug=False):        
        # Connect to the Arduino board
        try:
            self.board = Arduino(ARDUINO_PORT)
        except OSError as e:
            raise Exception("Arduino not found on: {0}".format(ARDUINO_PORT))

        # Arduino pin for LED
        try:
            self.led_pin = self.board.get_pin('d:11:o')
        except AttributeError as e:
            # No Arduino :-(
            pass 

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
        if self.board:
            self.board.exit()

        # Close connection to 
        self.client.close()

    def connected(self):
        print '++ DDP Connected'

        # Subscribe to messages stream. Limit messages to 1 as we 
        # only want the latest message.
        sub_id = self.client.subscribe('messages', [{'limit': 1}])

    def closed(self, code, reason):
        print '++ DDP connection closed {} {}'.format(code, reason)

    def failed(self, data):
        print '++ DDP failed - data: {}'.format(str(data))

    def added(self, collection, id, fields):
        print '++ DDP added {} {}'.format(collection, id)

        # Light the LED when a message is added
        self._flash_led()

    def _flash_led(self):
        try:
            self.led_pin.write(1)
            time.sleep(2)
            self.led_pin.write(0)
        except AttributeError:
            print "** Pin not accessible"


if __name__ == "__main__":
    daemon = HoduinoDaemon('/tmp/daemon-hoduino.pid')

    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)
