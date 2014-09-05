""" start_node.py
Starts a dripline node and connects to a dripline mesh based on a configuration
file passed in with the 'c' flag, or '--config'.
"""
import argparse
from config import Config
from node import Node

# Argument parser setup
PARSER = argparse.ArgumentParser(description='Start a dripline node.')
PARSER.add_argument('-c',
                    '--config',
                    metavar='configuration file',
                    help='full path to a dripline YAML configuration file.')

def main():
    args = PARSER.parse_args()

    if args.config is not None:
        conf = Config(args.config)
        node = Node(conf)
        node.start_event_loop()
    else:
        print "oh "

if __name__ == '__main__':
    main()
