
import logging


class Logger:
    def __init__(self, log_file, name=None, level=logging.INFO, mode='a'):
        self.name = name if name is not None else "Logger"
        self.level = level
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.handler = logging.FileHandler(filename=log_file, mode=mode)
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)

    def log(self, level, message):
        self.logger.log(level, message)
