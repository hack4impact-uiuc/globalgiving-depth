import json

from SGDClassifier import NGOSGDClassifier

if __name__ == "__main__":
    with open("testing.json", "r") as testing_file:
        testing_data = json.load(testing_file)

    classifier = NGOSGDClassifier("training.json")
    classifier.fit()
    prob, pred = classifier.predict(testing_data)
    print(prob)
    print(pred)