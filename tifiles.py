# Module for parsing variable data and reading/writing the 68k TI file format.
# Attempts compatibility with TI Graph Link software format.

from settings import calc_type
from prot import *
import settings #settings.overwrite, etc.
from settings import debug
from os.path import exists
from univ import *

# Class for TI-68k variables.
# Data is stored in Python-friendly format and converted when saving/sending.
class tivar:
    def __init__(self): 
        self.TIDt = ''
        self.varname = ''
        self.signature = ''
        self.folder = ''
        self.comment = '' # Max 40 Chars
        self.vardata = bytearray()
        self.checksum = 0
        self.attr = 0
        self.offset_from_table = 0 # Used when writing to file only.
        self.file_offset = 0 # Used when reading from file only.

    # Get varname, TID, and data from silent request header+data TI packets
    def parse_silentreq(self, headerpack, datapack):
        header = headerpack.data
        data = datapack.data
        if header[4] in TID_tt:
            self.TIDt = TID_tt[header[4]]
        else:
            print("Var Type not recognized.")
            quit()
        self.varname = sanitize_name(header[6: 6 + header[5]])
        self.vardata = data[4:]  # Remove extra 4 bytes at top of var. 
        if checksum(self.vardata) == datapack.checksum:
            self.checksum = datapack.checksum
        else:
            print('Bad checksum received from calc.')
            quit()
            return False
        return True

 # Takes a list of tivars. Writes a single var for one or a group file for multiple.
def writevars(filename, varlist, MIDt):
    out = bytearray()
    
    if len(varlist) == 1: group = False
    else: group = True

    # Machine Type
    out.extend(signa[MIDt].encode('ascii'))
    out.extend(b'\x01\x00')

    # Set Default Folder to 0 if a group file otherwise write folder name
    if group: out.extend(b'\x00\x00\x00\x00\x00\x00\x00\x00')
    else:
        out.extend(varlist[0].folder.encode('ascii'))
        for i in range(0,8-len(varlist[0].folder)):
            out.append(0)

    # Comment will be null for now:
    for i in range(0,40):
        out.append(0x00) # Zero Terminate
            
    if group:
        vars_havefold = varlist
        vars_nofold = []
    else:
        vars_havefold = []
        vars_nofold = [varlist[0]]  # Just doing a single file

    # Number of Vars+Folder Entries
    out.extend((len(vars_nofold)+2*len(vars_havefold)).to_bytes(2,'little'))

    # Build the data section, keeping track of offsets from the var table
    data_section = bytearray()
    data_section.extend(b'\x00\x00\x00\x00')  # NOTE: This should be overwritten by the filesize later!!
    data_section.extend(b'\xA5\x5A')
    for var in vars_nofold:
        var.offset_from_table = len(data_section) # Record offset
        data_section.extend(b'\x00\x00\x00\x00') # 5 bytes of 0 or 4?
        data_section.extend(var.vardata)
        data_section.extend(var.checksum.to_bytes(2,'little'))
    for var in vars_havefold:
        var.offset_from_table = len(data_section) # Record offset
        data_section.extend(b'\x00\x00\x00\x00') # 5 bytes of 0 or 4?
        data_section.extend(var.vardata)
        data_section.extend(var.checksum.to_bytes(2,'little'))

    # Write variable table. Vars with folder each get a folder entry -- fix later?
        # Length of header + var table: 
    headertable_len = 60 + 16*len(vars_nofold) + 16*2*len(vars_havefold)
    numentries = len(vars_nofold) + 2*len(vars_havefold)
    for var in vars_nofold:
        out.extend((headertable_len + var.offset_from_table).to_bytes(4,'little'))
        out.extend(unsanitize_name(var.varname))
        for i in range(0,8-len(unsanitize_name(var.varname))):
            out.append(0) # Zero Terminate
        out.append(TID_ft[var.TIDt])
        out.append(var.attr)
        out.extend(b'\x00\x00') # Unused
    for var in vars_havefold:
        # Folder entry:
        out.extend((headertable_len + var.offset_from_table).to_bytes(4,'little')) # Offset to this var's data
                                                            #probably first var if multiple in folder?
        out.extend(unsanitize_name(var.folder))
        for i in range(0,8-len(unsanitize_name(var.folder))):
            out.append(0) # Zero Terminate
        out.append(0x1F) # Folder Type
        out.append(0x00)
        out.extend(int(1).to_bytes(2,'little')) # 1 var per folder entry for now -- FIX?
        # Var entry:
        out.extend((headertable_len + var.offset_from_table).to_bytes(4,'little'))
        out.extend(unsanitize_name(var.varname))
        for i in range(0,8-len(unsanitize_name(var.varname))):
            out.append(0) # Zero Terminate
        out.append(TID_ft[var.TIDt])
        out.append(var.attr)
        out.extend(b'\x00\x00') # Unused

    data_section[0:4] = (headertable_len + len(data_section)).to_bytes(4,'little') # Filesize
    out.extend(data_section) # Append header/table with data section

    if group:
        filename_ext = filename + '.' + MID_ext[MIDt] +'g'
    else:
        filename_ext = varlist[0].folder + '.' + varlist[0].varname + '.' + MID_ext[MIDt] + TID_tl[varlist[0].TIDt]
    if exists(filename_ext) and settings.overwrite == False:
        print('** ' + filename_ext + ' exists. Skipping. [Overwrite: -o] **')
    else:
        with open(filename_ext, 'wb') as f:
            f.write(out)
            if group:
                print('  ' + filename_ext + ' written (groupfile, ' + str(len(varlist)) + ' TI-vars).' )
            else:
                print('  ' + filename_ext + ' written (' + varlist[0].TIDt + ', ' + str(len(varlist[0].vardata)) + ' bytes).' )


