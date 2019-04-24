# General
## Training json file
This training file contains training data for the classifiers, pulled directly from the Global Giving API
Format:
{
    "targets" : [[0, 2, 3, 8], [1, 7 17]...]
    "
}


# Bag of Words
## Dictionary json file
This dictionary contains the relevant words for each category and their respective tf-idf scores
Format:
{
    "Education": {
        "word" : (float) tf-idf score
    },
    "Children": {...},
    "Women and Girls": {...},
    "Animals": {...},
    "Climate Change": {...},
    "Democracy and Governance": {...},
    "Disaster Recovery": {...},
    "Economic Development": {...},
    "Environment": {...},
    "Microfinance": {...},
    "Health": {...},
    "Humanitarian Assistance": {...},
    "Human Rights": {...},
    "Sport": {...},
    "Technology": {...},
    "Hunger": {...},
    "Arts and Culture": {...},
    "LGBTQAI+": {...},
}

## Predictions json file
This file contains the predictions made by the bag of words classifier
Format:
[
    [0,0,0,0,0,0,0,0,1,1,0,0]...
]