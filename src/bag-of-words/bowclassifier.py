import requests
import json
import nltk
import gensim
import enchant
import numpy as np
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import sys

sys.path.append("..")
from utils.dataset_db import dynamo_db

def main():
    bow = BOWClassifier("trained.json", "dictionaries/categories_dict.json")
    #bow.train(json.load(open("dictionaries/test.json")))
    #bow.predict_set(dynamo_db.get_dataset("organizations_text"))
    #bow.save_predictions("dictionaries/predictions.json")
    bow.load_targets(json.load(open("trained.json")))
    bow.get_f1_score(json.load(open("dictionaries/predictions.json")))


class BOWClassifier:
    themes = {}
    training_data = {}
    dictionary = None

    probabilities = None
    predictions = None

    testing_data = None
    testing_targets = None


    def __init__(self, train_data: str, dict_data: str):  # TODO: write spec for input data, make default file
        with open(train_data, "r") as input_file:
            self.training_data = json.load(input_file)
            self.themes = self.training_data["themes"]

        with open(dict_data, "r") as input_dict:
            self.dictionary = json.load(input_dict)
            
            # ensuring dictionary is correctly structured
            for theme in self.themes:
                assert self.dictionary.get(theme), "dictionary does not contain proper theme keys."

            theme = next(iter(self.themes))
            word = next(iter(self.dictionary[theme]))
            assert self.dictionary.get(theme).get(word).get("idf"), "dictionary does not contain tf-idf score"


    def predict_set(self, testing_data: dict):
        assert self.dictionary

        # storing testing data, subject to be deleted later
        self.testing_data = testing_data

        self.predictions = []

        i = 0
        for project in testing_data:
            if project.get("text") != None:
                self.predictions.append(self.predict_org(project["text"]))
            i += 1
            print(i) 

        return self.predictions

    
    def train(self, dataset):
        themes = {
            "Animals": 11,
            "Arts and Culture": 14,
            "Children": 6,
            "Climate Change": 5,
            "Democracy and Governance": 15,
            "Disaster Recovery": 12,
            "Economic Development": 0,
            "Education": 1,
            "Environment": 7,
            "Microfinance": 2,
            "Women and Girls": 3,
            "Health": 8,
            "Humanitarian Assistance": 9,
            "Hunger": 16,
            "LGBTQAI+": 17,
            "Human Rights": 4,
            "Sport": 13,
            "Technology": 10
        }  # themes to indices
        targets = []  # indices of themes, parallel to text array
        text = []
        urls = []

        for project in dataset:
            if len(project["text"]) != 0:
                text.append(project["text"])
                urls.append(project["url"])
                temp_themes = []
                for theme in project["themes"]:
                    temp_themes.append(themes[theme["name"]])
                targets.append(temp_themes)

        data = {}
        data["themes"] = themes
        data["targets"] = targets
        data["urls"] = urls
        data["text"] = text

        with open("trained.json", "w") as output_file:  # trained.json
            json.dump(
                data,
                output_file,
                sort_keys=True,
                indent=2,
                ensure_ascii=False,
            )

        return themes


    def save_predictions(self, output_file):
        assert self.predictions, "predictions have not been made yet"

        with open(output_file, "w") as predictions_json:
            json.dump(
                self.predictions,
                predictions_json,
                sort_keys=True,
                indent=2,
                ensure_ascii=False,
            )
        

    def predict_org(self, text: str):
        """
        Classifies organizations through bag of words implementation
        """
        scores = [0]*18
        # calculating sum of relevant words in each category
        total = 0
        for word in text:
            for category, category_words in self.dictionary.items():
                if category_words.get(word) is not None:
                    scores[self.themes[category]] += category_words.get(word).get("idf")
                    total += category_words.get(word).get("idf")

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


    def get_f1_score(self, predictions):
        # output mean f1 score by document, then category
        # for every document, calculate the matrix, then f1 score
        f1_scores = []
        accuracies = []
        print("predictions: ", len(predictions))
        print("targets: ", len(self.testing_targets))
        for i in range(len(predictions)):
            fp = 0
            fn = 0
            tp = 0
            tn = 0
            for j in range(len(predictions[i])):
                if predictions[i][j] == 1:
                    if j in self.testing_targets[i]:
                        tp += 1
                    else:
                        fp += 1
                else:
                    if j in self.testing_targets[i]:
                        fn += 1
                    else:
                        tn += 1
            precision = 0 if tp+fp == 0 else tp/(tp+fp)
            recall = 0 if tp+fn == 0 else tp/(tp+fn)
            f1 = 0 if precision+recall == 0 else 2*(precision*recall)/(precision+recall)
            f1_scores.append(f1)
            accuracies.append((tp+tn)/len(predictions[i]))

        print(np.mean(np.array(f1_scores)))
        print(f1_scores)
        print(np.mean(np.array(accuracies)))
        print(accuracies)

        # TODO: add f1score by category
        

    def load_targets(self, target_data: dict):  #private
        assert target_data.get("targets")
        self.testing_targets = target_data["targets"]

        return 0

if __name__ == "__main__":
    main()