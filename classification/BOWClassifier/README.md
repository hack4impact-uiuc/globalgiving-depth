# Bag of Words Classifier
Bag of words is a statistical method of classifying documents based off the frequency and relevance of words in a document's text. In this implementation, bag of words is used to classify nonprofit organizations using their website's text.

Bag of words works in two steps:
1. Generate a dictionary of words with tf-idf scores for each category for the classifier to reference
2. Use the bag of words algorithm to classify organizations by counting/scoring the words contained in the website's text. The highest scored categories are the predicted classifications given to the organization

- concepts: what is tf-idf?
- input, output
- good to know