import json
from sklearn.model_selection import train_test_split

from SGDClassifier import (
    NGO_SGDClassifier,
    set_up_training_data,
    save_classifier,
    load_classifier,
)


if __name__ == "__main__":
    with open("data.json", "r") as in_file:
        dataset = json.load(in_file)
    train_data, test_data = train_test_split(dataset, test_size=0.2, random_state=42)
    formatted_train_data = set_up_training_data(train_data, "formatted_train.json")

    # Create the classifier from the sample training.json
    classifier = NGOSGDClassifier()
    classifier.fit(formatted_train_data)

    # Save the classifier to be used for later so we don't need to fit every time
    save_classifier(classifier, "SGDClassifier.obj")

    classifier2 = load_classifier("SGDClassifier.obj")

    # Predict from the sample testing.json
    probabilities, predictions = classifier2.predict(test_data)
    print(probabilities)
    print(predictions)

    mean_document_f1_score, category_f1_scores = classifier2.get_f1_scores()
    print(mean_document_f1_score)
    print(category_f1_scores)
