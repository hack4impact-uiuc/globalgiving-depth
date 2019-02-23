import sys
import json

from ngram_base import get_words, get_tfidf_values

def main():
    with open(sys.argv[1], "r") as input_file:  # ../visible-text/scraping_data.json
        input_data = json.load(input_file)
    data = {}
    data["projects"] = []

    for p in input_data["projects"]:
        project = {}
        project["url"] = p["url"]
        project["themes"] = []
        if len(p["text"]) != 0:
            project["text"] = p["text"]
            words = get_words(project["text"])
        data["projects"].append(project)

    tfidf_values, features = get_tfidf_values(
        x["text"] for x in data["projects"]
    )
    features_set = set(features)

    with open("training_scores.json", "r") as training_data_file:
        training_data = json.load(training_data_file)
    training_features = training_data["features"]
    training_indices = []
    for i in range(len(training_features)):
        if training_features[i] in features_set:
            training_indices.append(i)
    for project in data["projects"]:
        project.pop("text", None)
        for index in training_indices:
            for training_project in training_data["projects"]:
                for training_theme in training_project["themes"]:
                    if training_theme not in project["themes"]:
                        project["themes"].append(training_theme)
                    for theme in project["themes"]:
                        if "confidence" in theme:
                            theme["confidence"] += training_project["tfidf_values"][index]
                        else:
                            theme["confidence"] = 0
    # take top "m" most important n-grams, search testing data to see if present and make a guess?
    # find common n-grams, add up values, rank

    with open(sys.argv[2], "w") as output_file:  # classified_data.json
        json.dump(data, output_file)

if __name__ == "__main__":
    main()
