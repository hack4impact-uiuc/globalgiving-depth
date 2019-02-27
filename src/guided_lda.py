import sys

import json
import re

import numpy as np
import guidedlda


def main():
    with open("json/" + sys.argv[1], "r") as input_file:
        input_data = json.load(input_file)

    seed_topic_list = generate_seed_topic_list(input_data)

    seed_topic_list = [['game', 'team', 'win', 'player', 'season', 'second', 'victory'],
                       ['percent', 'company', 'market', 'price',
                           'sell', 'business', 'stock', 'share'],
                       ['music', 'write', 'art', 'book', 'world', 'film'],
                       ['political', 'government', 'leader', 'official', 'state', 'country', 'american', 'case', 'law', 'police', 'charge', 'officer', 'kill', 'arrest', 'lawyer']]

    model = guidedlda.GuidedLDA(
        n_topics=5, n_iter=100, random_state=7, refresh=20)

    seed_topics = {}
    for t_id, st in enumerate(seed_topic_list):
        for word in st:
            seed_topics[word2id[word]] = t_id

    with open("json/" + sys.argv[2], "a") as output_file:
        output_file.write("]}")

    input_file.close()
    output_file.close()
    return


def generate_seed_topic_list(data):
    for project in data["projects"]:
        topic = project["theme"][0]["id"]


if __name__ == "__main__":
    main()
