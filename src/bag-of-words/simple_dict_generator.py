import sys
import json
import requests
from nltk.corpus import stopwords


def main():
    print("success")


def generate_dict():
    """
    Method to generate dictionary of synonyms and related words from api(s)
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

    # setting up initial api requests for each category
    category_calls = {
        "Education": ["education"],
        "Children": ["children"],
        "Women and Girls": ["women", "girls"],
        "Animals": ["animals"],
        "Climate Change": ["climate+change", "global+warming"],
        "Democracy and Governance": ["democracy", "government"],
        "Disaster Recovery": ["disaster", "recovery"],
        "Economic Development": ["economy"],
        "Environment": ["environment"],
        "Microfinance": ["microfinance", "finance"],
        "Health": ["health"],
        "Humanitarian Assistance": ["humanitarian+assistance", "humanitarian"],
        "Human Rights": ["human", "rights", "human+rights"],
        "Sport": ["sport"],
        "Technology": ["technology"],
        "Hunger": ["hunger", "food"],
        "Arts and Culture": ["arts", "culture"],
        "LGBTQAI+": ["lesbian", "gay", "transgender", "bisexual", "queer"],
    }

    # initializing stop words to avoid parsing
    stop_words = stopwords.words("english")

    # calling api and storing data
    for category in category_calls:
        for keyword in category_calls[category]:
            r = requests.get("https://api.datamuse.com/words?ml=" + keyword)
            for word in r.json():
                if word not in stop_words:
                    category_dict[category][word.get("word")] = parse_content(
                        word, None
                    )

    # second iteration of related word searches
    first_word_batch = create_category_word_lists(category_dict)

    # calling api and finding related words to initial set of words and adding to dictionary
    for category in category_calls:
        for keyword in first_word_batch[category]:
            r = requests.get("https://api.datamuse.com/words?ml=" + keyword)
            for word in r.json():
                if word not in stop_words:
                    # if word is already present, average the two scores returned
                    if word.get("word") in category_dict[category]:
                        original_word = category_dict[category][word.get("word")]
                        category_dict[category][word.get("word")] = parse_content(
                            word, original_word
                        )
                    else:
                        category_dict[category][word.get("word")] = parse_content(
                            word, None
                        )

    # dumping data
    with open("categories.json", "w") as categories_json:
        json.dump(
            category_dict, categories_json, sort_keys=True, indent=2, ensure_ascii=False
        )


def parse_content(word, original_word):
    """
    Helper method to parse content and filter relevant data
    Args:
        word: word dictionary returned from api data
    Return:
        Dictionary of filtered parameters from word json
    """
    if (
        original_word is not None
        and word.get("score") is not None
        and original_word.get("score") is not None
    ):
        score = (word.get("score") + original_word.get("score")) / 2
    else:
        score = word.get("score")

    tags = word.get("tags")

    return {"score": score, "tags": tags}


def create_category_word_lists(categories_dict):
    """
    Converts category dictionary into an easily iterable list for efficiency
    """
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
        "LGBTQAI+": [],
    }

    # adding words to lists in categories dict
    for key in categories_dict:
        for word in categories_dict[key]:
            category_lists[key].append(word)

    return category_lists


def remove_duplicates(categories_dict):
    """
    Removes duplicate words from categories dict
    """
    for category in categories_dict:
        unique_words = set(categories_dict[category].keys())
        print("original: " + str(len(categories_dict[category])))
        print("new: " + str(len(unique_words)))


if __name__ == "__main__":
    main()
