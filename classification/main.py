import json

from SGDClassifier import NGOSGDClassifier

# testing and training both from memory
if __name__ == "__main__":
    with open("testing.json", "r") as testing_file:
        testing_data = json.load(testing_file)

    # Create the classifier from the sample training.json
    classifier = NGOSGDClassifier("training.json")
    classifier.fit()
    # Save the classifier to be used for later so we don't need to fit every time
    classifier.save_classifier("SGDClassifier.joblib")

    classifier2 = NGOSGDClassifier("training.json")
    classifier2.load_classifier("SGDClassifier.joblib")
    # Predict from the sample testing.json
    probabilities, predictions = classifier2.predict(testing_data)
    print(probabilities)
    print(predictions)

    mean_document_f1_score, category_f1_scores = classifier2.get_f1_scores()
    print(mean_document_f1_score)
    print(category_f1_scores)
