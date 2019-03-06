import requests
import json
import nltk
import gensim
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import sys
sys.path.append("..")
from utils.dataset_db import db

# Heuristic Method to statistically classify organizations

''' Planned outline:
        1. Create dictionaries of associated words to each category
        2. Create weighted classification system that weights certain types of words more than others
            2a. Word repetition will be accounted for by counting each word individually.
        3. Develop algorithm to classify organizations by words on website, weighted and summed
        4. Create tests to test classification accuracy
        5. Randomize algorithm weights (pseudo-machine learning) to test which weights are most effective
        6. Profit
'''
def main():
    '''
    '''
    # classifying orgs
    with open("dictionaries/LDA_categories_80.json") as categories:
        classify_org(json.load(categories))
    print("classification success")

    # testing classification accuracy
    with open("classifications/correct_classifications.json") as classifications:
        with open("classifications/classifications_final.json") as predictions:
            correct = test_classification_accuracy(json.load(predictions), json.load(classifications))
        print("classification accuracy: " + str(correct))

    print("success")


def classify_org(category_data):
    '''  
    Classifies organizations based off words
    '''
    # pseudocode
    # parse words (through nltk)
    # initialize category dictionaries of related words, weights of each word type, category counters
    # create lists for word type (item/supplies, verbs, nouns, pronouns)
    # scrub data and add words to lists of word type
    # for each category, calculate sum of word relevance to each category to category counter
    # return highest category counter

    # fetching website data
    websites = db.get_dataset("organizations_text")
    classifications = {}

    # tokenizing scraped website data into words
    for i in range((int) (len(websites) * 0.8), len(websites) - 1):
        website = websites[i]
        if (website.get("text") is None):
            continue

        text = preprocess_text(website.get("text"))

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
            "LGBTQAI+": 0
        }

        # calculating sum of relevant words in each category
        for word in text:
            for category in category_data:
                if category_data[category].get(word) is not None:
                    category_scores[category] += category_data[category][word]["freq"] #score_word(word, category_data[category][word])

        # finding max score result
        classification = "Education"
        max = category_scores["Education"]
        for category in category_scores:
            if (category_scores[category] > max):
                max = category_scores[category]
                classification = category

        # storing results
        classifications[website.get("name")] = {
            "theme": classification
        }

        print(i / len(websites))

    # dumping data
    with open("classifications/classifications_final.json", "w") as classifications_json:
        json.dump(classifications, classifications_json, sort_keys=True, indent=2, ensure_ascii=False)    


def test_classification_accuracy(predictions, classifications):
    correct = 0
    total = len(predictions)

    for prediction in predictions:
        for classification in classifications[prediction]["themes"]:
            if predictions[prediction]["theme"] == classification["name"]:
                correct += 1

    return correct / total


def stem_word(text: str):
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


def score_word_by_type(word):
    tags = word.get("tags")
    if tags is not None:
        if tags[0] == "N":
            return 10
        if tags[0] == "V":
            return 2
        if tags[0] == "J":
            return 5
    
    return 1


def score_word_by_amplified_relevance(word):
    if word.get("freq", 0) > 1:
        return word.get("freq") * 2
    else:
        return 1

if __name__ == "__main__":
    main()