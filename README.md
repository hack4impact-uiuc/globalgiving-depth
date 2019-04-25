# GlobalGiving Depth &middot; [![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE) [![CircleCI Status](https://circleci.com/gh/hack4impact-uiuc/globalgiving-depth.svg?style=shield&circle-token=:circle-token)](https://circleci.com/gh/hack4impact-uiuc/globalgiving-depth) ![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)

**Problem Statement:** GlobalGiving’s network consists of many organizations based in the US along with some nonprofits in other countries. There are still hundreds of thousands more organiztions which GlobalGiving knows *of*, but may not have information on the types of work they do. It is possible, given an NGO's website, to discern and characterize the work of these NGOs using statistics, natural language processing, and machine learning in an automated way.


**Repo Description:** This repo consists of our various approaches to characterizing the work of various NGOs. These approaches fall into a few different categories:
- **Classification** (see `/classification` folder for code, details, and examples)

Using machine learning classifiers, we can feed in text from an NGO's website and predict with reasonable accuracy the categories which that NGO may fall into. The classifiers provided here consist of a [Stochastic Gradient Descent](https://github.com/hack4impact-uiuc/globalgiving-depth/wiki/Stochastic-Gradient-Descent-(SGD)-Classifier) classifier and a [Bag of Words](https://github.com/hack4impact-uiuc/globalgiving-depth/wiki/Bag-of-Words-(BOW)-Classifier) classifier.

- **Clustering** (see `/clustering` folder for code, details, and examples)

GlobalGiving's existing categorization scheme is certainly sufficient for the purposes it serves, but a categorization scheme based on the logical differences between language used on NGO websites would be more useful in identifying/characterizing unknown NGOs. The clustering algorithms provided here consist of a [K-Means implementation using Document Embeddings](https://github.com/hack4impact-uiuc/globalgiving-depth/wiki/Document-Embeddings) and an implementation of [Latent Dirichlet Allocation](https://github.com/hack4impact-uiuc/globalgiving-depth/wiki/Latent-Dirichlet-Allocation-(LDA)).

- **Processing** (see `/processing` folder for code, details, and examples)

How we classify/cluster the data is just as important as the way we obtain/process the data. For this project, we used an [HTML Parser](processing/HTMLParser.py) that leverages the BeautifulSoup library to pull clean and filtered text from NGO websites.

- **Past approaches**

Refer to the [wiki](https://github.com/hack4impact-uiuc/globalgiving-depth/wiki) to read about some other past approaches which were tried and abandoned.

## Getting Started

### Installation

Dependencies can be installed into a virtual environment from the requirements.txt file using pipenv:

`pipenv install -r requirements.txt`

For LDA: It is necessary to use the NLTK Downloader to obtain “stopwords,” “WordNetLemmatizer,” and other resources from the Natural Language Toolkit. 
For more information on the NLTK Downloader, please refer to [NLTK Documentation](https://www.nltk.org/data.html).

### Usage

Each subfolder (classification, clustering, processing) has Jupyter notebooks with examples of code usage. Refer to the [wiki](https://github.com/hack4impact-uiuc/globalgiving-depth/wiki) for detailed function documentation.

## Team

 - Product Manager - Josh Burke ([@JoshBurke](https://github.com/JoshBurke))
 - Technical Lead - Aryn Harmon ([@achcello](https://github.com/achcello))

### Software Devs

 - Jacqueline Osborn ([@jackieo5023](https://github.com/jackieo5023))
 - Lam Tran ([@Lam7150](https://github.com/Lam7150))
 - Eugenia Chen ([@Polarpi](https://github.com/Polarpi))
 - Prashant Pokhriyal ([@psp2](https://github.com/psp2))

## License

This project is [licensed](LICENSE) under the terms of the MIT license.
