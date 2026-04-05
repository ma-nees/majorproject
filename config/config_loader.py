import yaml
import os


class ConfigLoader:

    def __init__(self):

        with open("config/config.yaml", "r") as file:
            self.config = yaml.safe_load(file)

    def get(self, key):

        return self.config.get(key)


config = ConfigLoader()