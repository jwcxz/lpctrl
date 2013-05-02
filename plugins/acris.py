import time
import backend.plugin
from backend.constants import *

import zmq

CMDS = {
        'pulse_on'   : 1,
        'pusle_off'  : 2,
        'set_decay'  : 3,
        'set_speed'  : 4,
        'set_shape'  : 5,
        'strobe_on'  : 6,
        'strobe_off' : 7,
        'sine_on'    : 8,
        'sine_off'   : 9,
        };

class Plugin(backend.plugin.Plugin):
    def __init__(self, dev, args):
        backend.plugin.Plugin.__init__(self, dev, args);

        # zmq context
        self.zmq_ctx = zmq.Context();
        self.zmq_pub = self.zmq_ctx.socket(zmq.PUB);

        self.grid = [ [0]*8 for i in xrange(8) ];

        rc = [ [ 0x01, 0x10, 0x01, 0x01, 0x01 ],
               [ 0x01, 0x10, 0x10, 0x10, 0x10 ] ];

        for i in xrange(8):
            for j in xrange(5):
                self.grid[i][j] = rc[i%2][j%2];

        for i in xrange(4, 8):
            for j in xrange(5,8):
                self.grid[i][j] = backend.plugin.SLIDER_VALS[5];

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
                cmd = CMDS['pulse_on'];
            else:  
                cmd = CMDS['pulse_off'];

            sendobj = (cmd, addr);
            
        elif x < 8:
            if on:
                self.slider(x, y);

                cmd = (CMDS['set_decay'], CMDS['set_speed'], CMDS['set_shape'])[x-5];
                params = (7-y,)

                sendobj = (cmd, params);

        else:
            # special effects and shit
            self.push((x,y), LP_BTN_YLW, on);

            if y == 7:
                # strobe
                if on:
                    sendobj = (CMDS['strobe_on'],(None,))
                else:
                    sendobj = (CMDS['strobe_off'],(None,))

            elif y == 6:
                if on:
                    sendobj = (CMDS['sine_on'],(None,))
                else:
                    sendobj = (CMDS['sine_off'],(None,))


        if sendobj != None:
            self.zmq_pub.send_pyobj(sendobj);
