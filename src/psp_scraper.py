import sys
import re
import multiprocessing as mp
import json
import requests
from bs4 import BeautifulSoup
from bs4.element import Comment


def main():
    with open(sys.argv[1], "r") as input_file:
        input_data = json.load(input_file)

    url_list = []
    for project in input_data["projects"]:
        if len(project["url"]) != 0:
            url_list.append(project["url"])

    scraping_data = {}
    scraping_data["projects"] = []
    for url in url_list:
        project = {}
        project["url"] = url
        project["text"] = text_scraper(url)
        scraping_data["projects"].append(project)

    with open("scraping_data.json", "w") as output_file:
        # parsed = json.load(scraping_data)
        json.dump(scraping_data, output_file)
    return


def text_scraper(url):
    """
    text_scraper can be used as a blackbox with a given url.
    It will RETURN a string with text parsed from:
    1) The original site
    2) Associated links
    """
    assert type(url) == str
    try:
        request = requests.get(url)
    except requests.exceptions.ConnectionError as e:
        print(e)
        return ""

    html_doc = request.text
    soup = BeautifulSoup(html_doc, "html.parser")
    other_links = get_other_links(soup, url)
    # Get all text from url and subpages
    text = soup.findAll(text=True)
    text = " ".join(filter_text(text))
    for link in other_links:
        child_html_doc = requests.get(link).text
        child_soup = BeautifulSoup(child_html_doc, "html.parser")
        child_text = child_soup.findAll(text=True)
        child_text = " ".join(filter_text(child_text))
        text += child_text
    return text


def get_other_links(soup, url):
    links = set()

    tags = soup.findAll(href=True)
    regex = re.compile("^" + url)
    for tag in tags:
        sub_url = tag.get("href")
        if re.match(regex, sub_url):
            if sub_url not in links:
                links.add(sub_url)
        else:
            if tag.get("target") == "_self" or tag.get("data-target") == "#":
                if sub_url.startswith("/"):
                    sub_url = sub_url[1:]
                    if url.endswith("/"):
                        url = url[:-1]
                    link = url + "/" + sub_url
                    links.add(link)
                else:
                    if url.endswith("/"):
                        url = url[:-1]
                    link = url + "/" + sub_url
                    links.add(link)

    return links


def filter_text(texts):
    filtered_text = []
    for text in texts:
        if not isinstance(text, Comment) and text.parent.name not in {
            "style",
            "script",
            "head",
            "meta",
        }:
            stripped_text = text.strip()
            if stripped_text:
                filtered_text.append(stripped_text)
    return filtered_text


if __name__ == "__main__":
    main()
