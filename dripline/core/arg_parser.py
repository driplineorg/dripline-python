import argparse

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
        #self._stream_handler = logging.StreamHandler()
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
        return args
