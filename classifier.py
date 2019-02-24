import time

import gensim.downloader
import matplotlib.pyplot as plt
import nltk
import numpy as np
from tensorflow import keras
from tensorflow import errors as tf_errors

#from narrative_tree import tree

word2vec = gensim.downloader.load("glove-twitter-25")

def get_x_y():
    "Load in all data"
    with open('data.csv', 'r') as f:
        lines = [line.strip().lower() for line in f.readlines()]
    y = np.array([int(line[-1]) for line in lines], bool)
    lines = [line[:-1] for line in lines]

    token_lists = [nltk.word_tokenize(line) for line in lines]
    max_length = max(len(l) for l in token_lists)
    x = [] # np.zeros([len(token_lists), max_length, 25], float)
    for token_list in token_lists:
        x.append([])
        for token in token_list:
            try: vec = word2vec.get_vector(token)
            except KeyError: continue
            x[-1].append(vec)
            #X[i, -j-1] = vec
    x = keras.preprocessing.sequence.pad_sequences(x, maxlen=None, dtype='float32')
    return x, y

def run_experiment(model_maker, x, y, epochs=20, batch_size=100, k=5):
    "Given a model, train it and run cross validation and make plots"
    start = time.time()
    print("start time:", time.ctime())
    name = model_maker.__name__
    print("Running model", name, "three times...")
    model = model_maker()
    #config_dict = model.get_config()
    histories = []
    for i, xtr, ytr, xv, yv in k_fold_split(x, y, k):
        print("Starting validation", i, "...")
        model = model_maker()
        histories.append(model.fit(xtr, ytr, batch_size, epochs, validation_data=(xv, yv), verbose=1))
    make_acc_plot(histories, name)
    make_loss_plot(histories, name)
    model.summary()
    print("finish time:", time.ctime())
    print("Total time in seconds:", time.time() - start)
    return histories

def make_acc_plot(histories, title=None):
    "Plot accuracy from keras training histories"
    colors = [((.4,0,0),(.9,0,0)),((0,.4,0),(0,.9,0)),((0,0,.4),(0,0,.9)),((.4,.4,0),(.9,.9,0)),((0,.4,.4),(0,.9,.9)),((.4,0,.4),(.9,0,.9))]
    for i, ((c1, c2), history) in enumerate(zip(colors,histories)):
        acc_values = history.history['acc']
        val_acc_values = history.history['val_acc']
        epochs = range(1, len(acc_values) + 1)
        plt.plot(epochs, acc_values, label='Training {}'.format(i), color=c1)
        plt.plot(epochs, val_acc_values, label='Validation {}'.format(i), color=c2)
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy')
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    for y in [.65, .7, .75, .8]:
        plt.axhline(y=y, color='black', linestyle='dashed')
    if title:
        plt.title(title)
    plt.show()

def make_loss_plot(histories, title=None):
    "Plot loss from keras training histories"
    colors = [((.4,0,0),(.9,0,0)),((0,.4,0),(0,.9,0)),((0,0,.4),(0,0,.9)),((.4,.4,0),(.9,.9,0)),((0,.4,.4),(0,.9,.9)),((.4,0,.4),(.9,0,.9))]
    for i, ((c1, c2), history) in enumerate(zip(colors,histories)):
        loss_values = history.history['loss']
        val_loss_values = history.history['val_loss']
        epochs = range(1, len(loss_values) + 1)
        plt.plot(epochs, loss_values, label='Training {}'.format(i), color=c1)
        plt.plot(epochs, val_loss_values, label='Validation {}'.format(i), color=c2)
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    if title:
        plt.title(title)
    plt.show()

def k_fold_split(x, y, k=5):
    "Simple k-fold cross-validation"
    n = len(x)
    w = n // k
    p = list(np.random.permutation(n))
    for i in range(k):
        tr = p[:i*w] + p[(i+1)*w:]
        v = p[i*w:(i+1)*w]
        yield i, x[tr], y[tr], x[v], y[v]

def make_lstm():
    "Make a basic recurrent classifier"
    model = keras.models.Sequential()
    model.add(keras.layers.LSTM(50))
    model.add(keras.layers.Dense(1, activation='sigmoid'))
    model.compile(optimizer='rmsprop', loss='binary_crossentropy', metrics=['accuracy'])
    return model

x, y = get_x_y()

#run_experiment(make_lstm, x, y, epochs=50, batch_size=50, k=5)

# Train one model on all data for predictions on the plot events
model = make_lstm()
model.fit(x, y, batch_size=50, epochs=35)

def to_matrix(sentence):
    vectors = []
    for t in nltk.word_tokenize(sentence.lower()):
        try:
            vectors.append(word2vec.get_vector(t))
        except KeyError:
            continue # just skip unknown words
    return np.array([vectors])

def repl():
    while True:
        sentence = input("Enter sentence: ")
        m = to_matrix(sentence)
        try:
            p = model.predict(m)[0, 0]
            print("That is %.1f%% gallant, or %.1f%% percent goofus" % (100*p, 100 - 100*p))
        except tf_errors.InvalidArgumentError:
            print("Model failure")

#
#event_scores = dict()
#def get_event_scores(tree):
#    for event in tree:
#        if event in event_scores:
#            continue
#        x = to_matrix(event)
#        event_scores[event] = model.predict_proba(x)[0,0]
#    for subtree in tree.values():
#        get_event_scores(subtree)
#get_event_scores(tree)
#print("Event scores:")
#print(event_scores)


# M = keras.preprocessing.sequence.pad_sequences([[word2vec.get_vector(t) for t in nltk.word_tokenize(event)] for event in events], maxlen=27, dtype='float32')
