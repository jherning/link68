#### BlackLink ####
# Notes:
# Bit-Banging for BlackLink based on flowcharts in hardware.html
#   and $4 link schematic in cable.html of Link Guide.
#   Currently UNTESTED on a real UART!
# RTS: pull RED line
# CTS: read RED line
# DTR: pull WHITE line
# DSR: read WHITE line
import time     # For timeouts 
import serial
from settings import serial_port, TI_92_init
class glink:
    def __init__(self):
        print('Initializing BlackLink on ' + serial_port + ' ..')
        self.ser = serial.Serial()
        self.ser.port = serial_port
        self.ser.baudrate=9600
        self.ser.parity=serial.PARITY_NONE
        self.ser.stopbits=serial.STOPBITS_ONE
        self.ser.bytesize=serial.EIGHTBITS
        if not TI_92_init: # 89/92+ like a "reset" cycle. 92 seems to not like it..
            self.ser.rts=0 # Signal "reset" state.
            self.ser.dtr=0 # In order to set simultaneously w/ pySerial we have to set then open
            self.ser.open()
            while (self.ser.cts or self.ser.dsr): continue # Busy wait low lines
            time.sleep(0.01) # >= 0.003 found to work well by trial and error. OS delay?
            self.ser.close()  # Reset time should be ~250us according to LG.
        self.ser.rts=1 # Set initial high state
        self.ser.dtr=1
        self.ser.open()
        while not (self.ser.dsr and self.ser.cts): continue  # Wait for initial state.

    def read(self, numbytes):
        data = bytearray()
        for bytenum in range(0, numbytes):
            byte = 0
            for mask in [1, 2, 4, 8, 16, 32, 64, 128]:
                tic = time.perf_counter()
                while (self.ser.cts and self.ser.dsr):  # Busy wait for a pull low
                    if time.perf_counter() - tic > 2.1:
                        print('Link read timeout. Byte ' + str(bytenum) + '  Mask: ' + str(mask))
                        quit()
                if self.ser.cts:                           # If R=1 it's W=0
                    bit = 1                     
                    self.ser.rts = 0                        # R = 0
                    while not self.ser.dsr: continue        # Wait for W = 1
                    self.ser.rts = 1                        # R = 1
                else:
                    bit = 0
                    self.ser.dtr = 0                        # W = 0
                    while not self.ser.cts: continue       # Wait for R = 1
                    self.ser.dtr = 1                        # W = 1
                byte += mask * bit
            data.extend(byte.to_bytes(1,byteorder='little')) # Add byte to data.
        return data
    def write(self, data):  # data should be a bytearray
        for byte in data:
            for mask in [1, 2, 4, 8, 16, 32, 64, 128]:
                tic = time.perf_counter()
                while (not self.ser.cts or not self.ser.dsr):  # Busy wait high lines
                    if time.perf_counter() - tic > 2.1:
                        print('Link write timeout. Mask: ' + str(mask))
                        quit()
                if int(byte) & mask:
                    bit = 1
                else:
                    bit = 0
                if (bit):                           # bit == 1
                    self.ser.dtr = 0                # Set W=0
                    while self.ser.cts: continue    # Wait for R = 0
                    self.ser.dtr = 1                # Set W=1
                    while not self.ser.cts: continue    # Wait for R = 1
                else:                               # bit == 0
                    self.ser.rts = 0                # Set R=0
                    while self.ser.dsr: continue        # Wait for W = 0
                    self.ser.rts = 1                # Set R=1
                    while not self.ser.dsr: continue   # Wait for W = 1
    def __del__(self):
        self.ser.close()
        self.ser.dtr = 0
        self.ser.rts = 0
        self.ser.open()
        self.ser.close()
    def softreset(self):
        return
