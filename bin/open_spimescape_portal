#!/usr/bin/python
'''
Script to replace start_node using the spimescape abstraction upgrades
'''

from __future__ import print_function

import yaml

import dripline

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def open_spimescape_portal(**kwargs):
    '''
    '''
    # create the portal:
    module = None
    if 'module' not in kwargs:
        module = dripline.core.Service
    else:
        module = kwargs.pop('module')
        if hasattr(dripline.instruments, module):
            module = getattr(dripline.instruments, module)
        elif hasattr(dripline.core, module):
            module = getattr(dripline.core, module)
        else:
            raise NameError('no module "{}" in dripline.core or dripline.instruments'.format(module))
    these_endpoints = kwargs.pop('endpoints', [])
    service = module(**kwargs)
    logger.info('starting {}'.format(service.name))
    ##### need to fix the node class here...
    for provider in these_endpoints:
        service.add_endpoint(create_child(service, provider))
    logger.info('spimescapes created and populated')
    logger.info('Configuration of {} complete, starting consumption'.format(service.name))
    service.start_event_loop()

def create_child(portal, conf_dict):
    module = conf_dict.pop('module')
    child_confs = conf_dict.pop('endpoints', [])
    logger.info('creating a <{}> with args:\n{}'.format(module, conf_dict))
    if hasattr(dripline.instruments, module):
        this_child = getattr(dripline.instruments, module)(**conf_dict)
    elif hasattr(dripline.core, module):
        this_child = getattr(dripline.core, module)(**conf_dict)
    else:
        raise NameError('no module "{}" in dripline.core or dripline.instruments'.format(module))

    for child_dict in child_confs:
        this_child.add_endpoint(create_child(portal, child_dict))
    if isinstance(this_child, dripline.core.Provider):
        for grandchild in this_child.endpoints:
            portal.add_endpoint(this_child.endpoints[grandchild])
    return this_child

if __name__ == '__main__':
    parser = dripline.core.DriplineParser(extra_logger=logger, 
                                          amqp_broker=True,
                                          config_file=True,
                                          tmux_support=True,
                                          twitter_support=True,
                                          slack_support=True,
                                         )
    parser.add_argument('-k', '--keys',
                        metavar='BINDING_KEYS',
                        help='amqp binding keys to match against',
                        default='#',
                        nargs='*',
                       )
    
    args = parser.parse_args()
    logger.info('args parsed, reading config')
    conf_dict = args.config
    logger.info('config parsed')
    if args.broker:
        conf_dict.update({'broker':args.broker})
    try:
        open_spimescape_portal(**conf_dict)
    except KeyboardInterrupt:
        import threading
        logger.info('there are {} total threads'.format(threading.active_count()))
        for thread in threading.enumerate():
            if thread.name.startswith('logger_'):
                logger.info('canceling a thread named: {}'.format(thread.name))
                thread.cancel()
