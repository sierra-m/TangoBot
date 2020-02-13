import serial
from sys import version_info

PY2 = version_info[0] == 2   # Running Python 2.x?


# ---------------------------
# Maestro Servo Controller
# ---------------------------
#
# Support for the Pololu Maestro line of servo controllers
#
# Steven Jacobs -- Aug 2013
# https://github.com/FRC4564/Maestro/
#
# These functions provide access to many of the Maestro's capabilities using the
# Pololu serial protocol
#
# Edited by Sierra MacLeod to conform to PEP
# This is Python, we're not savages


class Controller:
    # When connected via USB, the Maestro creates two virtual serial ports
    # /dev/ttyACM0 for commands and /dev/ttyACM1 for communications.
    # Be sure the Maestro is configured for "USB Dual Port" serial mode.
    # "USB Chained Mode" may work as well, but hasn't been tested.
    #
    # Pololu protocol allows for multiple Maestros to be connected to a single
    # serial port. Each connected device is then indexed by number.
    # This device number defaults to 0x0C (or 12 in decimal), which this module
    # assumes.  If two or more controllers are connected to different serial
    # ports, or you are using a Windows OS, you can provide the tty port.  For
    # example, '/dev/ttyACM2' or for Windows, something like 'COM3'.
    def __init__(self, tty_str='/dev/ttyACM0', device=0x0c):
        # Open the command port
        self.usb = serial.Serial(tty_str)
        # Command lead-in and device number are sent for each Pololu serial command.
        self.pololu_cmd = chr(0xaa) + chr(device)
        # Track target position for each servo. The function is_moving() will
        # use the Target vs Current servo position to determine if movement is
        # occurring.  Upto 24 servos on a Maestro, (0-23). Targets start at 0.
        self.Targets = [0] * 24
        # Servo minimum and maximum targets can be restricted to protect components.
        self.mins = [0] * 24
        self.maxes = [0] * 24
        
    # Cleanup by closing USB serial port
    def close(self):
        self.usb.close()

    # Send a Pololu command out the serial port
    def send_cmd(self, cmd):
        cmd_str = self.pololu_cmd + cmd
        if PY2:
            self.usb.write(cmd_str)
        else:
            self.usb.write(bytes(cmd_str, 'latin-1'))

    # Set channels min and max value range.  Use this as a safety to protect
    # from accidentally moving outside known safe parameters. A setting of 0
    # allows unrestricted movement.
    #
    # ***Note that the Maestro itself is configured to limit the range of servo travel
    # which has precedence over these values.  Use the Maestro Control Center to configure
    # ranges that are saved to the controller.  Use set_range for software controllable ranges.
    def set_range(self, chan, min, max):
        self.mins[chan] = min
        self.maxes[chan] = max

    # Return Minimum channel range value
    def get_min(self, chan):
        return self.mins[chan]

    # Return Maximum channel range value
    def get_max(self, chan):
        return self.maxes[chan]
        
    # Set channel to a specified target value.  Servo will begin moving based
    # on Speed and Acceleration parameters previously set.
    # Target values will be constrained within Min and Max range, if set.
    # For servos, target represents the pulse width in of quarter-microseconds
    # Servo center is at 1500 microseconds, or 6000 quarter-microseconds
    # Typically valid servo range is 3000 to 9000 quarter-microseconds
    # If channel is configured for digital output, values < 6000 = Low output
    def set_target(self, chan, target):
        # if Min is defined and Target is below, force to Min
        if self.mins[chan] > 0 and target < self.mins[chan]:
            target = self.mins[chan]
        # if Max is defined and Target is above, force to Max
        if 0 < self.maxes[chan] < target:
            target = self.maxes[chan]
        #    
        lsb = target & 0x7f  # 7 bits for least significant byte
        msb = (target >> 7) & 0x7f  # shift 7 and take next 7 bits for msb
        cmd = chr(0x04) + chr(chan) + chr(lsb) + chr(msb)
        self.send_cmd(cmd)
        # Record Target value
        self.Targets[chan] = target
        
    # Set speed of channel
    # Speed is measured as 0.25microseconds/10milliseconds
    # For the standard 1ms pulse width change to move a servo between extremes, a speed
    # of 1 will take 1 minute, and a speed of 60 would take 1 second.
    # Speed of 0 is unrestricted.
    def set_speed(self, chan, speed):
        lsb = speed & 0x7f  # 7 bits for least significant byte
        msb = (speed >> 7) & 0x7f  # shift 7 and take next 7 bits for msb
        cmd = chr(0x07) + chr(chan) + chr(lsb) + chr(msb)
        self.send_cmd(cmd)

    # Set acceleration of channel
    # This provide soft starts and finishes when servo moves to target position.
    # Valid values are from 0 to 255. 0=unrestricted, 1 is slowest start.
    # A value of 1 will take the servo about 3s to move between 1ms to 2ms range.
    def set_accel(self, chan, accel):
        lsb = accel & 0x7f  # 7 bits for least significant byte
        msb = (accel >> 7) & 0x7f  # shift 7 and take next 7 bits for msb
        cmd = chr(0x09) + chr(chan) + chr(lsb) + chr(msb)
        self.send_cmd(cmd)
    
    # Get the current position of the device on the specified channel
    # The result is returned in a measure of quarter-microseconds, which mirrors
    # the Target parameter of set_target.
    # This is not reading the true servo position, but the last target position sent
    # to the servo. If the Speed is set to below the top speed of the servo, then
    # the position result will align well with the actual servo position, assuming
    # it is not stalled or slowed.
    def get_position(self, chan):
        cmd = chr(0x10) + chr(chan)
        self.send_cmd(cmd)
        lsb = ord(self.usb.read())
        msb = ord(self.usb.read())
        return (msb << 8) + lsb

    # Test to see if a servo has reached the set target position.  This only provides
    # useful results if the Speed parameter is set slower than the maximum speed of
    # the servo.  Servo range must be defined first using set_range. See set_range comment.
    #
    # ***Note if target position goes outside of Maestro's allowable range for the
    # channel, then the target can never be reached, so it will appear to always be
    # moving to the target.  
    def is_moving(self, chan):
        if self.Targets[chan] > 0:
            if self.get_position(chan) != self.Targets[chan]:
                return True
        return False
    
    # Have all servo outputs reached their targets? This is useful only if Speed and/or
    # Acceleration have been set on one or more of the channels. Returns True or False.
    # Not available with Micro Maestro.
    def get_moving_state(self):
        cmd = chr(0x13)
        self.send_cmd(cmd)
        if self.usb.read() == chr(0):
            return False
        else:
            return True

    # Run a Maestro Script subroutine in the currently active script. Scripts can
    # have multiple subroutines, which get numbered sequentially from 0 on up. Code your
    # Maestro subroutine to either infinitely loop, or just end (return is not valid).
    def run_script_sub(self, sub_number):
        cmd = chr(0x27) + chr(sub_number)
        # can pass a param with command 0x28
        # cmd = chr(0x28) + chr(subNumber) + chr(lsb) + chr(msb)
        self.send_cmd(cmd)

    # Stop the current Maestro Script
    def stop_script(self):
        cmd = chr(0x24)
        self.send_cmd(cmd)


