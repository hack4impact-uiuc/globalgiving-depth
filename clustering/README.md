# Clustering

## Summary

Clustering NGOs provides us with understanding of ....

## K-Means

using document embeddings, ....

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
### EM
something something
### GuidedLDA

We attempted to design a Semi-Supervised LDA algorithm based on an article published online, but were unable to get the code to run. Here is the [article](https://medium.freecodecamp.org/how-we-changed-unsupervised-lda-to-semi-supervised-guidedlda-e36a95f3a164) for reference.
