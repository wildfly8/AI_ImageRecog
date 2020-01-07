#!/usr/bin/env python3
# coding=utf-8

import os
import sys
from datetime import datetime

from bs4 import BeautifulSoup
import nltk
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.classify import ClassifierI
import pickle

from addext import *
from gettxt import *
from fixdates import *
from IdSector import *
from text import *
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


prints = lambda s: print("[{}] {}".format(datetime.now().strftime("%H:%M:%S"), s))
prints("START")

classifier_f = open("bestModel.pickle", "rb")
classifier = pickle.load(classifier_f)
classifier_f.close()

nltk.download('stopwords')
nltk.download('punkt')
stopwords = set(stopwords.words('english'))

warnings.simplefilter("ignore", category=sa_exc.SAWarning)

config = get_config()

webUser = config['web']['user']
webPass = config['web']['password']
baseURL = config['web']['baseURL']
allItemsURL = baseURL + config['web']['allItems']

memsql_engine = create_memsql_engine(cfg=config['memsql'])

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
    sentiment = classifier.classify(author, word_tokenize(text.lower()))
    if "new iss" in name.lower():
        if sentiment == "sell":
            sentiment = "pass"
    return sentiment


def get_url(url):
    url = str(url).split('"')
    url = url[1]
    url = url.replace(' ', "%20")
    return url

def get_next_url(url):
    url = str(url).split('"')
    url = url[3]
    url = url.replace(' ', "%20").replace("amp;", "")
    return url

def get_name(url):
    url = url.split("/")
    url = url[len(url) - 1].replace('%20', ' ')
    return url

coltitles = ["Document Author", "Date", "Ticker", "Secondary Ticker",
               "Name", "Title", "Report Type", "Investment Sector",
               "Barclays Class Level 3", "Barclays Class Level 4", "Company Name", "WAM Office Location",
               "Modified Date", "Modified By", "2a-7 Related Documents", "Country", "Checked Out To", "File URL"]
data = {}
for title in coltitles:
    data[title] = []

l = 0

url = allItemsURL
prints("Sending GET to: {}".format(url))
r = requests.get(url, auth=HttpNtlmAuth(webUser, webPass))

# If GET request failed
if not r.ok:
    prints("Error with GET request")
    prints("Status code: {}".format(r.status_code))
    prints("Reason: {}".format(r.reason))
    sys.exit()

break_it = False
while not break_it:
    soup = BeautifulSoup(r.content,'lxml')
    table = soup.find_all("table")[8]

    all_a = soup.find_all("a")
    next_url = all_a[len(all_a) - 2]
    next_url = get_next_url(next_url)
    next_url = baseURL + next_url

    j = 0
    for row in table.find_all('tr'):
        # Go through each document in the HTML page, check if exists in DB
        # If exists skip, otherwise extract metadata from HTML page (ticker, report name, URL, etc)
        if j < 4:
            j += 1
            continue
        columns = row.find_all('td')
        names = row.find_all('a')
        if len(columns) < 15:
            continue
        else:
            if len(columns[1].get_text().strip()) != 0:
                url = baseURL + get_url(names[2])
                results = memsql_engine.execute("SELECT ID from wardini WHERE File_URL = " + '"' + url.replace('%', '%%') + '"')
                for row in results:
                    break_it = True
                if break_it:
                    break
                data["File URL"] += [url]
                columns = columns[1:]
            else:
                url = baseURL + get_url(names[0])
                results = memsql_engine.execute("SELECT ID from wardini WHERE File_URL = " + '"' + url.replace('%', '%%') + '"')
                for row in results:
                    break_it = True
                if break_it:
                    break
                data["File URL"] += [url]
                columns = columns[2:]
        for title, column in zip(coltitles, columns):
            if title == "File URL":
                continue
            data[title] += [str(column.get_text()).replace(u'\xa0', u'').replace('\n', '')]
        l += 1
    try:
        if not break_it:
            r = requests.get(next_url, auth=HttpNtlmAuth(webUser, webPass))
    except:
        break


ids = []
starting_id = 1
results = memsql_engine.execute("SELECT ID from wardini ORDER BY ID DESC LIMIT 1")
for row in results:
    starting_id += row["ID"]

for i in range(len(data["Name"])):
    ids.append(starting_id + i)
data["ID"] = ids

# Format dates for DB storage
for i in range(len(data["Date"])):
    data["Date"][i] = fix_date(data["Date"][i])

for i in range(len(data["Modified Date"])):
    data["Modified Date"][i] = fix_second_date(data["Modified Date"][i])

