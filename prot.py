# Protocol Module for sending/receiving & constructing/parsing TI packets

from settings import debug
import settings
from univ import *

# Replace any character with code over 127 w/ '+XX' where XX is hex, return name string.
def sanitize_name(unsafe_name):
    safe_name = ''
    for i in unsafe_name:
        if i > 0x7F:
            safe_name += '+' + format(i,'x')
        elif i == 0: break # sanitize checks for zero-termination.
        else:
            safe_name += chr(i)  #FIX as this is unicode???
    return(safe_name)
# Reverse the above, return a bytearray.
def unsanitize_name(safe_name):
    unsafe_name = bytearray()
    pluses = safe_name.split('+')
    unsafe_name.extend(pluses[0].encode('ascii')) # first piece 
    for segment in pluses[1:]:
        unsafe_name.append(int(segment[0:2], 16))
        unsafe_name.extend(segment[2:].encode('ascii'))
    return(unsafe_name)

def checksum(data):
    sum = 0
    for b in data:
        sum += b
    sum = sum % 65536  # Get lowest two bytes only
    return(sum)

def getpacket(link):
    pack = packet()
    pack.read(link)
    return(pack)

def quicksend(cid, link):
    outpack = packet()
    outpack.CIDt = cid
    outpack.buildsend(link)

def makevarheader(varname, typeIDnum, varsize):
    data = bytearray()
    data.extend(varsize.to_bytes(4,'little'))
    data.append(typeIDnum)
    data.append(len(unsanitize_name(varname)))
    data.extend(unsanitize_name(varname))
    data.append(0)  # Nonzero for v200/89T ams flashing.
    return(data)

def sendRTS(folder, name, typeIDnum, size, link):
    varname = name
    if folder != '': varname = folder + '\\' + varname # Concat folder\name if folder non-empty
    outpack = packet()
    outpack.CIDt = 'RTS'
    outpack.data = makevarheader(varname, typeIDnum, size + 4) # LG says size should include the padding
    outpack.buildsend(link)

# Special RTS packet for 89/92+ AMS
def send8992amsRTS(name, size, link):
    outpack = packet()
    outpack.CIDt = 'RTS'
    outpack.data = makevarheader(name, 0x23, size)
    outpack.data.pop() # Remove the mysterious extra byte.
    # TI-92+ complains w/o this when recovering from bootloader. 89 doesn't seem to.
    outpack.buildsend(link)

# Special RTS packet for V200/89T AMS    
def sendV200amsRTS(size, hw_id, link):
    outpack = packet()
    outpack.CIDt = 'RTS'
    outpack.data = makevarheader('', 0x23, size) # blank name, 0x23:ams
    outpack.data.pop() # Normally this byte is a zero.
    outpack.data.append(0x08)
    outpack.data.append(0x00)
    outpack.data.append(hw_id)
    outpack.buildsend(link)

def sendvarREQ(name, link):
    outpack = packet()
    outpack.CIDt = 'REQ'
    outpack.data = makevarheader(name, 0, 2) # Type and size may be wrong. Calc responds w/ actual.
    outpack.buildsend(link)

# Get a packet, bail if it's not what we expect.
def quickget(cid, link):
    inpack = getpacket(link)
    if cid and (inpack.CIDt != cid):
        print('Got ' + inpack.CIDt + ' packet when expecting ' + cid +'. Quitting.')
        debug(inpack.data)
        quit()
    return(inpack)

# Request var list
def sendglobalREQ(link):
    outpack = packet()
    outpack.CIDt = 'REQ'
    # Datapart is a non-standard variable header
    outpack.data = bytearray()
    if settings.calc_type == 'TI-92':
        outpack.data.extend(b'\x00\x00\x00\x00\x19\x00')
    else:    
        outpack.data.extend(b'\x00\x00\x00\x1B\x1A\x00') # "Phase 2" list request
        outpack.data.append(len('main'))
        outpack.data.extend(bytes('main', 'ascii'))
    outpack.buildsend(link)
    
# Class for directory info
class calcdir:
    def __init__(self):
        self.folders = []
        self.files = [] # with full path
        self.apps = []
        self.currdir = 'main'
        v200_detected = False
# Parse filename/flashapp data:
    def parse_dirDATA(self, datapack, echo):
        data = datapack.data
        # Detect a v200 by empty extra data.
        v200 = 0
        if len(data) > 18 and data[18] == 0:
            v200 = 1 
            self.v200_detected = True
            print('V200-style directory data detected.')

        for offset in range(4, len(data), 14 + v200*8):  # 14 -> 22 for V200
            if data[offset+8] == 0x24: # flash app
                self.apps.append(sanitize_name(data[offset:offset+8]))
                if echo:
                    print(' FLASH APP: ' + sanitize_name(data[offset:offset+8]) )
            elif data[offset+8] == 0x1F: #folder
                self.currdir = sanitize_name(data[offset:offset+8])
                self.folders.append(self.currdir)
                if echo:
                    print(' FOLDER: ' + sanitize_name(data[offset:offset+8]) )
            else: # file? 
                self.files.append(self.currdir + '\\' + sanitize_name(data[offset:offset+8]))
                if echo:
                    print('   ' + sanitize_name(data[offset:offset+8]) + ' -- ' + TID_tt[data[offset+8]] )


# Class for handling DBUS packets.
class packet:
    def __init__(self):
        self.MIDt = '' 
        self.CIDt = ''
        self.data_len = 0
        self.header = bytearray()
        self.data = bytearray()
        self.checksum = 0
        self.output = bytearray()

    def read(self, link):
        self.header = link.read(4)
        if self.header[0] in MID_tt:
            self.MIDt = MID_tt[self.header[0]]  # bytes slices are bytes but are integers when indexed.
        else:
            print('Unknown calc Machine ID(' + str(self.header[0]) + '). Quitting.')
            quit()
        if self.header[1] in CID_tt:
            self.CIDt = CID_tt[self.header[1]]
        else:
            print("Received unknown Command ID from calc. Quitting.")
            quit()
        self.data_len = self.header[2] + 256 * self.header[3]
        debug(self.MIDt + ': ' + self.CIDt + ' ' + str(self.data_len))
        if CID_hasdata[self.CIDt]:
            dat = link.read(self.data_len + 2)  # Read data + checksum
            self.data = dat[0 : self.data_len]
            self.checksum = dat[self.data_len] + 256 * dat[self.data_len+1]
            debug("Recvd " + str(self.data_len) + " bytes of data. Checksum: " + str(self.checksum) )
        return(self)


    def buildsend(self, link):  # Build & send output bytearray from MID, CID, and data.
                                # Computes checksum and data_len as well.
        self.MIDt = settings.comp_MIDt
        self.data_len = len(self.data)      # Compute data length.
        self.checksum = checksum(self.data) # and checksum.

        self.output = bytearray()           # Start putting output together
        self.output.append(MID_ft[self.MIDt])
        self.output.append(CID_ft[self.CIDt])
        self.output.extend((self.data_len % 65536).to_bytes(2,'little')) #If 64k->0 (flash transfers)
        if CID_hasdata[self.CIDt]:
            self.output.extend(self.data)
            self.output.extend(self.checksum.to_bytes(2,'little'))
        link.write(self.output)
        debug(self.MIDt + ': ' + self.CIDt + ' ' +str(self.data_len))   
        return(True)

