#!/usr/bin/env python2

import argparse, serial, socket, sys
import pygame.midi as pm
import plugins
import backend.input, backend.selector
from backend.constants import *

class LPCtrl:
    def __init__(self, host='localhost', port=33333, devsig='Launchpad MIDI 1'):
        # build plugins list
        self.plugins = {};
        self.pluglst = [];
        self.refresh_plugins();

        self.qselect = ['', '', '', '', '', '', ''];
        # assign the first 7 plugins to the quickselect slots
        for i in xrange(min(8, len(self.pluglst))):
            self.qselect[i] = self.pluglst[i];

        # connect to launchpad
        self.lpin, self.lpout = self.lp_connect(devsig);

        # select first plugin
        self.plugin = None;
        self.input = None;

        # socket configuration
        self.host = host;
        self.port = port;

    def run(self):
        # start input thread to allow plugin selection via the launchpad
        self.input = backend.input.InputHandler(self, self.lpin, self.lpout);
        self.input.start();

        # set up socket server to listen for incoming plugin requests
        blog = 5;
        size = 1024;

        self.skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
        self.skt.bind( (self.host,self.port) );
        self.skt.listen(blog);

        while True:
            try:
                client, address = self.skt.accept();
                print ":: Accepted", address
                data = client.recv(size);
                print "::   Received:", data.rstrip();
                statusmsg = "";
                if data:
                    # data contains a command and optional arguments
                    data = data.split(None);
                    cmd = data[0]

                    if cmd == "plugin":
                       if data[1] in self.plugins:
                            statusmsg = "Activating %s with args %r" %(data[1], data[2:]);
                            self.stop_plugin();
                            self.activate_plugin(data[1], data[2:]);
                       else:
                            statusmsg = "Plugin %s (with args %r) not found)" %(data[1], data[2:]);

                    elif cmd == "stop":
                        statusmsg = "Stopping plugin";
                        self.stop_plugin();

                    elif cmd == "list":
                        statusmsg = "Available plugins: %s" % ' '.join(self.plugins.keys());

                    elif cmd == "refresh":
                        statusmsg = "Reloading plugins"
                        self.refresh_plugins();

                    elif cmd == "die":
                        # stop plugins
                        self.stop_plugin();
                        #if self.input and self.input.enabled:
                            #self.input.stop();

                        # close the socket
                        statusmsg = "Exiting";
                        print "::  ", statusmsg;  # hack
                        client.send(statusmsg);   #
                        self.skt.shutdown(socket.SHUT_RDWR);
                        self.skt.close();
                        
                        # close launchpad controller
                        self.lpin.close();
                        self.lpout.close();
                        # TODO: why doesn't this work?
                        #pm.quit();

                        sys.exit(0);

                    else:
                        statusmsg = "Invalid command";

                print "::  ", statusmsg;
                client.send(statusmsg+"\n");
                client.close();
            except socket.error:
                print "whoops"

    def activate_plugin(self, pluginname, args):
        self.input = backend.input.InputHandler(self, self.lpin, self.lpout);
        self.input.start();

        # reset the controller
        self.lpout.write_short(0xB0, 0x00, 0x00);

        if pluginname == 'selector':
            # activate special selector plugin
            self.plugin = backend.selector.Plugin(self, self.lpout);
            self.plugin.top = [0]*8;
            self.plugin.top[7] = LP_BTN_CLR | LP_BTN_CPY | LP_BTN_GRN;
            self.lpout.write_short(LP_ADDR_CTRL, 
                    LP_REGS_TPRW+0x7, 
                    LP_BTN_CLR | LP_BTN_CPY | LP_BTN_GRN);
            self.plugin.start();
        else:
            pluginobj = self.plugins[pluginname];
            self.plugin = pluginobj(self.lpout, args);

            if pluginname in self.qselect:
                self.plugin.top = [0]*8;
                self.plugin.top[self.qselect.index(pluginname)] = LP_BTN_CLR | LP_BTN_CPY | LP_BTN_GRN;

                self.lpout.write_short(LP_ADDR_CTRL,
                        LP_REGS_TPRW+self.qselect.index(pluginname),
                        LP_BTN_CLR | LP_BTN_CPY | LP_BTN_GRN);

            self.plugin.start();

    def stop_plugin(self):
        if self.input != None and self.input.enabled:
            self.input.stop();
            self.input = None;

        if self.plugin != None and self.plugin.enabled:
            self.plugin.stop();
            self.plugin = None; # garbage collect

    def refresh_plugins(self):
        reload(plugins);

        self.pluglst = plugins.__all__;

        for p in self.pluglst:
            _ = __import__('plugins.'+p, globals(), locals(), [p], -1);
            reload(_);
            self.plugins[p] = _.Plugin;

        print "-> Refreshed plugins: %s" % ' '.join(self.pluglst);

    def lp_connect(self, devsig):
        devsigin = ('ALSA', devsig, 1, 0, 0);
        devsigout = ('ALSA', devsig, 0, 1, 0);

        pm.init();
        for i in xrange(pm.get_count()):
            _ = pm.get_device_info(i)
            if _ == devsigin:
                lpin = pm.Input(i);
                print " -> Found In";

            if _ == devsigout:
                lpout = pm.Output(i);
                print " -> Found Out";

        if lpin == None or lpout == None:
            print "Didn't find controller";
            sys.exit(1);

        # initialize controller (reset, select X-Y mode)
        lpout.write_short(0xB0, 0x00, 0x00);
        lpout.write_short(0xB0, 0x00, 0x01);

        return [lpin, lpout];


p = argparse.ArgumentParser(description="The Launchpad Controller Master Server");

p.add_argument('-s', '--host', dest='host', action='store', default='localhost', help='host address to bind to');
p.add_argument('-p', '--port', dest='port', action='store', default='33333', help='host port to bind to');
p.add_argument('-d', '--devsig', dest='devsig', action='store', default='Launchpad MIDI 1', help='device signature');

args = p.parse_args();

lpctrl = LPCtrl(args.host, int(args.port), args.devsig);
lpctrl.run();
