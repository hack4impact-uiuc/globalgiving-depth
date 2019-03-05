## Training

- Reads a JSON file of projects in the form of

```json
{
  "projects": [
    {
      "url": "url",
      "text": "text",
      "themes": [{ "id": "id", "name": "name" }]
    }
  ]
}
```

- Generates unigrams, bigrams, and trigrams over every project, as well as the associated [tfi-df](https://en.wikipedia.org/wiki/Tf%E2%80%93idf) values
- Dumps generated JSON in the form of

```json
{
  "projects": [
    {
      "url": "url",
      "themes": [{ "id": "id", "name": "name" }],
      "tfidf_values": [],
      "features": []
    }
  ]
}
```

## Classifying

- Given a JSON file in the form of

```json
{
  "projects": [
    {
      "url": "url",
      "text": "text
    }
  ]
}
```

- Gets the features and tf-idf values for the projects
- Formats given projects' data into a `pandas` DataFrame with columns `url`, `tfidf_value`, and `feature`
- Formats the "training" data into a `pandas` DataFrame with columns `url`, `theme`, `tfidf_value`, and `feature` (may want to move this into a different python file)
- Each DataFrame will have multiple rows with the same url and theme, but each row will have a different theme and associated tf-idf value

## WIP

- Classify the projects by comparing tf-idf values for common features, possibly with Naive Bayes (given a tf-idf value of a feature, what is the probability the website is a certain theme)
- Build training data from more than the current 4 websites