##### decode null terminated bytearray to a python string####
def dnull(array):
    output = ''
    for i in array:
        if i: output = output + chr(i)  ### FIX? chr() is for unicode chars
        else: break
    return(output)

##### Read a TI File into a list of one or more vars #######
def parse_tifile(filename):
    if exists(filename):
        with open(filename, 'rb') as file:
            filedata = file.read()
    else:
        print('!! Computer file ' + filename + ' not found. Skipping.')
        return ([]) # No vars to add.
    try: calc_string = filedata[0:8].decode('ascii')
    except: calc_string = 'BAD'
    if calc_string not in signab:
        print('** ' + filename + ': invalid signature. Not a var file? Skipping. **')
        return()
    default_folder = dnull(filedata[10:18])
    tivars = []
    
    ## Read folder / variable table ##
    num_entries = filedata[58] + 256 * filedata[59]
    curr_folder = default_folder
    for i in range(0, num_entries):
        offset = 60 + 16 * i  # This entry's offset. Header is 60 bytes, each entry is 16
        tentry = filedata[offset : offset + 16] # Slice off the table entry
        TID = tentry[12]
        if TID == 0x1F:  # It's a folder entry.
            curr_folder = dnull(tentry[4 : 12])
        else:  # It's a variable; fill in eveything except the data:
            newvar = tivar()
            newvar.signature = calc_string
            newvar.folder = curr_folder
            newvar.varname = sanitize_name((tentry[4:12]))
            newvar.TIDt = TID_tt[TID]
            newvar.attr = tentry[13]
            newvar.file_offset = tentry[0] + 2**8 * tentry[1] + 2**16 * tentry[2] + 2**24 * tentry[3]  # Fix: probably a better way..
            tivars.append(newvar)
    
    ## Now iterate through variables and get data sections.
    ## Maddeningly the file format does not include the data length for each var!!!
    startpoint = [] # Create lists of start and endpoints for the variable data, including leading 0's and checksums
    endpoint = []
    for var in tivars:
        startpoint.append(var.file_offset)
    endpoint = startpoint[1:]
    endpoint.append(len(filedata))
    ## Finally, get the raw var data: ##
    i = 0
    for var in tivars:
        var.vardata = filedata[startpoint[i]+4 : endpoint[i] - 2]  # Strip leading 0s and checksum.
        debug('Loaded ' + var.folder + '\\' + var.varname + '  (' + str(endpoint[i] - 1 - (startpoint[i]+4)) +' bytes).' )
        i += 1    ## Fix? Maybe we should check the checksum??
        var.checksum = checksum(var.vardata)
    return (tivars)
        
##  Flash transfer stuff ##
class tiflash:
    def __init__(self):  # Not everything here is needed for sending flash apps.
        # .. we may implemeent receiving later.
        #self.revision = [0, 0]  # [major, minor]
        #self.flags = 0x00
        #self.date = [0, 0, 0, 0, 0, 0, 0, 0]    #ddmmyyyy
        self.name = ''
        self.MID = 0 # Read but currently unused.
        self.TID = 0  # 0x23: 'os', 0x24: 'app'
        self.hw_id = 0 #1: 92+, 3: 89, 8: V200, 9: 89T
        self.data = bytearray()
        self.checksum = 0
    # Load one or more flash apps/os from a file into a list of tiflash objects.
    # At the moment we only load data needed for sending.
def parse_flashfile(filename):
    varlist = []
    if exists(filename):
        with open(filename, 'rb') as file:
            fileraw = file.read()
    else:
        print(filename + ' not found. Skipping.')
        return(varlist)
    offs = 0
    while offs < len(fileraw): #LG claims a single file could have "1-3 headers."
        newvar = tiflash()
        if fileraw[0:8].decode() != '**TIFL**':
            print('** '+ filename + ' does not seem to be TI Flash format. Skipping. **')
            return(varlist)
        newvar.name = sanitize_name(fileraw[17:25])
        newvar.MID = fileraw[0x30]
        newvar.TID = fileraw[0x31]
        if newvar.TID == 0x23: # Flash apps seem to have this info in neither place, so don't load.
            newvar.hw_id = fileraw[0x56] # Note LG says this is at 0x48, so maybe older ROMS are different???
        datasize = fileraw[74] + 2**8 * fileraw[75] + 2**16 * fileraw[76] + + 2**24 * fileraw[77]
        newvar.data = fileraw[78: 78+datasize]
        # !!! Contrary to LG, TI flash file does not seem to have a checksum! !
        fileraw = fileraw[78 + datasize:]
        if newvar.name == 'License':
            print('** Found a software license embedded in file. Use a hex editor or appropriate TI software for viewing. **')
        else:
            print('Found flash data: ' + newvar.name + ', ' + str(len(newvar.data)) +' bytes.')
            varlist.append(newvar)
    return(varlist)


















