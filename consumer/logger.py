import logging
import sys
import traceback
from typing import Callable

import datetime

def get_current_time():
    current_time = datetime.datetime.now()
    return current_time


class FileIsNotLogError(Exception):
    pass

class Logger:
    FORMAT = '%(levelname)-8s %(message)s'
    def __init__(self, file_name:str) -> None:

        if ".log" not in file_name:
            raise FileIsNotLogError(f"{file_name} is not a valid log file (.log)")

        self.logger = self.__get_logger(file_name)

    def __get_logger(self, file_name:str) -> logging.Logger:
        # create logger with 'file_name'
        logger = logging.getLogger(f"{file_name}")
        logger.setLevel(logging.DEBUG)
        # create file handler which logs even debug messages
        file_handler = logging.FileHandler(f"{file_name}")
        file_handler.setLevel(logging.DEBUG)
        # create console handler with a higher log level
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        # create formatter and add it to the handlers
        formatter = logging.Formatter(self.FORMAT)
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)
        # add the handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
        return logger

    def _get_error_detail(self, error:Exception) -> str:
        error_class_name = error.__class__.__name__ # class name that causes the exception
        error_detail = error.args[0] # detailed info
        _, _, trace_back = sys.exc_info() # get comprehensive error information of current call stack
        last_call_stack = traceback.extract_tb(trace_back)[-1] # get the last line of error info
        file_name_error_occurred, error_line_number, func_name, _ = last_call_stack
        error_msg = f"Time: {get_current_time()}, Exception raise in file: {file_name_error_occurred}, line {error_line_number}, in {func_name}: [{error_class_name}] {error_detail}."
        return error_msg

    def log_error(self, exception: Exception) -> None:
        error_detail = self._get_error_detail(exception)
        self.logger.error(error_detail)


    def log_error_decor(self, func:Callable) -> None:
        def wrapper(*args, **kwargs) -> Callable:
            try:
                return func(*args, **kwargs)
            except Exception as error:
                error_detail = self._get_error_detail(error)
                self.logger.error(error_detail)

        return wrapper