# Format tickers for storage in DB
tickers = data["Ticker"]
secondaries = data["Secondary Ticker"]
fixed_tickers = []
for tick, sec in zip(tickers, secondaries):
    fixed_tickers.append(fixTicker(tick, sec))
data["Ticker"] = fixed_tickers

# Get text from each doc
prints("Retrieving text from each doc...")
exts = []
text = []
urls = data["File URL"]
for url in urls:
    ext = get_ext(url)
    exts.append(ext)
    if ext == "oft" or ext == "msg":
        text.append(re.sub(r"\S*@\S*\s?", "", getText(url, ext, webUser, webPass)))
    else:
        text.append(getText(url, ext, webUser, webPass))
data["ext"] = exts
data["File Text"] = text

prints("Retrieving moodys/fitchs from text...")
# Retrieve moodys and fitchs from text
moodys = []
fitchs = []
for text in data["File Text"]:
    moodys.append(getMoody(text))
    fitchs.append(getFitch(text))
data["moody"] = moodys
data["fitch"] = fitchs

for key in data.keys():
    if key == "ID" or key == "File Text":
        continue
    for i in range(len(data[key])):
        if data[key][i] is None:
            continue
        data[key][i] = data[key][i].replace('"', '').replace("'", '').replace('%', '%%')

insert = "INSERT INTO wardini (ID, Document_Author, Date_, Ticker, Secondary_Ticker, Name,Title, Report_Type, Investment_Sector, Barclays_Class_Level_3, Barclays_Class_Level_4, Company_Name, WAM_Office_Location,Modified_Date, Modified_By, 2a_7_Related_Documents, Country, Checked_Out_To, File_URL, File_Text, moody, fitch, sentiment, ext, sector) VALUES "

prints("Generating insert query...")
for i in range(len(data["ID"])):
    id = str(data["ID"][i])
    author = '"' + data["Document Author"][i] + '"'
    date = '"' + data["Date"][i] + '"'
    ticker = '"' + data["Ticker"][i] + '"'
    secondary_ticker = '"' + data["Secondary Ticker"][i] + '"'
    name = '"' + data["Name"][i] + '"'
    title = '"' + data["Title"][i] + '"'
    reports = '"' + data["Report Type"][i] + '"'
    invsector = '"' + data["Investment Sector"][i] + '"'
    barclays3 = '"' + data["Barclays Class Level 3"][i] + '"'
    barclays4 = '"' + data["Barclays Class Level 4"][i] + '"'
    company = '"' + data["Company Name"][i] + '"'
    office = '"' + data["WAM Office Location"][i] + '"'
    modified = '"' + data["Modified Date"][i] + '"'
    modified_by = '"' + data["Modified By"][i] + '"'
    a_7 = '"' + data["2a-7 Related Documents"][i] + '"'
    country = '"' + data["Country"][i] + '"'
    checked = '"' + data["Checked Out To"][i] + '"'
    url = '"' + data["File URL"][i] + '"'
    if data["File Text"][i] != "NULL":
        text = '"' + data["File Text"][i].replace('\\', '') + '"'
    else:
        text = "NULL"
    if data["moody"][i] is None:
        moody = "NULL"
    elif data['moody'][i] != "NULL":
        moody = '"' + data["moody"][i] + '"'
    else:
        moody = data["moody"][i]
    if data["fitch"][i] is None:
        fitch = "NULL"
    elif data["fitch"][i] != "NULL":
        fitch = '"' + data["fitch"][i] + '"'
    else:
        fitch = data["fitch"][i]
    ext = '"' + data["ext"][i] + '"'
    if data["File Text"][i] == "NULL" or not (ext in ['"docx"', '"doc"', '"pdf"', '"msg"']):
        sentiment = '"None"'
    else:
        sentiment = '"' + getSentiment(data["Name"][i], data["Document Author"][i], data["File Text"][i]) + '"'
    sectors = '"' + getSector(data["Ticker"][i]) + '"'
    insert += "(" + id + ',' + author + ',' + date + ',' + ticker + ',' + secondary_ticker + ',' + name + ',' + title + ',' + reports + ',' + invsector + ',' + barclays3 + ',' + barclays4 + ',' + company + ',' + office + ',' + modified + ',' + modified_by + ',' + a_7 + ',' + country + ',' + checked + ',' + url + ',' + text + ',' + moody + ',' + fitch + ',' + sentiment + ',' + ext + ',' + sectors + '),'

prints("Inserting into DB...")
# Insert new documents into DB
if len(data["ID"]) > 0:
    memsql_engine.execute(insert[:-1])
    #print(insert[:-1])

prints("Inserted {} docs".format(len(data["ID"])))

for name in os.listdir('.'):
    if name.split('.')[0] == "document":
        os.remove(name)

prints("DONE")
