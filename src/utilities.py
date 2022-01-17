import logging
import coloredlogs
from decouple import config


class Utilities:

    def compare_dict(self, dict1, dict2):
        output = []
        for key1 in dict1:
            if key1 not in dict2:
                output.append(key1)
        return output

    def compare_list(self, list1, list2):
        return list(set(list1)-set(list2))

    @staticmethod
    def setup_logger():
        logger = logging.getLogger("netregator")
        if config("DEBUG", False, cast=bool):
            coloredlogs.install(fmt='[%(asctime)s] [%(levelname)s] %(message)s', logger=logger, level=logging.DEBUG)
        else:
            coloredlogs.install(fmt='[%(asctime)s] [%(levelname)s] %(message)s', logger=logger, level=logging.INFO)
        return logger


