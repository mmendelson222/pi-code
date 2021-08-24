# use an i2c rotary switch (with pushbutton) to rotate through lines of text

import time
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import digitalio as dio
from adafruit_seesaw import seesaw, rotaryio, digitalio

seesaw = seesaw.Seesaw(board.I2C(), addr=0x36)

# Create the SSD1306 OLED class.
# The first two parameters are the pixel width and pixel height.  Change these to the right size for your display!
oled_reset = dio.DigitalInOut(board.D4) # Define the Reset Pin
disp = adafruit_ssd1306.SSD1306_I2C(128, 32, board.I2C(), addr=0x3d, reset=oled_reset)

seesaw.pin_mode(24, seesaw.INPUT_PULLUP)
button = digitalio.DigitalIO(seesaw, 24)
encoder = rotaryio.IncrementalEncoder(seesaw)

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new("1", (width, height))
draw = ImageDraw.Draw(image)        # Get drawing object to draw on image.
top = -2; left = 0                  # for positioning text

#font = ImageFont.load_default()
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 9)

def draw_screen(start_item):
    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    # Write four lines of text.
    for i in range(4):
        display_item = (i + start_item) % len(lines) 
        draw.text((left, top + i*8), f'{display_item+1}. {lines[display_item]}', font=font, fill=255)
    # Display image.
    disp.image(image)
    disp.show()

message = "Item one\nItem two \nItem three\nItem four\nNumber five"
lines = message.split("\n")
start_line = 0          #text item
rotary_position = 0     #rotary position
start_line_orig = None  #this will force the first image to be drawn

while True:
    if button.value:                # Down button is False
        button_pressed = False
    elif not button_pressed:        # it's a new button press!
        start_line += 1
        button_pressed = True
        draw_screen(start_line, lines)
    
    rpos = -encoder.position    # make clockwise rotation positive
    if rpos > rotary_position:       
        start_line += 1
    elif rpos < rotary_position:       
        start_line -= 1
    rotary_position = rpos
    
    if start_line_orig != start_line:
        start_line = start_line % len(lines)
        draw_screen(start_line)
        start_line_orig = start_line    
        
    #time.sleep(0.1)
