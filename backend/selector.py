"""
    This is the master selector.  After pressing it, press one of the grid
    buttons to select a plugin.  Or press a side button followed by a grid
    button to assign it to an appropriate quickselect slot.
"""

import time
import backend.plugin
from backend.constants import *

class Plugin(backend.plugin.Plugin):
    def __init__(self, parent, dev):
        backend.plugin.Plugin.__init__(self, dev, []);
        self.parent = parent;
        self.grid = [ [0]*8 for i in xrange(8) ];
        self.qselswitch = None;

        # initialize grid
        self.makegrid();

    def run(self):
        backend.plugin.Plugin.run(self);

        self.dbuf = LP_DBC_ENB | LP_DBC_CPY | LP_DBC_B0U | LP_DBC_B1D;
        self.dev.write_short(LP_ADDR_CTRL, LP_REGS_DBUF, self.dbuf);
        self.dbuf = self.dbuf ^ ( LP_DBC_B1U | LP_DBC_B1D );
        self.showgrid(self.grid);

    def handle_input(self, pkt):
        x = pkt[1] & 0xF;
        y = pkt[1] >> 4;

        if pkt[2]==127 and y*8+x < len(self.parent.pluglst) and x < 8 and y < 8:
            if self.qselswitch != None:
                self.parent.qselect[self.qselswitch] = self.parent.pluglst[y*8+x];
                self.makegrid();
                self.showgrid(self.grid);
            else:
                self.parent.activate_plugin(self.parent.pluglst[y*8+x], []);


        elif x == 0x8:
            if pkt[2] == 127:
                if self.qselswitch == y:
                    # if it's already selected, deselect it
                    self.qselswitch = None;
                    self.dev.write_short(LP_ADDR_SETB, pkt[1], LP_BTN_CLR|LP_BTN_CPY);
                elif self.qselswitch:
                    # if a different one was selected, deselect it and select
                    # the new one
                    self.dev.write_short(LP_ADDR_SETB, (self.qselswitch<<4)|0x8, LP_BTN_CLR|LP_BTN_CPY);
                    self.qselswitch = y;
                    self.dev.write_short(LP_ADDR_SETB, pkt[1], LP_BTN_CLR|LP_BTN_CPY|LP_BTN_YLW);
                else:
                    self.qselswitch = y;
                    self.dev.write_short(LP_ADDR_SETB, pkt[1], LP_BTN_CLR|LP_BTN_CPY|LP_BTN_YLW);

    def makegrid(self):
        for i in xrange(len(self.parent.pluglst)):
            if self.parent.pluglst[i] in self.parent.qselect:
                self.grid[i/8][i%8] = LP_BTN_YLW;
            else:
                self.grid[i/8][i%8] = LP_BTN_GRN;
