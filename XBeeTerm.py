
"""XBeeTerm.py is a XBee serial command shell for interacting with XBee radios

    This command interpretors establishes communications with XBee radios so that AT Commands can be sent to the XBee.
    The interpretors output is color coded to help distinguish user input, from XBee radio output, and from
    interpretors output. This command-line interpretor uses Python module Cmd, and therefore, inherit bash-like history-list
    editing (e.g. Control-P or up-arrow scrolls back to the last command, Control-N or down-arrow forward to the next one,
    Control-F or right-arrow moves the cursor to the right non-destructively, Control-B or left-arrow moves the cursor
    to the left non-destructively, etc.).

    XBeeTerm is not a replacement for the Digi X-CTU program but a utility program for the Linux environment.  You can pipe
    scripts of XBee configuration commands, making it easy to multiple radios.  Also, XBeeTerm wait for the arrival of a
    XBee data packet, print the XBee frame, and wait for the next packet, much like a packet sniffer.

    XBeeTerm Commands:
        baudrate <rate>     set the baud rate at which you will communicate with the XBee radio
        serial <device>     set the serial device that the XBee radio is attached
        term                wait for the arrive serial data, prints it, and sends keyboard input as serial data
        watch               wait for the arrival of a XBee data packet, print it, wait for the next
        shell or !          pause the interpreter and invoke command in Linux shell
        exit or EOF         exit the XBeeTerm
        help or ?           prints out short discription of the commands (similar to the above)

    Just like the Digi X-CTU program, the syntax for the AT commands are:
        AT+ASCII_Command+Space+Optional_Parameter+Carriage_Return
        Example: ATDL 1F<CR>

    Example Session:
        baudrate 9600        # (XBeeTerm command) set the baudrate used to comm. with the XBee
        serial /dev/ttyUSB0  # (XBeeTerm command) serial device which has the XBee radio
        +++                  # (XBee command) enter AT command mode on the XBee
        ATRE                 # (XBee command) restore XBee to factory settings
        ATAP 2               # (XBee command) enable API mode with escaped control characters
        ATCE 0               # (XBee command) make this XBee radio an end device
        ATMY AAA1            # (XBee command) set the address of this radio to eight byte hex
        ATID B000            # (XBee command) Set the PAN ID to eight byte hex
        ATCH 0E              # (XBee command) set the Channel ID to a four byte hex
        ATPL 0               # (XBee command) power level at which the RF module transmits
        ATWR                 # (XBee command) write all the changes to the XBee non-volatile memory
        ATFR                 # (XBee command) reboot XBee radio
        exit                 # (XBeeTerm command) exit python shell

    Reference Materials:
        XBee 802.15.4 (Series 1) Module Product Manual (section 3: RF Module Configuration)
            ftp://ftp1.digi.com/support/documentation/90000982_A.pdf
        python-xbee Documentation: Release 2.0.0, Paul Malmsten, December 29, 2010
            http://python-xbee.googlecode.com/files/XBee-2.0.0-Documentation.pdf
        cmd - Support for line-oriented command interpreters
            http://docs.python.org/2/library/cmd.html
        cmd - Create line-oriented command processors
            http://bip.weizmann.ac.il/course/python/PyMOTW/PyMOTW/docs/cmd/index.html
        Easy command-line applications with cmd and cmd2
            http://pyvideo.org/video/306/pycon-2010--easy-command-line-applications-with-c

    Originally Created By:
        Portions of this created by Amit Snyderman (amit@amitsnyderman.com) &
        Paul Malmsten (pmalmsten@gmail.com) and taken from
        https://github.com/sensestage/xbee-tools
        http://code.google.com/p/python-xbee/

    Modified By:
        Jeff Irland (jeff.irland@gmail.com) in January 2013
"""

# imported modules
import os                   # portable way of using operating system dependent functionality
import sys                  # provides access to some variables used or maintained by the interpreter
import time                 # provides various time-related functions
import cmd                  # provides a simple framework for writing line-oriented command interpreters
import serial               # encapsulates the access for the serial port
import argparse             # provides easy to write and user-friendly command-line interfaces
from xbee import XBee       # implementation of the XBee serial communication API
from pretty import switchColor, printc  # provides colored text for xterm & VT100 type terminals using ANSI escape sequences

# authorship information
__author__ = "Jeff Irland"
__copyright__ = "Copyright 2013"
__credits__ = "Amit Snyderman, Marije Baalman, Paul Malmsten"
__license__ = "GNU General Public License"
__version__ = "0.2"
__maintainer__ = "Jeff Irland"
__email__ = "jeff.irland@gmail.com"
__status__ = "Development"
__python__ = "Version 2.7.3"

# text colors to be used during terminal sessions
ERROR_TEXT = 'bright red'
CMD_INPUT_TEXT = 'normal'
CMD_OUTPUT_TEXT = 'bright yellow'
XBEE_OUTPUT_TEXT = 'red'
SHELL_OUTPUT_TEXT = 'bright cyan'
WATCH_OUTPUT_TEXT = 'bright green'
TERM_OUTPUT_TEXT = 'purple'
TERM_INPUT_TEXT = 'bright purple'


