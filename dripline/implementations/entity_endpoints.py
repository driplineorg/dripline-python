'''
A Entity is an enhanced implementation of a Dripline Endpoint with simple logging capabilities.
The Entitys defined here are more broad-ranging than a single service, obviating the need to define new Entitys for each new service or provider.

When implementing a Entity, please remember:
- All communication must be configured to return a response.  If no useful get is possible, consider a \*OPC?
- set_and_check is a generally desirable functionality

Generic Entity catalog (in order of ease-of-use):
- SimpleSCPIEntity: quick and simple minimal Entity
- SimpleSCPIGetEntity/SimpleSCPISetEntity: limited instance of above with disabled Get/Set
- FormatEntity: utility Entity with expanded functionality
'''

import asteval # used for FormatEntity
import re # used for FormatEntity

from dripline.core import Entity, calibrate, ThrowReply

import logging
logger = logging.getLogger(__name__)

__all__ = []

__all__.append('SimpleSCPIEntity')
class SimpleSCPIEntity(Entity):
    '''
    Convenience Entity for interacting with SCPI endpoints that support basic assignment and query syntax.
    (That is, assignments of the form "base_string <new_value>" and queries of the form "base_string?")
    Commands requiring a more complex structure, such as specifying channels or other arguments, should use FormatEntity or a custom Entity.
    '''

    def __init__(self,
                 base_str=None,
                 **kwargs):
        '''
        Args:
            base_str (str): string used to generate SCPI commands; get will be of the form "base_str?"; set will be of the form "base_str <value>;base_str?"
        '''
        if base_str is None:
            raise ValueError('<base_str> is required to __init__ SimpleSCPIEntity instance')
        else:
            self.cmd_base = base_str
        Entity.__init__(self, **kwargs)

    @calibrate()
    def on_get(self):
        to_send = [self.cmd_base + '?']
        result = self.service.send_to_device(to_send)
        logger.debug(f'raw result is: {result}')
        return result

    def on_set(self, value):
        to_send = [f'{self.cmd_base} {value};{self.cmd_base}?']
        return self.service.send_to_device(to_send)


__all__.append('SimpleSCPIGetEntity')
class SimpleSCPIGetEntity(SimpleSCPIEntity):
    '''
    Identical to SimpleSCPIEntity, but with an explicit exception if on_set is attempted
    '''

    def __init__(self, **kwargs):
        SimpleSCPIEntity.__init__(self, **kwargs)

    def on_set(self, value):
        raise ThrowReply('message_error_invalid_method', f"endpoint '{self.name}' does not support set")


__all__.append('SimpleSCPISetEntity')
class SimpleSCPISetEntity(SimpleSCPIEntity):
    '''
    Modelled on SimpleSCPIEntity, but with an explicit exception if on_get is attempted.
    Uses \*OPC? to ensure a response is generated when making an assignment.
    '''

    def __init__(self, **kwargs):
        SimpleSCPIEntity.__init__(self, **kwargs)

    def on_get(self):
        # exceptions.DriplineMethodNotSupportedError
        raise ThrowReply('message_error_invalid_method', f"endpoint '{self.name}' does not support get")

    def on_set(self, value):
        to_send = [f'{self.cmd_base} {value};*OPC?']
        return self.service.send_to_device(to_send)


__all__.append('FormatEntity')
class FormatEntity(Entity):
    '''
    Utility Entity allowing arbitrary set and query syntax and formatting for more complicated usage cases
    No assumption about SCPI communication syntax.
    '''

    def __init__(self,
                 get_str=None,
                 get_reply_float=False,
                 set_str=None,
                 set_value_lowercase=True,
                 set_value_map=None,
                 extract_raw_regex=None,
                 **kwargs):
        '''
        Args:
            get_str (str): sent verbatim in the event of on_get; if None, getting of endpoint is disabled
            get_reply_float (bool): apply special formatting to get return
            set_str (str): sent as set_str.format(value) in the event of on_set; if None, setting of endpoint is disabled
            set_value_lowercase (bool): default option to map all string set value to .lower()
                **WARNING**: never set to False if using a set_value_map dict
            set_value_map (str||dict): inverse of calibration to map raw set value to value sent; either a dictionary or an asteval-interpretable string
            extract_raw_regex (str): regular expression search pattern applied to get return. Must be constructed with an extraction group keyed with the name "value_raw" (ie r'(?P<value_raw>)' ) 
        '''
        Entity.__init__(self, **kwargs)
        self._get_reply_float = get_reply_float
        self._get_str = get_str
        self._set_str = set_str
        self._set_value_map = set_value_map
        self._extract_raw_regex = extract_raw_regex
        self.evaluator = asteval.Interpreter()
        if set_value_map is not None and not isinstance(set_value_map, (dict,str)):
            raise ValueError(f"Invalid set_value_map config for {self.name}; type is {type(set_value_map)} not dict")
        self._set_value_lowercase = set_value_lowercase
        if isinstance(set_value_map, dict) and not set_value_lowercase:
            raise ValueError(f"Invalid config option for {self.name} with set_value_map and set_value_lowercase=False")

    @calibrate()
    def on_get(self):
        if self._get_str is None:
            # exceptions.DriplineMethodNotSupportedError
            raise ThrowReply('message_error_invalid_method', f"endpoint '{self.name}' does not support get")
        result = self.service.send_to_device([self._get_str])
        logger.debug(f'result is: {result}')
        if self._extract_raw_regex is not None:
            first_result = result
            matches = re.search(self._extract_raw_regex, first_result)
            if matches is None:
                logger.error('matching returned none')
                # exceptions.DriplineValueError
                raise ThrowReply('resource_error', 'device returned unparsable result, [{}] has no match to input regex [{}]'.format(first_result, self._extract_raw_regex))
            logger.debug(f"matches are: {matches.groupdict()}")
            result = matches.groupdict()['value_raw']
        return result

    def on_set(self, value):
        if self._set_str is None:
            # exceptions.DriplineMethodNotSupportedError
            raise ThrowReply('service_error', f"endpoint '{self.name}' does not support set")
        if isinstance(value, str) and self._set_value_lowercase:
            value = value.lower()
        if self._set_value_map is None:
            mapped_value = value
        elif isinstance(self._set_value_map, dict):
            mapped_value = self._set_value_map[value]
        elif isinstance(self._set_value_map, str):
            mapped_value = self.evaluator(self._set_value_map.format(value))
        logger.debug(f'value is {value}; mapped value is: {mapped_value}')
        return self.service.send_to_device([self._set_str.format(mapped_value)])
        
        
        
        
__all__.append('ProviderAttributeEntity')
class ProviderAttributeEntity(Entity):
    '''
    Spime allowing communication with provider property.
    '''

    def __init__(self,
                 attribute_name,
                 disable_set=False,
                 **kwargs):
       Entity.__init__(self, **kwargs)
       self._attribute_name = attribute_name
       self._disable_set = disable_set

    @calibrate()
    def on_get(self):
        return getattr(self.service, self._attribute_name)

    def on_set(self, value):
        setattr(self.service, self._attribute_name, value)
        

