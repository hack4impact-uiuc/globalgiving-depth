import re
import json
import requests
from bs4 import BeautifulSoup
from bs4.element import Comment


class HTMLParser:
    def scrape_all_from_file(self, infile, outfile):
        """
        This is the only function of the class you should really use.
        This function takes a file containing JSON records of NGO's, which must
        include a 'url' field, pulls all text from each URL & recursively from
        URLs in the same domain, and generates new records with the text in an
        additional text field. It saves these new records in a new JSON file.
        Parameters:
            infile - string: filename of file containing JSON records of NGOs.
                this JSON file must have a "projects" key which contains a list
                of NGO records, which each must have a "url" field.
            outfile - string: filename of a new file to write augmented NGO
                records with additioinal 'text' field.
        Returns:
            None
        """
        with open(infile, "r") as input_file:
            input_data = json.load(input_file)

        scraping_data = {}
        scraping_data["projects"] = []
        for project in input_data["projects"]:
            url = project.get("url")
            if url:
                project["text"] = self.scrape_url(url)
                scraping_data["projects"].append(project)

        with open(outfile, "w") as output_file:
            json.dump(scraping_data, output_file)

    def scrape_url(self, url: str) -> str:
        """
        scrape_url can be used as a blackbox with a given url.
        It will RETURN a string with text parsed from:
        1) The original site
        2) Associated links
        Parameters:
            url - string: url of page to scrape
        Returns:
            text - string: text of original site specified by 'url' along with
                text from associated links on the page.
        """
        try:
            request = requests.get(url)
        except requests.exceptions.ConnectionError as e:
            print(e)
            return ""

        html_doc = request.text
        soup = BeautifulSoup(html_doc, "html.parser")
        other_links = self.get_other_links(soup, url)
        # Get all text from url and subpages
        text = soup.findAll(text=True)
        text = " ".join(self.filter_text(text))
        for link in other_links:
            child_html_doc = requests.get(link).text
            child_soup = BeautifulSoup(child_html_doc, "html.parser")
            child_text = child_soup.findAll(text=True)
            child_text = " ".join(self.filter_text(child_text))
            text += " "
            text += child_text
        return text

    def get_other_links(self, soup, url):
        """
        This function gets associated links from a webpage.
        The links should be within the same domain, and not stylesheets.
        This function is known to have some bugs.
        Parameters:
            soup - BeautifulSoup object: should be an html parser
            url - string: url of page to get associated links from.
        Returns:
            links - set: set of intra-domain urls found on 'url' page.
        """
        links = set()

        tags = soup.findAll(href=True)
        regex = re.compile("^" + url)
        for tag in tags:
            bad_tags = ["head", "video", "script"]
            if tag.parent.name in bad_tags:
                continue
            sub_url = tag.get("href")
            if ".css" in sub_url or ".pdf" in sub_url:
                continue

            if re.match(regex, sub_url):
                links.add(sub_url)
            elif tag.get("data-target") == "#" or sub_url.startswith("./"):
                if sub_url.startswith("./"):
                    sub_url = sub_url[2:]
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

        if url in links:  # safety check
            links.remove(url)
        if url + "/" in links:
            links.remove(url + "/")
        return links

    def filter_text(self, texts):
        """
        This function filters out tags/scripts from HTML.
        Parameters:
            texts - list of strings: list of strings from some URL that should
                be filtered.
        Returns:
            filtered_text - string: concatenated body of text without tags/
                scripts.
        """
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
