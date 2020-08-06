__all__ = []

import scarab

from dripline.core import op_t, Core, DriplineConfig, Receiver, MsgRequest, DriplineError

import logging
logger = logging.getLogger(__name__)

__all__.append("Interface")
class Interface(Core):
    '''
    A class on top of dripline.core.Core with more user-friendly methods for dripline interactions.
    Intended for use as a dripline client in scripts or interactive sessions.
    '''
    def __init__(self, dripline_config={}, confirm_retcodes=True, lockout_key = None):
        '''
        dripline_config (dict): passed to dripline.core.Core to configure connection details
        confirm_retcodes (bool): if True and if a reply is received with retcode!=0, raise an exception
        '''
        default_config = DriplineConfig().to_python()
        default_config.update(dripline_config)
        Core.__init__(self, config=scarab.to_param(default_config))
        self._confirm_retcode = confirm_retcodes
        self._receiver = Receiver()

    def _send_request(self, msgop, target, specifier=None, payload=None, timeout=None, lockout_key=None):
        '''
        internal helper method to standardize sending request messages
        '''
        if not (isinstance(lockout_key, str) or lockout_key == None):
            raise DriplineError('lockout_key needs to be a string')
        a_specifier = specifier if specifier is not None else ""
        if lockout_key == None:
            a_request = MsgRequest.create(payload=scarab.to_param(payload), msg_op=msgop, routing_key=target, specifier=a_specifier)
        else:
            a_request = MsgRequest.create(payload=scarab.to_param(payload), msg_op=msgop, routing_key=target, specifier=a_specifier, lockout_key = lockout_key)
        receive_reply = self.send(a_request)
        if not receive_reply.successful_send:
            raise DriplineError('unable to send request')
        return receive_reply

    def get(self, endpoint, specifier=None, timeout=0, lockout_key=None):
        '''
        [kw]args:
        endpoint (string): routing key to which an OP_GET will be sent
        specifier (string|None): specifier to add to the message
        '''
        if not (isinstance(lockout_key, str) or lockout_key == None):
            raise DriplineError('lockout_key needs to be a string')
        reply_pkg = self._send_request( msgop=op_t.get, target=endpoint, specifier=specifier, lockout_key = lockout_key )
        result = self._receiver.wait_for_reply(reply_pkg, timeout)
        return result

    def set(self, endpoint, value, specifier=None, timeout=0, lockout_key=None):
        '''
        [kw]args:
        endpoint (string): routing key to which an OP_GET will be sent
        value : value to assign
        specifier (string|None): specifier to add to the message
        '''
        if not (isinstance(lockout_key, str) or lockout_key == None):
            raise DriplineError('lockout_key needs to be a string')
        payload = {'values':[value]}
        reply_pkg = self._send_request( msgop=op_t.set, target=endpoint, specifier=specifier, payload=payload, lockout_key = lockout_key )
        result = self._receiver.wait_for_reply(reply_pkg, timeout)
        return result

    def cmd(self, endpoint, method, ordered_args=[], keyed_args={}, timeout=0, lockout_key=None):
        '''
        [kw]args:
        endpoint (string): routing key to which an OP_GET will be sent
        method (string): specifier to add to the message, naming the method to execute
        arguments (dict): dictionary of arguments to the specified method
        '''
        if not (isinstance(lockout_key, str) or lockout_key == None):
            raise DriplineError('lockout_key needs to be a string')
        payload = {'values': ordered_args}
        payload.update(keyed_args)
        reply_pkg = self._send_request( msgop=op_t.cmd, target=endpoint, specifier=method, payload=payload, lockout_key = lockout_key )
        result = self._receiver.wait_for_reply(reply_pkg, timeout)
        return result
