import tushare as ts
import os
import json
import logging
from datetime import date

from src.util.ConfigUtils import ConfigUtils
from src.util.LogUtils import LogUtils


class SinaFinanceNewsCollector:

    def __init__(self):
        self.config = ConfigUtils.generate_config("path")
        self.MAX_NEWS_COUNT = 1000
        LogUtils.generate_logger("logger_path")

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
                    current_news.insert(0, downloaded_news[i])
                news_added_count += 1
            i += 1

        self.__write_news_list()
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

    def __get_data_file_name(self):
        data_pool = self.config.get('data_pool','data_pool')
        data_file = self.config.get('tushare_news','data_file')
        return os.path.join(data_pool, data_file)

    def __read_previous_news_list(self):
        if os.path.isfile(self.__get_data_file_name()):
            logging.info("Reading news list file")
            f = open(self.__get_data_file_name(), 'rb')
            news_list = json.load(f)
            f.close()
        else:
            news_list = []

        return news_list

    def __write_news_list(self, news_list):
        logging.info("Writing news list file")
        f = open(self.__get_data_file_name(), 'wb')
        json.dump(news_list, f)
        f.close()
