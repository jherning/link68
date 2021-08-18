#!/usr/bin/env python3

from sys import argv
from os.path import exists
import time
# Now get Joe's modules:
from prot import *
from tifiles import *
import settings
from univ import *

# Used LOUD as its own command and not LOUD for find / overwrite checks
# Gets a listing from the calc and returns as a calcdir object.
def ls(link, loud):
    if loud: print('Getting directory listing..')
    entries = []
# Should get folders, files, and flash apps
    sendglobalREQ(link)
    quickget('ACK', link)
    quickget('VAR', link) # disregarding
    # Loop until EOT (needed for 92 only):
    calcdata = calcdir()
    while True:
        quicksend('ACK', link)
        quicksend('CTS', link)
        quickget('ACK', link)
        DATApack = quickget('DATA', link)
        calcdata.parse_dirDATA(DATApack, loud)
        quicksend('ACK', link)
        if getpacket(link).CIDt == 'EOT': break
    quicksend('ACK', link)
    return(calcdata)

# List matching var path/names, return list of matching path/names.
def find(args, link, loud):
    if loud: print('Getting directory listing to search..')
    calclist = ls(link, False)
    filelist = []
    for strtofind in args:
        strtofind = strtofind.replace('/', '\\')
        for entry in calclist.files:
            if entry.find(strtofind) != -1:
                entry = entry.replace('\\', '/')
                filelist.append(entry)
                if loud: print('  ' + entry)
    return(filelist)

# Combine find and get.
def findget(args, link, grouped):
    if len(args) < 2:
        print('Usage: findgetg [string(s) to match] group_file_base_name')
        quit()
    if grouped: groupfile = args.pop() # Remove group file name before searching.
    filelist = find(args, link, False)
    if grouped: filelist.append(groupfile)
    get(filelist, link, grouped)

# Backup all variables to a group file.
def backup(args, link):
    if len(args) == 0: backupname = 'backup'
    else: backupname = args[0]
    print('Getting directory listing..')
    calclist = ls(link, False)
    getargs = calclist.files
    print('  ' + str(len(getargs)) + ' vars to backup.')
    getargs.append(backupname) # Get needs the group file base name.
    get(getargs, link, True)

# Load TI vars from computer files. Return list of tivar objects.
def loadvars(filenames):
    tivars = []
    for filename in filenames:
            tivars.extend(parse_tifile(filename))  # Files may have multiple vars.
    return(tivars)

# Load TI vars from computer then write individually.
def ungroup(filenames):
    tivars = loadvars(filenames)
    for var in tivars:
        writevars(var.varname, [var], settings.calc_type)
# ungroup 'folder.something.89p -92' Will write folder.something.9xp

# Load TI vars from computer then write as a group file.
def group(filenames):
    if len(filenames) < 3:
        print('Usage: group [files to group] group_file_base_name')
        quit()
    pcfile = filenames.pop()
    tivars = loadvars(filenames)
    writevars(pcfile, tivars, settings.calc_type)

# Write flash file(s) to calc.
def flash(filenames, link, recovery):
    flashvarsALL = []
    for ffile in filenames: # Load flash files.
        flashvarsALL.extend(parse_flashfile(ffile))
    
    flashvars = [] # Check for overwrites
    if (not settings.overwrite) and (not recovery):
        print("Getting directory listing for overwrite check..")
        calclist = ls(link, False)
        for var in flashvarsALL:
            if var.name in calclist.apps:
                print('** ' + var.name + ' app exists. Skipping. **')
            else:
                flashvars.append(var)
    else: flashvars = flashvarsALL
    
    if recovery: # In recovery mode, we haven't auto-detected anything.
        settings.comp_MIDt = 'Computer->89/92+/V200' # No TI-92s in this rodeo.
    
    for var in flashvars: # Flash the Calc!
        link.softreset()  # Good for SilverLink
        if var.TID == 0x23:
            input("Warning: about to attempt an AMS flash update. This will clear your RAM and may damage your calculator. Press ENTER to proceed.")
        if var.TID == 0x23 and var.hw_id >= 8: # AMS flash V200/89T!
            sendV200amsRTS(len(var.data), var.hw_id, link) # 0x08: V200, 0x09: Titanium
        elif var.TID == 0x23: # AMS flash 89/92+
            send8992amsRTS(var.name, len(var.data), link)
        else:
            sendRTS('', var.name, var.TID, len(var.data), link) # App
        ## Send 64k at a time:
        while (var.data):
            quickget('ACK', link)
            quickget('CTS', link)
            quicksend('ACK', link)
            outpack = packet()
            outpack.data.extend(var.data[0:64*1024])
            var.data = var.data[64*1024:] # slice off data we'll be sending (kills object)
            outpack.CIDt = 'DATA'
            print(' Flashing ' + var.name + '  (' + str(len(outpack.data)) + ' byte block).')
            outpack.buildsend(link)
            quickget('ACK', link)
            if var.data: # There's more!
                quicksend('CONT', link)
        quicksend('EOT', link)
        quickget('ACK', link)
    print('Done flashing.')
    if recovery: quit()

