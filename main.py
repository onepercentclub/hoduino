#!/usr/bin/env python

from DDPClient import DDPClient

SERVER_URL = 'ws://127.0.0.1:3000/websocket'
DEBUG = True


class Hoduino():
    def __init__(self, server_url, debug=False):
        self.client = DDPClient(server_url)
        self.client.debug = debug

        # Some events to handle
        self.client.on('added', self.added)
        self.client.on('connected', self.connected)
        self.client.on('socket_closed', self.closed)
        self.client.on('failed', self.failed)

        self.client.connect()

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

def main():
    # Connect to server
    Hoduino(SERVER_URL, DEBUG)

if __name__ == "__main__":
    try:
        main()
    except:
        import sys
        print sys.exc_info()[0]
        import traceback
        print traceback.format_exc()
    finally:
        print "Press Enter to quit ..." 
        raw_input()
