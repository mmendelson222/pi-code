# SPDX-FileCopyrightText: 2017 Tony DiCola for Adafruit Industries
# SPDX-FileCopyrightText: 2017 James DeVito for Adafruit Industries
# SPDX-License-Identifier: MIT

# This example is for use on (Linux) computers that are using CPython with
# Adafruit Blinka to support CircuitPython libraries. CircuitPython does
# not support PIL/pillow (python imaging library)!

# use a simple button to rotate through lines of text. 

import time
import subprocess

from board import SCL, SDA
import board
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import digitalio

# Define the Reset Pin
oled_reset = digitalio.DigitalInOut(board.D4)

button1 = digitalio.DigitalInOut(board.D26)
button1.direction = digitalio.Direction.INPUT
button1.pull = digitalio.Pull.UP

# Create the I2C interface.
i2c = busio.I2C(SCL, SDA)

# Create the SSD1306 OLED class.
# The first two parameters are the pixel width and pixel height.  Change these
# to the right size for your display!
disp = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, addr=0x3d, reset=oled_reset)

# Clear display.
disp.fill(0)
disp.show()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new("1", (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=0)
top = -2
left = 0

#font = ImageFont.load_default()
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 9)

def draw_screen(start_item, lines):
    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    # Write four lines of text.
    for i in range(4):
        display_item = (i + startat) % len(lines) 
        draw.text((left, top + i*8), f'{display_item+1}. {lines[display_item]}', font=font, fill=255)
    
    # Display image.
    disp.image(image)
    disp.show()

message = "Item one\nItem two \nItem three\nItem four\nNumber five"
lines = message.split("\n")
startat = 0
button_pressed = False
draw_screen(startat, lines)

while True:
    if button1.value:   # Down button is False
        button_pressed = False
    elif not button_pressed:
        # it's a new button press!
        startat = (startat + 1) % len(lines)
        button_pressed = True
        draw_screen(startat, lines)
        
    time.sleep(0.1)
