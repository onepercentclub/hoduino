from Arduino import Arduino
import time
from Arduino.arduino import Servos


def Wave():
    print "Here we go"
    board = Arduino(baud='9600', port='/dev/ttyACM2', timeout=4)
    servos = Servos(board)
    print servos
    print "Groovy"

    servos.attach(9)
    print "Howdy"

    servos.write(9, 0)
    print servos.read(9)
    print "Groovy"

    time.sleep(1)
    servos.write(9, 90)
    print servos.read(9)


if __name__ == "__main__":
    print "Test"
    Wave()