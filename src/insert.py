#needed to avoid a sqlalchemy error

import sqlalchemy as sa
import warnings
from sqlalchemy import exc as sa_exc

import pickle

from util import *

class FullModel:
    def __init__(self, default, authormodels):
        self.defaultmodel = default
        self.models = authormodels

    def classify(self, author, features):
        for model in self.models:
            modelAuthor = model.author
            if modelAuthor == author:
                return model.classify(features)
        return self.defaultmodel.classify(find_features(features))

    def prob_classify(self, author, features):
        for model in self.models:
            modelAuthor = model.author
            if modelAuthor == author:
                return model.prob_classify(features)
        return None


class AuthorModel:
    def __init__(self, author, authorModel, features):
        self.author = author
        self.authorModel = authorModel
        self.features = features
    def classify(self, features):
        return self.authorModel.classify(self.featureFunc(features))

    def prob_classify(self, features):
        return self.authorModel.prob_classify(self.featureFunc(features))

    def featureFunc(self, tokens):
        words = set(tokens)
        features = {}
        for w in self.features:
            features[w] = (w in words)
        return features

class BySentimentClassifier(ClassifierI):
    def __init__(self, Hold_classifier, Sell_classifier, Buy_classifier):
        self.holdClassifier = Hold_classifier
        self.sellClassifier = Sell_classifier
        self.BuyClassifier = Buy_classifier

    def classify(self, features):
        holdConfidence = self.holdClassifier.prob_classify(features).prob('hold')
        sellConfidence = self.sellClassifier.prob_classify(features).prob('sell')
        buyConfidence = self.BuyClassifier.prob_classify(features).prob('buy')
        if max(holdConfidence, sellConfidence, buyConfidence) == holdConfidence:
            return "hold"
        elif max(holdConfidence, sellConfidence, buyConfidence) == buyConfidence:
            return "buy"
        else:
            return "sell"

classifier_f = open("bestModel.pickle", "rb")
classifier = pickle.load(classifier_f)
classifier_f.close()

stopwords = set(stopwords.words('english'))

warnings.simplefilter("ignore", category=sa_exc.SAWarning)

memsql_engine = create_memsql_engine()
results = memsql_engine.execute("SELECT File_Text FROM wardini ORDER BY ID ASC LIMIT 2000")

all_words = []
for row in results:
    for w in word_tokenize(row["File_Text"].lower()):
        all_words.append(w.lower())

all_words = nltk.FreqDist(all_words)

word_features = list(map(lambda x: x[0], all_words.most_common(2000)))

def get_features(texts):
    all_words = []
    for text in texts:
        for w in word_tokenize(text.lower()):
            all_words.append(w.lower())
    all_words = nltk.FreqDist(all_words)
    return list(map(lambda x: x[0], all_words.most_common(2000)))


def clean_features(features):
    i = 0
    while i < len(features):
        if (features[i].lower() in stopwords) or (not features[i].isalpha()):
            features.pop(i)
        else:
            i += 1

clean_features(word_features)

def find_features(document):
    words = set(document)
    features = {}
    for w in word_features:
        features[w] = (w in words)
    return features

def getSentiment(name, author, text):
    if text == "NULL":
        return "None"
    sentiment = classifier.classify(author, word_tokenize(text.lower()))
    if "new iss" in name.lower():
        if sentiment == "sell":
            sentiment = "pass"
    return sentiment

