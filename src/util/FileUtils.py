# -*- coding: utf-8 -*-
import pickle
import os


class FileUtils:

    @staticmethod
    def touch(dir_path, file_name):
        file_path = os.path.join(dir_path, file_name)
        basedir = os.path.dirname(dir_path)
        if not os.path.exists(basedir):
            os.makedirs(basedir)

        with open(file_path, 'a'):
            os.utime(file_path, None)

    @staticmethod
    def write_list_to_local_path(list, path):
        f = open(path, 'wb')
        pickle.dump(list, f)
        f.close()

    @staticmethod
    def read_list_from_local_path(path):
        if os.path.isfile(path):
            f = open(path, 'rb')
            loaded_list = pickle.load(f)
            f.close()
        else:
            loaded_list = []
        return loaded_list
