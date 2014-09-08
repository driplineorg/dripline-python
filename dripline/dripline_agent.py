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
PARSER.add_argument('value')

def verb_list():
    """
    A list of acceptable verb arguments.
    """
    return ['get', 'set', 'describe']

def main():
    # TODO: we shouldn't have to start an entire node to do this, should we?
    # a connection should suffice...
    args = PARSER.parse_args()

    # TODO: can't we use argparse to do this somehow?
    # if the request verb is not one of the accepted verbs, barf here.
    request_verb = args.verb
    if request_verb not in verb_list():
        print("ERROR: verb argument must be one of: get, set, or describe.")
        return -1

    conf = Config(args.config)
    node = Node(conf)

    if request_verb == 'get':
        request = message.RequestMessage(target=args.target,
                                         msgop=constants.OP_SENSOR_GET)

        reply = node.send_sync(request)
        print(reply.payload)
    elif request_verb == 'set':
        request = message.RequestMessage(target=args.target,
                                         msgop=constants.OP_SENSOR_SET,
                                         payload=args.value)
        reply = node.send_sync(request)
        print(reply.payload)

if __name__ == '__main__':
    main()

