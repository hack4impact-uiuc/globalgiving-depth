import requests
import json
import copy
import nltk
import gensim
import enchant
import numpy as np
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import sys

sys.path.append("..")
from utils.dataset_db import db


def main():
    with open("dictionaries/categories_dict.json") as categories_dict:
        # fetching website data
        websites = db.get_dataset("organizations_text")
        dictionary = json.load(categories_dict)
        classifications = {}

    # tokenizing scraped website data into words
    for i in range((int)(len(websites) * 0.8), len(websites)):
        # fetching and processing text
        if websites[i].get("text") is None:
            continue

        text = preprocess_text(websites[i].get("text"))

        # storing classifications
        classifications[websites[i]["name"]] = classify_org(dictionary, text)

        # progress bar for satisfaction
        print((i - len(websites) * 0.8) / (len(websites) * 0.2))

    # dumping data
    with open("classifications/bow_classifications.json", "w") as classifications_json:
        json.dump(
            classifications,
            classifications_json,
            sort_keys=True,
            indent=2,
            ensure_ascii=False,
        )

    print("classification success")

    # testing classification accuracy
    with open("classifications/correct_2.json") as classifications:
        with open("classifications/bow_classifications.json") as predictions:
            f1_score(json.load(predictions), json.load(classifications))

    print("success")


def classify_org(dictionary: dict, text: str):
    """  
    Classifies organizations through bag of words implementation
    """
    # initializing category scores
    categories = {
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
        "Technology": 10,
    }

    scores = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    total = 0
    for word in text:
        for category, category_words in dictionary.items():
            if category_words.get(word) is not None:
                scores[categories[category]] += category_words.get(word)
                total += category_words.get(word)

    # finding second max score result
    temp = copy.deepcopy(scores)
    temp.sort()
    threshold = temp[-2]

    for i in range(len(scores)):
        scores[i] = 1 if scores[i] >= threshold else 0

    # storing results
    return scores


def f1_score(predictions: dict, classifications: dict):

    total_accu = 0
    total_prec = 0
    total_reca = 0
    total_f1 = 0

    for category in range(18):
        tp = 0
        tn = 0
        fp = 0
        fn = 0

        for org_name, pred_themes in predictions.items():
            # get correct themes
            corr_themes = classifications[org_name]

            if pred_themes[category] == 1 and corr_themes[category] == 1:
                tp += 1
            if pred_themes[category] == 1 and corr_themes[category] == 0:
                fp += 1
            if pred_themes[category] == 0 and corr_themes[category] == 1:
                fn += 1
            if pred_themes[category] == 0 and corr_themes[category] == 0:
                tn += 1

        accuracy = (tp + tn) / len(predictions)
        precision = tp / (tp + fp) if (tp + fp) != 0 else 0
        recall = tp / (tp + fn) if (tp + fn) != 0 else 0
        f1 = 2 * (
            (precision * recall) / (precision + recall)
            if (precision + recall) != 0
            else 0
        )

        total_accu += accuracy
        total_prec += precision
        total_reca += recall
        total_f1 += f1

    print("Average Accuracy:", total_accu / 18)
    print("Average Precision:", total_prec / 18)
    print("Average Recall:", total_reca / 18)
    print("Average F1:", total_f1 / 18)


def stem_word(text: str):
    """
    Stemming words
    """
    wnl = WordNetLemmatizer()

    # Returns input word unchanged if can't be found in WordNet
    return wnl.lemmatize(text)


def preprocess_text(text: str):
    """
    1) Tokenize
    2) Remove Stopwords
    3) Stem Words
    """
    processed_text = []
    stop_words = set(stopwords.words("english"))
    d = enchant.Dict("en_US")  # english words

    for token in gensim.utils.simple_preprocess(text):
        if token not in stop_words and d.check(token) and len(token) != 1:
            processed_text.append(stem_word(token))

    processed_text = list(set(processed_text))

    return processed_text


if __name__ == "__main__":
    main()
