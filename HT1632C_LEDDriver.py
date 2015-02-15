import RPi.GPIO as GPIO
import time
import traceback
from HT1632CFontLib import *
import random

# Constants for LED commands
COMMAND = 0x8000
DATA = 0xA000
SYS_DIS = 0x00
SYS_EN = 0x01
LED_OFF = 0x02
LED_ON = 0x03
BLINK_OFF = 0x08
BLINK_ON = 0x09
SLAVE_MODE = 0x10
RC_MASTER_MODE = 0x18
EXT_CLK_MASTER_MODE = 0x1C
COMMON_8NMOS = 0x20
PWM16 = 0xAF

BOARD0 = 0x00
BOARD1 = 0x01

# --------------------------------------------------------------------------------------------
# A class that implements simple function to contract a HT1632C LED Matrix
# --------------------------------------------------------------------------------------------
class HT1632C_LEDDriver:

    # --------------------------------------------------------------------------------------------
    # Name: __init__
    # Description: The initialization function for the class
    #
    # Inputs:
    # TheWRPin - The RaspberryPi GPIO line the HT1632C (Board0 & Board1) WR line is connected to
    # TheDataPin - The RaspberryPi GPIO line the HT1632C (Board0 & Board1) DATA line is connected to
    # TheCS0Pin - The RaspberryPi GPIO line the HT1632C (Board0) CS line is connected to, 0 if not used
    # TheCS1Pin - The RaspberryPi GPIO line the HT1632C (Board1) CS line is connected to, 0 if not used
    #
    # Method:
    # Sets up the direction of the GPIO pins then initialises the HT1632C
    #
    # Outputs: None
    # --------------------------------------------------------------------------------------------
    def __init__(self, TheWRPin, TheDataPin, TheCS0Pin, TheCS1Pin):

        self.TheWRPin = TheWRPin
        self.TheDataPin = TheDataPin
        self.TheCS0Pin = TheCS0Pin
        self.TheCS1Pin = TheCS1Pin

        # Setup the GPIO lines
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.TheWRPin, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(self.TheDataPin, GPIO.OUT, initial=GPIO.LOW)

        if (self.TheCS0Pin != 0):
            GPIO.setup(self.TheCS0Pin, GPIO.OUT, initial=GPIO.HIGH)
        #endif

        if (self.TheCS1Pin != 0):
            GPIO.setup(self.TheCS1Pin, GPIO.OUT, initial=GPIO.HIGH)
        #endif

        # Init the LED Matrix (board0 & board1)
        if (self.TheCS0Pin != 0):
            self.InitHT1632CDisplay(BOARD0)
        #endif

        if (self.TheCS1Pin != 0):
            self.InitHT1632CDisplay(BOARD1)
        #endif

        #Import Font for text
        self.Font = TerminalFont

        return
    #enddef

    # --------------------------------------------------------------------------------------------
    # Name: InitHT1632CDisplay
    # Description: The initialization function for the LED Matrix
    #
    # Inputs:
    # TheBoard = The HT1632C to initi (BOARD0 or BOARD1)
    #
    # Method:
    # Sets up the HT1632C LED Matrix, sequence and codes taken from the Datasheet and Arduino
    # example https://github.com/gauravmm/HT1632-for-Arduino
    #
    # Outputs: None
    # --------------------------------------------------------------------------------------------
    def InitHT1632CDisplay(self, TheBoard):
        self.WriteCommand(SYS_DIS, TheBoard)
        self.WriteCommand(COMMON_8NMOS, TheBoard)
        self.WriteCommand(SYS_EN, TheBoard)
        self.WriteCommand(LED_ON, TheBoard)
        self.WriteCommand(PWM16, TheBoard)
        time.sleep(0.1)                     # Might not be needed, but works!
        return
    #enddef

    # --------------------------------------------------------------------------------------------
    # Name: ClearScreen
    # Description: Clears (switches off) all the LEDs on the Matrix
    #
    # Inputs: None
    #
    # Method:
    # Writes out 0x00 to all addresses to switch off any LEDs that are on
    #
    # Outputs: None
    # --------------------------------------------------------------------------------------------
    def ClearScreen(self):
        for i in range(0, 128, 2):
            self.WriteDataByte(i, 0x00)          # write out 0x00 to all LED addresses
        #endfor
        return
    #enddef

    # --------------------------------------------------------------------------------------------
    # Name: POST
    # Description: Does a quick Power On Self Test by switching on all LEDs then off again
    #
    # Inputs: None
    #
    # Method:
    # Writes 0xFF to all addresses to switch on all LED, then writes 0x00 to switch all off
    #
    # Outputs: None
    # --------------------------------------------------------------------------------------------
    def POST(self):

        for i in range(0, 128, 2):       # because full columns are being populated addresses are even (0x00, 0x02, 0x04 ... 0x7F)
            self.WriteDataByte(i, 0xFF)
        #endfor

        time.sleep(0.1)

        for i in range(0, 128, 2):       # because full columns are being populated addresses are even (0x00, 0x02, 0x04 ... 0x7F)
            self.WriteDataByte(i, 0x00)
        #endfor

        return
    #enddef

    # --------------------------------------------------------------------------------------------
    # Name: DisplayString
    # Description: Writes out a string to the LED Matrix, if the string is longer than five chars
    # only the first five are fully written, the sixth is partially written.  If the second board is
    # connected then writing continues onto this.
    #
    # Inputs:
    # TheString - The string to write out to the LEd Matrix
    # StartCol - The column to start writing the string to [0..64]
    #
    # Method:
    # Looks up the LED pattern for the string character and writes it out to the LED Matrix
    #
    # Outputs: None
    # --------------------------------------------------------------------------------------------
    def DisplayString(self, TheString, StartCol):

        # Columns start at even addresses, so multiply by two
        currentColumn = (StartCol * 2)

        for c in TheString:
            #Get the ascii value and then subtract 32 as the font does not have any characters before the 32nd implemented.
            fontIndex = ord(c) - 32
            self.WriteFontCharacter(self.Font[fontIndex], currentColumn)
            currentColumn += 12         # six characters or 12 columns have been written, so increment
        #endfor
        return
    #enddef

    # --------------------------------------------------------------------------------------------
    # Name: ScrollString
    # Description: Writes out a string to the LED Matrix and scrolls it based on arguments
    #
    # Inputs:
    # TheString - The string to write out to the LED Matrix
    # TheSpeed - The scroll speed, range 1 to 1000000: 1=slowest; 1000000=fastest
    # TheCycles - The number of times to display the message, range 1 to 100000
    #
    # Method:
    # Uses the DisplayString() function to write out the string and adjusts the StartCol
    # to give the illusion of scrolling
    #
    # Outputs: None
    # --------------------------------------------------------------------------------------------
    def ScrollString(self, TheString, TheSpeed, TheCycles):

    # Each character consumes 6 columns, so multiple by to get length
        StringColLength = len(TheString) * -6

        for x in range(0, TheCycles):
            for i in range(0, StringColLength, -1):
                self.DisplayString(TheString, i)
                time.sleep(1.0 / TheSpeed)
            #endfor
        #endfor

        return
    #enddef

    # --------------------------------------------------------------------------------------------
    # A Function to swap the bits in the passed value, useful for serial output of Bytes
    # adapted from an article here:-
    # http://stackoverflow.com/questions/11725343/implementing-a-bit-swap-hack-in-python
    #
    # Input: Value to reverse
    # Return: The reverse of that value
    # --------------------------------------------------------------------------------------------
    def swapbits(self, b):
        return (b * 0x0202020202 & 0x010884422010) % 1023
    #enddef

    # --------------------------------------------------------------------------------------------
    # Name: WriteFontCharacter
    # Description: Writes out a six bytes to the LED Matrix to represent the character
    # to ensure spaces between the characters a blank column (0x00) is written out after
    # the last column of the character.  The bits of the font need to be swapped so that
    # MSB is sent out first and LSB last
    #
    # Inputs:
    # TheChar - An array of five bytes, that represent the columns of the font, to write out
    # AddressColumn - The address to write the five bytes out
    #
    # Method:
    # Uses the WriteDataByte() write out the byte that represents the column
    #
    # Outputs: None
    # --------------------------------------------------------------------------------------------
    def WriteFontCharacter(self, TheChar, AddressColumn):

        bytestream = TheChar

        i = AddressColumn

        # Write out the five bytes for the font
        for b in bytestream:
            self.WriteDataByte(i, self.swapbits(b))
            i += 2
        #endfor

        # Write out a blank column to space them
        self.WriteDataByte(i, 0x00)
        return
    #enddef

    # --------------------------------------------------------------------------------------------
    # Name: WriteCommand
    # Description: Writes out a single command to the LED Matrix, forming the correct word pattern
    #
    # Inputs:
    # TheCommand - The command code to send to the LED Matrix
    # TheBoard - The board to write to (BOARD0 or BOARD1)
    #
    # Method:
    # Uses the WriteTheWord() to send the command to the LED Matrix
    #
    # Outputs: None
    # --------------------------------------------------------------------------------------------
    def WriteCommand(self, TheCommand, TheBoard):
        TheWord = COMMAND | (TheCommand << 5)

        if (TheBoard == BOARD0):
            self.WriteTheWord(TheWord, 12, self.TheCS0Pin)
        elif (TheBoard == BOARD1):
            self.WriteTheWord(TheWord, 12, self.TheCS1Pin)
        else:
            print("WriteCommand(self, TheCommand, TheBoard)::Invalid board specified!")
            return
        #endif
        return
    #enddef

    # --------------------------------------------------------------------------------------------
    # Name: WriteDataNibble
    # Description: Writes out half a column of data to the Matrix, forming the correct word
    #
    # Inputs:
    # TheAddress - The address to write the nibble to [0..127] values outside of this range are
    # ignored
    #
    # Method:
    # Uses the WriteTheWord() to send the command to the LED Matrix
    #
    # Outputs: None
    # --------------------------------------------------------------------------------------------
    def WriteDataNibble(self, TheAddress, TheDataNibble):

        if ((TheAddress >= 0) & (TheAddress <= 0x3F)):
            TheWord = DATA | ((TheAddress & 0x3F) << 6) | ((TheDataNibble & 0x0F) << 2)
            self.WriteTheWord(TheWord, 14, self.TheCS0Pin)
        #endif

        if ((TheAddress >= 0x40) & (TheAddress <= 0xFF)):
            TheWord = DATA | ((TheAddress & 0x3F) << 6) | ((TheDataNibble & 0x0F) << 2)
            self.WriteTheWord(TheWord, 14, self.TheCS1Pin)
        #endif

        return
    #enddef

    # --------------------------------------------------------------------------------------------
    # Name: WriteDataByte
    # Description: Writes out a full column of data to the Matrix, forming the correct word
    #
    # Inputs:
    # TheAddress - The address to write the nibble to [0..127] values outside of this range are
    # ignored, because a full column is written the address must be even, odd addresses will cause
    # only half the word to be shown in the column, with the other half in the next column
    #
    # Method:
    # Uses the WriteTheWord() send the command to the LED Matrix
    #
    # Outputs: None
    # --------------------------------------------------------------------------------------------
    def WriteDataByte(self, TheAddress, TheDataByte):

        if ((TheAddress >= 0) & (TheAddress <= 0x3F)):
            TheWord = (DATA << 2) | ((TheAddress & 0x3F) << 8) | (TheDataByte & 0xFF)
            self.WriteTheWord(TheWord, 18, self.TheCS0Pin)
        #endif

        if ((TheAddress >= 0x40) & (TheAddress <= 0x7F)):
            TheWord = (DATA << 2) | ((TheAddress & 0x3F) << 8) | (TheDataByte & 0xFF)
            self.WriteTheWord(TheWord, 18, self.TheCS1Pin)
        #endif
        return
    #enddef

    # --------------------------------------------------------------------------------------------
    # Name: WriteTheWord
    # Description: Writes out a 18, 14 or 12 bit word to the LED Matrix
    #
    # Inputs:
    # TheWord - The word to write to the LED Matrix (integer, 16 bits only, unused bits set to zero)
    # BitsToWrite - The length of the word to write to the Matrix.
    # 18 bits for a full column: 3 ID + 7 ADDRESS + 8 DATA
    # 14 bits for a half column: 3 ID + 7 ADDRESS + 4 DATA
    # 12 bits for a command    : 3 ID + 8 COMMAND + BLANK
    # TheCSPin - The CS pin to use for writing to the HT1632C, allows multiple boards to be used
    #
    # Method:
    # Writes out the bits directly to the LED Matrix using the CS, WR and DATA lines
    #
    # Outputs: None
    # --------------------------------------------------------------------------------------------
    def WriteTheWord(self, TheWord, BitsToWrite, TheCSPin):

        if (TheCSPin == 0):
            print("WriteTheWord(TheWord, BitsToWrite, TheCSPin)::TheCSPin cannot be zero!")
            return
        #endif

        GPIO.output(self.TheWRPin, GPIO.HIGH)       # WR high to start the write cycle

        GPIO.output(TheCSPin, GPIO.LOW)             # Pull CS Low to start cycle

        # Command is 12 bits; NibbleData is 14 bits; ByteData is 18 bits -- we are bit banging so
        # only output what is needed, as it is faster!
        if (BitsToWrite == 18):
            Start=17
            Stop=-1
        elif (BitsToWrite == 14):
            Start=15
            Stop=1
        elif (BitsToWrite == 12):
            Start=15
            Stop=3
        else:
            print("WriteTheWord(TheWord, BitsToWrite, TheCSPin)::Invalid Word Length!")
            return
        #endif

        for i in range(Start, Stop, -1):            # MSB has to go first, LSB last so do it in reverse order

            TheMask = pow(2, i)                     # Generate the bit mask

            if (TheWord & TheMask == TheMask):
                TheBit = 1
            else:
                TheBit = 0
            #endif

            GPIO.output(self.TheDataPin, TheBit)   # Send the bit
            GPIO.output(self.TheWRPin, GPIO.LOW)   # WR low to clock into the device
            GPIO.output(self.TheWRPin, GPIO.HIGH)  # WR high to end the write cycle
        #endfor

        GPIO.output(TheCSPin, GPIO.HIGH)            # Pull CS High to finish cycle

        return
    #enddef

    # --------------------------------------------------------------------------------------------
    # Name: __del__
    # Description: The destructor function for the class
    #
    # Inputs: None
    #
    # Method:
    # Clears the screen to remove any remaining pixels to reduce power consumption and releases
    # the GPIO pins
    #
    # Outputs: None
    # --------------------------------------------------------------------------------------------
    def __del__(self):
        self.ClearScreen()                      # Clear the screen to finish, otherwise LED left on!
        GPIO.cleanup()                          # Release all GPIO lines
        return
    #enddef

#endclass
