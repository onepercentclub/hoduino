#!/usr/bin/env python
import time, sys
from DDPClient import DDPClient
from board_interface import HoduinoBoardInterface
from daemon import Daemon

SERVER_URL = 'wss://stream.onepercentclub.com/websocket'
ARDUINO_PORT = '/dev/tty.usbmodem1431'
DEBUG = False
SERVO_MODE = 4

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
    """
        A listener for the arduino
    """

    def __init__(self, ddp_server_url, debug=False):
        self.shutting_down = False
        self.server_url = ddp_server_url
        self.debug = debug

        self.board_interface = HoduinoBoardInterface(port=ARDUINO_PORT)

        # Setup connection to the DDP server
        self.ddp_connect()

    def ddp_connect(self):
        print '++ DDP connection attempt...'
        self.ddp_client = DDPClient(self.server_url)
        self.ddp_client.debug = self.debug

        # Some events to handle from DDP
        self.ddp_client.on('added', self.added)
        self.ddp_client.on('connected', self.connected)
        self.ddp_client.on('socket_closed', self.closed)
        self.ddp_client.on('failed', self.failed)

        # Connect to DDP server
        self.ddp_client.connect()

    def exit(self):
        self.shutting_down = True

        # Close connect to Arduino
        if self.board_interface:
            self.board_interface.close_arduino()

        # Close connection to 
        self.ddp_client.close()

    def connected(self):
        print '++ DDP Connected'
        self.ddp_connected = True

        # Subscribe to messages stream. Limit messages to 1 as we 
        # only want the latest message.
        sub_id = self.ddp_client.subscribe('messages', [{'limit': 1}])

    def closed(self, code, reason):
        print '++ DDP connection closed {} {}'.format(code, reason)
        self.ddp_connected = False

        if not self.shutting_down:
            while not self.ddp_connected:
                self.ddp_connect()
                sleep(5)

    def failed(self, data):
        print '++ DDP failed - data: {}'.format(str(data))

    def added(self, collection, id, fields):
        print '++ DDP added {} {}'.format(collection, id)

        self.board_interface.donation_reaction()



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