class ArgsParser():
    """Within this object class you should load all the command-line switches, parameters, and arguments to operate this utility"""
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="This command interpretors establishes communications with XBee radios so that AT Commands can be sent to the XBee.  It can be used to configure or query the XBee radio", epilog="This utility is primarily intended to change the AT Command parameter values, but could be used to query for the parameter values.")
        self.optSwitches()
        self.reqSwitches()
        self.optParameters()
        self.reqParameters()
        self.optArguments()
        self.reqArguments()

    def optSwitches(self):
        """optional switches for the command-line"""
        self.parser.add_argument("--version", action="version", version=__version__, help="print version number on stdout and exit")
        self.parser.add_argument("-v", "--verbose", action="count", help="produce verbose output for debugging")

    def reqSwitches(self):
        """required switches for the command-line"""
        pass

    def optParameters(self):
        """optional parameters for the command-line"""
        self.parser.add_argument("-b", "--baudrate", required=False, action="store", metavar="RATE", type=int, default=9600, help="baud rate used to communicate with the XBee radio")
        self.parser.add_argument("-p", "--device", required=False, action="store", metavar="DEV", type=str, default='/dev/ttyUSB0', help="open this serial port or device to communicate with the XBee radio")

    def reqParameters(self):
        """required parameters for the command-line"""
        pass

    def optArguments(self):
        """optional arguments for the command-line"""
        self.parser.add_argument(nargs="*", action="store", dest="inputs", default=None, help="XBeeTerm script file with AT Commands to be executed")

    def reqArguments(self):
        """required arguments for the command-line"""
        pass

    def args(self):
        """return a object containing the command-line switches, parameters, and arguments"""
        return self.parser.parse_args()


class XBeeShell(cmd.Cmd):
    def __init__(self, baudrate=None, device=None, inputFile=None):
        cmd.Cmd.__init__(self)
        self.serial = serial.Serial()
        if baudrate is not None and device is not None:
            self.serial.port = device
            self.serial.baudrate = baudrate
            self.serial.open()
        if inputFile is None:
            self.intro = "Command-Line Interpreter for Configuring and Communicate with XBee Radios"
            self.prompt = "xbee% "
        else:
            self.intro = "Configuring XBee Radios via command file"
            self.prompt = ""            # Do not show a prompt after each command read
            sys.stdin = inputFile

    def default(self, p):
        """Command is assumed to be an AT Commands for the XBee radio"""
        if not self.serial.isOpen():
            print "You must set a serial port first."
        else:
            if p == '+++':
                self.serial.write('+++')
                time.sleep(2)
            else:
                self.serial.write('%s\r' % p)
                time.sleep(0.5)

            output = ''
            while self.serial.inWaiting():
                output += self.serial.read()
            if output == '':
                print 'XBee timed out, so reissue "+++". (Or maybe XBee doesn\'t understand "%s".)' % p
            else:
                switchColor(XBEE_OUTPUT_TEXT)
                print output.replace('\r', '\n').rstrip()

    def emptyline(self):
        """method called when an empty line is entered in response to the prompt"""
        return None        # do not repeat the last nonempty command entered

    def precmd(self, p):
        """executed just before the command line line is interpreted"""
        switchColor(CMD_OUTPUT_TEXT)
        return cmd.Cmd.precmd(self, p)

    def postcmd(self, stop, p):
        """executed just after a command dispatch is finished"""
        switchColor(CMD_INPUT_TEXT)
        return cmd.Cmd.postcmd(self, stop, p)

    def do_baudrate(self, p):
        """Set the baud rate used to communicate with the XBee"""
        self.serial.baudrate = p
        print 'baudrate set to %s' % self.serial.baudrate

    def do_serial(self, p):
        """Linux serial device path to the XBee radio (e.g. /dev/ttyUSB0)"""
        try:
            self.serial.port = p
            self.serial.open()
            print 'Successfully opened serial port %s' % p
        except Exception:
            print 'Unable to open serial port %s' % p

    def do_shell(self, p):
        """Pause the interpreter and invoke command in Linux shell"""
        print "running shell command: ", p
        switchColor(SHELL_OUTPUT_TEXT)
        print os.popen(p).read()

    def do_term(self, p):
        """Assuming you have setup XBee modems to communicate in a point-to-point mode, the interpretor will establish a serial terminal interface to the XBee.  Data arriving at XBee will be printed and characters entered at the keyboard will be sent via the XBee."""
        if not self.serial.isOpen():
            print "You must set a serial port first."
        else:
            print "Entering \"term\" mode (Ctrl-C to abort)..."
            try:
                #self.serial.timeout = 0
                while True:
                    # read a line from XBee and convert it from b'xxx\r\n' to xxx
                    switchColor(TERM_OUTPUT_TEXT)
                    line = self.serial.readline().decode('utf-8')[:-2]
                    if line:
                        print line
                    # read data from the keyboard and send via the XBee modem
                    switchColor(TERM_INPUT_TEXT)
                    line = sys.stdin.readline()
                    self.serial.writelines(line)
                    self.serial.flush()
                    """
                    output = ''
                    while self.serial.inWaiting():
                        output += self.serial.read()
                    if output == '':
                        print 'XBee timed out, so reissue "+++". (Or maybe XBee doesn\'t understand "%s".)' % p
                    else:
                        print output.replace('\r', '\n').rstrip()
                    """
            except KeyboardInterrupt:
                printc("\n*** Ctrl-C keyboard interrupt ***", ERROR_TEXT)
            finally:
                switchColor(WATCH_OUTPUT_TEXT)

    def do_watch(self, p):
        """Assuming you have set the XBee to data mode, wait for the arrival of a XBee data packet, print it when it arrives, and wait for the next packet."""
        if not self.serial.isOpen():
            print "You must set a serial port first."
        else:
            print "Entering \"watch\" mode (Ctrl-C to abort)..."
            ser = serial.Serial(self.serial.port, self.serial.baudrate)     # Open XBee serial port
            xbee = XBee(ser)                        # Create XBee object to manage packets
            dispatch = Dispatch(xbee=xbee)          # Start the dispatcher that will call packet handlers
            switchColor(WATCH_OUTPUT_TEXT)
            try:
                dispatch.run()    # run() will loop infinitely while waiting for and processing packets which arrive.
            except KeyboardInterrupt:
                printc("\n*** Ctrl-C keyboard interrupt ***", ERROR_TEXT)
            ser.close()
            switchColor(WATCH_OUTPUT_TEXT)
            # while 1:
                # packet = xbee.find_packet(self.serial)
                # if packet:
                    # xb = xbee(packet)
                    # print xb

    def do_exit(self, p):
        """Exits from the XBee serial terminal"""
        self.serial.close()
        print "Exiting", os.path.basename(__file__)
        return True

    def do_EOF(self, p):
        """EOF (end-of-file) or Ctrl-D will return True and drops out of the interpreter"""
        self.serial.close()
        print "Exiting", os.path.basename(__file__)
        return True

    def help_help(self):
        """Print help messages for command arguments"""
        print 'help\t\t', self.help_help.__doc__
        print 'serial <dev>\t', self.do_serial.__doc__
        print 'baudrate <rate>', self.do_baudrate.__doc__
        print 'watch\t\t', self.do_watch.__doc__
        print 'term\t\t', self.do_term.__doc__
        print 'shell <cmd>\t', self.do_shell.__doc__
        print 'EOF or Ctrl-D\t', self.do_EOF.__doc__
        print 'exit\t\t', self.do_exit.__doc__


