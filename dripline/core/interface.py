__all__ = []

import scarab

from _dripline.core import op_t, create_dripline_auth_spec, Core, DriplineConfig, Receiver, MsgRequest, MsgReply, DriplineError
from .request_sender import RequestSender

import logging
logger = logging.getLogger(__name__)

__all__.append("Interface")
class Interface(Core, RequestSender):
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
        RequestSender.__init__(self, sender=self)

        self._confirm_retcode = confirm_retcodes
        self.timeout_s = timeout_s
        self._receiver = Receiver()

