import sys
import json
import re
import numpy as np

from sklearn.feature_extraction.text import (
    TfidfVectorizer,
    CountVectorizer,
    TfidfTransformer,
)
from sklearn.naive_bayes import MultinomialNB, GaussianNB, BernoulliNB
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.linear_model import SGDClassifier


def get_words(text):
    text = text.lower()
    wordlist = text.split()
    clean_list = []
    for word in wordlist:
        # only get words (no digits)
        if not word.isdigit() and not re.match(r"[^\w]", word):
            clean_list.append(word)

    return " ".join(clean_list)


def train():
    with open(
        sys.argv[1], "r"
    ) as input_file:  # training_data.json or ngos_text_113.json
        input_data = json.load(input_file)
    print(len(input_data["projects"]))

    next_index = 0
    themes = {}  # themes to indices
    targets = []  # indices of themes, parallel to text array
    text = []
    urls = []

    for project in input_data["projects"]:
        if len(project["text"]) != 0:
            words = get_words(project["text"])
            for theme in project["themes"]:
                if theme["id"] not in themes:
                    themes[theme["id"]] = next_index
                    next_index += 1
                targets.append(themes[theme["id"]])
                text.append(words)
                urls.append(project["url"])

    data = {}
    data["themes"] = themes
    data["targets"] = targets
    data["urls"] = urls
    data["text"] = text
    with open(sys.argv[2], "w") as output_file:  # predictions.json
        json.dump(data, output_file)


def classify():
    with open("predictions.json", "r") as input_file:
        training_data = json.load(input_file)
    with open(sys.argv[3], "r") as input_file:  # ../visible-text/scraping_data.json
        testing_data = json.load(input_file)
    urls = []
    text = []
    for project in testing_data["projects"]:
        if len(project["text"]) != 0:
            text.append(get_words(project["text"]))
            urls.append(project["url"])

    text_clf = Pipeline(
        [
            (
                "vect",
                CountVectorizer(ngram_range=(1, 1), stop_words="english", max_df=0.6),
            ),
            ("tfidf", TfidfTransformer()),
            ("clf", SGDClassifier(max_iter=50, random_state=42)),
        ]
    )
    test_words = text
    text_clf.fit(training_data["text"], training_data["targets"])
    predicted = text_clf.predict(test_words)

    return predicted


if __name__ == "__main__":
    train()
    predictions = classify()
    testing_targets = [4, 2, -1, 5, 2]
    print(np.mean(predictions == testing_targets))
    print(predictions, testing_targets)
