import sys
import json
import re
import numpy as np

from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.pipeline import Pipeline
from sklearn.multiclass import OneVsRestClassifier
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import train_test_split
from sklearn import metrics

sys.path.append("..")

from utils.dataset_db import dynamo_db


def get_words(text):
    text = text.lower()
    wordlist = text.split()
    clean_list = []
    for word in wordlist:
        # only get words (no digits)
        if not word.isdigit() and not re.match(r"[^\w]", word):
            clean_list.append(word)

    return " ".join(clean_list)


def get_targets(data, data_with_targets, themes):
    targets = []
    i = 0
    for project in data:
        m_themes = project["themes"]
        for matching_project in data_with_targets:
            if matching_project["url"] == project["url"]:
                m_themes = matching_project["themes"]
                break
        targets.append([])
        for theme in m_themes:
            if theme["id"] not in themes:
                targets[i].append(-1)
            targets[i].append(themes[theme["id"]])
        i += 1

    return targets


def get_themes_map():
    with open(sys.argv[1], "r") as input_file:  # trained.json
        training_data = json.load(input_file)

    return training_data["themes"]


"""
Generates a JSON in the format we want of the given training data
"""


def set_up_training_data(dataset, matching_dataset):
    next_index = 0
    themes = {}  # themes to indices
    targets = []  # indices of themes, parallel to text array
    text = []
    urls = []

    i = 0
    for project in dataset:
        m_themes = project["themes"]
        for matching_project in matching_dataset:
            if matching_project["url"] == project["url"]:
                m_themes = matching_project["themes"]
                break
        if len(project["text"]) != 0:
            words = get_words(project["text"])
            urls.append(project["url"])
            text.append(words)
            targets.append([])
            for theme in m_themes:
                if theme["id"] not in themes:
                    themes[theme["id"]] = next_index
                    next_index += 1
                targets[i].append(themes[theme["id"]])
        i += 1

    data = {}
    data["themes"] = themes
    data["targets"] = targets
    data["urls"] = urls
    data["text"] = text
    with open(sys.argv[1], "w") as output_file:  # trained.json
        json.dump(data, output_file)

    return themes


"""
Vectorizes both training and testing data, then classifies.
Returns tuple of a 2D numpy array of probabilities of each document being each category,
and a 2D numpy array of 0s and 1s, where 1s are the predicted categories.
"""


def classify(testing_data, testing_targets):
    with open(sys.argv[1], "r") as input_file:  # trained.json
        training_data = json.load(input_file)

    urls = []
    text = []
    targets = []
    i = 0
    for project in testing_data:
        if len(project["text"]) != 0:
            text.append(get_words(project["text"]))
            urls.append(project["url"])
            targets.append([])
            for theme in project["themes"]:
                if theme["id"] not in training_data["themes"]:
                    continue
                targets[i].append(training_data["themes"][theme["id"]])
        i += 1

    text_clf = Pipeline(
        [
            ("vect", CountVectorizer(ngram_range=(1, 2), max_df=0.6)),
            ("tfidf", TfidfTransformer()),
            ("clf", OneVsRestClassifier(SGDClassifier(random_state=42, loss="log"))),
        ]
    )

    y = training_data["targets"]
    y = MultiLabelBinarizer().fit_transform(y)

    test_words = text
    text_clf.fit(training_data["text"], y)
    probabilites = text_clf.predict_proba(test_words)
    predicted = text_clf.predict(test_words)

    return probabilites, predicted


"""
args: trained.json predictions.json
"""
if __name__ == "__main__":
    dataset = dynamo_db.get_dataset("organizations_text")
    train_data, test_data = train_test_split(dataset, test_size=0.2, random_state=42)

    matching_dataset = dynamo_db.get_dataset("organizations")
    themes = set_up_training_data(train_data, matching_dataset)
    testing_targets = get_targets(test_data, matching_dataset, themes)

    probabilities, predictions = classify(test_data, testing_targets)
    with open("predictions.json", "w") as output_file:
        json.dump(
            predictions.tolist(),
            output_file,
            separators=(",", ":"),
            sort_keys=True,
            indent=4,
        )
    with open("probabilities.json", "w") as output_file:
        json.dump(
            probabilities.tolist(),
            output_file,
            separators=(",", ":"),
            sort_keys=True,
            indent=4,
        )
