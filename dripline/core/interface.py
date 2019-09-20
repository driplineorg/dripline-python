__all__ = []

import scarab

from dripline.core import op_t, Core, DriplineConfig, Receiver, MsgRequest

__all__.append("Interface")
class Interface(Core):
    '''
    A class on top of dripline.core.Core with more user-friendly methods for dripline interactions.
    Intended for use as a dripline client in scripts or interactive sessions.
    '''
    def __init__(self, dripline_config={}, confirm_retcodes=True):
        '''
        dripline_config (dict): passed to dripline.core.Core to configure connection details
        confirm_retcodes (bool): if True and if a reply is received with retcode!=0, raise an exception
        '''
        default_config = DriplineConfig().to_python()
        default_config.update(dripline_config)
        Core.__init__(self, config=scarab.to_param(default_config))
        self._confirm_retcode = confirm_retcodes
        self._receiver = Receiver()

    def _send_request(self, msgop, target, specifier=None, payload=None, timeout=None, lockout_key=False):
        '''
        internal helper method to standardize sending request messages
        '''
        a_specifier = specifier if specifier is not None else ""
        a_request = MsgRequest.create(payload=scarab.to_param(payload), msg_op=msgop, routing_key=target, specifier=a_specifier)
        return self.send(a_request)

    def get(self, endpoint, specifier=None, timeout=0):
        '''
        [kw]args:
        endpoint (string): routing key to which an OP_GET will be sent
        specifier (string|None): specifier to add to the message
        '''
        reply_pkg = self._send_request( msgop=op_t.get, target=endpoint, specifier=specifier )
        result = self._receiver.wait_for_reply(reply_pkg, timeout)
        return result

    def set(self, endpoint, value, specifier=None, timeout=0):
        '''
        [kw]args:
        endpoint (string): routing key to which an OP_GET will be sent
        value : value to assign
        specifier (string|None): specifier to add to the message
        '''
        payload = {'values':[value]}
        reply_pkg = self._send_request( msgop=op_t.get, target=endpoint, specifier=specifier, payload=payload )
        result = self._receiver.wait_for_reply(reply_pkg, timeout)
        return result

    def cmd(self, endpoint, method, ordered_args=[], keyed_args={}, timeout=0):
        '''
        [kw]args:
        endpoint (string): routing key to which an OP_GET will be sent
        method (string): specifier to add to the message, naming the method to execute
        arguments (dict): dictionary of arguments to the specified method
        '''
        payload = {'values': ordered_args}
        payload.update(keyed_args)
        reply_pkg = self._send_request( msgop=op_t.get, target=endpoint, specifier=method, payload=payload )
        result = self._receiver.wait_for_reply(reply_pkg, timeout)
        return result
