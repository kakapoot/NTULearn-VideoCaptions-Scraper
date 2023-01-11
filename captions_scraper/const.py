from os import getenv
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = str(Path(__file__).parent.parent.absolute()) + "\\"
OUTPUT_DIR = ROOT_DIR + "outputs\\"
INPUT_FILE_PATH = ROOT_DIR + "input.txt"

NTULEARN_URL = "https://ntulearn.ntu.edu.sg/"


def load_env(key):
    load_dotenv()
    value = getenv(key)
    if value is not None:
        return value


def get_username():
    username = load_env("NTU_USERNAME")
    if not username:
        print("NTULearn username missing from .env file")
    return username


def get_password():
    password = load_env("NTU_PASSWORD")
    if not password:
        print("NTULearn password missing from .env file")
    return password
