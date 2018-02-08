# -*- coding: utf-8 -*-
from gensim.models import word2vec


class VectorGenerator:
    def __init__(self):
        pass

    @staticmethod
    def generate_training_model():
        sentences = word2vec.Text8Corpus("corpus.csv")  # 加载语料
        model = word2vec.Word2Vec(sentences, size=400)  # 训练skip-gram模型

        # 保存模型，以便重用
        model.save("corpus.model")

        # 对应的加载方式
        # model = word2vec.Word2Vec.load("corpus.model")

        # 以一种C语言可以解析的形式存储词向量
        model.save_word2vec_format("corpus.model.bin", binary=True)

        # 对应的加载方式
        # model = word2vec.Word2Vec.load_word2vec_format("corpus.model.bin", binary=True)
