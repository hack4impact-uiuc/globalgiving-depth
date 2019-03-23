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
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC, LinearSVC
from sklearn import metrics
from sklearn.model_selection import GridSearchCV

sys.path.append("..")

from utils.dataset_db import db

from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer

"""
Not used in optimal sol'n - also makes it take hours to run
"""


class LemmaTokenizer(object):
    def __init__(self):
        self.wnl = WordNetLemmatizer()

    def __call__(self, doc):
        return [self.wnl.lemmatize(t) for t in word_tokenize(doc)]


def get_words(text):
    text = text.lower()
    wordlist = text.split()
    clean_list = []
    for word in wordlist:
        # only get words (no digits)
        if not word.isdigit() and not re.match(r"[^\w]", word):
            clean_list.append(word)

    return " ".join(clean_list)


"""
Doesn't actually train, just generates a JSON in the format we want of training data
"""


def train(dataset):
    next_index = 0
    themes = {}  # themes to indices
    targets = []  # indices of themes, parallel to text array
    text = []
    urls = []

    for project in dataset:
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
    with open(sys.argv[1], "w") as output_file:  # trained.json
        json.dump(data, output_file)

    return themes


"""
Vectorizes both training and testing data, then classifies
"""


def classify(testing_data, testing_targets):
    with open(sys.argv[1], "r") as input_file:  # trained.json
        training_data = json.load(input_file)

    urls = []
    text = []
    targets = []
    for project in testing_data:
        if len(project["text"]) != 0:
            text.append(get_words(project["text"]))
            urls.append(project["url"])
            for theme in project["themes"]:
                if theme["id"] not in training_data["themes"]:
                    continue
                targets.append(training_data["themes"][theme["id"]])

    text_clf = Pipeline(
        [
            ("vect", CountVectorizer(ngram_range=(1, 2), max_df=0.6)),
            ("tfidf", TfidfTransformer()),
            # ("clf", SVC(kernel="linear", C=2))
            ("clf", SGDClassifier(random_state=42, max_iter=50, class_weight={0: 0.6})),
        ]
    )

    test_words = text
    text_clf.fit(training_data["text"], training_data["targets"])
    predicted = text_clf.predict(test_words)

    with open(sys.argv[2], "w") as output_file:  # predictions.json
        json.dump(
            predicted.tolist(),
            output_file,
            separators=(",", ":"),
            sort_keys=True,
            indent=4,
        )

    return predicted


def get_targets(data, themes):
    targets = []
    for project in data:
        for theme in project["themes"]:
            if theme["id"] not in themes:
                targets.append(-1)
            targets.append(themes[theme["id"]])

    return targets


"""
args: trained.json predictions.json
"""
if __name__ == "__main__":
    dataset = db.get_dataset("organizations_text")
    print(len(dataset))
    train_data, test_data = train_test_split(dataset, test_size=0.2, random_state=42)
    print(len(train_data), len(test_data))
    themes = train(train_data)
    testing_targets = get_targets(test_data, themes)
    predictions = classify(test_data, testing_targets)
    print(len(testing_targets))
    print(set(testing_targets))
    print(np.mean(predictions == testing_targets))
    print(metrics.confusion_matrix(testing_targets, predictions))
