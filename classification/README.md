# NGO Classification

## Summary
Files in this module are concerned with classifying NGOs. There are two major classifiers that show reasonable accuracy on classifying NGOs:
* Stochastic Gradient Descent (SGD)
* Bag of Words (BOW)

## Stochastic Gradient Descent
[Stochastic gradient descent](https://en.wikipedia.org/wiki/Stochastic_gradient_descent) is a method of optimization that can be used to train models such as linear support vector machines (SVMSs) and logistic regression models.  We are using scikit-learn’s stochastic gradient descent classifier with log loss (giving us a logistic regression model) as a way to classify an NGO based off of text from an NGO’s website.  In order to label an NGO as multiple themes (multi-label classification), we wrap the `SGDClassifier` in a `OneVsRestClassifier`.

Here is an example of how to use this classifier:
```
train_data, test_data = train_test_split(dataset, test_size=0.2, random_state=42)
formatted_train_data = set_up_training_data(train_data, "formatted_train.json")
classifier = NGO_SGDClassifier()
classifier.fit(formatted_train_data)
probabilities, predictions = classifier.predict(test_data)
```
In this case, `dataset` should be of the format specified in the [wiki](https://github.com/hack4impact-uiuc/globalgiving-depth/wiki/Stochastic-Gradient-Descent-(SGD)-Classifier#file-structures).  For more information on the overall implementation and use of this classifier, check out the [wiki page](https://github.com/hack4impact-uiuc/globalgiving-depth/wiki/Stochastic-Gradient-Descent-(SGD)-Classifier)!

## Bag of Words Classifier
Bag of words is a statistical method of classifying documents based off the frequency and relevance of words in a document's text. In this implementation, given a organization's website text, using bag of words algorithm, the classifier will predict the themes of the organization.

Bag of words works in two steps:
1. Generate a dictionary of words with tf-idf scores for each category for the classifier to reference
2. Use the bag of words algorithm to classify organizations by counting/scoring the words contained in the website's text. The highest scored categories are the predicted classifications given to the organization

## What is TF-IDF?
Tf-idf is a weighting scheme that assigns each term in a document a weight based on its term frequency (tf) and inverse document frequency (idf). Tf-idf is especially valuable in the bag of words algorithm to increase the accuracy of its predictions by scoring words in an organization's text with a weighted score accounting for its relevance to each category, rather than simply summing the number of words that appear in each category.

* For example, the word "peacock" is more rare compared to the word "girl" across all categories. This rarity is accounted for by the "idf" in tf-idf scoring to make clear that it is a stronger indicator of a specific category, which in this case would be animals.
* The word "peacock" would also be more common in websites with the theme "animal", rather than "economic development", accounted for by the "tf" in tf-idf scoring to indicate that multiple occurences of the same word in a given category will incline a prediction of that category.

## Important note:
In this current implementation, bag of words predicts the 5 highest scored categories to give a broad understanding of the organizations mission, as well as the highest f1 score. This number is 100% arbitrary and can be changed, more details can be seen on the wiki [page](https://github.com/hack4impact-uiuc/globalgiving-depth/wiki/Bag-of-Words-(BOW)-Classifier)

## Input files
### Training json file
The training file contains training data for the classifiers, pulled directly from the Global Giving API. In the training file, data is primarily stored in lists, with each index corresponding to a specific organization across all of them. More specific details of the formatting can be found at [here](https://github.com/hack4impact-uiuc/globalgiving-depth/wiki/Bag-of-Words-(BOW)-Classifier)

### Dictionary json file (bag of words specific)
This dictionary contains the words for each category and their respective tf-idf scores. More specific details of the formatting can be found at [here](https://github.com/hack4impact-uiuc/globalgiving-depth/wiki/Bag-of-Words-(BOW)-Classifier)

## Output files
### Predictions json file
This file contains the predictions made by the bag of words classifier. Predictions are stored as a list of lists of themes of each organization, with a 1 indicating a predicted theme, corresponding to the index specified by training.json's themes map. More specific details of the formatting can be found [here](https://github.com/hack4impact-uiuc/globalgiving-depth/wiki/Bag-of-Words-(BOW)-Classifier)
