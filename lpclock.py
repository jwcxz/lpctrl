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


N = 0x00
Y = 0x33;
R = 0x03;
E = 0x10;
F = 0x20;
G = 0x30;

frames = [
    [ [N,N,N,N,N,N,G,G],    # 12
      [N,N,N,N,N,G,G,G], 
      [N,N,N,N,N,Y,G,N], 
      [N,N,N,N,E,N,N,N], 
      [N,N,N,N,N,N,N,N], 
      [N,N,N,N,N,N,N,N], 
      [N,N,N,N,N,N,N,N], 
      [N,N,N,N,N,N,N,N], ],
    
    [ [N,N,N,N,N,N,N,R],    # 1
      [N,N,N,N,N,N,R,G], 
      [N,N,N,N,N,Y,G,G], 
      [N,N,N,N,F,Y,G,G], 
      [N,N,N,N,N,N,N,N], 
      [N,N,N,N,N,N,N,N], 
      [N,N,N,N,N,N,N,N], 
      [N,N,N,N,N,N,N,N], ],

    [ [N,N,N,N,N,N,N,R],    # 2
      [N,N,N,N,N,N,R,R], 
      [N,N,N,N,N,Y,R,R], 
      [N,N,N,N,G,Y,R,R], 
      [N,N,N,N,N,Y,G,G], 
      [N,N,N,N,N,N,G,G], 
      [N,N,N,N,N,N,N,G], 
      [N,N,N,N,N,N,N,N], ],

    [ [N,N,N,N,N,N,N,R],    # 3
      [N,N,N,N,N,N,R,R], 
      [N,N,N,N,N,Y,R,R], 
      [N,N,N,N,G,Y,R,R], 
      [N,N,N,N,E,Y,R,R], 
      [N,N,N,N,N,Y,G,R], 
      [N,N,N,N,N,G,G,G], 
      [N,N,N,N,N,N,G,G], ],

    [ [N,N,N,N,N,N,N,R],    # 4
      [N,N,N,N,N,N,R,R], 
      [N,N,N,N,N,Y,R,R], 
      [N,N,N,N,G,Y,R,R], 
      [N,N,N,N,F,Y,R,R], 
      [N,N,N,N,Y,Y,R,R], 
      [N,N,N,N,G,G,R,R], 
      [N,N,N,N,G,G,G,R], ],

    [ [N,N,N,N,N,N,N,R],    # 5
      [N,N,N,N,N,N,R,R], 
      [N,N,N,N,N,Y,R,R], 
      [N,N,N,N,G,Y,R,R], 
      [N,N,N,N,G,Y,R,R], 
      [N,N,N,Y,Y,Y,R,R], 
      [N,N,G,G,R,R,R,R], 
      [N,G,G,G,R,R,R,R], ],

    [ [N,N,N,N,N,N,N,R],    # 6
      [N,N,N,N,N,N,R,R], 
      [N,N,N,N,N,Y,R,R], 
      [N,N,N,N,G,Y,R,R], 
      [N,N,N,E,G,Y,R,R], 
      [N,G,Y,Y,Y,Y,R,R], 
      [G,G,G,R,R,R,R,R], 
      [G,G,R,R,R,R,R,R], ],

    [ [N,N,N,N,N,N,N,R],    # 7
      [N,N,N,N,N,N,R,R], 
      [N,N,N,N,N,Y,R,R], 
      [N,N,N,N,G,Y,R,R], 
      [G,G,Y,F,G,Y,R,R], 
      [G,G,Y,Y,Y,Y,R,R], 
      [G,R,R,R,R,R,R,R], 
      [R,R,R,R,R,R,R,R], ],

    [ [N,N,N,N,N,N,N,R],    # 8
      [G,N,N,N,N,N,R,R], 
      [G,G,N,N,N,Y,R,R], 
      [G,G,Y,N,G,Y,R,R], 
      [R,R,Y,G,G,Y,R,R], 
      [R,R,Y,Y,Y,Y,R,R], 
      [R,R,R,R,R,R,R,R], 
      [R,R,R,R,R,R,R,R], ],

    [ [G,G,N,N,N,N,N,R],    # 9
      [G,G,G,N,N,N,R,R], 
      [R,G,Y,N,N,Y,R,R], 
      [R,R,Y,E,G,Y,R,R], 
      [R,R,Y,G,G,Y,R,R], 
      [R,R,Y,Y,Y,Y,R,R], 
      [R,R,R,R,R,R,R,R], 
      [R,R,R,R,R,R,R,R], ],

    [ [R,G,G,G,N,N,N,R],    # 10
      [R,R,G,G,N,N,R,R], 
      [R,R,Y,Y,N,Y,R,R], 
      [R,R,Y,F,G,Y,R,R], 
      [R,R,Y,G,G,Y,R,R], 
      [R,R,Y,Y,Y,Y,R,R], 
      [R,R,R,R,R,R,R,R], 
      [R,R,R,R,R,R,R,R], ],

    [ [R,R,R,R,G,G,G,R],    # 11
      [R,R,R,R,G,G,R,R], 
      [R,R,Y,Y,Y,Y,R,R], 
      [R,R,Y,G,G,Y,R,R], 
      [R,R,Y,G,G,Y,R,R], 
      [R,R,Y,Y,Y,Y,R,R], 
      [R,R,R,R,R,R,R,R], 
      [R,R,R,R,R,R,R,R], ]
    ];

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
                frames[(datetime.now().second) % 12] ];

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
            lpout.write_short(0x92, row[i], row[i+1]);
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
