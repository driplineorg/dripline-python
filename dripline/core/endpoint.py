__all__ = []

import scarab
from _dripline.core import _Endpoint
from .throw_reply import ThrowReply

import logging

logger = logging.getLogger(__name__)

__all__.append('Endpoint')


class Endpoint(_Endpoint):
    '''
    Base class for all objects which can be sent dripline requests.
    Every object described in a runtime configuration passed to `dl-serve` should derive from this class (either directly or indirectly).
    '''

    def __init__(self, name):
        '''
        Args:
            name (str) : the name of the endpoint, specifies the binding key for request messages to which this object should reply
        '''
        _Endpoint.__init__(self, name)

    def result_to_scarab_payload(self, result: str):
        """
        Intercept result values and throw error if scarab is unable to convert to param
        TODO: Handles global Exception case, could be more specific
        Args:
            result (str): request message passed
        """
        try:
            return scarab.to_param(result)
        except Exception as e:
            raise ThrowReply('service_error_bad_payload',
                             f"{self.name} unable to convert result to scarab payload: {result}")

    def do_get_request(self, a_request_message):
        logger.info("in get_request")
        a_specifier = a_request_message.specifier.to_string()
        if (a_specifier):
            logger.debug("has specifier")
            try:
                logger.debug(f"specifier is: {a_specifier}")
                an_attribute = getattr(self, a_specifier)
                logger.debug(f"attribute '{a_specifier}' value is [{an_attribute}]")
                the_node = scarab.ParamNode()
                the_node["values"] = scarab.ParamArray()
                the_node["values"].push_back(scarab.ParamValue(an_attribute))
                return a_request_message.reply(payload=the_node)
            except AttributeError as this_error:
                raise ThrowReply('service_error_invalid_specifier',
                                 f"endpoint {self.name} has no attribute {a_specifier}, unable to get")
        else:
            logger.debug('no specifier')
            the_value = self.on_get()
            return a_request_message.reply(payload=self.result_to_scarab_payload(the_value))

    def do_set_request(self, a_request_message):

        a_specifier = a_request_message.specifier.to_string()
        if not "values" in a_request_message.payload:
            raise ThrowReply('service_error_bad_payload',
                             'setting called without values, but values are required for set')
        new_value = a_request_message.payload["values"][0]()
        new_value = getattr(new_value, "as_" + new_value.type())()
        logger.debug(f'Attempting to set new_value to [{new_value}]')

        if (a_specifier):
            if not hasattr(self, a_specifier):
                raise ThrowReply('service_error_invalid_specifier',
                                 "endpoint {} has no attribute {}, unable to set".format(self.name, a_specifier))
            setattr(self, a_specifier, new_value)
            return a_request_message.reply()
        else:
            result = self.on_set(new_value)
            return a_request_message.reply(payload=self.result_to_scarab_payload(result))

    def do_cmd_request(self, a_request_message):
        # Note: any command executed in this way must return a python data structure which is
        #       able to be converted to a Param object (to be returned in the reply message)
        method_name = a_request_message.specifier.to_string()
        try:
            method_ref = getattr(self, method_name)
        except AttributeError as e:
            raise ThrowReply('service_error_invalid_method',
                             "error getting command's corresponding method: {}".format(str(e)))
        the_kwargs = a_request_message.payload.to_python()
        the_args = the_kwargs.pop('values', [])
        result = method_ref(*the_args, **the_kwargs)
        return a_request_message.reply(payload=self.result_to_scarab_payload(result))

    def on_get(self):
        '''
        placeholder method for getting the value of an endpoint.
        Implementations may override to enable OP_GET operations.
        The implementation must return a value which is able to be passed to the ParamValue constructor.
        '''
        raise ThrowReply('service_error_invalid_method', "{} does not implement on_get".format(self.__class__))

    def on_set(self, _value):
        '''
        placeholder method for setting the value of an endpoint.
        Implementations may override to enable OP_SET operations.
        Any returned object must already be a scarab::Param object
        '''
        raise ThrowReply('service_error_invalid_method', "{} does not implement on_set".format(self.__class__))
