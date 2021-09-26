#!/usr/bin/env python
# Display a runtext with double-buffering.
from samplebase import SampleBase
from rgbmatrix import graphics
import time
import os
import glob
import argparse
import threading
from queue import Queue
from datetime import datetime
import gtasks

FILTER = "/home/pi/rpi-rgb-led-matrix/fonts/*.bdf"

class RunText(SampleBase):
    def __init__(self, *args, **kwargs):
        super(RunText, self).__init__(*args, **kwargs)
        self.parser.add_argument("-t", "--text", help="The text to scroll on the RGB LED panel", default="Hello world!")
        self.parser.add_argument("-f", "--font", help="font id", default=2, type=int)

    def run(self, q):
        font_file = self.choose_font(self.args.font)
        offscreen_canvas = self.matrix.CreateFrameCanvas()
        font = graphics.Font()
        font.LoadFont(font_file)
        font_height = 6
        textColor = graphics.Color(255, 255, 0)
        scroll = False
        while True:
            if not q.empty():
                display_lines = q.get()
                ypos = font_height
                xpos = 0
                # if scroll:
                #     pos = offscreen_canvas.width
            offscreen_canvas.Clear()
            ypos = font_height 
            len = 0 #used for scrolling
            for t in display_lines:
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
    q = Queue()
    q.put(["Hello there."])
    run_text = RunText()
    render_thread = threading.Thread(target=run_text.process, args=[q], name="render_thread", daemon=True)
    time.sleep(1)
    render_thread.start()
    while render_thread.is_alive():
        time.sleep(5)
        tasks = gtasks.get_tasks()
        q.put(tasks)

def __refresh_offday(render_thread, data):  # type: (threading.Thread, Data) -> None
    debug.log("Main has selected the offday information to refresh")

def start_nonthreaded():
    run_text = RunText()
    if (not run_text.process()):
        run_text.print_help()
    return 


# Main function
if __name__ == "__main__":
    start_threaded()
        
