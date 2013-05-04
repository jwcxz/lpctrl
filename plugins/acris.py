import time
import backend.plugin
from backend.constants import *

import zmq


CMDS = {
        'clock_pulse' : 0,
        'action_on'   : 1,
        'action_off'  : 2,
        'set'         : 3,
        'set_action'  : 4,
        };


class Plugin(backend.plugin.Plugin):
    def __init__(self, dev, args):
        backend.plugin.Plugin.__init__(self, dev, args);

        # zmq context
        self.zmq_ctx = zmq.Context();
        self.zmq_push = self.zmq_ctx.socket(zmq.PUSH);

        self.grid = [ [0]*8 for i in xrange(8) ];

        rc = [ [ 0x01, 0x10, 0x01, 0x01, 0x01 ],
               [ 0x01, 0x10, 0x10, 0x10, 0x10 ] ];

        for i in xrange(8):
            for j in xrange(5):
                if i == 1 or i == 4 or i == 7:
                    self.grid[i][j] = 0x11;
                else:
                    self.grid[i][j] = rc[i%2][j%2];

        for i in xrange(4, 8):
            for j in xrange(5,8):
                self.grid[i][j] = backend.plugin.SLIDER_VALS[5];

        self.sides = [ LP_BTN_CLR | LP_BTN_CPY | LP_BTN_YLW,
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

        self.zmq_push.connect("tcp://127.0.0.1:44444");

    def stop(self):
        backend.plugin.Plugin.stop(self);
        self.zmq_ctx.destroy();

    def handle_input(self, pkt):
        x,y = self.addr_to_button(pkt[1]);

        on = (pkt[2] == 127);

        sendobj = None;

        if x < 5:
            # main mixer board
            self.push((x,y), LP_BTN_YLW, on, self.grid[y][x]);
            
            addr = (x, 7-y);

            if on:
                cmd = CMDS['action_on'];
            else:  
                cmd = CMDS['action_off'];

            sendobj = (cmd, addr);
            
        elif x < 8:
            if on:
                self.slider(x, y);
                params = (x-5, 7-y);
                sendobj = (CMDS['set'], params);

        else:
            # effect adjustment
            if on:
                if y == 7:
                    sendobj = (CMDS['clock_pulse'],(None,));
                else:
                    self.set((x,y), LP_BTN_YLW);
                    if   y == 0: action = 'pulse';
                    elif y == 1: action = 'sine';
                    else:        action = 'pulse';
                    
                    sendobj = (CMDS['set_action'],(action,));


        if sendobj != None:
            self.zmq_push.send_pyobj(sendobj);
