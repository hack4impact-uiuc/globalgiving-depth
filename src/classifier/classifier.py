import requests
import json
import nltk

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
    with open("test.json") as categories:
        classify_org(json.load(categories))
    print("classification success")

    # testing classification accuracy
    with open("reformatted_orgs.json") as classifications:
        with open("classifications_big.json") as predictions:
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
    with open("test.json") as scraping_data:
        websites = json.load(scraping_data)
        
    classifications = {}
    # tokenizing scraped website data into words
    for i in range(len(websites)):
        website = websites[i]
        if (website.get("text") is None):
            continue

        website["tokens"] = nltk.word_tokenize(website.get("text"))

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

        # fetching category word lists
        category_words = create_category_word_lists(category_data)

        # calculating sum of relevant words in each category
        for word in website["tokens"]:
            for category in category_words:
                if word in category_words[category]:
                    category_scores[category] += 1 #score_word(word, category_data[category][word])

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

    # dumping data
    with open("classifications_LDA.json", "w") as classifications_json:
        json.dump(classifications, classifications_json, sort_keys=True, indent=2, ensure_ascii=False)    
        
    # returning concluded classification
    return classification

def test_classification_accuracy(predictions, classifications):
    correct = 0
    total = len(predictions)

    for prediction in predictions:
        for classification in classifications[prediction]["themes"]:
            if predictions[prediction]["theme"] == classification["name"]:
                correct += 1

    return correct / total


def reformat_orgs():
    with open("../get-orgs/orgs.json") as orgs:
        orgs_json = json.load(orgs)["projects"]
        reformatted_orgs = {}
        for orgs in orgs_json:
            reformatted_orgs[orgs.get("name")] = parse_orgs(orgs)

        with open("reformatted_orgs.json", "w") as r_orgs_json:
            json.dump(reformatted_orgs, r_orgs_json, sort_keys=True, indent=2, ensure_ascii=False)


def create_category_word_lists(categories_dict):
    '''
    Converts category dictionary into an easily iterable list for efficiency
    '''
    category_lists = {
        "Education": [],
        "Children": [],
        "Women and Girls": [],
        "Animals": [],
        "Climate Change": [],
        "Democracy and Governance": [], 
        "Disaster Recovery": [],
        "Economic Development": [],
        "Environment": [],
        "Microfinance": [],
        "Health": [],
        "Humanitarian Assistance": [],
        "Human Rights": [],
        "Sport": [],
        "Technology": [],
        "Hunger": [],
        "Arts and Culture": [],
        "LGBTQAI+": []
    }

    # adding words to lists in categories dict
    for key in categories_dict:
        for word in categories_dict[key]:
            category_lists[key].append(word)
    
    return category_lists

def score_word(word, reference):
    tags = reference.get("tags")
    if tags is not None:
        for tag in reference["tags"]:
            if tag == "n":
                return 10
            if tag == "adj":
                return 2
            if tag == "v":
                return 5
    
    return 1

def parse_orgs(org):
    new_org = {}
    new_org["themes"] = org.get("themes")

    return new_org

if __name__ == "__main__":
    main()