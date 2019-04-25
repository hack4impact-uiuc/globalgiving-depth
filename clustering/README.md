# Clustering

## Summary

Clustering NGOs provides us with understanding of ....

## LDA

The NGOUnguidedLDA Class allows users to form an LDA Model with clusters representing the variety of topics within a dataset of NGO Projects or Organizations. 

The LDA Model can then be used to “assign” new projects to a particular cluster that roughly describes the purpose of that project or organization.

The NGOUnguidedLDA Class can be found in [UnguidedLDA.py](UnguidedLDA.py); an example of its usage can be found in [lda_main.py](lda_main.py).
It uses [project_summaries.json](project_summaries.json) for both training and testing data.
In general, this unguided LDA implementation is more effective when “clean” text is used (as opposed to scraped data).

See the [Wiki Page](https://github.com/hack4impact-uiuc/globalgiving-depth/wiki/Latent-Dirichlet-Allocation-(LDA)) for more information on input formatting, code documentation, and conclusions drawn.

Note: 
It may be necessary to use the NLTK Downloader to obtain “stopwords,” “WordNetLemmatizer,” and other resources from the Natural Language Tool Kit. 
If errors occur due to the above issue, your terminal should provide information on the NLTK Downloader.

## Word Vectors

The WordVectors Class allows users to represent documents as word vectors summed together. Users can then visualize these naive document vectors with first reducing the dimensionality with PCA and graphing them with Matplotlib.

The WordVectors Class can be found in [WordVectors.py](WordVectors.py). The documents are opened from a dataset of project summaries and themes; we used [project_summaries.json](project_summaries.json). Any dataset of many documents consisting of a "summary" and "theme" field can be used.

See the [Wiki Page](https://github.com/hack4impact-uiuc/globalgiving-depth/wiki/Document-Embeddings) for information.

## Document Vectors and K-Means

The DocumentEmbeddings Class allows users to create document vectors using Gensim's Doc2Vec model. Users can then cluster these document vectors using K-Means, reduce clusters with PCA, and visualize clusters with Matplotlib.

The DocumentEmbeddings Class can be found in [DocumentEmbeddings.py](DocumentEmbeddings.py). The documents are opened from a dataset of project summaries; we used [project_summaries.json](project_summaries.json). Any dataset of many documents consisting of a "summary" text field can be used.

See the [Wiki Page](https://github.com/hack4impact-uiuc/globalgiving-depth/wiki/Document-Embeddings) for information.

## Previous Attempts

### GuidedLDA

We attempted to design a Semi-Supervised LDA algorithm based on an article published online, but were unable to get the code to run. Here is the [article](https://medium.freecodecamp.org/how-we-changed-unsupervised-lda-to-semi-supervised-guidedlda-e36a95f3a164) for reference.
