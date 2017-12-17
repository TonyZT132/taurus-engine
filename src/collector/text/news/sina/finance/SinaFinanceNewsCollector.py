# -*- coding: utf-8 -*-
import tushare as ts
import os
import logging

from datetime import date
from datetime import datetime
from configparser import ConfigParser

from src.util.FileUtils import FileUtils


class SinaFinanceNewsCollector:

    def __init__(self, max_news):
        self.__init_logger()
        self.config = ConfigParser()
        self.config.read("configuration/collector/text/collector_sina.config")
        self.MAX_NEWS_COUNT = max_news if max_news is not None else self.config.get('MAX_NEWS_COUNT', 'value')

    @staticmethod
    def __init_logger():
        log_folder_path = "log/collector/text/sina"
        log_file_name = datetime.now().strftime('%c') + ".log"
        log_file_path = os.path.join(log_folder_path, log_file_name)

        if not os.path.isfile(log_file_path):
            FileUtils.touch(log_folder_path, log_file_name)

        logging.basicConfig(filename=log_file_path, level=logging.INFO)
        log_formatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
        root_logger = logging.getLogger()
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(log_formatter)
        root_logger.addHandler(file_handler)

    def collect(self):
        result = self.__download_news()
        if result is not None:
            downloaded_news = self.__get_us_stock_news_list(result)
            self.__update_news(downloaded_news)

    def __download_news(self):
        logging.info("Downloading latest news from Sina Finance")
        return ts.get_latest_news(top=self.MAX_NEWS_COUNT, show_content=True)

    def __get_us_stock_news_list(self, result):
        list_classify = self.__get_list_classify(result)
        list_content = self.__get_list_content(result)
        list_title = self.__get_list_title(result)

        logging.info("Filtering US stock news")
        updated_news_list = []
        for index, title in enumerate(list_classify):
            if title == u"美股":
                news_dict = dict()
                news_dict["date"] = date.today().strftime('%Y-%m-%d').encode('utf8')
                news_dict["title"] = list_title[index].encode('utf8') if list_title[index] is not None else "".encode('utf8')
                news_dict["content"] = list_content[index].encode('utf8') if list_content[index] is not None else "".encode('utf8')
                updated_news_list.insert(len(updated_news_list), news_dict)

        return updated_news_list

    def __update_news(self, downloaded_news):
        current_news = self.__read_previous_news_list()
        current_news = self.__reduce_list(current_news)
        downloaded_news.reverse()
        length = len(downloaded_news)

        count = self.MAX_NEWS_COUNT
        if length < self.MAX_NEWS_COUNT:
            count = length

        i = 0
        news_added_count = 0
        while i < count:
            temp = downloaded_news[i]
            if self.__contains(current_news, temp) is False:
                if len(current_news) >= self.MAX_NEWS_COUNT:
                    current_news.pop()
                current_news.insert(0, temp)
                news_added_count += 1
            i += 1

        self.__write_news_list(current_news)
        logging.info("New added news count: %(count)d " % {"count": news_added_count})
        logging.info("Total news count: %(count)d " % {"count": len(current_news)})

    @staticmethod
    def __get_list_classify(result):
        return result["classify"].values.tolist()

    @staticmethod
    def __get_list_title(result):
        return result["title"].values.tolist()

    @staticmethod
    def __get_list_content(result):
        return result["content"].values.tolist()

    @staticmethod
    def __contains(list, obj):
        for item in list:
            if item["title"] == obj["title"]:
                return True
        return False

    def __reduce_list(self, news_list):
        while len(news_list) > self.MAX_NEWS_COUNT:
            news_list.pop()

        return news_list

    def __read_previous_news_list(self):
        logging.info("Reading news list file")
        return FileUtils.read_list_from_local_path_json(self.__get_data_file_path())

    def __write_news_list(self, news_list):
        logging.info("Writing news list file")
        FileUtils.write_list_to_local_path_json(news_list, self.__get_data_file_path())

    def __get_data_file_path(self):
        data_pool = self.config.get('LOCAL_DATA_POOL_PATH', 'value')
        data_file = self.config.get('LOCAL_NEWS_DATA_PATH', 'value')
        return os.path.join(data_pool, data_file)
