import requests
import json
import nltk
import gensim
import enchant
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import sys

sys.path.append("..")
from utils.dataset_db import dynamo_db
from utils.dataset_db import db


def main():
    with open("dictionaries/categories_dict.json") as categories_dict:
        # fetching website data
        dictionary = json.load(categories_dict)
        websites = db.get_dataset("organizations_text")
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
    with open("classifications/correct_classifications.json") as classifications:
        with open("classifications/bow_classifications.json") as predictions:
            f1_score(json.load(predictions), json.load(classifications))
        #    correct = test_classification_accuracy(
        #        json.load(predictions), json.load(classifications)
        #    )
        #print("classification accuracy: " + str(correct))

    print("success")


def classify_org(dictionary: dict, text: str):
    """  
    Classifies organizations through bag of words implementation
    """
    # initializing category scores
    categories = {
        "Education": 0,
        "Children": 1,
        "Women and Girls": 2,
        "Animals": 3,
        "Climate Change": 4,
        "Democracy and Governance": 5,
        "Disaster Recovery": 6,
        "Economic Development": 7,
        "Environment": 8,
        "Microfinance": 9,
        "Health": 10,
        "Humanitarian Assistance": 11,
        "Human Rights": 12,
        "Sport": 13,
        "Technology": 14,
        "Hunger": 15,
        "Arts and Culture": 16,
        "LGBTQAI+": 17,
    }

    scores = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

    # calculating sum of relevant words in each category
    total = 0
    for word in text:
        for category, category_words in dictionary.items():
            if category_words.get(word) is not None:
                scores[categories[category]] += category_words.get(word).get("idf")
                total += category_words.get(word).get("idf")

    # calculating percentage of relevant words in each category
    #for i in range(len(scores)):
    #    scores[i] /= total if total != 0 else 1

    # finding second max score result
    max = scores[0]
    max_2 = 0
    for score in scores:
        if score > max:
            max = score
        elif score > max_2:
            max_2 = score

    #for i in range(len(scores)):
    #    scores[i] = 1 if scores[i] >= max_2 else 0
        
    # storing results
    return scores


def f1_score(predictions: dict, classifications: dict):
    categories = {
        "Education": 0,
        "Children": 1,
        "Women and Girls": 2,
        "Animals": 3,
        "Climate Change": 4,
        "Democracy and Governance": 5,
        "Disaster Recovery": 6,
        "Economic Development": 7,
        "Environment": 8,
        "Microfinance": 9,
        "Health": 10,
        "Humanitarian Assistance": 11,
        "Human Rights": 12,
        "Sport": 13,
        "Technology": 14,
        "Hunger": 15,
        "Arts and Culture": 16,
        "LGBTQAI+": 17,
    }

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
            corr_themes = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            for theme in classifications[org_name]["themes"]:
                corr_themes[categories[theme["name"]]] = 1

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
        f1 = 2 * ((precision * recall) / (precision + recall) if (precision + recall) != 0 else 0)

        '''print(category + ":")
        print("Accuracy:", accuracy)
        print("Precision:", precision)
        print("Recall:", recall)
        print("F1:", f1)
        print("    T  F")
        print("T  " + str(tp) + ", " + str(fp))
        print("F  " + str(fn) + ", " + str(tn))
        print() '''
        total_accu += accuracy
        total_prec += precision
        total_reca += recall
        total_f1 += f1

    print("Average Accuracy:", total_accu / 18)
    print("Average Precision:", total_prec / 18)
    print("Average Recall:", total_reca / 18)
    print("Average F1:", total_f1 / 18)


def print_results(organization, results: dict):
    """ 
    Helper method to display classification scores of an organization for testing purposes
    """

    print(organization)
    print("Category scores: ")
    for category in results:
        print(category + ": " + str(results[category]))
    print("\n\n")


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