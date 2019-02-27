# globalgiving-depth
Gain a depth in insight into NGOs discovered through an automated process.

After initial preprocessing, psp_lda.py eventually creates a list which contains, for each project, each word that appears and its count.
A LDA Model is created and then trained with the above list, which creates topics representing the types of projects.

We can test new/unseen projects on the model and see which topics are deemed to have the highest correspondence with said project.

NOTE: This differs from Eugenia's LDA model, which is a Guided LDA model. We decided to implement both to see which will work well, if any.
