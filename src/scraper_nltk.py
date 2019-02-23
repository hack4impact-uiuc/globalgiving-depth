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

# import NLTK
import nltk
from nltk.stem.snowball import SnowballStemmer


def main():
    with open("json/" + sys.argv[1], "r") as input_file:
        input_data = json.load(input_file)
    nltk_data = {}
    nltk_data["projects"] = []

    for project in input_data["projects"]:
        nltk_project = {}
        nltk_project["url"] = project["url"]
        if len(project["text"]) != 0:
            text = project["text"]
            nltk_project["text"] = text
            words = get_words(text)
            nltk_project["most_freq_words"] = get_top_100_words(
                words)
        nltk_data["projects"].append(nltk_project)

    with open("json/" + sys.argv[2], "w") as output_file:
        json.dump(nltk_data, output_file)


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
