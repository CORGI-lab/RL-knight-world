import pickle
import random
from sys import stdin

import nltk
import numpy as np
from sklearn.model_selection import KFold
from sklearn.linear_model import LogisticRegression

from narrative_tree import tree

with open('data.csv', 'r') as f:
    lines = [line.strip() for line in f.readlines()]
#lines = [line.strip() for line in stdin]
labels = np.array([bool(int(line[-1])) for line in lines])
lines = [line[:-1] for line in lines]

porterstemmer = nltk.stem.PorterStemmer()

token_lists = [[porterstemmer.stem(token.lower())
                for token in nltk.word_tokenize(line)]
               for line in lines]

all_tokens = sorted(set(t for tl in token_lists for t in tl))
token_to_index = {t: i for i, t in enumerate(all_tokens)}

X = np.zeros([len(token_lists), len(all_tokens)], bool)
for i, token_list in enumerate(token_lists):
    for token in token_list:
        j = token_to_index[token]
        X[i][j] = True

classifier = LogisticRegression(solver='lbfgs')
classifier.fit(X, labels)
print("Full train accuracy:")
print(classifier.score(X, labels))



event_scores = dict()
def get_event_scores(tree):
    for event in tree:
        if event in event_scores:
            continue
        tokens = [porterstemmer.stem(token.lower())
                  for token in nltk.word_tokenize(event)]
        x = np.zeros([1, len(all_tokens)], bool)
        for t in tokens:
            if t in token_to_index:
                x[0, token_to_index[t]] = True
        event_scores[event] = classifier.predict_proba(x)[0][0]
    for subtree in tree.values():
        get_event_scores(subtree)
get_event_scores(tree)
print("Event scores:")
print(event_scores)


# print("Saving fully trained model...")
# with open('classifier.pickle', 'wb') as f:
#     pickle.dump(classifier, f)

kfold = KFold(n_splits=5)
for split_num, (train_index, test_index) in enumerate(kfold.split(X)):
    classifier.fit(X[train_index], labels[train_index])
    print("Split number", split_num, ":")
    print(classifier.score(X[test_index], labels[test_index]))


