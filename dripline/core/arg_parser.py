'''
A wrapper for argparse.ArgumentParser with some standardized arguments and behaviors

.. todo:: does arg_parse belong in core?
'''
from __future__ import absolute_import

import argparse
import os
import subprocess
import sys

from .constants import TIME_FORMAT
from .status_logger import SlackHandler, TwitterHandler
from .. import __version__

import logging
logger = logging.getLogger('dripline')
logger.setLevel(logging.DEBUG)

__all__ = ['DriplineParser']


class DotAccess(object):
    def __init__(self, adict):
        self.__dict__.update(adict)


class DriplineParser(argparse.ArgumentParser):
    '''
    A wrapper of the logger.ArgumentParser for dripline scripts
    '''
    
    def __init__(self,
                 extra_logger=None,
                 amqp_broker=False,
                 config_file=False,
                 tmux_support=False,
                 twitter_support=False,
                 slack_support=False,
                 **kwargs):
        '''
        Keyword Args:
            extra_logger (logging.Logger): reference to a Logger instance, (handlers created will be connected to it)
            amqp_broker (bool): enable a '-b' option for specifying the broker's network address
            config_file (bool): enable a '-c' option for specifying an input configuration file
            tmux_support (bool): enable a '-t' option to start the process in a tmux session rather than on the active shell
            twitter_support (bool): enable a '-T' option to send a logger messages of critical or higher severity as tweets
            slack_support (bool): enable a '-S' option to send log messages to slack channels

        '''
        self.extra_logger = extra_logger
        argparse.ArgumentParser.__init__(self, formatter_class=argparse.ArgumentDefaultsHelpFormatter, **kwargs)
        self.add_argument('-v',
                          '--verbose',
                          default=0,
                          action='count',
                          help='increases terminal output verbosity',
                        )
        self.add_argument('-l',
                          '--logfile',
                          help='file to save logged output',
                         )
        self.add_argument('-V',
                          '--version',
                          action='version',
                          version=__version__,
                          help='display dripline version',
                         )
        self._handlers = []
        self._handlers.append(logging.StreamHandler())
        logger.addHandler(self._handlers[0])
        if extra_logger:
            extra_logger.setLevel(logging.DEBUG)
            extra_logger.addHandler(self._handlers[0])
        self.__set_format()
        if amqp_broker:
            self.add_argument('-b',
                              '--broker',
                              help='network path for the AMQP broker, if not provided (and if a config file is provided) use the value from the config file; if the option is present with no argument then "localhost" is used',
                              default=None,
                              nargs='?',
                              const='localhost',
                             )
        if config_file:
            self.add_argument('-c',
                              '--config',
                              help='path (absolute or relative) to configuration file',
                             )
        if tmux_support:
            self.add_argument('-t',
                              '--tmux',
                              help='enable running in, and optionally naming, a tmux session',
                              nargs='?',
                              default=None, # value if option not given
                              const=False, # value if option given with no argument
                             )
        if twitter_support:
            self.add_argument('-T',
                              '--twitter',
                              help='enable sending critical messages as tweets',
                              nargs='?',
                              default=False, # value if option not given
                              const=True, # value if option given with no argument
                             )
        if slack_support:
            self.add_argument('-S',
                              '--slack',
                              help='enable sending critical messages as slack messages to #p8_alerts',
                              nargs='?',
                              default=False, # value if option not given
                              const=True, # value if option given with no argument
                             )

    def __set_format(self):
        base_format = '%(asctime)s{}[%(levelname)-8s] %(name)s(%(lineno)d) -> {}%(message)s'
        try:
            import colorlog
            self.fmt = colorlog.ColoredFormatter(
                    base_format.format('%(log_color)s', '%(purple)s'),
                    datefmt = TIME_FORMAT[:-1],
                    reset=True,
                    )
        except ImportError:
            self.fmt = logging.Formatter(
                    base_format.format(' ', ''),
                    TIME_FORMAT[:-1]
                    )
        self._handlers[0].setFormatter(self.fmt)

    def __process_tmux(self, args):
        new_argv = list(sys.argv)
        if not args.tmux:
            if hasattr(args, 'config'):
                session_name = args.config.split('/')[-1].split('.')[0]
            else:
                raise AttributeError('one of a config file or tmux session name is required')
            if '-t' in new_argv:
                new_argv.pop(new_argv.index('-t'))
            elif '--tmux' in new_argv:
                new_argv.pop(new_argv.index('--tmux'))
            else:
                raise Exception
        else:
            session_name = args.tmux
            if '-t' in new_argv:
                ind = new_argv.index('-t')
                new_argv.pop(ind)
                new_argv.pop(ind)
            if '--tmux' in new_argv:
                ind = new_argv.index('--tmux')
                new_argv.pop(ind)
                new_argv.pop(ind)
        session_exists = 0 == subprocess.call('tmux has-session -t {}'.format(session_name).split(),
                                         stdout=open('/dev/null'),
                                         stderr=subprocess.STDOUT,
                                        )
        if session_exists:
            print('session already exists')
            sys.exit()
        else:
            subprocess.check_call('tmux new-session -d -s {}'.format(session_name).split(),
                                  stdout=open('/dev/null'),
                                  stderr=subprocess.STDOUT,
                                 )
            if hasattr(sys, 'real_prefix'):
                subprocess.call(['tmux', 'send-keys', 'source {}/bin/activate\n'.format(sys.prefix)])
            subprocess.check_call(['tmux', 'send-keys', ' '.join(new_argv+['\n'])],
                                  stdout=open('/dev/null'),
                                  stderr=subprocess.STDOUT,
                                 )
            print('tmux session {} created'.format(session_name))
            sys.exit()

    def __process_twitter(self):
        twitter_handler = TwitterHandler()
        self.__add_critical_handler(twitter_handler)

    def __process_slack(self):
        slack_handler = SlackHandler()
        self.__add_critical_handler(slack_handler)

    def __add_critical_handler(self, a_handler):
        a_handler.setLevel(logging.CRITICAL)
        logger.addHandler(a_handler)
        if hasattr(self, 'extra_logger'):
            self.extra_logger.addHandler(a_handler)
        self._handlers.append(a_handler)

    def parse_args(self):
        '''
        '''
        # first, parse the args
        these_args = argparse.ArgumentParser.parse_args(self)
        args_dict = vars(these_args)

        # add args specified in a config file if there is one
        if 'config' in these_args:
            if these_args.config is not None:
                try:
                    file_str = open(these_args.config).read()
                    import yaml
                    conf_file = yaml.load(file_str)
                    if 'broker' in args_dict and 'broker' in conf_file:
                        if args_dict['broker'] is None:
                            args_dict['broker'] = conf_file['broker']
                    conf_file.update(args_dict)
                    args_dict['config'] = conf_file
                    these_args = DotAccess(args_dict)
                except:
                    print("parsing of config failed")
                    raise

        # setup loggers and handlers
        log_level = max(0, 25-these_args.verbose*10)
        self._handlers[0].setLevel(log_level)
        if not these_args.logfile is None:
            _file_handler = logging.FileHandler(these_args.logfile)
            _file_handler.setFormatter(self.fmt)
            _file_handler.setLevel(log_level)
            logger.addHandler(_file_handler)
            if self.extra_logger:
                self.extra_logger.addHandler(_file_handler)
            self._handlers.append(_file_handler)

        # take care of tmux if needed
        if hasattr(these_args, 'tmux'):
            if not these_args.tmux is None:
                self.__process_tmux(these_args)

        # and add twitter to the log handling if enabled
        if hasattr(these_args, 'twitter'):
            if these_args.twitter:
                self.__process_twitter()

        # and add slack to the log handling if enabled
        if hasattr(these_args, 'slack'):
            if these_args.slack:
                self.__process_slack()
        
        return these_args
