import logging


def create_logger():

    level = logging.INFO
    # create logger
    logger = logging.getLogger()
    logger.setLevel(level)

    # create console handler
    ch = logging.StreamHandler()
    ch.setLevel(level)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    return logger
