"""
    This is a simple drawing plugin that illustrates input-driven output.  It
    keeps state in a self.grid but only updates the LEDs it needs to when
    drawing.

    TODO: add "brush" selection to select green, red, and yellow.
"""

import time
import backend.plugin
from backend.constants import *

class Plugin(backend.plugin.Plugin):
    def __init__(self, dev, args):
        backend.plugin.Plugin.__init__(self, dev, args);
        self.grid = [ [0]*8 for i in xrange(8) ];

    def run(self):
        backend.plugin.Plugin.run(self);

        self.dbuf = LP_DBC_ENB | LP_DBC_CPY | LP_DBC_B0U | LP_DBC_B1D;
        self.dev.write_short(LP_ADDR_CTRL, LP_REGS_DBUF, self.dbuf);
        self.dbuf = self.dbuf ^ ( LP_DBC_B1U | LP_DBC_B1D );

        #while self.enabled:
            #self.showgrid(self.grid);
            #time.sleep(1);

    def handle_input(self, pkt):
        x = pkt[1] & 0xF;
        y = pkt[1] >> 4;

        if pkt[2]==127 and x < 8 and y < 8:
            _ = self.grid[y][x];
            if _ == LP_BTN_RED:
                self.grid[y][x] = LP_BTN_GRN;
            elif _ == LP_BTN_GRN:
                self.grid[y][x] = 0
            else:
                self.grid[y][x] = LP_BTN_RED;

            self.dev.write_short(LP_ADDR_SETB, pkt[1], 
                    LP_BTN_CLR | LP_BTN_CPY | self.grid[y][x]);

        elif pkt[2]==127 and pkt[1]==0x8:
            for x in xrange(8):
                for y in xrange(8):
                    self.grid[x][y] = 0;
            self.showgrid(self.grid);
