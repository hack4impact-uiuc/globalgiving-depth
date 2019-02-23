import sys
import json
import re

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

def main():
    with open(sys.argv[1], "r") as input_file: # ../visible-text/scraping_data.json
        input_data = json.load(input_file)
    data = {}
    data["projects"] = []

    for p in input_data["projects"]:
        project = {}
        project["url"] = p["url"]
        if len(p["text"]) != 0:
            project["text"] = p["text"]
            words = get_words(project["text"])
        data["projects"].append(project)

    tfid_values = get_tfid_values(x["text"] for x in data["projects"]) # need to map to themes list
    # take top "n" most important words, 

    with open(sys.argv[2], "w") as output_file: # scores.json
        json.dump(data, output_file)

def get_words(text):
    text = text.lower()
    wordlist = text.split()
    clean_list = []
    for word in wordlist:
        # only get words (no digits)
        if not word.isdigit() and not re.match(r'[^\w]', word):
            clean_list.append(word)

    return " ".join(clean_list)

def get_tfid_values(words):
    vectorizer = TfidfVectorizer(ngram_range=(2,2)) # bigrams
    X = vectorizer.fit_transform(list(words))
    arr = X.toarray()
    return arr
    # print(np.argmax(arr[1]))
    # print(arr[1][627])
    # print(vectorizer.get_feature_names()[627])

if __name__ == "__main__":
    main()