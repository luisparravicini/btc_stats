import logging
import os


def create_logger(name, dir_path):
    logging.basicConfig(
        filename=os.path.join(dir_path, name) + '.log',
        datefmt='%Y-%m-%d %H:%M:%S',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    return logger
