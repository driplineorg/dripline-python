try:
    import asteval
except ImportError:
    # optional only when doing a docs build
    pass
from .throw_reply import ThrowReply


__all__ = []

import logging
logger = logging.getLogger(__name__)

__all__.append("calibrate")
def calibrate(cal_functions=None):
    if callable(cal_functions):
        cal_functions = {cal_functions.__name__: cal_functions}
    elif isinstance(cal_functions, list):
        cal_functions = {f.__name__:f for f in cal_functions}
    elif cal_functions is None:
        cal_functions = {}
    def calibration(fun):
        def wrapper(self, *args, **kwargs):
            very_raw = fun(self)
            if isinstance(very_raw, list):
                very_raw = very_raw[0]
            val_dict = {'value_raw':very_raw}
            logger.debug('attempting to calibrate')
            if val_dict['value_raw'] is None:
                return None
            if self._calibration is None:
                pass
            elif isinstance(self._calibration, str):
                evaluator = asteval.Interpreter(usersyms=cal_functions)
                if isinstance(val_dict['value_raw'], float):
                    eval_str = self._calibration.format(val_dict['value_raw'])
                elif isinstance(val_dict['value_raw'], str):
                    eval_str = self._calibration.format(val_dict['value_raw'].strip())
                else:
                    eval_str = self._calibration.format(val_dict['value_raw'])
                logger.debug(f"formatted cal is:\n{eval_str}")
                try:
                    cal = evaluator(eval_str)
                except OverflowError:
                    raise ThrowReply('service_error_bad_payload', 'GOT AN OVERFLOW ERROR')
                except Exception as e:
                    raise ThrowReply('service_error_invalid_value', repr(e))
                if cal is not None:
                    val_dict['value_cal'] = cal
            elif isinstance(self._calibration, dict):
                logger.debug('calibration is dictionary, looking up value')
                value_raw_str = str(val_dict['value_raw'])
                if value_raw_str in self._calibration:
                    val_dict['value_cal'] = self._calibration[str(val_dict['value_raw'])]
                else:
                    raise ThrowReply('service_error_invalid_value', f"raw value <{str(val_dict['value_raw'])}> {type(val_dict['value_raw'])} not in cal dict with calibrate dict {self._calibration}")
                logger.debug(f"formatted cal is:\n{ val_dict['value_cal'] }")
            else:
                logger.warning('the _calibration property is of unknown type')
            return val_dict
        return wrapper
    return calibration



