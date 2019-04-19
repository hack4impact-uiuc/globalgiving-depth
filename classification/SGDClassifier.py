import json
import re
import numpy as np

from sklearn.externals import joblib
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.pipeline import Pipeline
from sklearn.multiclass import OneVsRestClassifier
from sklearn.preprocessing import MultiLabelBinarizer
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


def set_up_training_data(dataset, outfile_name):
    next_index = 0
    themes = {}  # themes to indices
    targets = []  # indices of themes, parallel to text array
    text = []
    urls = []

    i = 0
    for project in dataset:
        m_themes = project["themes"]
        if len(project["text"]) != 0:
            words = get_words(project["text"])
            urls.append(project["url"])
            text.append(words)
            targets.append([])
            for theme in m_themes:
                if theme["name"] not in themes:
                    themes[theme["name"]] = next_index
                    next_index += 1
                targets[i].append(themes[theme["name"]])
        i += 1

    data = {}
    data["themes"] = themes
    data["targets"] = targets
    data["urls"] = urls
    data["text"] = text
    with open(outfile_name, "w") as output_file:  # trained.json
        json.dump(data, output_file)

    return themes


class NGOSGDClassifier:

    themes = {}
    training_data = {}

    probabilities = None
    predictions = None

    testing_data = None
    testing_targets = None

    SGDPipeline = None

    def __init__(
        self, train_data
    ):  # TODO: write spec for input data, make default file
        with open(train_data, "r") as input_file:
            self.training_data = json.load(input_file)
            self.themes = self.training_data["themes"]

    def save_classifier(self, filename):
        joblib.dump(self.SGDPipeline, filename)

    def load_classifier(self, filename):
        self.SGDPipeline = joblib.load(filename)
        return self.SGDPipeline

    def fit(self):
        text_clf = Pipeline(
            [
                ("vect", CountVectorizer(ngram_range=(1, 2), max_df=0.6)),
                ("tfidf", TfidfTransformer()),
                (
                    "clf",
                    OneVsRestClassifier(SGDClassifier(random_state=42, loss="log")),
                ),
            ]
        )

        y = self.training_data["targets"]
        y = MultiLabelBinarizer().fit_transform(y)

        text_clf.fit(self.training_data["text"], y)
        self.SGDPipeline = text_clf
        return self.SGDPipeline

    def predict(self, testing_data):
        assert self.SGDPipeline

        self.testing_data = testing_data

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
                    if theme["name"] not in self.themes:
                        continue
                    targets[i].append(self.themes[theme["name"]])
            i += 1

        test_words = text

        self.probabilities = self.SGDPipeline.predict_proba(test_words)
        self.predictions = self.SGDPipeline.predict(test_words)

        return self.probabilities, self.predictions

    def get_f1_score(self):
        # output mean f1 score by document, then category
        testing_targets = self.get_testing_targets()

        # for every document, calculate the matrix, then f1 score
        document_f1_scores = []
        accuracies = []  # are we still doing this?
        for i in range(len(self.predictions)):
            fp = 0
            fn = 0
            tp = 0
            tn = 0
            for j in range(len(self.predictions[i])):
                if self.predictions[i][j] == 1:
                    if j in testing_targets[i]:
                        tp += 1
                    else:
                        fp += 1
                else:
                    if j in testing_targets[i]:
                        fn += 1
                    else:
                        tn += 1
            precision = 0 if tp + fp == 0 else tp / (tp + fp)
            recall = 0 if tp + fn == 0 else tp / (tp + fn)
            f1 = (
                0
                if precision + recall == 0
                else 2 * (precision * recall) / (precision + recall)
            )
            document_f1_scores.append(f1)
            accuracies.append((tp + tn) / len(self.predictions[i]))

        category_f1_scores = {}
        for theme_name, theme_number in self.themes.items():
            tp = 0
            tn = 0
            fp = 0
            fn = 0
            for i in range(len(self.predictions)):
                if (
                    self.predictions[i][theme_number] == 1
                    and theme_number in testing_targets[i]
                ):
                    tp += 1
                if (
                    self.predictions[i][theme_number] == 1
                    and theme_number not in testing_targets[i]
                ):
                    fp += 1
                if (
                    self.predictions[i][theme_number] == 0
                    and theme_number in testing_targets[i]
                ):
                    fn += 1
                if (
                    self.predictions[i][theme_number] == 0
                    and theme_number not in testing_targets[i]
                ):
                    tn += 1

            precision = tp / (tp + fp) if (tp + fp) != 0 else 0
            recall = tp / (tp + fn) if (tp + fn) != 0 else 0
            f1 = (
                2 * ((precision * recall) / (precision + recall))
                if (precision + recall) != 0
                else 0
            )

            category_f1_scores[theme_name] = f1

        return np.mean(np.array(document_f1_scores)), category_f1_scores

    def get_testing_targets(self):
        if self.testing_data:
            targets = []
            i = 0
            for project in self.testing_data:
                m_themes = project["themes"]
                targets.append([])
                for theme in m_themes:
                    if theme["name"] not in self.themes:
                        targets[i].append(-1)
                    targets[i].append(self.themes[theme["name"]])
                i += 1
            self.testing_targets = targets

        return self.testing_targets

    def get_target_map(self):
        return self.themes
