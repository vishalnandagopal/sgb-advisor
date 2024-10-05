import configparser

config = configparser.ConfigParser()
config_filename: str = "config.ini"

default_config: dict[str, str] = {
    "RiskFreeRate": "3",
}


def read_config():
    return config.read(config_filename)


def write_config():
    config["DEFAULT"] = default_config
    with open(config_filename, "w") as f:
        config.write(f)
