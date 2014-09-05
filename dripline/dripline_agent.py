""" dripline_agent.py
Do simple stuff like gets and sets.
"""
import argparse
from node import Node
from config import Config
import message
import constants

# Argument parser setup
PARSER = argparse.ArgumentParser(description='Start a dripline node.')
PARSER.add_argument('-c',
                    '--config',
                    metavar='configuration file',
                    help='full path to a dripline YAML configuration file.',
                    required=True)
PARSER.add_argument('verb')
PARSER.add_argument('target')

def main():
    # TODO: we shouldn't have to start an entire node to do this, should we?
    # a connection should suffice...
    args = PARSER.parse_args()

    if args.verb == 'get':
        conf = Config(args.config)
        node = Node(conf)

        request = message.RequestMessage(target=args.target,
                                 msgop=constants.OP_SENSOR_GET).to_msgpack()

        reply = node.conn.send_request(args.target,request)
        print(message.Message.from_msgpack(reply).payload)
    else:
        print("sorry!  only get is supported for now.")

if __name__ == '__main__':
    main()

