import pickle
import random
from sys import stdin
import nltk
import numpy as np
from sklearn.model_selection import KFold
from sklearn.linear_model import LogisticRegression

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

x = np.zeros([len(token_lists), len(all_tokens)], bool)
for i, token_list in enumerate(token_lists):
    for token in token_list:
        j = token_to_index[token]
        x[i][j] = True

classifier = LogisticRegression(solver='lbfgs')
classifier.fit(x, labels)
print("Full train accuracy:")
print(classifier.score(x, labels))

print("Saving fully trained model...")
with open('classifier.pickle', 'wb') as f:
    pickle.dump(classifier, f)

kfold = KFold(n_splits=5)
for split_num, (train_index, test_index) in enumerate(kfold.split(x)):
    classifier.fit(x[train_index], labels[train_index])
    print("Split number", split_num, ":")
    print(classifier.score(x[test_index], labels[test_index]))
