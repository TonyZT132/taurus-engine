# -*- coding: utf-8 -*-
import os
import logging
import jieba
import jieba.analyse

from datetime import datetime
from configparser import ConfigParser

from src.util.FileUtils import FileUtils


class BenchmarkTokenizer:

    def __init__(self):
        self.__init_logger()
        self.config = ConfigParser()
        self.config.read("configuration/analytics/text/benchmark/benchmark.config")

    def __init_logger(self):
        log_folder_path = "log/analytics/text/benchmark"
        log_file_name = self.__class__.__name__ + " " + datetime.now().strftime('%c') + ".log"
        log_file_path = os.path.join(log_folder_path, log_file_name)

        if not os.path.isfile(log_file_path):
            FileUtils.touch(log_folder_path, log_file_name)

        logging.basicConfig(filename=log_file_path, level=logging.INFO)
        log_formatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
        root_logger = logging.getLogger()
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(log_formatter)
        root_logger.addHandler(file_handler)

    def get_segmented_news_item(self, item_news):
        logging.info("Segmenting new's article")
        segmented_news = dict()
        list_sentence = self.__cut_to_sentence(item_news["content"].decode("utf8"))
        sentence_list = []
        for sentence in list_sentence:
            tokenize_list = jieba.cut(sentence.strip(), cut_all=False)
            segment_list = []
            for seg in tokenize_list:
                segment_list.append(str(seg).strip())
            sentence_list.append(segment_list)
        segmented_news["segment"] = sentence_list
        return segmented_news

    def __cut_to_sentence(self, text):
        result = []
        line = []

        for i in text:
            if self.__find_token(i):
                line.append(i)
                result.append(''.join(line))
                line = []
            else:
                line.append(i)
        return result

    @staticmethod
    def __find_token(char):
        return char in "。！？"
