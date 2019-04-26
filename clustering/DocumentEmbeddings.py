import json
import random
import re
from pprint import pprint
import numpy
import gensim
from gensim.parsing.preprocessing import remove_stopwords, preprocess_string
from gensim.models import Doc2Vec
from sklearn.cluster import KMeans

LabeledSentence = gensim.models.doc2vec.TaggedDocument


def get_words(text):
    """
    Parameters:
        text: a string of text which needs to be processed
    Returns:
        string of all words extracted from the input string
    """
    text = text.lower()
    wordlist = text.split()
    clean_list = []
    for word in wordlist:
        # only get words (no digits)
        if re.match(r"^[a-z]+$", word):
            clean_list.append(word)
    return " ".join(clean_list)


class DocumentEmbeddings:
    """
    Represent documents as vectors with embedded meanings. The document
    embedding model is trained on the input data. Part of training a document
    embedding model involves training a word embedding model; this is used in
    the analysis of clustering.

    Methods:
    __init__(self, dataset)
    train(self, ...) (see the function for a description of each parameter)
    cluster(self, n_clusters=14)
    get_centroids(self)
    print_centroids(self, n_closest=10)
    """

    documents = []  # list of processed documents with "summary" and "theme" fields

    model = None  # Doc2Vec model

    kmeans_model = None  # kmeans model
    labels = []  # cluster labels from kmeans
    themes = []  # themes assigned from records

    def __init__(self, data_file):
        """
        Construct DocumentEmeddings object and read in the dataset.
        data_file: string of path to data file
        """

        with open(data_file, "r") as df:
            json.dump(self.dataset, df)
        # shuffle the dataset to better train vectors
        random.shuffle(self.dataset)

        documents = []
        for uid, doc in enumerate(self.dataset):
            document = preprocess_string(remove_stopwords(get_words(doc["summary"])))
            documents.append(LabeledSentence(document, [uid]))
        self.documents = documents

        self.themes = [doc["theme"] for doc in self.documents]

    def train(
        self,
        vector_size=100,
        window=10,
        min_count=500,
        workers=1000,
        dm=1,
        alpha=0.025,
        min_alpha=0.001,
        epochs=1,
        start_alpha=0.002,
        end_alpha=-0.016,
    ):
        """
        Train documents with Doc2Vec
        Parameters:
            vector_size: int - size of document vectors generated
            window: int - maximum distance between the current and predicted
                word within a sentence
            min_count: int - ignores all words with total frequency lower than this
            workers: int - uses this many worker threads to train the model
            dm: {1,0} defines the training algorithm. If dm=1, uses 'distributed
                memory (PV-DM); otherwise uses 'distributed bag of words' (PV-DBOW)
            alpha: float - initial learning rate
            min_alpha: float - learning rate linearly drops to min_alpha
            epochs: int - number of iterations (epochs) over the corpus
            start_alpha: float - initial learning rate (replaces initial alpha
                in constructor)
            end_alpha: float - final learning rate; drops linearly from start_alpha.
                replaces min_alpha from constructor
        Returns:
          model: Doc2Vec model
        """
        model = Doc2Vec(
            self.documents,
            vector_size=vector_size,
            window=window,
            min_count=min_count,
            workers=workers,
            dm=dm,
            alpha=alpha,
            min_alpha=min_alpha,
        )
        model.train(
            self.documents,
            total_examples=model.corpus_count,
            epochs=epochs,
            start_alpha=start_alpha,
            end_alpha=-end_alpha,
        )
        self.model = model
        return model

    def cluster(self, n_clusters=14):
        """
        Cluster document vectors using k-means
        n_clusters: int - number of clusters

        Return:
          kmeans_model: KMeans model
        """
        kmeans_model = KMeans(n_clusters=n_clusters)
        kmeans_model.fit(self.model.docvecs.vectors_docs)
        labels = kmeans_model.labels_.tolist()
        kmeans_model.fit_predict(self.model.docvecs.vectors_docs)
        self.kmeans_model = kmeans_model
        self.labels = labels
        return kmeans_model

    def get_centroids(self):
        """
        Get centroids (center of each cluster) from the KMeans model
        Return:
          centroids
        """
        centroids = self.kmeans_model.cluster_centers_
        return centroids

    def print_centroids(self, n_closest=10):
        """
        Print n words closest to each centroid from the KMeans model. The words
        are obtained using the word embedding model.
        Prints: [[word, similarity (as a float)], ... ]

        Parameters:
            n_closest: int - closest n words to print
        """
        pprint(
            [
                self.model.wv.similar_by_vector(centroid, topn=n_closest)
                for centroid in self.kmeans_model.cluster_centers_
            ]
        )

    def visualize(self):
        """
        Plots the reduced matrix of document embeddings using MatPlotLib.
        Plotted documents are colored according to given labels.
        Also plots a graph of explained variance vs. dimensions
        Returns:
            (fig, ax): the figure object and axis object which describes the
                figure. This is returned so it can be plotted or saved.
        """
        labels = numpy.array(self.themes)
        fig, ax = plt.subplots(2)
        labelset = set(labels)
        for label in labelset:
            ax[0].plot(
                # plot only the labels which match the current label being plotted
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
        return fig, ax
