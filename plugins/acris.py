import time
import backend.plugin
from backend.constants import *

import zmq

CMDS = {
        'add_pulse': 1,
        'pulse_decay': 2,
        'pulse_speed': 3,
        'pulse_shape': 4,
        'strobe_on': 5,
        'strobe_off': 6,
        'sine_on': 7,
        'sine_off': 8,
        };

class Plugin(backend.plugin.Plugin):
    def __init__(self, dev, args):
        backend.plugin.Plugin.__init__(self, dev, args);

        # zmq context
        self.zmq_ctx = zmq.Context();
        self.zmq_pub = self.zmq_ctx.socket(zmq.PUB);

        self.grid = [ [0]*8 for i in xrange(8) ];

        self.sides = [ LP_BTN_CLR | LP_BTN_CPY,
                       LP_BTN_CLR | LP_BTN_CPY,
                       LP_BTN_CLR | LP_BTN_CPY,
                       LP_BTN_CLR | LP_BTN_CPY,
                       LP_BTN_CLR | LP_BTN_CPY,
                       LP_BTN_CLR | LP_BTN_CPY,
                       LP_BTN_CLR | LP_BTN_CPY,
                       LP_BTN_CLR | LP_BTN_CPY ];

    def run(self):
        backend.plugin.Plugin.run(self);

        self.dbuf = LP_DBC_ENB | LP_DBC_CPY | LP_DBC_B0U | LP_DBC_B1D;
        self.dev.write_short(LP_ADDR_CTRL, LP_REGS_DBUF, self.dbuf);
        self.dbuf = self.dbuf ^ ( LP_DBC_B1U | LP_DBC_B1D );
        self.showgrid(self.grid, self.sides);

        self.zmq_pub.bind("tcp://*:44444");

    def handle_input(self, pkt):
        x,y = self.addr_to_button(pkt[1]);

        on = (pkt[2] == 127);

        sendobj = None;

        if x < 5:
            # main mixer board
            self.push((x,y), LP_BTN_YLW, on);
            
            if on:
                sendobj = (CMDS['add_pulse'], (x, 7-y));
            
        elif x < 8:
            if on:
                for yy in xrange(8):
                    if yy < y:
                        self.set((x, yy), 0);
                    else:
                        self.set((x, yy), LP_BTN_GRN);

                cmd = CMDS.keys()[x-4];
                params = (7-y,)

                sendobj = (cmd, params);

        else:
            # special effects and shit
            self.push((x,y), LP_BTN_YLW, on);

            if y == 7:
                # strobe
                if on:
                    sendobj = (CMDS['strobe_on'],)
                else:
                    sendobj = (CMDS['strobe_off'],)

            elif y == 6:
                if on:
                    sendobj = (CMDS['sine_on'],)
                else:
                    sendobj = (CMDS['sine_off'],)


        if sendobj != None:
            self.zmq_pub.send_pyobj(sendobj);
