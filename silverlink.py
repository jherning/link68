#### SilverLink ####
# Notes:
# idVendor=0x0451, idProduct=0xe001
# IN endpoint: 0x81
# OUT endpoint: 0x02
#   Always should read 32 bytes at a time, so a read buffer is used because
#   we may get some of the next packet.
import usb.core # For Silver Links
import usb.util # For Silver Links
class glink:
    def __init__(self):
        print('Initializing SilverLink ..')
        self.usbdev = usb.core.find(idVendor=0x0451, idProduct=0xe001)
        if self.usbdev is None:
            print('SilverLink not found.')
            quit()
        usb.util.dispose_resources(self.usbdev) # Seems to help things. [Had used .reset()]
        self.usbdev.set_configuration() # Should only be one configuration, so this should work..
        self.readbuf = bytearray() # The read buffer is only used for the SilverLink
    def read(self, numbytes):
        while len(self.readbuf) < numbytes: # Not enough data is in the buffer, read link:
            try:
                indata = self.usbdev.read(0x81, 32, 25000) # 25s max packet allowance OK?
            except:
                print('!! USB link READ error. Quitting.')
                quit()
            self.readbuf.extend(indata)
        data = self.readbuf[0:numbytes]
        self.readbuf = self.readbuf[numbytes:]
        return data
    def write(self, data):  # data should be a bytearray
        try:
            self.usbdev.write(0x02, data, 25000)
        except:
                print('!! USB link WRITE error. Quitting.')
                quit()
    def __del__(self):
        usb.util.dispose_resources(self.usbdev)
    def softreset(self):
        self.readbuf = bytearray()
        usb.util.dispose_resources(self.usbdev)
        self.usbdev.set_configuration()
