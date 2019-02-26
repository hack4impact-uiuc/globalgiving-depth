import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


def populate_dict(input_data):
    data = {}
    data["projects"] = []

    for p in input_data["projects"]:
        project = {}
        project["url"] = p["url"]
        if len(p["text"]) != 0:
            project["words"] = get_words(p["text"])
        if "themes" in p:
            project["themes"] = p["themes"]
        else:
            project["themes"] = []
        data["projects"].append(project)

    return data


def get_words(text):
    text = text.lower()
    wordlist = text.split()
    clean_list = []
    for word in wordlist:
        # only get words (no digits)
        if not word.isdigit() and not re.match(r"[^\w]", word):
            clean_list.append(word)

    return " ".join(clean_list)


def get_tfidf_values(words):
    """
    Given a list of strings from separate documents,
    this returns a tuple of a 2D list of tf-idf values and their corresponding features
    """
    vectorizer = TfidfVectorizer(ngram_range=(1, 3))  # unigrams and bigrams
    X = vectorizer.fit_transform(list(words))
    arr = X.toarray()
    return arr, vectorizer.get_feature_names()
    # print(np.argmax(arr[1]))
    # print(arr[1][627])
    # print(vectorizer.get_feature_names()[627])
