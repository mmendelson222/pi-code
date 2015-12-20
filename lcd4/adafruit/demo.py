import sys
import time
from Adafruit_CharLCD import Adafruit_CharLCD


def scroll():
	global lcd
	for x in range(0, 200):
		lcd.DisplayLeft()
		time.sleep(0.1)


message = sys.argv[1]
lcd = Adafruit_CharLCD()
lcd.begin(4,20)
lcd.clear()
lcd.message(message)
