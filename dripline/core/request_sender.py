__all__ = []

import scarab

from _dripline.core import op_t, Core, Receiver, MsgRequest, MsgReply, DriplineError
import uuid
import logging
logger = logging.getLogger(__name__)

__all__.append("RequestSender")
class RequestSender():
    '''
    A mixin class that provides convenient methods for dripline interactions in a dripline objects.
    Intended for use as a dripline client in scripts or interactive sessions.
    '''
    def __init__(self, sender: Core, timeout_s: int=10, confirm_retcodes: bool=True):
        '''
        Configures an interface with the necessary parameters.

        Parameters
        ----------
            sender : Core
                Provide a Core object which will use this mixin. This object will be the one to actually send the messages as it implements the Core functions
            timeout_s: int, optional
                Time to wait for a reply, in seconds -- default is 10 s
            confirm_retcodes: bool, optional  
                If True, and if a reply is received with retcode != 0, raises an exception -- default is True          
        '''
        self.sender = sender
        self._confirm_retcode = confirm_retcodes
        self.timeout_s = timeout_s
        self._receiver = Receiver()

    def _send_request(self, msgop, target, specifier=None, payload=None, timeout=None, lockout_key:str|uuid.UUID=None):
        '''
        internal helper method to standardize sending request messages
        '''
        a_specifier = specifier if specifier is not None else ""
        a_request = MsgRequest.create(payload=scarab.to_param(payload), msg_op=msgop, routing_key=target, specifier=a_specifier)
        if lockout_key is not None:
            try:
                a_request.lockout_key = lockout_key
            except RuntimeError as err:
                err.add_note(f"Lockout key [{lockout_key}] is not uuid format compliant.")
                raise
        receive_reply = self.sender.send(a_request)
        if not receive_reply.successful_send:
            raise DriplineError('unable to send request')
        return receive_reply

    def _receive_reply(self, reply_pkg, timeout_s):
        '''
        internal helper method to standardize receiving reply messages
        '''
        sig_handler = scarab.SignalHandler()
        sig_handler.add_cancelable(self._receiver)
        result = self._receiver.wait_for_reply(reply_pkg, timeout_s * 1000) # receiver expects ms
        sig_handler.remove_cancelable(self._receiver)
        return result.payload.to_python()

    def get(self, endpoint: str, specifier: str=None, lockout_key: str | uuid.UUID=None, timeout_s: int=0) -> MsgReply:
        '''
        Send a get request to an endpoint and return the reply message.

        Parameters
        ----------
            endpoint: str
                Routing key to which the request should be sent.
            specifier: str, optional
                Specifier to add to the request, if needed.
            timeout_s: int | float, optional
                Maximum time to wait for a reply in seconds (default is 0)
                A timeout of 0 seconds means no timeout will be used.
        '''
        reply_pkg = self._send_request( msgop=op_t.get, target=endpoint, specifier=specifier, lockout_key=lockout_key )
        result = self._receive_reply( reply_pkg, timeout_s )
        return result

    def set(self, endpoint: str, value: str | int | float | bool, specifier: str=None, lockout_key: str | uuid.UUID=None, timeout_s: int | float=0) -> MsgReply:
        '''
        Send a set request to an endpoint and return the reply message.

        Parameters
        ----------
            endpoint: str
                Routing key to which the request should be sent.
            value: str | int | float | bool
                Value to assign in the set operation
            specifier: str, optional
                Specifier to add to the request, if needed.
            timeout_s: int | float, optional
                Maximum time to wait for a reply in seconds (default is 0)
                A timeout of 0 seconds means no timeout will be used.
        '''
        payload = {'values':[value]}
        reply_pkg = self._send_request( msgop=op_t.set, target=endpoint, specifier=specifier, payload=payload, lockout_key=lockout_key )
        result = self._receive_reply( reply_pkg, timeout_s )
        return result

    def cmd(self, endpoint: str, specifier: str, ordered_args=None, keyed_args=None, lockout_key: str | uuid.UUID=None, timeout_s: int | float=0) -> MsgReply:
        '''
        Send a cmd request to an endpoint and return the reply message.

        Parameters
        ----------
            endpoint: str
                Routing key to which the request should be sent.
            ordered_args: array, optional
                Array of values to assign under 'values' in the payload, if any
            keyed_args: dict, optional
                Keyword arguments to assign to the payload, if any
            specifier: str
                Specifier to add to the request.  For a dripline-python endpoint, this will be the method executed.
            timeout_s: int | float, optional
                Maximum time to wait for a reply in seconds (default is 0)
                A timeout of 0 seconds means no timeout will be used.
        '''
        payload = {'values': [] if ordered_args is None else ordered_args}
        payload.update({} if keyed_args is None else keyed_args)
        reply_pkg = self._send_request( msgop=op_t.cmd, target=endpoint, specifier=specifier, lockout_key=lockout_key, payload=payload )
        result = self._receive_reply( reply_pkg, timeout_s )
        return result
