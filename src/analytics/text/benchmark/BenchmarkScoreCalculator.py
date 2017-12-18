# -*- coding: utf-8 -*-
from collections import defaultdict
import os
import logging
import traceback

from configparser import ConfigParser
from datetime import datetime

from src.analytics.text.benchmark.BenchmarkTokenizer import BenchmarkTokenizer
from src.util.FileUtils import FileUtils

from src.exception.ResourceNotFoundException import ResourceNotFoundException


class BenchmarkScoreCalculator:

    def __init__(self, org, cat):
        self.__init_logger()
        self.config = ConfigParser()
        self.config.read("configuration/analytics/text/benchmark/benchmark.config")

        self.organization = org
        self.category = cat

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

    def calculate_scores(self):
        news_list = []
        news_list_with_score = []

        if self.organization == "sina" and self.category == "finance":
            news_list = FileUtils.read_list_from_local_path(self.__get_data_file_path())
        else:
            raise ResourceNotFoundException("Could not find news resources for: "
                                            + self.organization + " " + self.category)

        for item_new in news_list:
            tokenizer = BenchmarkTokenizer()
            segmented_new = tokenizer.get_segmented_news_item(item_new)

            final_score = 0
            count = 0
            for sentence in segmented_new["segment"]:
                cate = self.__classify_words(sentence)
                score = self.__calculate_score_for_each_sentence(cate[0], cate[1], cate[2], sentence)
                final_score += float(score)
                count += 1

                print(sentence)
                print(final_score)

            if count == 0:
                logging.warning("Invalid segmentation, reset final score to zero ")
                final_score = float(0)
                count = 1

            item_new["sentiment_score"] = float(final_score / float(count))
            news_list_with_score.insert(0, item_new)

        FileUtils.write_list_to_local_path(news_list_with_score, self.__get_result_data_path(
            self.__get_result_data_folder_path(),
            self.organization + "_" + self.category + "-" + datetime.now().strftime('%c')))

    def __classify_words(self, word_list):
        # 情感词
        logging.info("Loading sentiment dictionary")
        list_sentiment_word = self.__load_dict(self.__get_training_data_file_path_sentiment_word(), False)

        dict_sentiment_word = defaultdict()
        for s in list_sentiment_word:
            pair = s.split(' ')
            if len(pair) > 1:
                dict_sentiment_word[pair[0]] = pair[1]

        # 否定词
        logging.info("Loading dropped word dictionary")
        list_dropped_word = self.__load_dict(self.__get_training_data_file_path_degree_word(), True)

        # 程度副词
        logging.info("Loading degree word dictionary")
        list_degree_word = self.__load_dict(self.__get_training_data_file_path_dropped_word(), True)
        dict_degree_word = defaultdict()
        for d in list_degree_word:
            pair = d.split(',')
            if len(pair) > 1:
                dict_degree_word[pair[0]] = pair[1]

        sentiment_word = defaultdict()
        dropped_word = defaultdict()
        degree_word = defaultdict()

        for i in range(0, len(word_list)):
            word = word_list[i]
            if word in dict_sentiment_word.keys() and word not in list_dropped_word and word not in dict_degree_word.keys():
                sentiment_word[i] = dict_sentiment_word[word]
            elif word in list_dropped_word and word not in dict_degree_word.keys():
                dropped_word[i] = -1
            elif word in dict_degree_word.keys():
                degree_word[i] = dict_degree_word[word]
        return sentiment_word, dropped_word, degree_word

    @staticmethod
    def __calculate_score_for_each_sentence(sentiment_word, dropped_word, degree_word, sentence):
        weight = 1
        score = 0

        logging.info("Calculating sentiment score")
        try:
            # 存所有情感词的位置的列表
            sentiment_word_location = list(sentiment_word.keys())
            dropped_word_location = list(dropped_word.keys())
            degree_word_location = list(degree_word.keys())
            sentiment_word_location_index = -1

            # 遍历句中所有单词segResult，i为单词绝对位置
            for i in range(0, len(sentence)):
                # 如果该词为情感词
                if i in sentiment_word_location:
                    # loc为情感词位置列表的序号
                    sentiment_word_location_index += 1
                    # 直接添加该情感词分数
                    score += weight * float(sentiment_word[i])
                    # print "score = %f" % score
                    if sentiment_word_location_index < len(sentiment_word_location) - 1:
                        # 判断该情感词与下一情感词之间是否有否定词或程度副词,j为绝对位置
                        for j in range(sentiment_word_location[sentiment_word_location_index],
                                   sentiment_word_location[sentiment_word_location_index + 1]):
                            # 如果有否定词
                            if j in dropped_word_location:
                                weight *= -1
                            # 如果有程度副词
                            elif j in degree_word_location:
                                weight *= float(degree_word[j])

                # i定位至下一个情感词
                if sentiment_word_location_index < len(sentiment_word_location) - 1:
                    i = sentiment_word_location[sentiment_word_location_index + 1]
            return score
        except Exception as e:
            logging.error(str(e))
            logging.error(traceback.print_exc())

    @staticmethod
    def __load_dict(file_path, gbk_encoding):
        result = []
        encoding = "utf8"
        if gbk_encoding is True:
            encoding = "gbk"

        with open(file_path, encoding=encoding) as fp:
            for line in fp:
                result.append(str(line.strip()))

        return result

    def __get_data_file_path(self):
        data_pool = self.config.get('LOCAL_DATA_POOL_PATH', 'value')
        data_file = self.config.get('LOCAL_SINA_FINANCE_NEWS_DATA_PATH', 'value')
        return os.path.join(data_pool, data_file)

    def __get_training_data_file_path_sentiment_word(self):
        data_pool = self.config.get('LOCAL_DATA_POOL_PATH', 'value')
        data_file = self.config.get('TRAINING_DATA_SENTIMENT_WORD', 'value')
        return os.path.join(data_pool, data_file)

    def __get_training_data_file_path_degree_word(self):
        data_pool = self.config.get('LOCAL_DATA_POOL_PATH', 'value')
        data_file = self.config.get('TRAINING_DATA_DEGREE_WORD', 'value')
        return os.path.join(data_pool, data_file)

    def __get_training_data_file_path_dropped_word(self):
        data_pool = self.config.get('LOCAL_DATA_POOL_PATH', 'value')
        data_file = self.config.get('TRAINING_DATA_DROPPED_WORD', 'value')
        return os.path.join(data_pool, data_file)

    def __get_result_data_folder_path(self):
        data_pool = self.config.get('LOCAL_DATA_POOL_PATH', 'value')
        data_file = self.config.get('RESULT_DATA_PATH', 'value')
        return os.path.join(data_pool, data_file)

    @staticmethod
    def __get_result_data_path(folder, filename):
        return os.path.join(folder, filename)
