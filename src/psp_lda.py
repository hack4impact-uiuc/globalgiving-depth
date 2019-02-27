import sys
import json
from collections import Counter

# Make sure to Install NLTK and Gensim, download stopwords
import nltk
import gensim
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# from nltk.stem.snowball import SnowballStemmer
from gensim.utils import simple_preprocess


def main():
    with open(sys.argv[1], "r") as input_file:
        input_data = json.load(input_file)

    assert len(input_data["projects"]) > 0
    processed_projects = []
    for project_dict in input_data["projects"]:
        if project_dict["text"]:
            processed_text = preprocess_text(project_dict["text"])
            processed_projects.append(processed_text)

    corpus_dict = create_corpus_dict(processed_projects, 0.6, 10000)
    lda_model = create_lda_model(corpus_dict, processed_projects, 10)
    for idx, topic in lda_model.print_topics(-1):
        print("Topic: {} \nWords: {}".format(idx, topic))

    # EVERYTHING HERE IS TEMPORARY (note that below lines will break if bad input)
    # Temporary random test for now on a random org
    # Once more scraped data, we can test on NEW/UNSEEN orgs
    random_org = input_data["projects"][8]
    test_lda_model(corpus_dict, lda_model, random_org["name"], random_org["text"])
    # Later, once I know for sure if this works well given more data for the LDA model,
    # I will output all results into .txt or .JSON files for further (manual?) classification


def create_corpus_dict(processed_projects: list, max_proportion, num_keep):
    """
    Once we have our list of processed text for each project,
    create dictionary containing number of times each word appeard in overall corpus.
    Keys will be token ID's, values will be the words themselves.

    Filter out the extremes:
    1) Should be in no more than "max proportion" of the overall corpus
    2) Keep only the "num_keep" most common words
    """
    corpus_dict = gensim.corpora.Dictionary(processed_projects)
    corpus_dict.filter_extremes(no_above=max_proportion, keep_n=num_keep)
    return corpus_dict


def create_lda_model(corpus_dict, processed_projects: list, num_topics):
    """
    1) Bow Corpus: For each project, create a list with the "good" words (see corpus_dict)
    present and their count. Words are represented by token_id (see corpus_dict).
    Example Project List: [(some_token_id_1, count), (some_token_id_1, count), etc.]

    2) LDA Model: Create/Train LDA Model, which will use the projects in the Bow Corpus to
    create "num_topics" topics which represent the variety of projects.
    """
    bow_corpus = [corpus_dict.doc2bow(project) for project in processed_projects]
    lda_model = gensim.models.LdaMulticore(
        bow_corpus, num_topics=num_topics, id2word=corpus_dict, passes=2, workers=2
    )
    return lda_model


def test_lda_model(corpus_dict, lda_model, project_name, project_text):
    """
    Tests the LDA Model by giving it a new project list, which is matched to LDA's topics.
    "Scores" indicate which topic matches new project best.
    """
    bow_list = corpus_dict.doc2bow(preprocess_text(project_text))
    print("Testing LDA model on " + project_name)
    for index, score in sorted(lda_model[bow_list], key=lambda tup: -1 * tup[1]):
        print("Score: {}\t Topic: {}".format(score, lda_model.print_topic(index, 5)))


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
        if token not in stop_words:
            processed_text.append(stem_word(token))
    return processed_text


if __name__ == "__main__":
    main()
