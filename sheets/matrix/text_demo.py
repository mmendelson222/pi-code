#!/usr/bin/env python
# Display a runtext with double-buffering.
from samplebase import SampleBase
from rgbmatrix import graphics
import time
import os
import glob
import argparse
import threading

FILTER = "/home/pi/rpi-rgb-led-matrix/fonts/*.bdf"

class RunText(SampleBase):
    display_lines = ["Some Text", "some more text"]
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
        #my_text = os.path.basename(font_file) + ' ' + self.args.text

        scroll = True
        if scroll:
            xpos = offscreen_canvas.width
            xpos = 0
        else:
            xpos = 0

        font_height = 6
        while True:
            offscreen_canvas.Clear()
            ypos = font_height 

            len = 0 #used for scrolling
            for t in self.display_lines:
                len = max(graphics.DrawText(offscreen_canvas, font, xpos, ypos, textColor, t), len)
                ypos += (font_height)

            if scroll:
                xpos -= 1
                if (xpos + len < 0):
                    xpos = offscreen_canvas.width

            time.sleep(0.03)  #higher = slower
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


# create render thread
def start_threaded():
    render_thread = threading.Thread(target=start_nonthreaded, args=[], name="render_thread", daemon=True)
    time.sleep(1)
    render_thread.start()

    while render_thread.is_alive():
        time.sleep(5)
        print("hello")

def __refresh_offday(render_thread, data):  # type: (threading.Thread, Data) -> None
    debug.log("Main has selected the offday information to refresh")
   


def start_nonthreaded():
    run_text = RunText()
    if (not run_text.process()):
        run_text.print_help()


# Main function
if __name__ == "__main__":
    start_threaded()
