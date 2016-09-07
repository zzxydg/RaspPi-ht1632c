# RaspberryPi HT1632C

A repository for all things Raspberry Pi and related to HT1632C LED Driver

The first project this contains is an HT1632C LED Driver.

The LED module can be found for less than 10 GBP from a popular auction site including worldwide shipping from China.
This module has one great advantage over similar modules in that each LED is memory mapped and does not need to be constantly refreshed, so the burden on the CPU can be much reduced and timing is not critical.

The code I have uploaded is an early prototype for driving two of these displays directly from a Raspberry Pi using "bit-banging".  The modules are meant to be compatible with SPI, but this proved troublesome hence the bit banging.

- HT1632C_LEDDriver.py contains a class with the code to drive the module
- HT1632CFontLib.py contains the Font Class needed generate the text bitmaps.
- HT1632C-test.py is a simple set of test functions.

Do look at the list of imports to make sure you have the right python libraries installed and because it uses GPIO you will need to sudo when running from the command line to get the permissions needed to write to the ports.

Tested on Raspbery Pi Module B (original) but should work on any Raspberry Pi

A demo of the board can be found on YouTube here: https://youtu.be/oh6qLsTQRNE

Enjoy!
