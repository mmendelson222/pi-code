#!/usr/bin/env python
# Display a runtext with double-buffering.
from samplebase import SampleBase
from rgbmatrix import graphics
import time
import os
import glob
import argparse


FILTER = "/home/pi/rpi-rgb-led-matrix/fonts/*.bdf"

class RunText(SampleBase):
    def __init__(self, *args, **kwargs):
        super(RunText, self).__init__(*args, **kwargs)
        self.parser.add_argument("-t", "--text", help="The text to scroll on the RGB LED panel", default="Hello world!")
        self.parser.add_argument("-f", "--font", help="font id", default=0, type=int)

    def run(self):
        font_file = self.choose_font(self.args.font)

        offscreen_canvas = self.matrix.CreateFrameCanvas()
        font = graphics.Font()
        font.LoadFont(font_file)
        textColor = graphics.Color(255, 255, 0)
        my_text = os.path.basename(font_file) + ' ' + self.args.text

        scroll = True
        if scroll:
            pos = offscreen_canvas.width
            pos = 0
        else:
            pos = 0

        while True:
            offscreen_canvas.Clear()
            len = graphics.DrawText(offscreen_canvas, font, pos, 10, textColor, my_text)
            if scroll:
                pos -= 1
                if (pos + len < 0):
                    pos = offscreen_canvas.width
            time.sleep(0.05)
            offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)

    def list_fonts(self):
        file_list=glob.glob(FILTER)
        count = 0
        for f in file_list:
            print(count, f)
            count += 1

    def choose_font(self, id):
        file_list=glob.glob(FILTER)
        print(FILTER)
        if (id >= len(file_list)):
            print("file id too large")
        return file_list[id]


# Main function
if __name__ == "__main__":
    run_text = RunText()
    run_text.list_fonts()

    if (not run_text.process()):
        run_text.print_help()
