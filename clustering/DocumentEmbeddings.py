import json
import random
import pandas as pd
import gensim

from gensim.parsing.preprocessing import remove_stopwords, preprocess_string
from gensim.models import Doc2Vec
from sklean.cluster import KMeans
from pprint import pprint

LabeledSentence = gensim.models.doc2vec.TaggedDocument


def get_words(text):
    """
    Source: <@FIXME:/somewhere/>
    """
    text = text.lower()
    wordlist = text.split()
    clean_list = []
    for word in wordlist:
        # only get words (no digits)
        if not word.isdigit() and re.match(r"^[a-z]+$", word):
            clean_list.append(word)
    return " ".join(clean_list)


class DocumentEmbeddings:
    """
    @FIXME: class to represent document vectors
    """

    dataset = []  # list of dictionaries with "summary" field
    documents = []  # list of processed documents to train on

    model = None  # Doc2Vec model

    kmeans_model = None  # kmeans model
    labels = []  # cluster labels from kmeans

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
        id = 0
        for doc in self.dataset:
            document = preprocess_string(
                remove_stopwords(get_words(doc["summary"])))
            documents.append(LabeledSentence(document, [id]))
            id += 1
        self.documents = documents

    def train(self, vector_size=100, window=10, min_count=500,
              workers=1000, dm=1, alpha=0.025, min_alpha=0.001,
              epochs=1, start_alpha=0.002, end_alpha=-0.016):
        """
        Train documents with Doc2Vec
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

        Return:
          model: Doc2Vec model
        """
        model = Doc2Vec(self.documents, vector_size=vector_size, window=window,
                        min_count=min_count, workers=workers, dm=dm, alpha=alpha, min_alpha=min_alpha)
        model.train(self.documents, total_examples=model.corpus_count,
                    epochs=epochs, start_alpha=start_alpha, end_alpha=-end_alpha)
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
        X = kmeans_model.fit(self.model.docvecs.vectors_docs)
        labels=kmeans_model.labels_.tolist()
        l = kmeans_model.fit_predict(model.docvecs.vectors_docs)
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

      def print_centroids(self, topn):
        """
        Print top n words from each centroid from the KMeans model
        Prints (word, similarity (as a float))
        topn: int - top n words to print
        """
        centroids = self.kmeans_model.cluster_centers_
        pprint([model.wv.similar_by_vector(centroid, topn=10) for centroid in centroids])


