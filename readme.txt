*** Link 68 (link68) version 0.2 (alpha) README ***
Program and documentation copyright (c) Joseph Herning 2021.
This is experimental software. Please read license at the end of this file.

Link 68 is a pure Python computer-to-calc linking program for the TI 68k calculators using the traditional I/O port (2.5mm phone jack). It does not make use of external libraries except those Python modules needed to support various things (PySerial, PyUSB, PyPNG...). The TI-89, TI-89 Titanium, TI-92, TI-92+, and V200 are supported. As of release, testing has only been done on Linux. This manual assumes a Linux-like environment. Current features/capabilities:
 - sending/receiving normal variables using TI Graph Link format (including group format)
 - backing up all normal variables (i.e. not flash apps or AMS)
 - sending free flash apps and AMS updates
 - screenshots
 - listing calculator contents and simple variable searches
 - grouping and ungrouping variable files (TI Graph Link format, not .tig)

BASIC USAGE (assuming sh-type shell):
    ./link68.py COMMAND ARGS [optional switches]

 - Optional switches do not need to be at the end.

 
 --- Setup ---

Before running, set your link type and necessary port settings in settings.py. See the Link Cable Notes section. You may wish to look through the other settings as well. You will need a recent version of Python 3 (tested on 3.8). For serial cables, you will need PySerial. For USB cables you will need PyUSB. For screenshots, you will need PyPNG.

Make sure calculator is on and at the home screen before running, or you may have link issues. All transfers are silent and do not require additional action on the calculator.

You may need to make link68.py executable:
    chmod +x link68.py
If this doesn't work, you may need to modify the environment string at the beginning of the file or invoke your Python interpreter instead of using ./link68.py to run the program:
    <Python interpreter invocation> link68.py COMMAND ARGS [optional switches]
    
A good idea might be to create a new folder for your calculator data inside the source folder, e.g. link68/calcstuff. Then, working from the calcstuff folder, simply invoke link68 as "../link68.py" instead of "./link68.py". This will keep the program source files and your data from getting mixed together.

    
 --- Linking Examples ---

Take screenshot, save to myshot.png:
    ./link68.py shot myshot
 - Writes screenshot.png if no filename given.
 - Link read speed is also reported. PyPNG is required.

List all variables/apps on calculator:
    ./link68.py ls

Find variables on calculator matching a search string:
    ./link68.py find myfold/
 - This will list all the vars in myfold. A variable named "myfold" won't match because of the "/".
 - If multiple strings are given, vars matching ANY string are reported.

Get myvar1, myvar2, and myvar3 from calculator current directory:
    ./link68.py get myvar1 myvar2 myvar3
 - Files will be saved as main.myvarX.EXT where EXT is automatic.
 - The calculator does not report the current folder, so "main" is used.
 - get/getg are for normal vars; getting flash apps is not supported.

Get main/myvar1 and myfold/mayvr4:
    ./link68.py get main/myvar1 myfold/myvar4
 - You will get main.myvar1.EXT and myfold.myvar4.EXT
 - Computer files can be safely renamed. Metadata stores the on-calc var name and folder.

Get some files and save to a group file:
    ./link68.py getg main/myvar1 myfold/myvar4 groupfilebasename
 - As with normal files, the file extension is automatic (89g, 9xg, 92g).
    
Find variables then automatically get them: [Combines find and get/getg.]
    ./link68.py findget myfold/
    ./link68.py findgetg myfold/ groupfile

Put some files to the calculator (normal vars and/or group files):
    ./link68.py put myfold.nice.89p myfold2.fun.89e

Put some files to the current folder (disregarding folder metadata):
    ./link68.py put myfold.nice.89p myfold2.fun.89e -co
 - ** -co implicitly enables overwrite mode. **

Backup all normal vars to a groupfile:
    ./link68.py backup backupfile
 - If no file is provided, backup.XXg is used.

Flash the calculator with a flash apps or AMS:
    ./link68.py flash flashfile1.XXk/XXu flashfile2.XXk ...
 - AMS flashing may brick your calculator and is untested with many hardware/AMS combinations. See below.
 - WARNING: AMS flashing will delete all variables/data stored in RAM.
 - WARNING: HW1 calculators currently have trouble flashing AMS from the boot code with the SilverLink. This also gives TiLP trouble. It's possible the SilverLink does something incompatible with the HW1 boot code operation of the link port at the hardware protocol level (e.g. it's too fast). The GrayLink works fine. Note the SilverLink did not exist when the HW1 TI-89 was introduced. HW2 calculators are not affected.
 
 "Recover"/flash the calculator from the bootloader (after pressing "I to install product code"):
     ./link68.py rflash osfile.XXu
 - Bootloader gets confused by link68's normal calculator autodetection, so we need a special command.
 - Note: Bootloader is a little picky (especially on the TI-92+), so this MAY NOT work even if normal OS flashing is working. I have tested it on at least one 89/92+/V200 though.
 

 --- Optional Switches ---
 
