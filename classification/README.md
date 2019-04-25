# NGO Classification

## Summary
Files in this module are concerned with classifying NGOs. There are two major classifiers that show reasonable accuracy on classifying NGOs:
* Stochastic Gradient Descent (SGD)
* Bag of Words (BOW)

Each has its own strengths and weaknesses, blah blah blah

## Stochastic Gradient Descent
Something something

## Bag of Words Classifier
Bag of words is a statistical method of classifying documents based off the frequency and relevance of words in a document's text. In this implementation, given a organization's website text, using bag of words algorithm, the classifer will predict the themes of the organization.

Bag of words works in two steps:
1. Generate a dictionary of words with tf-idf scores for each category for the classifier to reference
2. Use the bag of words algorithm to classify organizations by counting/scoring the words contained in the website's text. The highest scored categories are the predicted classifications given to the organization

## What is TF-IDF?
Tf-idf is a weighting scheme that assigns each term in a document a weight based on its term frequency (tf) and inverse document frequency (idf). Tf-idf is especially valuable in the bag of words algorithm to increase the accuracy of its predictions by scoring words in an organization's text with a weighted score accounting for its relevance to each category, rather than simply summing the number of words that appear in each category.

* For example, the word "peacock" is more rare compared to the word "girl" across all categories. This rarity is accounted for by the "idf" in tf-idf scoring to make clear that it is a stronger indicator of a specific category, which in this case would be animals. 
* The word "peacock" would also be more common in websites with the theme "animal", rather than "economic development", accounted for by the "tf" in tf-idf scoring to indicate that multiple occurences of the same word in a given category will incline a prediction of that category.

## Important note:
In this current implementation, bag of words predicts the 5 highest scored categories to give a broad understanding of the organizations mission, as well as the highest f1 score. This number is 100% arbitrary and can be changed, more details can be seen on the wiki [page](https://github.com/hack4impact-uiuc/globalgiving-depth/wiki/Bag-of-Words-(BOW)-Classifier)