# Load then put normal vars to calculator.
def put(filenames, link):
    data_time = 0
    data_amount = 0
    putvarsALL = loadvars(filenames)
    putvars = []
    if not settings.overwrite:
        print("Getting directory listing for overwrite check..")
        calclist = ls(link, False)
        for var in putvarsALL:
            if var.folder + '\\' + var.varname in calclist.files:
                print('** ' + var.folder + '/' + var.varname + ' exists. Skipping. [Overwrite: -o] **')
            else:
                putvars.append(var)
    else: putvars = putvarsALL
            
    for var in putvars:
        link.softreset()  # SilverLink..
        if settings.current: # Send to current dir.
            var.folder = ''
        sendRTS(var.folder, var.varname, TID_ft[var.TIDt], len(var.vardata), link)
        quickget('ACK', link)
        quickget('CTS', link)
        quicksend('ACK', link)
        # Build and send the DATA packet:
        outpack = packet()
        outpack.data.extend(b'\x00\x00\x00\x00')
        outpack.data.extend(var.vardata)
        outpack.CIDt = 'DATA'
        print(' put ' + var.folder + '/' + var.varname + '  (' + var.TIDt + ', ' + str(len(var.vardata)) + ' bytes)' )
        timer = time.time()
        outpack.buildsend(link)
        data_time += time.time() - timer
        data_amount += len(outpack.output)
        ### /DATA
        quickget('ACK', link)
        quicksend('EOT', link) # Send EOT for each file. FIX?
        quickget('ACK', link) # Doesn't seem to work w/o doing this.
    if data_time: print("Done putting files. Link write speed: %i bytes/s" % (data_amount/data_time) )

# Get vars from calc; write individually or as a group file.
def get(args, link, grouped):
    data_time = 0
    data_amount = 0
    sendvars = []
    if grouped:
        groupfilename = args.pop()
    for filename in args:
        print("get " + filename)
        filename = filename.replace("/", "\\")  # Rewrite forward slash from command line.
        sendvarREQ(filename, link)
        quickget('ACK', link)
        headerpack = getpacket(link) # Is it a VAR or SKE?
        if headerpack.CIDt == 'VAR':
            quicksend('ACK', link)
            quicksend('CTS', link)
            quickget('ACK', link)
            timer = time.time()
            datapack = quickget('DATA', link)
            data_time += time.time() - timer
            data_amount += datapack.data_len + 6
            quicksend('ACK', link)
            quickget('EOT', link)
            quicksend('ACK', link)
            # Now parse the header/data.
            calcvar = tivar()
            calcvar.parse_silentreq(headerpack, datapack)
            # If invoked as "folder\filename", set folder.
            if "\\" in filename:
                calcvar.folder = filename.split("\\")[0]
            else:
                calcvar.folder = 'main' # If no dir specified, set to main. FIX?
            if grouped:
                sendvars.append(calcvar) # Add to list for group send later.
            else:
                writevars(filename, [calcvar], settings.calc_type)
        elif headerpack.CIDt == 'SKE':
            print(' ** Got SKE from calc. ' + filename + ' probably does not exist **')
            time.sleep(2.1) # Calculator seems to timeout after SKE.
                            # Then graylink gets a byte, so reset:
        link.softreset() # SilverLink!
    if data_time: print("Done getting files. Link read speed: %i bytes/s" % (data_amount/data_time) )
    if grouped:
        writevars(groupfilename, sendvars, settings.calc_type)

