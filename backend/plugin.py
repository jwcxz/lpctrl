import threading
from backend.constants import *

SLIDER_VALS = [ 0x30, 0x30,
                0x21, 0x21,
                0x12, 0x12,
                0x03, 0x03 ];

class Plugin(threading.Thread):
    enabled = False;

    def __init__(self, dev, args):
        threading.Thread.__init__(self);
        # what to do on initialization of the plugin
        self.dev = dev;
        self.args = args;
        self.enabled = False;
        self.dbuf = LP_DBC_ENB;
        self.top = [0]*8;

    def run(self):
        # called to start the thread
        self.enabled = True

    def stop(self):
        # called when the thread is stopped
        self.enabled = False

    def showgrid(self, grid, side=[0]*8):
        for row in grid:
            i = 0;
            while i < 8:
                self.dev.write_short(LP_ADDR_QWRT, row[i], row[i+1]);
                i+=2;

        i = 0;
        while i < 8:
            self.dev.write_short(LP_ADDR_QWRT, side[i], side[i+1]);
            i+=2;

        i = 0;
        while i < 8:
            self.dev.write_short(LP_ADDR_QWRT, self.top[i], self.top[i+1]);
            i+=2;

        self.dev.write_short(LP_ADDR_CTRL, LP_REGS_DBUF, self.dbuf);
        self.dbuf = self.dbuf ^ ( LP_DBC_B1U | LP_DBC_B1D );

    def handle_input(self, pkt):
        pass;

    def addr_to_button(self, addr):
        x = addr & 0xF;
        y = addr >> 4;
        return (x,y);

    def button_to_addr(self, button):
        addr = (button[1] << 4) | (button[0]);
        return addr;

    def set(self, button, color):
        val = LP_BTN_CLR | LP_BTN_CPY | color;
        addr = self.button_to_addr(button);
        self.dev.write_short(LP_ADDR_SETB, addr, val);

    def push(self, button, color, on, color_off=0):
        if on: v = color;
        else:  v = color_off;

        self.set(button, v);

    def slider(self, x, y):
        # slider from the bottom
        for yy in xrange(8):
            if yy < y:
                self.set((x, yy), 0);
            else:
                self.set((x, yy), SLIDER_VALS[y]);
