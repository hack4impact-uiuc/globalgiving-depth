import sys

import requests
import json
import multiprocessing as mp
from bs4 import BeautifulSoup
from bs4.element import Comment
import re
import os


def main():
    with open("json/" + sys.argv[1], "rw+") as input_file:
        input_file.seek(-1, os.SEEK_END)
        input_file.truncate()
        input_file.write("]}")
    input_file.close()
    return


if __name__ == "__main__":
    main()
