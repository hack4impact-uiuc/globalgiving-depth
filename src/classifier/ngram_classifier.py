import sys
import json

import pandas as pd

from ngram_base import populate_dict, get_tfidf_values


def main():
    with open(sys.argv[1], "r") as input_file:  # ../visible-text/scraping_data.json
        input_data = json.load(input_file)

    data = populate_dict(input_data)

    tfidf_values, features = get_tfidf_values(x["words"] for x in data["projects"])

    for i in range(len(tfidf_values)):
        data["projects"][i]["tfidf_values"] = []
        data["projects"][i]["features"] = []
        for j in range(len(tfidf_values[i])):
            data["projects"][i]["tfidf_values"].append(tfidf_values[i][j])
            data["projects"][i]["features"].append(features[j])
        data["projects"][i].pop("words", None)

    classifying_urls = []
    classifying_values = []
    classifying_features = []
    for project in data["projects"]:
        classifying_urls += [project["url"]] * len(project["tfidf_values"])
        classifying_values += [value for value in project["tfidf_values"]]
        classifying_features += [feature for feature in project["features"]]

    classifying_url_tfidf_feature_df = pd.DataFrame(
        {
            "url": classifying_urls,
            "tfidf_value": classifying_values,
            "feature": classifying_features,
        }
    )

    with open("training_scores.json", "r") as training_data_file:
        training_data = json.load(training_data_file)

    training_urls = []
    training_themes = []
    training_values = []
    training_features = []
    for project in training_data["projects"]:
        training_urls += (
            [project["url"]] * len(project["tfidf_values"]) * len(project["themes"])
        )
        training_themes += [theme["id"] for theme in project["themes"]] * len(
            project["tfidf_values"]
        )
        training_values += [value for value in project["tfidf_values"]] * len(
            project["themes"]
        )
        training_features += [feature for feature in project["features"]] * len(
            project["themes"]
        )

    training_url_tfidf_feature_df = pd.DataFrame(
        {
            "url": training_urls,
            "theme": training_themes,
            "tfidf_value": training_values,
            "feature": training_features,
        }
    )

    # get predicted values... naive bayes?

    with open(sys.argv[2], "w") as output_file:  # classified_data.json
        json.dump(data, output_file)


if __name__ == "__main__":
    main()
