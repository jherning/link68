
MID_tt = {
    0x09: 'Computer->92',
    0x08: 'Computer->89/92+/V200',
    0x88: 'TI-92+',
    0x98: 'TI-89',
    0x89: 'TI-92'
}

MID_ft = {
    'Computer->92': 0x09,
    'Computer->89/92+/V200': 0x08,
    'TI-92+': 0x88,
    'TI-89': 0x98,
    'TI-92': 0x89
}

CID_tt = {
    0x06: 'VAR',     # Variable header (VAR)
    0x09: 'CTS',     # CTS
    0x15: 'DATA',    # Data Packet (DATA)
    0x2D: 'VER',     # Request Versions (VER)
    0x36: 'SKE',     # Skip/Exit (SKE)
    0x56: 'ACK',     # ACK
    0x5A: 'ERR',     # ERR [checksum]
    0x68: 'RDY',     # Check if Ready (RDY)
    0x6D: 'SCR',     # Request Screenshot (SCR)
    0x78: 'CONT',    # Continue (CONT)
    0x87: 'CMD',     # Direct Command (CMD)
    0x88: 'DEL',     # Delete Var (DEL)
    0x92: 'EOT',     # End of Transmission (EOT)
    0xA2: 'REQ',     # Request Var (REQ)
    0xC9: 'RTS'      # Request to Send Var (RTS)
}

CID_ft = {
    'VAR': 0x06,
    'CTS': 0x09,
    'DATA': 0x15,
    'VER': 0x2D,
    'SKE': 0x36,
    'ACK': 0x56,
    'ERR': 0x5A,
    'RDY': 0x68,
    'SCR': 0x6D,
    'CONT': 0x78,
    'CMD': 0x87,
    'DEL': 0x88,
    'EOT': 0x92,
    'REQ': 0xA2,
    'RTS': 0xC9
}

CID_hasdata = {   # Does packet have data?
    'VAR': True,
    'CTS': False,
    'DATA': True,
    'VER': False,
    'SKE': True,
    'ACK': False,
    'ERR': False,
    'RDY': False,
    'SCR': False,
    'CONT': False,
    'CMD': False,
    'DEL': True,
    'EOT': False,
    'REQ': True,
    'RTS': True
}


TID_tt = {
    0x00: 'Expression',
    0x04: 'List',
    0x06: 'Matrix',
    0x0A: 'Data',
    0x0B: 'Text',
    0x0C: 'String',
    0x0D: 'GDB',
    0x0E: 'Figure',
    0x10: 'Picture',
    0x12: 'Program',
    0x13: 'Function',
    0x14: 'Macro',
    0x18: 'Date',
    0x1A: 'Folder/Apps Table',
    0x1B: 'Local DIRLIST',
    0x1C: 'Other',
    0x1D: 'Backup',
    0x1F: 'Global DIRLIST',
    0x20: 'Get Certificate',
    0x21: 'Assembly Program',
    0x22: 'Get IDLIST',
    0x23: 'AMS',
    0x24: 'Flash App',
    0x25: 'Certificate'
}

TID_ft = {
    'Expression': 0x00,
    'List': 0x04,
    'Matrix': 0x06,
    'Data': 0x0A,
    'Text': 0x0B,
    'String': 0x0C,
    'GDB': 0x0D,
    'Figure': 0x0E,
    'Picture': 0x10,
    'Program': 0x12,
    'Function': 0x13,
    'Macro': 0x14,
    'Date': 0x18,
    'Folder/Apps Table': 0x1A,
    'Local DIRLIST': 0x1B,
    'Other': 0x1C,
    'Backup': 0x1D,
    'Global DIRLIST': 0x1F,
    'Get Certificate': 0x20,
    'Assembly Program': 0x21,
    'Get IDLIST': 0x22,
    'AMS': 0x23,
    'Flash App': 0x24,
    'Certificate': 0x25
}

TID_tl = {
    'Expression': 'e',
    'List': 'l',
    'Matrix': 'm',
    'Data': 'c',
    'Text': 't',
    'String': 's',
    'GDB': 'd',
    'Figure': 'a',
    'Picture': 'i',
    'Program': 'p',
    'Function': 'f',
    'Macro': 'x',
    'Other': 'o',
    'Assembly Program': 'z',
    'AMS': 'u',
    'Flash App': 'k',
}

# File extensions
MID_ext = {
    'TI-92': '92',
    'TI-92+': '9x',
    'TI-89': '89'
}

# File Signatures
signa = {
    'TI-92': '**TI92**',
    'TI-92+': '**TI92P*',
    'TI-89': '**TI89**'
}

signab = ['**TI92**', '**TI92P*', '**TI89**']
