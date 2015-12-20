import time
from CharLCD import CharLCD

		
def main(lcd):
	  # Main program block
	  # Initialise display
	 
	  # Toggle backlight on-off-on
	  lcd.backlight(True)
	  time.sleep(0.5)
	  lcd.backlight(False)
	  time.sleep(0.5)
	  lcd.backlight(True)
	  time.sleep(0.5)
	 
	  while True:
		# Send some centred test
		lcd.write("--------------------",1,'C')
		lcd.write("Rasbperry Pi",2,'C')
		lcd.write("Model B",3,'C')
		lcd.write("--------------------",4,'C')
	 
		time.sleep(3) # 3 second delay
	 
		lcd.write("Raspberrypi-spy",1,'L')
		lcd.write(".co.uk",2,'L')
		lcd.write("",3)
		lcd.write("20x4 LCD Module Test",4)
	 
		time.sleep(3) # 20 second delay
	 
		# Blank display
		lcd.clear()
	 
		time.sleep(3) # 3 second delay
		
lcd = CharLCD()
try:
	main(lcd)
except KeyboardInterrupt:
	pass
finally:
	lcd.clear()
	lcd.write("Goodbye!",2,'C')
		
