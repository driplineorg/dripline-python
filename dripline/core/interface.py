__all__ = []

import scarab

from _dripline.core import op_t, create_dripline_auth_spec, Core, DriplineConfig, Receiver, MsgRequest, MsgReply, DriplineError

import logging
logger = logging.getLogger(__name__)

__all__.append("Interface")
class Interface(Core):
    '''
    A class that provides user-friendly methods for dripline interactions in a Python interpreter.
    Intended for use as a dripline client in scripts or interactive sessions.
    '''
    def __init__(self, username: str | dict=None, password: str | dict=None, dripline_mesh: dict=None, timeout_s: int=10, confirm_retcodes: bool=True):
        '''
        Configures an interface with the necessary parameters.

        Parameters
        ----------
            username : string or dict, optional
                Provide a username for authenticating with the broker, either directly or by indicating how to get the username information.
                Username can be provided directly as a string.  This will override all other username specifications (default, environment variable, etc).
                Options for providing the username can be supplied as a dict.  If a dict is used, the possible elements, and their dripline defaults, are:
                    - 'value': provide the username directly (same effect as if the string option were used).  This overrides the 'file', 'env', and 'default' options.
                    - 'file': provide a file that contains only the username.  This overrides the 'env' and 'default' options.
                    - 'env': provide an environment variable that contains the username -- the dripline default is 'DRIPLINE_USER'.  This overrides the 'default' value option.
                    - 'default': set the default username -- dripline default is 'dripline'
            password: string or dict, optional
                Provide a password directly or indicate how to get the password information.
                Password can be provided directly as a string, though this is not recommended since it will remain in your Python command history.  This will override all other password specifications (default, environment variable, etc).
                Recommended methods for providing a password are as an environment variable or in a password file.
                Options for providing the password can be supplied as a dict.  If a dict is used, the possible elements, and their dripline defaults, are:
                    - 'value': provide the password directly (same effect as if the string option were used).  This overrides the 'file', 'env', and 'default' options.
                    - 'file': provide a file that contains only the password.  This overrides the 'env' and 'default' options.
                    - 'env': provide an environment variable that contains the password -- the dripline default is 'DRIPLINE_PASSWORD'.  This overrides the 'default' value option.
                    - 'default': set the default password -- dripline default is 'dripline'
            dripline_mesh : dict, optional
                Provide optional dripline mesh configuration information (see dripline_config for more information)
            timeout_s: int, optional
                Time to wait for a reply, in seconds -- default is 10 s
            confirm_retcodes: bool, optional  
                If True, and if a reply is received with retcode != 0, raises an exception -- default is True          
        '''

        dripline_config = DriplineConfig().to_python()
        if dripline_mesh is not None:
            dripline_config.update(dripline_mesh)

        dl_auth_spec = create_dripline_auth_spec()
        auth_args = {
            'username': {} if username is None else username,
            'password': {} if password is None else password,
        }
        dl_auth_spec.merge( scarab.to_param(auth_args) )
        auth_spec = scarab.ParamNode()
        auth_spec.add('dripline', dl_auth_spec)
        logger.debug(f'Loading auth spec:\n{auth_spec}')
        auth = scarab.Authentication()
        auth.add_groups(auth_spec)
        auth.process_spec()

        Core.__init__(self, config=scarab.to_param(dripline_config), auth=auth)

        self._confirm_retcode = confirm_retcodes
        self.timeout_s = timeout_s
        self._receiver = Receiver()


    def _send_request(self, msgop, target, specifier=None, payload=None, timeout=None, lockout_key=None):
        '''
        internal helper method to standardize sending request messages
        '''
        a_specifier = specifier if specifier is not None else ""
        a_request = MsgRequest.create(payload=scarab.to_param(payload), msg_op=msgop, routing_key=target, specifier=a_specifier)
        a_request.lockout_key = lockout_key if lockout_key is not None else ""
        receive_reply = self.send(a_request)
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
        return result

    def get(self, endpoint: str, specifier: str=None, lockout_key=None, timeout_s: int=0) -> MsgReply:
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

    def set(self, endpoint: str, value: str | int | float | bool, specifier: str=None, lockout_key=None, timeout_s: int | float=0) -> MsgReply:
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

    def cmd(self, endpoint: str, specifier: str, ordered_args=None, keyed_args=None, lockout_key=None, timeout_s: int | float=0) -> MsgReply:
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
