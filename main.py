#!/usr/bin/env python
import time, sys
from DDPClient import DDPClient
from board_interface import HoduinoBoardInterface
from daemon import Daemon

SERVER_URL = 'wss://stream.onepercentclub.com/websocket'
ARDUINO_PORT = '/dev/ttyACM0'
DEBUG = False
SERVO_MODE = 4

class HoduinoDaemon(Daemon):
    def run(self):
        # Connect to server
        print "Starting Hoduino!"
        self.hoduino = Hoduino(SERVER_URL, DEBUG)

        while True:
            try:
                 time.sleep(10)
            except KeyboardInterrupt as i:
                 pass

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
    latest_hash = None

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
        print '++ DDP connection closed {0} {1}'.format(code, reason)
        self.ddp_connected = False

        if not self.shutting_down:
            while not self.ddp_connected:
                self.ddp_connect()
                time.sleep(30)

    def failed(self, data):
        print '++ DDP failed - data: {0}'.format(str(data))

    def added(self, collection, id, fields):
        print '++ DDP added {0} {1}'.format(len(collection), id)
        if id <> self.latest_hash:
            print '++ New messages!'
            self.board_interface.donation_reaction()
            self.latest_hash = id
        else:
            print '++ No new messages'



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
