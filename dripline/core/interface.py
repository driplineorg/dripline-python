__all__ = []

import scarab

from _dripline.core import op_t, create_dripline_auth_spec, Core, DriplineConfig, Receiver, MsgRequest, DriplineError

import logging
logger = logging.getLogger(__name__)

__all__.append("Interface")
class Interface(Core):
    '''
    A class on top of dripline.core.Core with more user-friendly methods for dripline interactions.
    Intended for use as a dripline client in scripts or interactive sessions.
    '''
    def __init__(self, timeout_s=10, confirm_retcodes=True, auth={}, dripline_mesh={}):
        '''
        dripline_config (dict): passed to dripline.core.Core to configure connection details
        confirm_retcodes (bool): if True and if a reply is received with retcode!=0, raise an exception
        '''

        dripline_config = DriplineConfig().to_python()
        dripline_config.update(dripline_mesh)

        dl_auth_spec = create_dripline_auth_spec()
        dl_auth_spec.merge( scarab.to_param(auth) )
        auth_spec = scarab.ParamNode()
        auth_spec.add('dripline', dl_auth_spec)
        logger.debug(f'Loading auth spec:\n{auth_spec}')
        auth = scarab.Authentication()
        auth.add_groups(auth_spec)
        auth.process_spec()

        self._confirm_retcode = confirm_retcodes
        self.timeout_s = timeout_s
        self._receiver = Receiver()

        Core.__init__(self, config=scarab.to_param(dripline_config), auth=auth)

    def _send_request(self, msgop, target, specifier=None, payload=None, timeout=None, lockout_key=False):
        '''
        internal helper method to standardize sending request messages
        '''
        a_specifier = specifier if specifier is not None else ""
        a_request = MsgRequest.create(payload=scarab.to_param(payload), msg_op=msgop, routing_key=target, specifier=a_specifier)
        receive_reply = self.send(a_request)
        if not receive_reply.successful_send:
            raise DriplineError('unable to send request')
        return receive_reply

    def _receive_reply(self, reply_pkg, timeout):
        '''
        internal helper method to standardize receiving reply messages
        '''
        sig_handler = scarab.SignalHandler()
        sig_handler.add_cancelable(self._receiver)
        result = self._receiver.wait_for_reply(reply_pkg, timeout)
        sig_handler.remove_cancelable(self._receiver)
        return result

    def get(self, endpoint, specifier=None, timeout=0):
        '''
        [kw]args:
        endpoint (string): routing key to which an OP_GET will be sent
        specifier (string|None): specifier to add to the message
        timeout (int|0): timeout in ms
        '''
        reply_pkg = self._send_request( msgop=op_t.get, target=endpoint, specifier=specifier )
        result = self._receive_reply( reply_pkg, timeout )
        return result

    def set(self, endpoint, value, specifier=None, timeout=0):
        '''
        [kw]args:
        endpoint (string): routing key to which an OP_GET will be sent
        value : value to assign
        specifier (string|None): specifier to add to the message
        timeout (int|0): timeout in ms
        '''
        payload = {'values':[value]}
        reply_pkg = self._send_request( msgop=op_t.set, target=endpoint, specifier=specifier, payload=payload )
        result = self._receive_reply( reply_pkg, timeout )
        return result

    def cmd(self, endpoint, method, ordered_args=[], keyed_args={}, timeout=0):
        '''
        [kw]args:
        endpoint (string): routing key to which an OP_GET will be sent
        method (string): specifier to add to the message, naming the method to execute
        arguments (dict): dictionary of arguments to the specified method
        timeout (int|0): timeout in ms
        '''
        payload = {'values': ordered_args}
        payload.update(keyed_args)
        reply_pkg = self._send_request( msgop=op_t.cmd, target=endpoint, specifier=method, payload=payload )
        result = self._receive_reply( reply_pkg, timeout )
        return result
