import logging
import coloredlogs
import verboselogs
from decouple import config
import inspect
import collections.abc


class Utilities:
    @staticmethod
    def compare_dict(dict1, dict2):
        output = []
        for key1 in dict1:
            if key1 not in dict2:
                output.append(key1)
        return output

    @staticmethod
    def compare_list(list1, list2):
        return list(set(list1)-set(list2))

    @staticmethod
    def update_multidimensional_dict(orig_dict, new_dict):
        for k, v in new_dict.items():
            if isinstance(v, collections.abc.Mapping):
                orig_dict[k] = Utilities.update_multidimensional_dict(orig_dict.get(k, {}), v)
            else:
                orig_dict[k] = v
        return orig_dict

    @staticmethod
    def setup_logger(additional_info: str = None):
        stack = inspect.stack()
        caller_classname = stack[1][0].f_locals["self"].__class__.__name__
        logger = verboselogs.VerboseLogger("netregator")  # logging.getLogger("netregator")
        logger.addHandler(logging.StreamHandler())
        if additional_info:
            caller_classname = f"{caller_classname}:{additional_info}"
        fmt = f'[%(asctime)s] [%(levelname)s] [{caller_classname}] %(message)s'
        if config("LOG_LEVEL", 2, cast=int) == 0:
            coloredlogs.install(fmt=fmt, logger=logger, level=verboselogs.SPAM)
        elif config("LOG_LEVEL", 2, cast=int) == 1:
            coloredlogs.install(fmt=fmt, logger=logger, level=logging.DEBUG)
        elif config("LOG_LEVEL", 2, cast=int) == 2:
            coloredlogs.install(fmt=fmt, logger=logger, level=logging.INFO)
        elif config("LOG_LEVEL", 2, cast=int) == 3:
            coloredlogs.install(fmt=fmt, logger=logger, level=logging.WARNING)
        elif config("LOG_LEVEL", 2, cast=int) == 4:
            coloredlogs.install(fmt=fmt, logger=logger, level=logging.ERROR)

        return logger
