import threading, time
from backend.constants import *

class InputHandler(threading.Thread):
    enabled = False;

    def __init__(self, parent, indev, outdev):
        threading.Thread.__init__(self);
        self.parent = parent;
        self.indev = indev;
        self.outdev = outdev;
        self.enabled = False;

    def run(self):
        # called to start the thread
        self.enabled = True
        while self.enabled:
            while self.enabled and not self.indev.poll():
                # ^ race condition protection
                time.sleep(.01);

            if not self.enabled:
                break;

            # poll for input
            pkt = [];
            p = self.indev.read(1);

            if p == []: break;
            while p != []:
                pkt.append(p[0]);
                p = self.indev.read(1);

            for p in pkt:
                p = p[0];   # strip timestamp

                if p[0] == 0xB0:
                    # top row -- handle internally
                    if p[2] == 127:
                        _ = p[1] - 0x68;
                        if _ != 7 and self.parent.qselect[_] != '':
                            self.parent.stop_plugin();
                            self.parent.activate_plugin(self.parent.qselect[_], []);
                        else:
                            # activate special plugin selector plugin
                            self.parent.stop_plugin();
                            self.parent.activate_plugin('selector', []);
                        
                else:
                    # send to plugin
                    if self.parent.plugin and self.parent.plugin.enabled:
                        self.parent.plugin.handle_input(p)

    def stop(self):
        # called when the thread is stopped
        self.enabled = False
