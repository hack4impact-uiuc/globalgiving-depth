import sys

import requests
import json
import multiprocessing as mp
from bs4 import BeautifulSoup
from bs4.element import Comment
import re


def main():
    with open("json/" + sys.argv[1], "r") as input_file:
        input_data = json.load(input_file)

    scraping_data = {}
    scraping_data["projects"] = []
    with open("json/" + sys.argv[2], "a") as output_file:
        output_file.write('{"projects": [')
        for project in input_data["projects"]:
            if len(project["url"]) != 0:
                new_project = {}
                new_project["country"] = project["country"]
                new_project["name"] = project["name"]
                if len(project["themes"]) < 1:
                    continue
                new_project["themes"] = []
                theme = {}
                theme["id"] = project["themes"][0]["id"]
                theme["name"] = project["themes"][0]["name"]
                new_project["themes"].append(theme)
                new_project["url"] = project["url"]
                new_project["text"] = text_scraper(new_project["url"])
                json.dump(new_project, output_file)
                output_file.write(",")
                # scraping_data["projects"].append(new_project)
        output_file.write("]}")
    # with open("json/" + sys.argv[2], "w") as output_file:
    #     json.dump(scraping_data, output_file)

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

    body = soup.find('body')
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
