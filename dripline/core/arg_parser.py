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
                 user_pass_support=False,
                 **kwargs):
        '''
        Keyword Args:
            extra_logger (logging.Logger): reference to a Logger instance, (handlers created will be connected to it)
            amqp_broker (bool): enable a '-b' option for specifying the broker's network address
            config_file (bool): enable a '-c' option for specifying an input configuration file
            tmux_support (bool): enable a '-t' option to start the process in a tmux session rather than on the active shell
            twitter_support (bool): enable a '-T' option to send a logger messages of critical or higher severity as tweets
            slack_support (bool): enable a '-S' option to send log messages to slack channels
            user_pass_support (bool): enable '-u' and '-p' for user and password specification. **Note:** these options should be replaced with either reading the standard file ~/.project8_authentication.json, and/or prompting the user for values interactively

        '''
        self.extra_logger = extra_logger
        argparse.ArgumentParser.__init__(self, **kwargs)
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
                              help='network path for the AMQP broker',
                              default='localhost',
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
        if user_pass_support:
            self.add_argument('-u',
                              '--user',
                              help='substitue user lines in config file',
                              default=None,
                             )
            self.add_argument('-p',
                              '--password',
                              help='substitue password lines in config file',
                              default=None,
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
        args = argparse.ArgumentParser.parse_args(self)
        args_dict = vars(args)

        # add args specified in a config file if there is one
        if 'config' in args:
            if args.config is not None:
                try:
                    file_str = open(args.config).read()
                    import yaml
                    if 'user' in args:
                        if args.user is not None:
                            logger.info('updating user')
                            import re
                            reg_ex = r'([ ]*[-]? user:[ ]*)([\S]*)(.*)'
                            new_user = r'\1{}\3'.format(args.user)
                            file_str = re.sub(reg_ex, new_user, file_str)
                    if 'password' in args:
                        if args.password is not None:
                            logger.info("updating password")
                            import re
                            reg_ex = r'([ ]*[-]? password:[ ]*)([\S]*)(.*)'
                            new_pass = r'\1{}\3'.format(args.password)
                            file_str = re.sub(reg_ex, new_pass, file_str)
                    conf_file = yaml.load(file_str)
                    conf_file.update(args_dict)
                    args_dict['config'] = conf_file
                    args = DotAccess(args_dict)
                except:
                    print("parsing of config failed")
                    raise

        # setup loggers and handlers
        log_level = max(0, 25-args.verbose*10)
        self._handlers[0].setLevel(log_level)
        if not args.logfile is None:
            _file_handler = logging.FileHandler(args.logfile)
            _file_handler.setFormatter(self.fmt)
            _file_handler.setLevel(log_level)
            logger.addHandler(_file_handler)
            if self.extra_logger:
                self.extra_logger.addHandler(_file_handler)
            self._handlers.append(_file_handler)

        # take care of tmux if needed
        if hasattr(args, 'tmux'):
            if not args.tmux is None:
                self.__process_tmux(args)

        # and add twitter to the log handling if enabled
        if hasattr(args, 'twitter'):
            if args.twitter:
                self.__process_twitter()

        # and add slack to the log handling if enabled
        if hasattr(args, 'slack'):
            if args.slack:
                self.__process_slack()
        
        return args
