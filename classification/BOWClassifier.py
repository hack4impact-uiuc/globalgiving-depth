import json
import numpy as np
import sys

sys.path.append("..")
from utils.dataset_db import dynamo_db


def main():
    bow = BOWClassifier("trained.json", "categories_dict.json")
    bow.predict_set(dynamo_db.get_dataset("organizations_text"))
    bow.save_predictions("predictions.json")
    bow.load_predictions("predictions.json")
    bow.load_targets(json.load(open("trained.json")))
    print(bow.get_f1_score())


class BOWClassifier:
    themes = {}
    training_data = {}
    dictionary = None

    predictions = None

    testing_data = None
    testing_targets = None

    """
    Initializes bag of words classifier object
    
    :param str train_data: training data filename
    :param str dict_data: dictionary of category words filename
    """

    def __init__(self, train_data: str, dict_data: str):
        with open(train_data, "r") as input_file:
            self.training_data = json.load(input_file)
            self.themes = self.training_data["themes"]

        with open(dict_data, "r") as input_dict:
            self.dictionary = json.load(input_dict)

            # ensuring dictionary is correctly structured
            for theme in self.themes:
                assert self.dictionary.get(
                    theme
                ), "dictionary does not contain proper theme keys."

            theme = next(iter(self.themes))
            word = next(iter(self.dictionary[theme]))
            assert (
                self.dictionary.get(theme).get(word).get("idf")
            ), "dictionary does not contain tf-idf score"

    """
    Predicts a set of organizations

    :param dict testing_data: the testing dataset to be predicted
    :return: list of predicted scores
    """

    def predict_set(self, testing_data: dict):
        assert self.dictionary
        self.predictions = []

        # predicting organizations
        for project in testing_data:
            if project.get("text") != None:
                self.predictions.append(self.predict_org(project["text"]))

        return self.predictions

    """
    Stores predictions made by the bag of words model

    :param str output_file: json file name for predictions to be stored in
    """

    def save_predictions(self, output_file: str):
        assert self.predictions, "predictions have not been made yet"

        with open(output_file, "w") as predictions_json:
            json.dump(
                self.predictions,
                predictions_json,
                sort_keys=True,
                indent=2,
                ensure_ascii=False,
            )

    """
    Load predictions from file

    :param str filename: json file of predictions to be imported from
    """

    def load_predictions(self, filename: str):
        with open(filename) as input_file:
            self.predictions = json.load(input_file)

    """
    Predicts an organizations themes based off text

    :param str text: text from the organization
    :return: list of predictions
    """

    def predict_org(self, text: str):
        # list to store scores
        scores = [0] * 18

        # calculating sum of relevant words in each category
        total = 0
        for word in text:
            for category, category_words in self.dictionary.items():
                if category_words.get(word) is not None:
                    scores[self.themes[category]] += category_words.get(word).get("tf-idf")
                    total += category_words.get(word).get("tf-idf")

        # finding second highest category score
        max = scores[0]
        max_2 = 0
        for score in scores:
            if score > max:
                max = score
            elif score > max_2:
                max_2 = score

        # predicting all themes of second highest score and above
        for i in range(len(scores)):
            scores[i] = 1 if scores[i] >= max_2 else 0

        # returning results
        return scores

    """
    Returns the f1 score for the predictions by organization then category
    """

    def get_f1_score(self):
        # output mean f1 score by document, then category
        assert self.testing_targets, "targets not loaded"
        testing_targets = self.testing_targets

        # for every document, calculate the matrix, then f1 score
        org_f1_scores = []
        accuracies = []
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
            org_f1_scores.append(f1)
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

        return np.mean(np.array(org_f1_scores)), category_f1_scores

    """
    Load the testing targets for testing dataset

    :param dict target_data: dictionary containing target data for testing dataset
    """

    def load_targets(self, target_data: dict):
        assert target_data.get("targets")
        self.testing_targets = target_data["targets"]


if __name__ == "__main__":
    main()
