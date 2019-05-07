import sys
import json
import nltk
import gensim
import langdetect

from collections import Counter
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from gensim.utils import simple_preprocess
from gensim import corpora, models
from langdetect import detect


def preprocess_text(text: str) -> list:
    """Tokenize, remove stopwords, and stem words."""
    processed_text = []
    stop_words = set(stopwords.words("english"))
    wnl = WordNetLemmatizer()
    for token in gensim.utils.simple_preprocess(text):
        if token not in stop_words:
            # Lemmatizer leaves input word unchanged if not found in WordNet
            processed_text.append(wnl.lemmatize(token))
    return processed_text


class NGOUnguidedLDA:
    """
    This is a class for developing and training an Unguided LDA Model.

    Methods:
    __init__(self, training_data: list)
    process_projects(self)
    create_training_dict(self, max_proportion: int, num_keep: int)
    create_lda_model(self, num_topics: int, num_workers: int, tf_idf: bool)
    print_lda_topics(self)
    test_lda_model(self, testing_data: list, top_topics=3, words_per_topic=5)
    """

    training_data = []
    testing_data = None
    processed_projects = []
    training_dict = {}
    word_corpus = []
    lda_model = None

    def __init__(self, training_data: list):
        """
        The constructor for the UnguidedLDA Class.

        Keyword Arguments:
        training_data -- List with dictionaries containing NGO project information. Used to train LDA Model.
        """
        self.training_data = training_data

    def process_projects(self) -> list:
        """
        Return list with pre-processed text from each project.

        May need to swap "summary" key for "text" depending on format of input JSON.

        Return Value:
        self.processed_projects -- List of processed (tokenized, stemmed, stopwords removed) text for each project.
        """
        for project_dict in self.training_data:
            project_text = project_dict["summary"]
            if project_text and detect(project_text) == "en":
                processed_text = preprocess_text(project_text)
                self.processed_projects.append(processed_text)
        return self.processed_projects

    def create_training_dict(self, max_proportion: int, num_keep: int) -> dict:
        """
        Creates dictionary containing the most significant words appearing in the training data.

        Note that dictionary keys are token ID's, values are the words/tokens themselves.

        Keyword Arguments:
        num_keep -- The number of top (most common) words stored in dictionary.
        max_proportion -- The maximum proportion of the training data a word can appear in.

        Return Value:
        self.training_dict -- Dictionary with top words (words meeting requirements set by keyword args).
        """
        assert self.processed_projects

        self.training_dict = gensim.corpora.Dictionary(self.processed_projects)
        self.training_dict.filter_extremes(no_above=max_proportion, keep_n=num_keep)
        return self.training_dict

    def create_lda_model(self, num_topics: int, num_workers: int, tf_idf: bool):
        """
        Builds Corpus, then creates and trains LDA Model.

        Default Corpus (Bag of Words) contains a list of words found in training_dict per project.
        Example Project List: [(token_id_1, count), (token_id_2, count)]

        For TF-IDF Corpus, set tf_idf to True.
        Benefits of using TF-IDF include providing weight to uncommon words in overall corpus,
        increasing the word's significance for classifying its project.

        Keyword Arguments:
        num_topics -- The number of topics/clusters for the LDA Model.
        num_workers -- The number of additional processes to use for parallelization.
        tf_idf -- If true, transform corpus into TF-IDF representation.

        Return Value:
        self.lda_model -- The LDA Model, with num_topics clusters.
        """
        assert self.processed_projects
        assert self.training_dict

        # Bag of Words Corpus
        corpus = [
            self.training_dict.doc2bow(project) for project in self.processed_projects
        ]
        if tf_idf:
            # Create tf-idf model object, then use to transform corpus
            tfidf = models.TfidfModel(corpus)
            corpus = tfidf[corpus]
        self.word_corpus = corpus

        self.lda_model = gensim.models.LdaMulticore(
            corpus,
            num_topics=num_topics,
            id2word=self.training_dict,
            passes=2,
            workers=num_workers,
        )
        return self.lda_model

    def print_lda_topics(self):
        """Print out top words for each topic in the LDA Model."""
        assert self.lda_model

        for idx, topic in self.lda_model.print_topics(-1):
            print("Topic: {} \nWords: {}".format(idx, topic))

    def test_lda_model(self, testing_data: list, top_topics=3, words_per_topic=5):
        """
        Tests LDA Model by printing out most likely topics for each testing project.

        "Scores" indicate probability of project being part of that topic.

        Keyword Arguments:
        testing_data -- List with dictionaries containing NGO project information.
        top_topics -- The number of topics to display, ordered by probability (default 3).
        words_per_topic -- The number of words to display for each topic (default 5).
        """
        assert self.lda_model
        assert self.training_dict

        self.testing_data = testing_data
        for project in testing_data:
            project_theme = project["theme"]
            # May need to swap "summary" key for "text" depending on format of input JSON
            project_text = project["summary"]
            # Double check language, as langdetect is nondeterministic
            if project_theme and project_text and detect(project_text) == "en":
                print(
                    "Project ID: " + str(project["_id"]) + ", Theme: " + project_theme
                )
                bow_list = self.training_dict.doc2bow(preprocess_text(project_text))
                for index, score in sorted(
                    self.lda_model[bow_list], key=lambda tup: -1 * tup[1]
                )[:top_topics]:
                    print(
                        "Score: {}\t Topic: {}".format(
                            score, self.lda_model.print_topic(index, words_per_topic)
                        )
                    )
