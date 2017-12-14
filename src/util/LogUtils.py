import datetime
import os
import logging
from src.util.FileUtils import FileUtils


class LogUtils:

    @staticmethod
    def generate_logger(log_folder_path):
        log_file_name = datetime.date.today().strftime('%Y%m%d') + ".log"
        log_file_path = os.path.join(log_folder_path, datetime.date.today().strftime('%Y%m%d') + ".log")

        if not os.path.isfile(log_file_path):
            FileUtils.touch(log_folder_path, log_file_name)

        logging.basicConfig(filename=log_file_path, level=logging.INFO)
        log_formatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
        root_logger = logging.getLogger()
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(log_formatter)
        root_logger.addHandler(file_handler)
