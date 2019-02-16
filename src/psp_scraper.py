import sys

import requests
import json
from bs4 import BeautifulSoup
from bs4.element import Comment

## Be able to automate getting links
## Add in multiprocessing / some other efficiency improvement

def main():
    input_file = open(sys.argv[1], "r")
    url_list = input_file.read().splitlines()

    scraping_data = []
    for url in url_list:
        html_doc = requests.get(url).text
        soup = BeautifulSoup(html_doc, "html.parser")
        text = soup.findAll(text=True)
        text = filter_text(text)
        scraping_data.append(text)

    with open("scraping_data.txt", "w") as output_file:
        json.dump(scraping_data, output_file)

    input_file.close()
    output_file.close()
    return


def filter_text(texts):
    filtered_text = []
    for text in texts:
        if not isinstance(text, Comment) and text.parent.name not in [
            "style",
            "script",
            "head",
            "meta",
        ]:
            stripped_text = text.strip()
            if len(stripped_text) != 0:
                filtered_text.append(stripped_text)
    return filtered_text


if __name__ == "__main__":
    main()
