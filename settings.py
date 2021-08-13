# Can be 'gray', 'black', 'silver', or 'custom'. See manual.txt:
link_type = 'gray'

# Serial Port name for black, gray, and custom serial links.
# Probably '/dev/ttyUSBx' or '/dev/ttySx' on Linux, 'COMx' on Windows.
serial_port = '/dev/ttyUSB0'

# Used to define file extensions/headers when not detected automatically
# (i.e. when command is 'group' or 'ungroup'). Has no effect otherwise.
# Use: 'TI-89', 'TI-92', or 'TI-92+'. -92, -92+, and -89 override this.
calc_type = 'TI-89'

# Overwrite files/vars by default (on both computer and calc).
overwrite = False

# Send to current folder by default. **Enables overwrite mode**.
current = False

# To make the BlackLink driver work better with the TI-92.
TI_92_init = False

# Debugging/verbose output:
# By default debug/verbose output is off, but it might help you diagnose a problem.
def debug(stuff):
    # Uncomment the next line for verbose debugging output. Comment it for normal output.
    #print(stuff)
    pass

# Globals. Don't touch me!
comp_MIDt = ''
