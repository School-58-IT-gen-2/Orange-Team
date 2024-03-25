import json


class NetConfig:
    def __init__(self):
        with open("./config/net_config.json", "r", encoding="utf-8") as file:
            config = json.load(file)
        if not config:
            raise Exception("No token, the file is empty.")
        if config["token"]:
            self.__token = config["token"]
        else:
            raise Exception("Token is empty.")

    def get_token(self):
        return self.__token