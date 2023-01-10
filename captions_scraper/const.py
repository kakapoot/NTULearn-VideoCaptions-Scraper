from os import getenv
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = str(Path(__file__).parent.parent.absolute()) + "\\"

OUTPUT_DIR = ROOT_DIR + "outputs\\"
# input file containing NTUlearn links with video player
INPUT_FILE_PATH = ROOT_DIR + "input.txt"


def load_env(key):
    load_dotenv()
    value = getenv(key)
    if value is not None:
        return value


def get_username():
    return load_env("NTU_USERNAME")


def get_password():
    return load_env("NTU_PASSWORD")