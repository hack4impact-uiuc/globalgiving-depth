import json
import copy
import numpy as np


class BOWClassifier:
    """
    A bag of words classifier to predict the themes of a non-profit organization given text.
    
    Methods:
    __init__(self, train_data: dict, dict_data: dict)
    predict_set(self, testing_data: dict)
    predict_org(self, text: str)
    save_predictions(self, output_file: str)
    load_predictions(self, predictions: dict)
    get_predictions(self)
    get_f1_score(self)
    load_targets(self, target_data: dict)
    """

    # internal necessities
    themes = {}  # a dict mapping themes to indices in a list
    dictionary = None  # dictionary of words for bag of words to utilize in scoring text

    predictions = (
        None
    )  # predictions made by the classifier : stored every time predict_set is called

    # testing datasets
    testing_data = None  # testing dataset to test accuracy
    testing_targets = None  # testing targets

    def __init__(self, train_data: dict, dict_data: dict):
        """
        Initializes bag of words classifier object
        
        :param dict train_data: training data 
        :param dict dict_data: dictionary of category words
        """
        self.themes = self.training_data["themes"]
        self.dictionary = dict_data

        # ensuring dictionary is correctly structured
        for theme in self.themes:
            assert self.dictionary.get(
                theme
            ), "dictionary does not contain proper theme keys."

        theme = next(iter(self.themes))
        word = next(iter(self.dictionary[theme]))
        assert (
            self.dictionary.get(theme).get(word).get("tf-idf")
        ), "dictionary does not contain tf-idf score"

    def predict_set(self, testing_data: dict):
        """
        Predicts a set of organizations

        :param dict testing_data: the testing dataset to be predicted
        :return: A list of lists of predicted scores
        """
        assert self.dictionary
        self.predictions = []

        # predicting organizations
        for project in testing_data:
            if project.get("text") != None:
                self.predictions.append(self.predict_org(project["text"]))

        return self.predictions

    def predict_org(self, text: str):
        """
        Predicts an organizations themes based off text

        :param str text: text from the organization
        :return: list of predictions
        """
        # list to store scores
        scores = [0] * 18

        # calculating sum of relevant words in each category
        total = 0
        for word in text:
            for category, category_words in self.dictionary.items():
                if category_words.get(word) is not None:
                    scores[self.themes[category]] += category_words.get(word).get(
                        "tf-idf"
                    )
                    total += category_words.get(word).get("tf-idf")

        # finding second highest category score
        temp = copy.deepcopy(scores)
        temp.sort()
        threshold = temp[-6]

        # predicting all themes of second highest score and above
        for i in range(len(scores)):
            scores[i] = 1 if scores[i] >= threshold else 0

        # returning results
        return scores

    def save_predictions(self, output_file: str):
        """
        Stores predictions made by the bag of words model

        :param str output_file: json file name for predictions to be stored in
        """
        assert self.predictions, "predictions have not been made yet"

        with open(output_file, "w") as predictions_json:
            json.dump(
                self.predictions,
                predictions_json,
                sort_keys=True,
                indent=2,
                ensure_ascii=False,
            )

    def load_predictions(self, predictions: dict):
        """
        Load predictions from file

        :param dict predictions: dict of predictions
        """
        self.predictions = predictions

    def get_predictions(self):
        return self.predictions

    def get_f1_score(self):
        """
        Returns the f1 score for the predictions by organization and category
        """
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
            precision = 0 if (tp + fp == 0) else tp / (tp + fp)
            recall = 0 if (tp + fn == 0) else tp / (tp + fn)
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

    def load_targets(self, target_data: dict):
        """
        Load the testing targets (correct classifications) for testing dataset
        Predictions made by the classifier are stored in a list of lists of the predicted scores.
        The testing targets to be loaded should also be a list of lists of predicted scores, with each index
        corresponding to the same organization in the predictions list.

        :param dict target_data: dictionary containing target data for testing dataset
        """
        assert target_data.get("targets"), "targets parameter needed in dictionary"
        self.testing_targets = target_data["targets"]
