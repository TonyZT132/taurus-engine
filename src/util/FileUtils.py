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