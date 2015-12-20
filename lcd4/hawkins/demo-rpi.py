import os
import rpi
import sys

lcd = rpi
lcd.lcd_init()
lcd.lcd_write(sys.argv[1], 2)
