# Clustering

## Summary

Clustering NGOs provides us with understanding of ....

## K-Means

K-Means clustering is an unsupervised algorithm that allows us to take a dataset and make inferences as to the similarities between documents. 

In our specific implementation, we used project summaries, given to us by GlobalGiving, as documents in our K-Means clustering algorithm. From those clusters, we are then able to visualize what projects are most similar to each other. Additionally, we used K-Means in conjunction with document vectors (from Doc2Vec) where the project summaries are the documents.

The goals is to then label these clusters and use them as a basis to compare new projects or non-profit organizations that have yet to be classified.

The DocumentEmbeddings class where we used K-Means clustering can be found in _______.

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

## Previous Attempts

### GuidedLDA

We attempted to design a Semi-Supervised LDA algorithm based on an article published online, but were unable to get the code to run. Here is the [article](https://medium.freecodecamp.org/how-we-changed-unsupervised-lda-to-semi-supervised-guidedlda-e36a95f3a164) for reference.
