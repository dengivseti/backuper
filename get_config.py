import os
from configparser import ConfigParser


def check_type(value):
    if "true" in value:
        return True
    elif "false" in value:
        return False
    elif "None" in value:
        return
    elif str(value).__contains__("|"):
        return value.split("|")
    elif str(value).__contains__("','"):
        try:
            return [s.replace("'", "") for s in value.split(",")]
        except:
            return []
    try:
        return int(value)
    except:
        return value


class GetConfig:
    @staticmethod
    def get_config(file_name):
        dict_settings = {}
        parser = ConfigParser()
        parent_dir = os.path.abspath(os.path.abspath(os.path.dirname(__file__)))
        path_file = os.path.join(parent_dir, "configs", file_name)
        parser.read(path_file)
        for k in parser:
            if "DEFAULT" in k:
                continue
            dict_settings[k.lower()] = {}
            for key in parser[k]:
                value = check_type(parser[k][key])
                dict_settings[k.lower()][key] = value
        return dict_settings
