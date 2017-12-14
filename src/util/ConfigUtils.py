from configparser import ConfigParser


class ConfigUtils:

    @staticmethod
    def generate_config(path):
        return ConfigParser().read(path)
