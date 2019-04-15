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
    # classifying orgs
    with open("dictionaries/categories_dict.json") as categories:
       classify_org(json.load(categories))
    print("classification success")

    # testing classification accuracy
    with open("classifications/correct_classifications.json") as classifications:
        with open("classifications/bow_classifications.json") as predictions:
            f1_categories(json.load(predictions), json.load(classifications))
        #    correct = test_classification_accuracy(
        #        json.load(predictions), json.load(classifications)
        #    )
        #print("classification accuracy: " + str(correct))

    print("success")


def classify_org(category_data: dict):
    """  
    Classifies organizations through bag of words implementation
    """
    # fetching website data
    websites = db.get_dataset("organizations_text")
    classifications = {}

    # tokenizing scraped website data into words
    for i in range((int)(len(websites) * 0.8), len(websites)):
        # fetching and processing text
        if websites[i].get("text") is None:
            continue

        text = preprocess_text(websites[i].get("text"))

        # initializing category scores
        category_scores = {
            "Education": 0,
            "Children": 0,
            "Women and Girls": 0,
            "Animals": 0,
            "Climate Change": 0,
            "Democracy and Governance": 0,
            "Disaster Recovery": 0,
            "Economic Development": 0,
            "Environment": 0,
            "Microfinance": 0,
            "Health": 0,
            "Humanitarian Assistance": 0,
            "Human Rights": 0,
            "Sport": 0,
            "Technology": 0,
            "Hunger": 0,
            "Arts and Culture": 0,
            "LGBTQAI+": 0,
        }

        # calculating sum of relevant words in each category
        total_score = 0
        for word in text:
            for category in category_data:
                if category_data[category].get(word) is not None:
                    category_scores[category] += category_data[category][word]["idf"]
                    total_score += category_data[category][word]["idf"]

        # calculating percentage of relevant words in each category
        for category in category_scores:
            category_scores[category] /= 1 if total_score == 0 else total_score

        # finding second max score result
        themes = []
        max = category_scores["Education"]
        max_2 = 0
        for category in category_scores:
            if category_scores[category] > max:
                max = category_scores[category]
            elif category_scores[category] > max_2:
                max_2 = category_scores[category]

        for category in category_scores:
            if category_scores[category] >= max_2:
                themes.append(category)

        # storing results
        classifications[websites[i]["name"]] = {"themes": themes}

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


def f1_categories(predictions: dict, classifications: dict):
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

    for category in categories:
        tp = 0
        tn = 0
        fp = 0
        fn = 0

        for org_name, org_themes in predictions.items():
            # get predicted themes
            pred_themes = org_themes["themes"]

            # get correct themes
            corr_themes = []
            for theme in classifications[org_name]["themes"]:
                corr_themes.append(theme["name"])

            if category in pred_themes and category in corr_themes:
                tp += 1
            if category in pred_themes and category not in corr_themes:
                fp += 1
            if category not in pred_themes and category in corr_themes:
                fn += 1
            if category not in pred_themes and category not in corr_themes:
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