import sys

import requests
import json
import multiprocessing as mp
import pymongo
from bs4 import BeautifulSoup
from bs4.element import Comment
import re
from utils.dataset_db.db import get_collection, upload_many


def main():
    # cursor which goes through raw data on db
    for project in get_collection().find():
        if not project["url"] or project["url"].strip().startswith("mailto"):
            continue
        new_project = {}
        new_project["country"] = project["country"]
        new_project["name"] = project["name"]
        if not project["themes"]:
            continue
        new_project["themes"] = []
        theme = {}
        theme["id"] = project["themes"][0]["id"]
        theme["name"] = project["themes"][0]["name"]
        new_project["themes"].append(theme)
        new_project["url"] = project["url"]
        new_project["text"] = text_scraper(new_project["url"])

        # send org with text to db
        upload_many([new_project], get_collection("organization-text"))
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
    except requests.exceptions.InvalidSchema as e:
        print(e)
        return ""
    except requests.exceptions.TooManyRedirects as e:
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
        text += " " + child_text

    text = text.encode("ascii", "ignore").decode("utf-8")
    return text


def get_other_links(soup, url):
    links = set()

    body = soup.find("body")
    if not body.findChildren():
        return ""
    body_contents = body.findChildren()[0]
    tags = body_contents.findAll(href=True)
    regex = re.compile("^" + url)
    for tag in tags:
        sub_url = tag.get("href")
        if sub_url.startswith("mailto"):
            continue
        if re.match(regex, sub_url):
            if sub_url not in links:
                links.add(sub_url)
        else:
            if tag.get("target") == "_self":
                if sub_url.startswith("/"):
                    sub_url = sub_url[1:]
                    if url.endswith("/"):
                        url = url[:-1]
                    link = url + "/" + sub_url
                    if link not in links:
                        links.add(link)
                else:
                    if url.endswith("/"):
                        url = url[:-1]
                    link = url + "/" + sub_url
                    if link not in links:
                        links.add(link)
            elif tag.get("data-target") == "#":
                if sub_url.startswith("/"):
                    sub_url = sub_url[1:]
                    if url.endswith("/"):
                        url = url[:-1]
                    link = url + "/" + sub_url
                    if link not in links:
                        links.add(link)
                else:
                    if url.endswith("/"):
                        url = url[:-1]
                    link = url + "/" + sub_url
                    if link not in links:
                        links.add(link)
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
