import sys
import json

from ngram_base import get_words, get_tfidf_values

def main():
    with open(sys.argv[1], "r") as input_file:  # small_training_data.json
        input_data = json.load(input_file)

    data = {}
    data["projects"] = []

    text = []
    for p in input_data["projects"]:
        project = {}
        project["url"] = p["url"]
        if len(p["text"]) != 0:
            project["text"] = p["text"]
            words = get_words(project["text"])
            text.append(words)
        project["themes"] = p["themes"]
        data["projects"].append(project)

    tfidf_values, features = get_tfidf_values(
        x["text"] for x in data["projects"]
    )
    data["features"] = features
    for i in range(len(tfidf_values)):
        data["projects"][i]["tfidf_values"] = list(tfidf_values[i])
        data["projects"][i].pop("text", None)
    # take top "m" most important n-grams, search testing data to see if present and make a guess?
    # find common n-grams, add up values, rank

    with open(sys.argv[2], "w") as output_file:  # training_scores.json
        json.dump(data, output_file)

if __name__ == "__main__":
    main()