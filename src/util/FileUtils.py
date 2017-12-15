import json
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
    def write_list_to_local_path_json(list, path):
        f = open(path, 'wb')
        json.dump(list, f)
        f.close()

    @staticmethod
    def read_lost_from_local_path_json(path):
        if os.path.isfile(path):
            f = open(path, 'rb')
            list = json.load(f)
            f.close()
        else:
            list = []

        return list
