import sys
import json

from ngram_base import populate_dict, get_tfidf_values

def main():
    with open(sys.argv[1], "r") as input_file:  # small_training_data.json
        input_data = json.load(input_file)

    data = populate_dict(input_data)

    tfidf_values, features = get_tfidf_values(
        x["words"] for x in data["projects"]
    )

    for i in range(len(tfidf_values)):
        data["projects"][i]["tfidf_values"] = []
        data["projects"][i]["features"] = []
        for j in range(len(tfidf_values[i])):
            data["projects"][i]["tfidf_values"].append(tfidf_values[i][j])
            data["projects"][i]["features"].append(features[j])
        data["projects"][i].pop("words", None)

    # projects: [
        # {
        #     url:
        #     themes: [{id: , name: }]
        #     tfidf_values: []
        #     features: []
        # }
    # ]
    with open(sys.argv[2], "w") as output_file:  # training_scores.json
        json.dump(data, output_file)

if __name__ == "__main__":
    main()