import requests
import json
import nltk
import gensim
import enchant
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import sys

sys.path.append("..")
from utils.dataset_db import db


def main():
    # classifying orgs
    with open("dictionaries/categories_dict.json") as categories:
        classify_org(json.load(categories))
    print("classification success")

    # testing classification accuracy
    with open("classifications/correct_classifications.json") as classifications:
        with open("classifications/bow_classifications.json") as predictions:
            correct = test_classification_accuracy(
                json.load(predictions), json.load(classifications)
            )
        print("classification accuracy: " + str(correct))

    print("success")


def classify_org(category_data):
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
        for word in text:
            for category in category_data:
                if category_data[category].get(word) is not None:
                    category_scores[category] += category_data[category][word]["idf"]

        # finding max score result
        classification = "Education"
        max = category_scores["Education"]
        for category in category_scores:
            if category_scores[category] > max:
                max = category_scores[category]
                classification = category

        # storing results
        classifications[websites[i].get("name")] = {"theme": classification}

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


def test_classification_accuracy(predictions, classifications):
    """
    Returns the accuracy of classifications by cross-referencing original GG database classifications
    """
    correct = 0
    total = len(predictions)

    # iterating through all classifications and counting number correct
    for prediction in predictions:
        for theme in classifications[prediction]["themes"]:
            if predictions[prediction]["theme"] == theme["name"]:
                correct += 1

    # returning percentage correct
    return correct / total


def test_category_accuracy(predictions, classifications):
    """
    Returns the accuracy of classifications within each category
    """
    # storing total category count
    category_count = {
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

    # counting total category occurrences in predictions
    for prediction in predictions:
        for theme in classifications[prediction]["themes"]:
            category_count[theme["name"]] += 1

    category_scores = {
        "Education": {"correct": 0, "total": category_count["Education"]},
        "Children": {"correct": 0, "total": category_count["Children"]},
        "Women and Girls": {"correct": 0, "total": category_count["Women and Girls"]},
        "Animals": {"correct": 0, "total": category_count["Animals"]},
        "Climate Change": {"correct": 0, "total": category_count["Climate Change"]},
        "Democracy and Governance": {"correct": 0, "total": category_count["Democracy and Governance"]},
        "Disaster Recovery": {"correct": 0, "total": category_count["Disaster Recovery"]},
        "Economic Development": {"correct": 0, "total": category_count["Economic Development"]},
        "Environment": {"correct": 0, "total": category_count["Environment"]},
        "Microfinance": {"correct": 0, "total": category_count["Microfinance"]},
        "Health": {"correct": 0, "total": category_count["Health"]},
        "Humanitarian Assistance": {"correct": 0, "total": category_count["Humanitarian Assistance"]},
        "Human Rights": {"correct": 0, "total": category_count["Human Rights"]},
        "Sport": {"correct": 0, "total": category_count["Sport"]},
        "Technology": {"correct": 0, "total": category_count["Technology"]},
        "Hunger": {"correct": 0, "total": category_count["Hunger"]},
        "Arts and Culture": {"correct": 0, "total": category_count["Arts and Culture"]},
        "LGBTQAI+": {"correct": 0, "total": category_count["LGBTQAI+"]},
    }

    # iterating through all classifications and counting number correct
    correct = False

    for prediction in predictions:
        correct = False

        # checking the prediction is correct for any themes classified
        for theme in classifications[prediction]["themes"]:
            if predictions[prediction]["theme"] == theme["name"]:
                correct = True
                break

        # if correct, increment correct score and deduct category totals from unclassified categories
        if correct:
            for theme in classifications[prediction]["themes"]:
                if predictions[prediction]["theme"] == theme["name"]:
                    category_scores[theme["name"]]["correct"] += 1
                else:
                    category_scores[theme["name"]]["total"] -= 1


def print_results(organization, results):
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


def score_word_by_type(word):
    """
    Returns weighted score of a word based off of it's lexical type
    """
    tags = word.get("tags")
    if tags is not None:
        if tags[0] == "N":
            return 8
        if tags[0] == "V":
            return 2
        if tags[0] == "J":
            return 5

    return 1


def score_word_by_amplified_relevance(word):
    """
    Returns an amplified weighted score of non-unique words
    """
    if word.get("freq", 0) > 1:
        return word.get("freq") * 4
    else:
        return 1


if __name__ == "__main__":
    main()