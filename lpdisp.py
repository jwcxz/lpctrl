#!/usr/bin/python2

import pygame.midi as pm
import time
import signal, sys

devsigin = ('ALSA', 'Launchpad MIDI 1', 1, 0, 0);
devsigout = ('ALSA', 'Launchpad MIDI 1', 0, 1, 0);
lpin = None;
lpout = None;

def endthis():
    if lpin != None:
        print "Closing device"
        lpin.close();
        lpout.close();
        pm.quit();

    sys.exit(0);
signal.signal(signal.SIGINT, endthis);
signal.signal(signal.SIGTERM, endthis);

def getstat(ncpu):
    stat = [];
    f = open("/proc/stat", 'r');
    f.readline();
    for i in xrange(ncpu):
        _ = [int(__) for __ in f.readline().split(" ")[1:5]];
        stat.append(_);
    return stat;

def getcpu(ncpu=1, interval=2):
    one = getstat(ncpu);
    time.sleep(interval)
    two = getstat(ncpu);
    delta = [ [x - y for x,y in zip(a, b)] for a,b in zip(one, two) ];
    cpu = [ 1 - (float(dt[-1])/(sum(dt)+.01)) for dt in delta ];
    return cpu

# initialize MIDI, find controller
pm.init();
for i in xrange(pm.get_count()):
    _ = pm.get_device_info(i)
    print _;
    if _ == devsigin:
        lpin = pm.Input(i);
        print " -> Found In";

    if _ == devsigout:
        lpout = pm.Output(i);
        print " -> Found Out";

if lpin == None or lpout == None:
    print "Didn't find controller";
    sys.exit(1);

# initialize controller
lpout.write_short(0xB0, 0x00, 0x00);
lpout.write_short(0xB0, 0x00, 0x01);

mask = [ 0x30, 0x30, 0x21, 0x22, 0x22, 0x12, 0x03, 0x03 ];

grid = [ [0]*8 for i in xrange(8) ];

ncpu = 8;
switch = 0x31;
lpout.write_short(0xB0, 0x00, switch);
switch = switch ^ 5;

while True:
    cpu = getcpu(ncpu, 2);

    for i in xrange(ncpu):
        _ = int(8*cpu[i])
        for j in xrange(8):
            if j < _:
                grid[7-j][i] = mask[j];
            else:
                grid[7-j][i] = 0;

    for row in grid:
        i = 0
        while i < 8:
            lpout.write_short(0x92, row[i], row[i+1]);
            i+=2;

    #lpout.write_short(0xB0, 0x00, 0x07);
    lpout.write_short(0xB0, 0x00, switch);
    switch = switch ^ 5;

endthis();
