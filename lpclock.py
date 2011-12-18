#!/usr/bin/python2

import pygame.midi as pm
import time
import signal, sys

from datetime import datetime

devsigin = ('ALSA', 'Launchpad MIDI 1', 1, 0, 0);
devsigout = ('ALSA', 'Launchpad MIDI 1', 0, 1, 0);
lpin = None;
lpout = None;

def die(x,y):
    if lpin != None:
        print "Closing device"
        lpin.close();
        lpout.close();
        pm.quit();

    sys.exit(0);

frames = [
    [ [0,0,0,0,0,0,4,4],    # 12
      [0,0,0,0,0,4,4,4], 
      [0,0,1,1,1,2,4,0], 
      [0,0,1,0,5,1,0,0], 
      [0,0,1,0,0,1,0,0], 
      [0,0,1,1,1,1,0,0], 
      [0,0,0,0,0,0,0,0], 
      [0,0,0,0,0,0,0,0], ],
    [ [0,0,0,0,0,0,0,3],    # 1
      [0,0,0,0,0,0,3,4], 
      [0,0,1,1,1,1,4,4], 
      [0,0,1,0,5,2,4,4], 
      [0,0,1,0,0,1,0,0], 
      [0,0,1,1,1,1,0,0], 
      [0,0,0,0,0,0,0,0], 
      [0,0,0,0,0,0,0,0], ],
    [ [0,0,0,0,0,0,0,3],    # 2
      [0,0,0,0,0,0,3,3], 
      [0,0,1,1,1,1,3,3], 
      [0,0,1,0,5,1,3,3], 
      [0,0,1,0,0,2,4,4], 
      [0,0,1,1,1,1,4,4], 
      [0,0,0,0,0,0,0,4], 
      [0,0,0,0,0,0,0,0], ],
    [ [0,0,0,0,0,0,0,3],    # 3
      [0,0,0,0,0,0,3,3], 
      [0,0,1,1,1,1,3,3], 
      [0,0,1,0,5,1,3,3], 
      [0,0,1,0,5,1,3,3], 
      [0,0,1,1,1,2,4,3], 
      [0,0,0,0,0,4,4,4], 
      [0,0,0,0,0,0,4,4], ],
    [ [0,0,0,0,0,0,0,3],    # 4
      [0,0,0,0,0,0,3,3], 
      [0,0,1,1,1,1,3,3], 
      [0,0,1,0,5,1,3,3], 
      [0,0,1,0,5,1,3,3], 
      [0,0,1,1,2,1,3,3], 
      [0,0,0,0,4,4,3,3], 
      [0,0,0,0,4,4,4,3], ],
    [ [0,0,0,0,0,0,0,3],    # 5
      [0,0,0,0,0,0,3,3], 
      [0,0,1,1,1,1,3,3], 
      [0,0,1,0,5,1,3,3], 
      [0,0,1,0,5,1,3,3], 
      [0,0,1,2,1,1,3,3], 
      [0,0,4,4,3,3,3,3], 
      [0,4,4,4,3,3,3,3], ],
    [ [0,0,0,0,0,0,0,3],    # 6
      [0,0,0,0,0,0,3,3], 
      [0,0,1,1,1,1,3,3], 
      [0,0,1,0,5,1,3,3], 
      [0,0,1,5,5,1,3,3], 
      [0,4,2,1,1,1,3,3], 
      [4,4,4,3,3,3,3,3], 
      [4,4,3,3,3,3,3,3], ],
    [ [0,0,0,0,0,0,0,3],    # 7
      [0,0,0,0,0,0,3,3], 
      [0,0,1,1,1,1,3,3], 
      [0,0,1,0,5,1,3,3], 
      [4,4,2,5,5,1,3,3], 
      [4,4,1,1,1,1,3,3], 
      [4,3,3,3,3,3,3,3], 
      [3,3,3,3,3,3,3,3], ],
    [ [0,0,0,0,0,0,0,3],    # 8
      [4,0,0,0,0,0,3,3], 
      [4,4,1,1,1,1,3,3], 
      [4,4,2,0,5,1,3,3], 
      [3,3,1,5,5,1,3,3], 
      [3,3,1,1,1,1,3,3], 
      [3,3,3,3,3,3,3,3], 
      [3,3,3,3,3,3,3,3], ],
    [ [4,4,0,0,0,0,0,3],    # 9
      [4,4,4,0,0,0,3,3], 
      [3,4,2,1,1,1,3,3], 
      [3,3,1,5,5,1,3,3], 
      [3,3,1,5,5,1,3,3], 
      [3,3,1,1,1,1,3,3], 
      [3,3,3,3,3,3,3,3], 
      [3,3,3,3,3,3,3,3], ],
    [ [3,4,4,4,0,0,0,3],    # 10
      [3,3,4,4,0,0,3,3], 
      [3,3,1,2,1,1,3,3], 
      [3,3,1,5,5,1,3,3], 
      [3,3,1,5,5,1,3,3], 
      [3,3,1,1,1,1,3,3], 
      [3,3,3,3,3,3,3,3], 
      [3,3,3,3,3,3,3,3], ],
    [ [3,3,3,3,4,4,4,3],    # 11
      [3,3,3,3,4,4,3,3], 
      [3,3,1,1,2,1,3,3], 
      [3,3,1,5,5,1,3,3], 
      [3,3,1,5,5,1,3,3], 
      [3,3,1,1,1,1,3,3], 
      [3,3,3,3,3,3,3,3], 
      [3,3,3,3,3,3,3,3], ]
    ];

pxl = [ 0, 0x03, 0x33, 0x03, 0x30, 0x30, 0x0 ]

signal.signal(signal.SIGINT, die);
signal.signal(signal.SIGTERM, die);

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

grid = [ [0]*8 for i in xrange(8) ];

switch = 0x31;
lpout.write_short(0xB0, 0x00, switch);
switch = switch ^ 5;

while True:
    _ = [ frames[datetime.now().hour % 12], 
                frames[(datetime.now().minute/5) % 12],
                frames[(datetime.now().second/5) % 12] ];

    for y in xrange(8):
        for x in xrange(8):
            if x >= 3 and x <= 4 and y >= 3 and y <= 4:
                grid[y][x] = _[2][y][x];

            elif x >= 2 and x <= 5 and y >= 2 and y <= 5:
                grid[y][x] = _[0][y][x];

            else:
                grid[y][x] = _[1][y][x];

    print grid

    for row in grid:
        i = 0
        while i < 8:
            lpout.write_short(0x92, pxl[row[i]], pxl[row[i+1]]);
            i+=2;

    lpout.write_short(0xB0, 0x00, switch);
    switch = switch ^ 5;
    time.sleep(1);
    
die(0,0);

"""
while True:
    while not lpin.poll():
        time.sleep(.01);

    pkt = lpin.read(5);
    if pkt == []:
        break;

    print pkt

    for p in pkt:
        p = p[0]
        x = p[1] & 0xF;
        y = p[1] >> 4;

        if p[2]==127 and x < 8 and y < 8:
            _ = grid[y][x];
            if _ == R:
                grid[y][x] = G
            elif _ == G:
                grid[y][x] = 0
            else:
                grid[y][x] = R
        elif p[2]==127 and p[1]==0x8:
            for x in xrange(8):
                for y in xrange(8):
                    grid[x][y] = 0;

    for row in grid:
        i = 0
        while i < 8:
            lpout.write_short(0x92, row[i], row[i+1]);
            i+=2;

    #lpout.write_short(0xB0, 0x00, 0x07);
    lpout.write_short(0xB0, 0x00, switch);
    switch = switch ^ 5;


"""