-o  (Overwrite):
    link68 performs a check before overwriting files on the computer or vars on the calc (requiring a directory listing from the calc). The default behavior is to skip potential overwrites, but this forces overwriting.
 
-co  (Current folder + Overwrite):
    link68.py puts vars to current folder on calc instead of to the folder in the file metadata. Also enables overwrite mode since we do not know the current folder on the calc to perform overwrite checks.

-89 / -92 / -92+
 - Change file writing format when using group/ungroup. Only applies to group/ungroup. Examples below.


 --- Utility Commands (link unused) ---

For group and ungroup commands, all variables are loaded from the file(s) specified into link68's internal representation then file(s) are written from that. Vars can be loaded from any 68k var file or group file (regardless of calculator type). 'Group' always writes a single groupfile while 'ungroup' always writes individual files. The calculator type metadata / file extensions are determined by 'calc_type' in settings.py. You can override this with -92, -92+, or -89. This writes the appropriate extension and changes the file metadata but does not alter the raw variable data.

Create a groupfile from multiple files. The groupfile base name is a required final argument:
    ./link68.py group file1.ext file2.ext groupfile

Ungroup a groupfile to multiple files:
    ./link68.py ungroup groupfile.89g

Convert a TI-92 expression file to a TI-89 one:
    ./link68.py ungroup exp.92e -89
Convert several at once:
    ./link68.py ungroup exp.92e prog.92p mat.92m -89
Convert a whole bunch:   [Requires BASH-like shell.]
    ./link68.py ungroup *.92* -89
Instead, convert to a groupfile:
    ./link68.py group exp.92e prog.92p mat.92m groupfile -89


 --- Link Cable Notes ---
 
For all cables: the current userspace Python "drivers" are quick-and-dirty. I really just wanted to get all official TI cables for the classic link port working to some degree.

** Gray TI Graphlink (Serial) **
This cable is, in my experience, the most compatible. (TI Graph Link can use it on Linux through WINE!) PySerial is required. To connect to a modern computer you will probably use a USB-to-RS232 converter. Many cheap converters do not support all modem control lines of the serial port, and the cable draws power from two of them. Most USB-to-RS232 ICs are capable of controlling the lines, but the lines are often not implemented either in the hardware or in the driver. I have had luck with several converters using pl2303 and ft232r chips. The link rate is about 1 kilobyte/s (9600 baud without flow control!). Currently the ~2s link timeout is not implemented.

Your user will need access to the serial ports. This is often means the user should be in the "dialout" group.

** Custom Serial Link **
This is identical to the Gray Link driver except it does not switch-on the modem control lines which power the Gray Link. Use it to support your experimental/homebrew serial link (Note the $4 "serial" link is not actually a serial link -- try the Black Link driver). Modify the serial port settings (baud rate, flow control, etc.) in customlink.py as needed. It could also be used as a template for implementing a new non-serial link.

** Silver TI Graphlink (USB) **
This cable is supported through PyUSB which typically uses libUSB (but can have various backends). This cable seems a little more finicky and requires some USB pipe resetting between transfers to keep from choking. Warning: I know very little about USB/USB programming. Still, it works well for me at the moment and link rate is about 5-6 kilobytes/s as expected. There are several revisions, some using TI microcontrollers and some older ones using Cypress chips. The Cypress cables seem about 1 kilobyte/s faster than the TI ones.

The cable is found on the USB bus by its vendor and product IDs, so only have one plugged at a time. You may need to grant permission for user access to the USB device on your system. On Ubuntu-ish systems the following may work:

Create a udev rule, something like "/etc/udev/rules.d/51-silverlink.rules" consisting of the line:
    SUBSYSTEM=="usb", ATTR{idVendor}=="0451", ATTR{idProduct}=="e001", MODE="0660", GROUP="plugdev", SYMLINK+="silverGL%n"
Then reload the udev rules:
    sudo udevadm control --reload-rules
Make sure your user is in the "plugdev" group. Re-plug and cross your fingers.
I have no idea what you might need to do on Windows.

** Black "Windows" TI GraphLink **
I wanted to get this cable working out of nostalgia as I had one "back in the day." PySerial is required. This cable connects to an RS232 serial port but is not an actual asynchronous serial device like the gray cable. The computer bit-bangs the modem control lines, toggling/reading several times per bit. The code is untested on a real UART (e.g. 16550) and is a bit hackish due to the limitations of PyUSB (modem control lines cannot be set at the same time except if the port is closed). I've tried several USB-to-RS232 adapters but have only had luck with FTDI ft2332r ones, and the speed is around 300 bytes/s. This is due to USB latency since several USB operations must happen per bit. Also remember that some ft232r adapters may not implement the necessary modem control lines in hardware. Homemade "$4 serial link" cables may work but are untested.