def screenshot(args, link):
    import png
    print('Getting screenshot.')
    quicksend('SCR', link)
    quickget('ACK', link)
    timer = time.time()
    inpack = quickget('DATA', link)
    timer = time.time() - timer
    print ('  Link rate: %i bytes/s' % ((inpack.data_len + 2)/timer))
    quicksend('ACK', link)

    sshot = [[0 for i in range(240)] for j in range(128)]  # 240 cols, 128 rows
    for row in range(0, 128):
        for colbyte in range(0,30): 
            recvd = inpack.data[row*30 + colbyte]
            for i in range(8):
                sshot[row][colbyte*8+7-i] = int(recvd&(2**i) == 0)

    sshot89 = [[0 for i in range(160)] for j in range(100)]  # 160x100
    for row in range(0,100): # Crop for TI-89
        for col in range(0,160):
            sshot89[row][col] = sshot[row][col]
    if len(args) > 0:
        filename = args[0] + '.png'
    else: filename = 'screenshot.png'
    if exists(filename) and settings.overwrite == False:
        print('** ' + filename + ' exists. Quitting. [Overwrite: -o] **')
        quit()
    with open(filename, 'wb') as f:
        if settings.calc_type == 'TI-89':
            w = png.Writer(160, 100, greyscale=1, bitdepth=1)
            w.write(f, sshot89)
        else:
            w = png.Writer(240, 128, greyscale=1, bitdepth=1)
            w.write(f, sshot)
        f.close()
        print('  Wrote ' + filename + '.')

#### MAIN ####

# Parse argv[] into cmd and args[], process flags.
argstemp = argv
argstemp.pop(0)
args = []
for el in argstemp: # Process any flags:
    if el == '-o':
        settings.overwrite = True
    elif el == '-co':
        settings.current = True
    elif el == '-89':
        settings.calc_type = 'TI-89'
    elif el == '-92':
        settings.calc_type = 'TI-92'
    elif el == '-92+':
        settings.calc_type = 'TI-92+'
    else: args.append(el)
    
if settings.current: settings.overwrite = True

if settings.current: print('** Current folder mode enabled. **')
if settings.overwrite: print('** Overwrite mode enabled. **')    

if len(args) == 0:
    print('Link 68 version 0.2 (alpha)')
    print('Usage: link68.py COMMAND ARGS [optional switches]')
    print(' COMMANDS: ls, shot, get, getg, put, find, finget, findgetg, flash, rflash, backup')
    print(' OPTIONS: -o: overwrite mode, -co: current folder + overwrite mode')
    print(' Settings contained in settings.py.')
    quit()
if args: cmd = args.pop(0)

    
# Do any commands that don't require the link cable, then quit:
if cmd == 'ungroup':
    ungroup(args)
    quit()
if cmd == 'group':
    group(args)
    quit()

# Init the link cable.
if settings.link_type == 'gray':
    from graylink import glink
elif settings.link_type == 'black':
    from blacklink import glink
elif settings.link_type == 'silver':
    from silverlink import glink
elif settings.link_type == 'custom':
    from customlink import glink
link = glink()

# Skip connectivity test for rflash:
if cmd == 'rflash': flash(args, link, True)

# Check connectivity & detect calculator type
settings.comp_MIDt = 'Computer->92' # Pretend we think it's a 92. Later models respond (as a 92), so it's safe.
quicksend('RDY', link)
inpack = quickget('ACK', link)
if inpack.header[3] & 1 == 1 and cmd != 'shot':
    print("Calc not ready. Are you at the homescreen?")
    quit()
if inpack.header[2] == 0x00: # Byte 3 of ACK seems to contain hardware version info.
    # Known responses: 0x0c: TI-92+ w/AMS 2.09, 0x04: TI-92+ w/ AMS 2.05
    # We are assuming all plain 92's give 00. TI-92-II???
    settings.calc_type = 'TI-92'
else:
    settings.comp_MIDt = 'Computer->89/92+/V200' # It's not a 92. Should ACK as 89 or 92+/V200.
    quicksend('RDY', link)
    inpack = quickget('ACK', link)
    settings.calc_type = inpack.MIDt
print('  ' + settings.calc_type  + ' detected.')

# Do requested linking command.
if cmd == 'shot': screenshot(args, link)
elif cmd == 'get': get(args, link, False)
elif cmd == 'getg': get(args, link, True)
elif cmd == 'put': put(args, link)
elif cmd == 'ls': ls(link, True)
elif cmd == 'find': find(args, link, True)
elif cmd == 'backup': backup(args, link)
elif cmd == 'flash': flash(args, link, False)
elif cmd == 'findget': findget(args, link, False)
elif cmd == 'findgetg': findget(args, link, True)
else: print('Unkown command: ' + cmd)



