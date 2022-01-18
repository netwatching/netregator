import logging
import coloredlogs
import verboselogs
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
        logger = verboselogs.VerboseLogger("netregator")  #logging.getLogger("netregator")
        logger.addHandler(logging.StreamHandler())
        if config("LOG_LEVEL", 2, cast=int) == 0:
            coloredlogs.install(fmt='[%(asctime)s] [%(levelname)s] %(message)s', logger=logger, level=verboselogs.SPAM)
        elif config("LOG_LEVEL", 2, cast=int) == 1:
            coloredlogs.install(fmt='[%(asctime)s] [%(levelname)s] %(message)s', logger=logger, level=logging.DEBUG)
        elif config("LOG_LEVEL", 2, cast=int) == 2:
            coloredlogs.install(fmt='[%(asctime)s] [%(levelname)s] %(message)s', logger=logger, level=logging.INFO)
        elif config("LOG_LEVEL", 2, cast=int) == 3:
            coloredlogs.install(fmt='[%(asctime)s] [%(levelname)s] %(message)s', logger=logger, level=logging.WARNING)
        elif config("LOG_LEVEL", 2, cast=int) == 4:
            coloredlogs.install(fmt='[%(asctime)s] [%(levelname)s] %(message)s', logger=logger, level=logging.ERROR)

        return logger
