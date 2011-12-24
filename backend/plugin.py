import threading
from backend.constants import *

class Plugin(threading.Thread):
    enabled = False;

    def __init__(self, dev, args):
        threading.Thread.__init__(self);
        # what to do on initialization of the plugin
        self.dev = dev;
        self.args = args;
        self.enabled = False;
        self.dbuf = LP_DBC_ENB;

    def run(self):
        # called to start the thread
        self.enabled = True
        # reset the controller
        self.dev.write_short(0xB0, 0x00, 0x00);

    def stop(self):
        # called when the thread is stopped
        self.enabled = False

    def showgrid(self, grid):
        for row in grid:
            i = 0
            while i < 8:
                self.dev.write_short(LP_ADDR_QWRT, row[i], row[i+1]);
                i+=2;

        self.dev.write_short(LP_ADDR_CTRL, LP_REGS_DBUF, self.dbuf);
        self.dbuf = self.dbuf ^ ( LP_DBC_B1U | LP_DBC_B1D );

    def handle_input(self, pkt):
        pass;