#!/usr/bin/env python
import time, sys
from DDPClient import DDPClient
from hoduinoCommandInterface import HoduinoBoardInterface
from daemon import Daemon

SERVER_URL = 'ws://127.0.0.1:3000/websocket'
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

    def __init__(self, server_url, debug=False):

        self.board_interface = HoduinoBoardInterface()

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
		if self.board_interface:
        	self.board_interface.close_arduino()

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

        self.arduinoBoardInterface.donationReaction()



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
