from __future__ import absolute_import

from subprocess import check_output
import logging

from ..core import Provider, AutoReply, DataLogger

__all__ = ['simple_shell_instrument', 'simple_shell_command',
           'sensors_command_temp']
logger = logging.getLogger(__name__)

class simple_shell_instrument(Provider):
    def __init__(self, name, *args):
        self.name = name
        self.endpoints = {}

    def add_endpoint(self, endpoint):
        self.endpoints[endpoint.name] = endpoint
        endpoint.set_provider(self)

    def list_endpoints(self):
        return self.endpoints.keys()

    def endpoint(self, endpoint):
        if endpoint in self.list_endpoints():
            return self.endpoints[endpoint]

    def send_sync(self, to_send):
        raw_result = None
        if to_send:
            raw_result = check_output(to_send)
        return raw_result


class simple_shell_command(AutoReply):
    def __init__(self, name, on_get=None, on_set=None):
        self.name = name
        self._provider = None
        self._on_get = on_get
        self._on_set = on_set

    def on_get(self):
        result = self._provider.send_sync(self._on_get)
        return result

    def on_set(self, value):
        result = self._provider.send_sync(self._on_set.format(value))
        return result

    def on_config(self):
        raise NotImplementedError

    def provider(self):
        return self._provider

    def set_provider(self, provider):
        self._provider = provider


# WARNING, this is not even close to portable
class sensors_command_temp(AutoReply, DataLogger):
    '''
    Temperature sensors on higgsino
    
    This assumes that the "sensors" command is installed, which it probably isn't.
    '''
    def __init__(self, name, core=0):  # , on_get='sensors', on_set=None):
        # DataLogger stuff
        super(sensors_command_temp, self).__init__()
        self.get_value = self.on_get
        self.store_value = self.report_log

        # local stuff
        self.name = name
        self._provider = None
        self._on_get = ['sensors']  # on_get
        self._on_set = None  # on_set
        self._core = core
    @staticmethod
    def report_log(value):
        logger.info("\n\nShould be logging value: {}\n\n".format(value))

    def on_get(self):
        result = None
        res_lines = self._provider.send_sync(self._on_get).split('\n')
        for line in res_lines:
            if line.startswith('Core {}:'.format(self._core)):
                result = line.split()[2].replace('\xc2\xb0', ' ')
        return result

    def on_set(self, value):
        result = self._provider.send_sync(self._on_set.format(value))
        return result

    def on_config(self, attribute, value):
        if hasattr(self, attribute):
            setattr(self, attribute, value)
            logger.info('set {} to {}'.format(attribute, value))
        else:
            raise AttributeError("No attribute: {}".format(attribute))

    def provider(self):
        return self._provider

    def set_provider(self, provider):
        self._provider = provider