class Dispatch(object):
    """For the "watch" command, this provides the Dispatch class, which allows one to filter
    incoming data packets from an XBee device and call an appropriate method when one arrives."""
    def __init__(self, ser=None, xbee=None):
        self.xbee = None
        if xbee:
            self.xbee = xbee
        elif ser:
            self.xbee = XBee(ser)
        self.handlers = []
        self.names = set()

    def register(self, name, callback, filter):
        """register: string, function: string, data -> None, function: data -> boolean -> None

        Register will save the given name, callback, and filter function for use when a packet arrives.
        When one arrives, the filter function will be called to determine whether to call its associated
        callback function. If the filter method returns true, the callback method will be called
        with its associated name string and the packet which triggered the call."""
        if name in self.names:
            raise ValueError("A callback has already been registered with the name '%s'" % name)
        self.handlers.append({'name': name, 'callback': callback, 'filter': filter})
        self.names.add(name)

    def run(self, oneshot=False):
        """run: boolean -> None

        run will read and dispatch any packet which arrives from the XBee device"""
        if not self.xbee:
            raise ValueError("Either a serial port or an XBee must be provided to __init__ to execute run()")
        while True:
            self.dispatch(self.xbee.wait_read_frame())
            if oneshot:
                break

    def dispatch(self, packet):
        """dispatch: XBee data dict -> None

        When called, dispatch checks the given packet against each registered callback
        method and calls each callback whose filter function returns true."""
        for handler in self.handlers:
            if handler['filter'](packet):
                handler['callback'](handler['name'], packet)    # Call the handler method with its associated name and the packet which passed its filter check


# Enter into XBee command-line processor
if __name__ == '__main__':
    # parse the command-line for switches, parameters, and arguments
    parser = ArgsParser()           # create parser object for the command-line
    args = parser.args()            # get list of command line arguments, parameters, and switches

    if args.verbose > 0:            # print what is on the command-line
        print os.path.basename(__file__), "command-line arguments =", args.__dict__

    # process the command-line arguments (i.e. script file) and start the command shell
    if len(args.inputs) == 0:       # there is no script file
        shell = XBeeShell(baudrate=args.baudrate, device=args.device)
        shell.cmdloop()
    else:                           # there is a script file on the command-line
        if len(args.inputs) > 1:
            print os.path.basename(__file__), "will process only the first command-line argument."
        if os.path.exists(args.inputs[0]):
            inputFile = open(args.inputs[0], 'rt')
            shell = XBeeShell(baudrate=args.baudrate, device=args.device, inputFile=inputFile)
            shell.cmdloop()
        else:
            print 'File "%s" doesn\'t exist. Program terminated.' % args.inputs[0]
