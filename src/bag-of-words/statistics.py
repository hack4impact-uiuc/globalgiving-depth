import requests
import json
import nltk
import gensim
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import sys

sys.path.append("..")
from utils.dataset_db import db


def main():
    """
    A module to generate statistics about the organizations classified for testing purposes
    """
    # printing category classification count
    with open("classifications/correct_classifications.json") as classifications:
        print_intersecting_categories(json.load(classifications))
        #print_confusion_matrix(json.load(classifications))

    # printing dictionary word count
    # with open("dictionaries/categories_dict.json") as dictionaries:
    #    print_category_dict_count(json.load(dictionaries))

    print("success")


def print_category_classification_count(classifications):
    """
    Calculates the total number of classifications in each category
    """
    category_scores = {
        "Education": {"correct": 0, "total": 0},
        "Children": {"correct": 0, "total": 0},
        "Women and Girls": {"correct": 0, "total": 0},
        "Animals": {"correct": 0, "total": 0},
        "Climate Change": {"correct": 0, "total": 0},
        "Democracy and Governance": {"correct": 0, "total": 0},
        "Disaster Recovery": {"correct": 0, "total": 0},
        "Economic Development": {"correct": 0, "total": 0},
        "Environment": {"correct": 0, "total": 0},
        "Microfinance": {"correct": 0, "total": 0},
        "Health": {"correct": 0, "total": 0},
        "Humanitarian Assistance": {"correct": 0, "total": 0},
        "Human Rights": {"correct": 0, "total": 0},
        "Sport": {"correct": 0, "total": 0},
        "Technology": {"correct": 0, "total": 0},
        "Hunger": {"correct": 0, "total": 0},
        "Arts and Culture": {"correct": 0, "total": 0},
        "LGBTQAI+": {"correct": 0, "total": 0},
    }

    # determining total number of classifications in each category
    for org in classifications:
        for theme in classifications[org]["themes"]:
            category_scores[theme["name"]]["total"] += 1

    for category in category_scores:
        print(category + ": " + str(category_scores[category]["total"]))


def print_intersecting_categories(classifications):
    count = [[0 for i in range(18)] for j in range(7)]
    total = [[0 for i in range(18)] for j in range(7)]

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


    for org in classifications:
        themes = []
        for theme in classifications[org]["themes"]:
            themes.append(theme["name"])

        counter = 0
        for theme in themes:
            if (theme in ["Children", "Women and Girls", "Animals"]):
                counter += 1

        for theme in themes:
            if (not (theme in ["Children", "Women and Girls", "Animals"])):
                for i in range(7):
                    total[i][categories[theme]] += 1

                if (counter == 1):
                    if ("Children" in themes):
                        count[0][categories[theme]] += 1
                    elif("Women and Girls" in themes):
                        count[1][categories[theme]] += 1
                    else:
                        count[2][categories[theme]] += 1
                elif (counter == 2):
                    if (set(["Children", "Animals"]).issubset(themes)):
                        count[3][categories[theme]] += 1
                    elif (set(["Children", "Women and Girls"]).issubset(themes)):
                        count[4][categories[theme]] += 1
                    elif (set(["Women and Girls", "Animals"]).issubset(themes)):
                        count[5][categories[theme]] += 1
                elif (counter == 3):
                    count[6][categories[theme]] += 1


    for i in range(7):
        for j in range(18):
            if (j < 1 or j > 3):
                print("{:0.2f}".format(count[i][j] / total[i][j]) + " ", end="")
        print()


def print_category_dict_count(category_dict):
    # category word count
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

    for category in category_dict:
        for word in category_dict[category]:
            category_count[category] += 1

    for category in category_count:
        print(category + ": " + str(category_count[category]))


def print_confusion_matrix(classifications):
    count = [[0 for i in range(18)] for j in range(18)]
    total = [[0 for i in range(18)] for j in range(18)]

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

    for org in classifications:
        themes = []
        for theme in classifications[org]["themes"]:
            themes.append(theme["name"])

        for theme in themes:
            for row in range(18):
                total[row][categories[theme]] += 1
            for theme_2 in themes:
                count[categories[theme]][categories[theme_2]] += 1

    for i in range(18):
        for j in range(18):
            print("{:0.2f}".format(count[i][j] / total[i][j]) + " ", end="")
        print()


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

    for token in gensim.utils.simple_preprocess(text):
        if token not in stop_words and len(token) != 1:
            processed_text.append(stem_word(token))

    processed_text = list(set(processed_text))

    return processed_text


if __name__ == "__main__":
    main()
