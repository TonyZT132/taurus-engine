# -*- coding: utf-8 -*-
import jieba
import re
import codecs
import os


class TrainingDataTokenizer:
    def __init__(self):
        pass

    @staticmethod
    def __read_lines(filename):
        # read txt or csv file
        fp = open(filename, 'r')
        lines = []
        for line in fp.readlines():
            line = line.strip()
            line = line.decode("utf-8")
            lines.append(line)
        fp.close()
        return lines

    @staticmethod
    def __parse_sentence(sentence):
        # use Jieba to parse sentences
        seg_list = jieba.cut(sentence)
        output = ' '.join(list(seg_list))  # use space to join them
        return output

    def generate_csv_data_file(self):
        # only content is valid
        pattern = "<content>(.*?)</content>"
        csv_file = codecs.open("corpus.csv", 'w', 'utf-8')
        file_directory = os.listdir("./corpus/")
        for file in file_directory:
            with open("./corpus/%s" % file, "r") as txtfile:
                for line in txtfile:
                    m = re.match(pattern, line)
                    if m:
                        sentence_segment = self.__parse_sentence(m.group(1))
                        csv_file.write("%s" % sentence_segment)
