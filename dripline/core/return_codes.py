__all__ = []

from _dripline.core import get_return_codes_map

import logging
logger = logging.getLogger(__name__)

__all__.append("get_return_codes_dict")
def get_return_codes_dict():
    '''
    Construct a dictionary of return codes, keyed on names (snake_case)

    NOTE: return codes can be dynamically added at runtime, this function returns the current set when it is called; you probably when to call it when you need the codes rather than creating the dict earlier.
    '''
    return {a_return_code.name:a_return_code for (_, a_return_code) in get_return_codes_map().items()}
