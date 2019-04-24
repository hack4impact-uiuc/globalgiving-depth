import json
import random
import re

import matplotlib.pyplot as plt
import numpy
import spacy
from gensim.parsing.preprocessing import remove_stopwords
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


def get_words(text):
    """
    Input:
        text: a string of text which needs to be processed
    Output:
        string of all words extracted from the input string
    """
    text = text.lower()
    wordlist = text.split()
    clean_list = []
    for word in wordlist:
        # only get words (no digits)
        if not word.isdigit() and not re.match(r"[^\w]", word):
            clean_list.append(word)
    return " ".join(clean_list)


class WordVectors:
    """
    Represent documents as word vectors
    """

    dataset = []  # list of dictionaries with "summary" and "_id" fields
    samples = 500  # just used for visualization; we don't want to dump all points
    # onto the plot, as they will overlap and overwhelm

    word_vectors = []
    word_embedding = None  # word embedding model; pretrained from spacy.io

    X = None
    explained_variance = None

    def __init__(self, data_file: str, samples=500):
        """
        Construct WordVectors object and read in the dataset.
        data_file: string of path to data file
        samples: integral number of datapoints to visualize
        """
        self.samples = samples

        with open(data_file, "r") as df:
            json.dump(self.dataset, df)
        # shuffle the dataset to better train vectors
        random.shuffle(self.dataset)

        print("loading word embedding model . . . ", end="")
        self.word_embedding = spacy.load("en_core_web_lg")
        print("done")

    def get_word_vectors(self):
        """
        Creates naive document vectors by summing all word
        vectors for each document and normalizes them.
        Returns a list of naive document vectors.
        """
        self.word_vectors = [
            self.word_embedding(remove_stopwords(get_words(doc["summary"]))).vector
            for doc in self.dataset[: self.samples - 1]
        ]
        return self.word_vectors

    def reduce_word_vectors(self, vectors):
        """
        Perform dimensionality reduction on feature matrix using PCA.
        vectors: list of word vectors
        Returns:
            X: reduced feature matrix, numpy.ndarray Nx2
            explained_variance: percentage increase in explained variance due
                to each principal component
        """
        X = numpy.vstack(vectors)
        scaler = StandardScaler()
        scaler.fit_transform(X)
        explained_variance = PCA().fit(X).explained_variance_ratio_
        self.explained_variance = explained_variance
        pca = PCA(n_components=2)
        pca.fit_transform(X)
        self.X = X
        return X, explained_variance

    def visualize(self, vector_labels):
        """
        Plots the reduced matrix of document embeddings using MatPlotLib.
        Plotted documents are colored according to given labels.
        Also plots a graph of explained variance vs. dimensions
        Returns:
            vector_labels: list of labels for each document
        """
        labels = numpy.array(vector_labels)
        fig, ax = plt.subplots(2)
        labelset = set(labels)
        for label in labelset:
            ax[0].plot(
                self.X[labels == label, 0],
                self.X[labels == label, 1],
                label=label,
                marker=".",
                linestyle="",
            )
        ax[0].set_title("{} NGO Summaries".format(self.samples))
        ax[0].set_xlabel("Principal Component 1")
        box = ax[0].get_position()
        ax[0].set_position([box.x0, box.y0, box.width * 0.75, box.height])
        ax[0].legend(loc="center left", bbox_to_anchor=(1, 0.5))
        ax[0].set_ylabel("Principal Component 2")
        ax[1].plot(  # plot the cumulative sums of explained variance
            [
                numpy.sum(self.explained_variance[:n])
                for n in range(len(self.explained_variance))
            ]
        )
        ax[1].set_title("Explained Variance")
        ax[1].set_xlabel("Number of Principal Components")
        ax[1].set_ylabel("Total Variance Ratio")
        fig.set_size_inches(12, 12)
