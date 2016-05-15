#!/usr/bin/env python3
# encoding: utf-8
"""
urlStreamHandler.py

"""

import sys
import os
import argparse
import json
import http.server
import socketserver
import datetime
import atexit
import signal
import time
from reader import Proposer

start_time = time.time()
proposer = Proposer("./data")
print("Initialised in %s seconds" % (time.time() - start_time))
date = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
filename = "data/urls_{}.csv".format(date)
logfile = open(filename, "w")
print('Writing to {}'.format(filename))

def at_exit():
    print("Closing logfile")
    logfile.close()
atexit.register(at_exit)

def do_exit(sig, frame):
    print("\nShutting down")
    sys.exit(0)
signal.signal(signal.SIGINT, do_exit)

class MyRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        """The GreaseMonkey script sends json data containing the url,
        timestamp, and html. We capture all POST requests irrespective of the
        path.
        """
        length = int(self.headers['Content-Length'])
        content = self.rfile.read(length)
        data = json.loads(content.decode(encoding='UTF-8'))
        url = data['url']
        ts = data['ts']
        action = data['action']
        # If a request from the settings page, handle separately
        if "http://localhost:8000/" in url:
            response = settings_handler(action)
        else:
            if action == 'load':
                toppage = data['top']
                #html = data['html']
                if toppage:
                    action_str = 'load'
                else:
                    action_str = 'bg'
                target = ''
                print('{:<15}: {}'.format(action_str, url))
            elif 'target' in data:
                action_str = action
                target = data['target']
                print('{:<15}: {} -> {}'.format(action_str, url, target))
            else:
                action_str = action
                target = ''
                print('{:<15}: {}'.format(action_str, url))
            inp = ts + ", " + action_str + ", " + url + ", " + target
            print(inp, file=logfile)
            start_time = time.time()
            suggestions = proposer.parse_action(inp)
            end_time = time.time() - start_time
            print("SUGGESTIONS")
            print(suggestions)
            print("Suggestions in %s seconds" % (end_time))
            if suggestions is not None and len(suggestions) > 0:
                response = {
                    'success': True,
                    'guesses': suggestions
                }
            else:
                # If no suggestions at all found (probably no previous data)
                # Return the top 5 most popular websites according to wikipedia
                response = {
                    'success': False,
                    'guesses': ["http://www.google.com",
                                "http://www.facebook.com",
                                "http://www.youtube.com",
                                "http://www.amazon.com", 
                                "http://www.wikipedia.org"]
                }
        jsonstr = bytes(json.dumps(response), "UTF-8")
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Content-length", len(jsonstr))
        self.end_headers()
        self.wfile.write(jsonstr)

def settings_handler(action):
    if action == 'remove':
        folder = "./data"
        print("Resetting all logs")
        global logfile
        logfile.close()
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            os.unlink(file_path)
        logfile = open(filename, "w")
        global proposer
        proposer = Proposer("./data")
        return {'success': True}
    
def start_from_csv(filenames):
    """List of csv files that contain a url stream as if they were comming
    from the GreaseMonkey script."""
    for filename in filenames:
        with open(filename, 'r') as csv_file:
            # TODO: Incrementally train your model based on these files
            print('Processing {}'.format(csv_file))


def main(argv=None):    
    parser = argparse.ArgumentParser(description='Record and suggest urls')
    parser.add_argument('--verbose', '-v', action='count',
                        help='Verbose output')
    parser.add_argument('--port', '-p', default=8000,
                        help='Server port')
    parser.add_argument('--csv', nargs='*',
                        help='CSV files with a url stream to start from')
    args = parser.parse_args(argv)

    if args.csv is not None:
        start_from_csv(args.csv)

    server = socketserver.TCPServer(("", args.port), MyRequestHandler)
    print("Serving at port {}".format(args.port))
    print("CTRL-C to exit")
    server.serve_forever()


if __name__ == "__main__":
    
    sys.exit(main())

