import argparse
import os
import subprocess
import sys

from dripline.core import constants

import logging
logger = logging.getLogger('dripline')
logger.setLevel(logging.DEBUG)

__all__ = ['DriplineParser']

class DriplineParser(argparse.ArgumentParser):
    '''
    A wrapper of the logger.ArgumentParser for dripline scripts
    '''
    
    def __init__(self,
                 extra_logger=None,
                 amqp_broker=False,
                 config_file=False,
                 tmux_support=False,
                 **kwargs):
        '''
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

    def __set_format(self):
        base_format = '%(asctime)s{}[%(levelname)-8s] %(name)s(%(lineno)d) -> {}%(message)s'
        try:
            import colorlog
            self.fmt = colorlog.ColoredFormatter(
                    base_format.format('%(log_color)s', '%(purple)s'),
                    datefmt = constants.TIME_FORMAT,
                    reset=True,
                    )
        except ImportError:
            self.fmt = logging.Formatter(
                    base_format.format(' ', ''),
                    constants.TIME_FORMAT
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
        session_exists = 0 == subprocess.call('tmux has-session -t {}'.format(session_name),
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
                subprocess.check_call('source {}/bin/activate'.format(sys.prefix).split(),
                                      stdout=open('/dev/null'),
                                      stderr=subprocess.STDOUT,
                                     )
            subprocess.check_call(['tmux', 'send-keys', ' '.join(new_argv+['\n'])],
                                  stdout=open('/dev/null'),
                                  stderr=subprocess.STDOUT,
                                 )
            print('tmux session {} created'.format(session_name))
            sys.exit()

    def parse_args(self):
        '''
        '''
        # first, the parse the args
        args = argparse.ArgumentParser.parse_args(self)
        # setup logging stuff
        log_level = max(0, 30-args.verbose*10)
        self._handlers[0].setLevel(log_level)
        if not args.logfile is None:
            _file_handler = logging.FileHandler(args.logfile)
            _file_handler.setFormatter(self.fmt)
            _file_handler.setLevel(log_level)
            logger.addHandler(_file_handler)
            if self.extra_logger:
                self.extra_logger.addHandler(_file_handler)
            self._handlers.append(_file_handler)
        if not args.tmux is None:
            self.__process_tmux(args)
        return args
