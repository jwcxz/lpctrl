#!/usr/bin/env python2

import argparse, os, socket, sys

parser = argparse.ArgumentParser(description="Client interface for lpctrl",
        epilog="Controls the lpctrl interface for the Novation Launchpad", 
        prog="lpctrl client");

parser.add_argument('-k', '--kill', action='store_true', dest='kill', help='kill the server');
parser.add_argument('-s', '--stop', action='store_true', dest='stop', help='stop plugin');
parser.add_argument('-r', '--refresh', action='store_true', dest='refresh', help='reload plugins');
parser.add_argument('-l', '--list', action='store_true', dest='list', help='list available plugins');
parser.add_argument('-p', '--plugin', action='store', dest='plugin', nargs='+', metavar=('PLUGIN', 'ARGS'), help='plugin to activate with arguments');
parser.add_argument('-R', '--raw', action='store', dest='raw', nargs='+', metavar='RAWDATA', help='raw data to send to server');
parser.add_argument('-H', '--host', action='store', dest='host', default='localhost', help='lpctrl server host');
parser.add_argument('-P', '--port', action='store', dest='port', default=33333, type=int, help='lpctrl server port');

args = parser.parse_args();

commands = [];

if args.refresh:
    commands.append("refresh");
if args.list:
    commands.append('list');
if args.plugin:
    commands.append('plugin ' + ' '.join(args.plugin));
elif args.raw:
    commands.append(' '.join(args.raw));
elif args.stop:
    commands.append('stop');

if args.kill:
    commands = ['die'];

for c in commands:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((args.host, args.port));
    print "Sending %s" % c;
    s.send(c);
    data = s.recv(1024)
    s.close()
    print data,
