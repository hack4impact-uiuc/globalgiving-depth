import json

from sklearn.model_selection.train_test_split import train_test_split

from SGDClassifier import NGOSGDClassifier


if __name__ == "__main__":
    with open("data.json", "r") as in_file:
        dataset = json.load(in_file)
    train_data, test_data = train_test_split(dataset, test_size=0.2, random_state=42)

    # Create the classifier from the sample training.json
    classifier = NGOSGDClassifier()
    classifier.fit(train_data)
    # Save the classifier to be used for later so we don't need to fit every time
    classifier.save_classifier("SGDClassifier.joblib")

    classifier2 = NGOSGDClassifier()
    classifier2.load_classifier("SGDClassifier.joblib")
    # Predict from the sample testing.json
    probabilities, predictions = classifier2.predict(test_data)
    print(probabilities)
    print(predictions)

    mean_document_f1_score, category_f1_scores = classifier2.get_f1_scores()
    print(mean_document_f1_score)
    print(category_f1_scores)
