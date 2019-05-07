import json
import sklearn

from sklearn.externals import joblib
from sklearn.model_selection import train_test_split

from UnguidedLDA import NGOUnguidedLDA

# Using project summaries instead of scraped data for improved clustering results.
with open("project_summaries.json", "r") as datafile:
    input_data = json.load(datafile)

# Set up training and testing data
# Clusters won't match NGO categories directly, so no need for huge testing data to compute "accuracy statistic")
training_data, testing_data = train_test_split(input_data, test_size=0.01)

clusterer = NGOUnguidedLDA(training_data)
clusterer.process_projects()
# Keeping 40000 top words in the training dictionary, each of which cannot appear in over 40% of corpus
clusterer.create_training_dict(0.4, 40000)

# Create LDA Model with 10 clusters, 3 extra processes for parallelization, and no tf-idf.
clusterer.create_lda_model(10, 3, False)

# Save NGOUnguidedLDA Object
joblib.dump(clusterer, "UnguidedLDAClusterer.joblib")

# Print out the top words from each LDA Cluster.
clusterer.print_lda_topics()
# For each project, print the top 5 words from (up to) 3 "closest" clusters to this project.
clusterer.test_lda_model(testing_data, 3, 5)
