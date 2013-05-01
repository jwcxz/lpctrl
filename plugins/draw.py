"""
    This is a simple drawing plugin that illustrates input-driven output.  It
    keeps state in a self.grid but only updates the LEDs it needs to when
    drawing.

    Select brush with the 4th, 5th, and 6th side button.  Adjust the brightness
    of the brush with the 3rd button.  Use the 2nd button to erase pixels and
    the 1st to clear the screen.  The 3rd right button displays the currently
    selected brush and brightness.
"""

import time
import backend.plugin
from backend.constants import *

class Plugin(backend.plugin.Plugin):
    def __init__(self, dev, args):
        backend.plugin.Plugin.__init__(self, dev, args);
        self.grid = [ [0]*8 for i in xrange(8) ];

        self.brush = [ LP_BTN_RED, 0x33 ];

        self.sides = [ LP_BTN_CLR | LP_BTN_CPY | self.brush[0]&self.brush[1],  # clear screen
                       LP_BTN_CLR | LP_BTN_CPY | LP_BTN_RED,         # red
                       LP_BTN_CLR | LP_BTN_CPY | LP_BTN_GRN,         # grn
                       LP_BTN_CLR | LP_BTN_CPY | LP_BTN_YLW,         # ylw
                       LP_BTN_CLR | LP_BTN_CPY,                      # level 0
                       LP_BTN_CLR | LP_BTN_CPY | self.brush[0]&0x11, # level 1
                       LP_BTN_CLR | LP_BTN_CPY | self.brush[0]&0x22, # level 2
                       LP_BTN_CLR | LP_BTN_CPY | self.brush[0]&0x33] # level 3

    def run(self):
        backend.plugin.Plugin.run(self);

        self.dbuf = LP_DBC_ENB | LP_DBC_CPY | LP_DBC_B0U | LP_DBC_B1D;
        self.dev.write_short(LP_ADDR_CTRL, LP_REGS_DBUF, self.dbuf);
        self.dbuf = self.dbuf ^ ( LP_DBC_B1U | LP_DBC_B1D );
        self.showgrid(self.grid, self.sides);

    def handle_input(self, pkt):
        x = pkt[1] & 0xF;
        y = pkt[1] >> 4;

        if pkt[2] == 127:
            if x == 8:
                # select brush
                if   y == 0: self.showgrid(self.grid, self.sides);
                elif y == 1: self.brush[0] = LP_BTN_CLR | LP_BTN_CPY | LP_BTN_RED;
                elif y == 2: self.brush[0] = LP_BTN_CLR | LP_BTN_CPY | LP_BTN_GRN;
                elif y == 3: self.brush[0] = LP_BTN_CLR | LP_BTN_CPY | LP_BTN_YLW;
                elif y == 4: self.brush[1] = LP_BTN_CLR | LP_BTN_CPY;
                elif y == 5: self.brush[1] = 0x11;
                elif y == 6: self.brush[1] = 0x22;
                elif y == 7: self.brush[1] = 0x33;

                self.sides[0] = LP_BTN_CLR | LP_BTN_CPY | (self.brush[0]&self.brush[1]);
                self.sides[5] = LP_BTN_CLR | LP_BTN_CPY | (self.brush[0]&0x11);
                self.sides[6] = LP_BTN_CLR | LP_BTN_CPY | (self.brush[0]&0x22);
                self.sides[7] = LP_BTN_CLR | LP_BTN_CPY | (self.brush[0]&0x33);
                self.dev.write_short(LP_ADDR_SETB, 0x08, self.sides[0]);
                self.dev.write_short(LP_ADDR_SETB, 0x58, self.sides[5]);
                self.dev.write_short(LP_ADDR_SETB, 0x68, self.sides[6]);
                self.dev.write_short(LP_ADDR_SETB, 0x78, self.sides[7]);
            else:
                # draw!
                self.dev.write_short(LP_ADDR_SETB, pkt[1], 
                        LP_BTN_CLR | LP_BTN_CPY | (self.brush[0]&self.brush[1]));
