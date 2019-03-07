# Results of all implementations

<h2> Initial implementation: Generate dictionaries of words relevant to each category through synonyms of category names <h2>

Accuracy Results:
Dictionaries of first-level synonyms: 0.26315
Dictionaries of second-level synonyms (synonyms of synonyms of categories included): 0.05263

<h2> Second implementation: Generate dictionaries of words by collecting words scraped from websites of already classified organizations, where frequency is taken into account to score words <h2>

Accuracy results:
All organizations: 0.60005
Subset of organizations (first 1/10) of all orgs for quick testing: 0.32853

<h3> Third implementation: Building off of the second implementation, cut common words between categories to keep only relevant words that differentiate categories <h3>
In this implementation, different word frequencies were tested to test which common word frequency cuts were most effective. (ex. if a word appeared in 7 or more categories, it would be cut). Tests for this implementation were based off of the first 1/10 of all orgs for quick testing.

Accuracy results (prefix: word_frequency):
Base comparison without common word cuts: 0.32853 (above)
> 7 occurrences: 0.34582
> 6 occurrences: 0.37175
> 5 occurrences: 0.38904
> 4 occurrences: 0.42939
> 3 occurrences: 0.50144
> 2 occurrences: 0.64265
> 1 occurrences (unique): 0.65994

> 2 occurrences with ALL organizations: 0.81025
> 1 occurrences with ALL organizations: 0.83328

> 1 occurrences with 80/20 split: 0.68587

<h4> Fourth implementation: Building off of the third implmentation, testing various methods of weighting word scores to further increase accuracy (80/20 splits) <h4>

Accuracy Results:
Amplifying word scores for scores > 1: 0.687319
Weighted by type (N: 10, V:2, J: 5): 0.68299
Weighted by type (N: 20, V:2, J: 2): 0.68155
Weighted by type (N: 2, V:20, J: 2): 0.66714