#### GrayLink ####
# Notes:
# The GrayLink is pretty self-explanatory.
# 9600 baud, no flow control. Powered by RTS & DTR lines.
import serial
from settings import serial_port
import time
class glink:
    def __init__(self):
        print('Initializing GrayLink on ' + serial_port + ' ..')
        self.ser = serial.Serial(
            port = serial_port,
            baudrate = 9600,
            parity = serial.PARITY_NONE,
            stopbits = serial.STOPBITS_ONE,
            bytesize = serial.EIGHTBITS,
            xonxoff = False,
            rtscts = False,
            dsrdtr = False,
            timeout = 65 # Read timeout. Might get 64k@9600 baud.
            )
        self.ser.rts = 1  # RTS & DTR power the GrayLink
        self.ser.dtr = 1
        time.sleep(.1)  # Give a little time for it to power up and init the lines.
        self.ser.reset_input_buffer()    # Seems to be necessary.
    def read(self, numbytes):
        return self.ser.read(numbytes)
    def write(self, data):  # data should be a bytearray
        self.ser.write(data)
        while self.ser.out_waiting: pass # Block until write finishes.
    def __del__(self):
        self.ser.close()
    def softreset(self):
        self.ser.reset_input_buffer()    # Clear byte read after SKP.

