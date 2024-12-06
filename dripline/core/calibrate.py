try:
    import asteval
except ImportError:
    # optional only when doing a docs build
    pass



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
                    logger.debug('GOT AN OVERFLOW ERROR')
                    cal = None
                except Exception as e:
                    raise ValueError(repr(e))
                if cal is not None:
                    val_dict['value_cal'] = cal
            elif isinstance(self._calibration, dict):
                logger.debug('calibration is dictionary, looking up value')
                if val_dict['value_raw'] in self._calibration:
                    val_dict['value_cal'] = self._calibration[val_dict['value_raw']]
                else:
                    raise ValueError(f"raw value <{repr(val_dict['value_raw'])}> not in cal dict)
            else:
                logger.warning('the _calibration property is of unknown type')
            return val_dict
        return wrapper
    return calibration



