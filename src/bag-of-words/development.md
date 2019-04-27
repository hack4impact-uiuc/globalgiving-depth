Issues run into during development:

Dictionary Generator:
- Removing duplicates from list
    - Problem: duplicates may have different scores because of different word relations (average them?)
    - Problem: converting to set and parsing back into list can be cpu heavy
- Related words from synonyms generate scores based of synonyms; not original words
- Plural and singular words aren't accounted for

More accurate dataset:
    - Parse through organizations already in Global Giving, cross-reference with current list and prune/add to dict

Classifier:
    - Test cases

Next Steps:
    - Develop test cases (organizations crawled from past project)
    - Develop more accurate dataset

Things to mention:
    - Dictionary generator is only english
    - Change category - index associations