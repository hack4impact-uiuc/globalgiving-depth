import sys

import requests
import json
from bs4 import BeautifulSoup
from bs4.element import Comment
import re

## Be able to automate getting links
## Add in multiprocessing / some other efficiency improvement

def main():
    input_file = open(sys.argv[1], "r")
    url_list = input_file.read().splitlines()

    scraping_data = []
    for url in url_list:
        html_doc = requests.get(url).text
        soup = BeautifulSoup(html_doc, "html.parser")
        other_links = get_other_links(soup, url)

        # Get all text from url and subpages
        text = soup.findAll(text=True)
        text = filter_text(text)
        for link in other_links:
            child_html_doc = requests.get(link).text
            child_soup = BeautifulSoup(child_html_doc, "html.parser")
            child_text = child_soup.findAll(text=True)
            child_text = filter_text(child_text)
            text += child_text

        scraping_data.append(text)

    with open("scraping_data.txt", "w") as output_file:
        json.dump(scraping_data, output_file)

    input_file.close()
    output_file.close()
    return

def get_other_links(soup, url):
    links = []
    
    tags = soup.findAll("a", attrs={"target": "_self"})
    for tag in tags:
        link = url + "/" + tag.get("href")
        if link not in links:
            links.append(link)

    tags = soup.findAll("a", attrs={"href": re.compile(url)})
    for tag in tags:
        link = tag.get("href")
        if link not in links:
            links.append(tag.get("href"))

    return links
    
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
