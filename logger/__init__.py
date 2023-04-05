import logging
import sys


class CustomExtraLogAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        my_context = kwargs.pop('extra', self.extra['extra'])
        return '[%s] %s' % (my_context, msg), kwargs


def get_logger(name, level=logging.DEBUG) -> logging.Logger:
    """"logging to logfile as well as on console"""
    FORMAT = "[%(levelname)s  %(name)s %(module)s:%(lineno)s - %(funcName)s() - %(asctime)s]\n\t %(message)s \n"
    TIME_FORMAT = "%d.%m.%Y %I:%M:%S %p"
    FILENAME = './log.log'
    logging.basicConfig(format=FORMAT, datefmt=TIME_FORMAT, level=level, filename=FILENAME)

    logger_instance = logging.getLogger(name)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    logger_instance.addHandler(handler)
    logger_instance = CustomExtraLogAdapter(logger_instance, {"extra": None})
    return logger_instance


logger = get_logger(__name__)

logger.info('Logger initiated')
