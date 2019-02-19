import sys

import requests
import json
import multiprocessing as mp
from bs4 import BeautifulSoup
from bs4.element import Comment
import re

def main():
    with open(sys.argv[1], "r") as input_file:
        input_data = json.load(input_file)

    url_list = []
    for project in input_data['projects']:
         if len(project["url"]) != 0:
             url_list.append(project["url"])

    scraping_data = []
    for url in url_list:
        scraping_data.append(text_scraper(url))
    scraping_data = ''.join(scraping_data)

    with open("scraping_data.txt", "w") as output_file:
        json.dump(scraping_data, output_file)

    input_file.close()
    output_file.close()
    return

"""
text_scraper can be used as a blackbox with a given url.
It will RETURN a string with text parsed from:
1) The original site
2) Associated links
"""
def text_scraper(url):
    assert(type(url) == str)
    html_doc = requests.get(url).text
    soup = BeautifulSoup(html_doc, "html.parser")
    other_links = get_other_links(soup, url)

    # Get all text from url and subpages
    text = soup.findAll(text=True)
    text = ''.join(filter_text(text))
    for link in other_links:
        child_html_doc = requests.get(link).text
        child_soup = BeautifulSoup(child_html_doc, "html.parser")
        child_text = child_soup.findAll(text=True)
        child_text = ''.join(filter_text(child_text))
        text += child_text
    return text

def get_other_links(soup, url):
    links = set()

    tags = soup.findAll("a", attrs={"target": "_self"})
    for tag in tags:
        link = url + "/" + tag.get("href")
        if link not in links:
            links.add(link)

    tags = soup.findAll("a", attrs={"href": re.compile(url)})
    for tag in tags:
        link = tag.get("href")
        if link not in links:
            links.add(tag.get("href"))

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
