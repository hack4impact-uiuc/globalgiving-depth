import json
import nltk
import math
import gensim
import enchant
import copy
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import sys

sys.path.append("..")
from utils.dataset_db import db


def main():
    generate_dict()
    print("success")


def generate_dict():
    """
    Generates a dictionary of relevant words for each category classification 
    """

    # initializing category dictionary
    category_dict = {
        "Education": {},
        "Children": {},
        "Women and Girls": {},
        "Animals": {},
        "Climate Change": {},
        "Democracy and Governance": {},
        "Disaster Recovery": {},
        "Economic Development": {},
        "Environment": {},
        "Microfinance": {},
        "Health": {},
        "Humanitarian Assistance": {},
        "Human Rights": {},
        "Sport": {},
        "Technology": {},
        "Hunger": {},
        "Arts and Culture": {},
        "LGBTQAI+": {},
    }

    # opening scraped website data
    websites = db.get_dataset("organizations_text")

     # opening scraped website data
    with open("classifications/correct_classifications.json") as correct:
        classifications = json.load(correct)

        # processing words and inserting them into categories dictionary
        for i in range((int)(len(websites) * 0.8)):
            # grabbing and processing text
            website = websites[i]
            if website.get("text") is None:
                continue

            text = preprocess_text(website.get("text"))
            text = nltk.pos_tag(text)

            # putting words into dictionary
            for theme in classifications[website["name"]]["themes"]:
                temp_dict = dict(text)
                for word in temp_dict:
                    # counting the frequency of words to be used for scores later
                    try:
                        category_dict[theme["name"]][word]["freq"] += 1
                    except:
                        category_dict[theme["name"]][word] = {
                            "tags": temp_dict[word],
                            "freq": 1,
                        }
            print(i / (len(websites) * 0.8))

        # calculating idf scores
        print("calculating idf scores...")
        calculate_idf_scores(category_dict)

    # dumping data
    with open("dictionaries/categories_dict.json", "w") as categories_json:
        json.dump(
            category_dict, categories_json, sort_keys=True, indent=2, ensure_ascii=False
        )


def stem_word(text: str):
    """
    Stems words
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


def remove_common_words_from_categories(categories):
    # creating dictionary of all unique words from categories
    all_words = set()
    for category in categories:
        all_words = all_words | set(categories[category].keys())

    all_words = dict.fromkeys(all_words, 0)

    # counting word freq in categories
    for category in categories:
        for word in categories[category].keys():
            all_words[word] += 1

    # removing words from categories with freq > 1 (non-unique words)
    for word in all_words:
        if all_words[word] > 1:
            for category in categories:
                categories[category].pop(word, None)

def calculate_idf_scores(categories):
    # creating dictionary of all unique words from categories
    all_words = set()
    for category in categories:
        all_words = all_words | set(categories[category].keys())

    all_words = dict.fromkeys(all_words, 0)

    # counting word freq in categories
    for category in categories:
        for word in categories[category].keys():
            all_words[word] += 1

    for word in all_words:
        for category in categories:
            for term in categories[category]:
                if (word == term):
                    categories[category][term]["idf"] = math.log10((18 / all_words[word]) + 1)
        

if __name__ == "__main__":
    main()