Your user will need access to the serial ports. This is often means the user should be in the "dialout" group.
 
 
  --- Other Notes, Some Being Important ---
  
 - Forward (/) and back (\) slashes can both be used between a folder and variable name on the calculator, but in most Linux shells "\" must be escaped. e.g.: "main\\myvar". I think it's easier just to use a forward slash: "main/myvar". I don't know how Windows behaves.

 - The TI-89 Titanium has now been tested and should work through its classic 2.5mm I/O port (not the USB port, although you can use a USB SilverLink cable). Only HW4 has been tested. There are no plans to support the USB port.
 
 - The TI-92-II, the TI-92 with Plus Module, and HW3 calcs are currently untested.
 
 - Not all physical-link/command/calc combinations have been tested. Most old AMS versions have not been tested.

 - When writing to computer, file extensions are added automatically; don't include them in filenames. When reading files from computer, full filenames should be used.
 
  - On most Linux-like environments you can use commands like "./link68.py put *" since "*" is expanded by the shell.

 - No calculator-type checking is performed when sending vars. That is, link68 is happy to send prog.92p to a TI-89. No adjustment is made to the variable data, but 68k calc variables are mostly compatible between calcs anyway, with exceptions including flash apps and ASM progs. Flash apps sent to the wrong calculator type will probably be rejected by the calculator at the end of transfer. This will essentially delete the existing version of the flash app from the calc.

 - Locked vars are problematic when in overwrite mode. Attempting to overwrite a locked var on the TI-92 seems to lead to a link timeout. Other calcs complain more gracefully.
 
  - Since the TI uses a modified ASCII character set to support Greek letters, etc., we currently convert these to their character codes in hex. For example, the mathtools package contains an expression named with two gammas on the calc. Link 68 will call it "+83+83" (83h being the code for a gamma in TI's charset). You can "./link68.py get mathtool/+83+83", and you will get the file "mathtool.+83+83.89e". If you send it back to the calculator it will have its original name. Var names and folders are stored in metadata and are not dependent on filenames, so feel free to rename your computer files (e.g. to remove the folder names).
  
   - Variable attributes (locked/unlocked, archived) are written to the computer files in what should be a TiLP compatible format (untested). Attributes are NOT restored when putting files to calculator which can lead to memory problems when restoring backups. This is the behavior of TI Graph Link since the link protocol for sending a var to the calc does not specify attributes. Programs seem to be an EXCEPTION. Locked programs are restored as locked which implies this information is stored in the raw variable data. The Link Guide does not seem to have information about this. Potential future support for remote control commands would allow us to change attributes after sending.
 
 
  --- Future Plans ---
  
  - Test on some older AMS versions and untested calcs (92 w+module, 92-II, HW3).
  - Polish code.
  - Better error checking & exception handling.
  - Support receiving flash files -- MAYBE.
  - Support remote commands -- MAYBE. Could be used to implement variable deletion, empty folder creation/deletion, archiving files when restoring a backup.
  
  
  --- Things I DON'T plan to do ---
  
   - Support the Z80 calculators or anything besides the 68k calcs.
   - Add a GUI.
   - Support for certificates or non-free apps.
   - Support CBL/CBR.
   - Support the TI-89 Titanium USB link port. I had assumed the USB port spoke the same protocol as the traditional I/O port, potentially with some extra wrapping. In reality it speaks an entirely different protocol (shared to large degree with the TI-84+ USB port), so supporting it is outside the scope of this project.


 --- WHY? ---
 
 Motivations for writing Link 68 include:
  - Programming practice: I haven't programmed anything complicated (besides LaTeX) in quite some time, so link68 was a chance to brush up on skills and learn more about Python.
  - I like using the 68k calcs and want to continue to use them in the future.
  - Historical preservation: The 68k calcs are end-of-life. TI will be phasing out the TI-89 Titanium if they're not already, and the TI-92 was over 25 years old when I started this project! Open source projects for supporting vintage platforms are critical to preserving computing history.
  - No fullish-featured, CLI linking program exists supporting all the 68k calcs.
  - I wanted a self-contained program with minimal dependencies.
  - I want to tinker with homebrew link cables.
  
  
 --- Thank You! ---
 
  - Tim Singer and Romain Liévin, authors of the Link Protocol Guide.
  - Other members of the TI-calculator hacking community who have posted useful information on various websites and message boards over the years.
  - TI for making an interesting calculating platform, regardless of their frequent ambivalence/animosity to the user and hacker communities.
 
 
 --- LICENSE ---
 
 Copyright (c) 2021 Joseph Herning

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

