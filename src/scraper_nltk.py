import sys

from bs4 import BeautifulSoup
from bs4.element import Comment
import urllib.request
import requests
import json
import operator
from collections import Counter
import re
import string
from utils.dataset_db.db import get_collection, upload_many

# import NLTK
import nltk
from nltk.stem.snowball import SnowballStemmer


def main():
    # cursor which goes through scraped data on db
    for project in get_collection("organizations-text").find():
        nltk_project = {}
        nltk_project["country"] = project["country"]
        nltk_project["name"] = project["name"]
        nltk_project["themes"] = []
        theme = {}
        theme["id"] = project["themes"][0]["id"]
        theme["name"] = project["themes"][0]["name"]
        nltk_project["themes"].append(theme)
        nltk_project["url"] = project["url"]
        text = project["text"]
        nltk_project["text"] = text
        words = get_words(text)
        nltk_project["most_freq_words"] = get_top_100_words(
            words)

        # send org with frequencies to db
        upload_many([nltk_project], get_collection("organizations-frequency"))
    return


def get_words(text):
    text = text.lower()
    wordlist = text.split()
    clean_list = []
    for word in wordlist:
        # only get words (no digits or punctuation)
        if not word.isdigit() and not re.match(r'[^\w]', word):
            # remove punctuation from words
            word = re.sub('['+string.punctuation+']', '', word)
            if not re.match(r'[0-9]+', word):
                word = re.sub(r'[0-9]+', '', word)
                clean_list.append(word)

    words = remove_stop_words(clean_list)
    words = stem_words(words)
    return words


def remove_stop_words(words):
    new_wordlist = []
    sw = nltk.corpus.stopwords.words("english")
    for word in words:
        if word not in sw:
            new_wordlist.append(word)
    return new_wordlist


def stem_words(words):
    stemmer = SnowballStemmer("english")
    new_wordlist = []
    for word in words:
        new_wordlist.append(stemmer.stem(word))
    return new_wordlist


def get_top_100_words(words):
    word_count = get_word_count(words)

    count = Counter(word_count)

    top_100 = count.most_common(100)
    return top_100


def get_word_count(words):
    word_count = {}

    for word in words:
        if word in word_count:
            word_count[word] += 1
        else:
            word_count[word] = 1
    return word_count


if __name__ == "__main__":
    main()
