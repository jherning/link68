#### Custom Serial Link ####
# Notes:
# Use this to support a custom serial link by modifying the port parameters.
# Or use this as a shell/example for an entirely new link!
# Reads and writes should block for proper functionality.
import serial
from settings import serial_port
import time
class glink:
    def __init__(self):
        print('Initializing Custom Link on ' + serial_port + ' ..')
        self.ser = serial.Serial(
            port = serial_port,
            baudrate = 9600,
            parity = serial.PARITY_NONE, # See PySerial documentation for constant options.
            stopbits = serial.STOPBITS_ONE,
            bytesize = serial.EIGHTBITS,
            xonxoff = False,
            rtscts = False,
            dsrdtr = False,
            timeout = 65 # Read timeout. The ~2s protocol timeout is not implemented.
            # Set this to a number of seconds longer needed to read 64k on your link.
            # Or just remove it for no read timeout.
            )
        #self.ser.rts = 1  # You can turn on modem control lines if needed (as with the GrayLink).
        #self.ser.dtr = 1
        time.sleep(.1)  # Give a little time for it to power up and init the lines.
                        # Remove or adjust if necessary.
        self.ser.reset_input_buffer()    # Necessary for GrayLink.
    def read(self, numbytes):
        return self.ser.read(numbytes)
    def write(self, data):  # data should be a bytearray
        self.ser.write(data)
        while self.ser.out_waiting: pass # Block until write finishes.
    def __del__(self):
        self.ser.close()
    def softreset(self):
        self.ser.reset_input_buffer()    # GrayLink sends an extra byte when it times-out.

