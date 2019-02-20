import sys

from bs4 import BeautifulSoup
from bs4.element import Comment
import urllib.request
import requests
import json
import operator
from collections import Counter

# import NLTK
import nltk


def main():
    with open(sys.argv[1], "r") as input_file:
        input_data = json.load(input_file)
    nltk_data = {}
    nltk_data["projects"] = []

    for project in input_data["projects"]:
        nltk_project = {}
        nltk_project["url"] = project["url"]
        if len(project["text"]) != 0:
            text = project["text"]
            nltk_project["text"] = text
            nltk_project["most_freq_words"] = get_top_100_words(text)
        nltk_data["projects"].append(nltk_project)

    with open(sys.argv[2], "w") as output_file:
        json.dump(nltk_data, output_file)


def get_top_100_words(text):
    word_count = get_word_count(text)

    count = Counter(word_count)

    top_100 = count.most_common(100)
    return top_100


def get_word_count(text):
    wordlist = remove_stop_words(text)
    word_count = {}

    for word in wordlist:
        if word in word_count:
            word_count[word] += 1
        else:
            word_count[word] = 1
    return word_count


def remove_stop_words(text):
    wordlist = get_words(text)
    new_wordlist = []
    sw = nltk.corpus.stopwords.words("english")
    for word in wordlist:
        if word not in sw:
            new_wordlist.append(word)
    return new_wordlist


def get_words(text):
    wordlist = text.split()

    return wordlist


if __name__ == "__main__":
    main()
