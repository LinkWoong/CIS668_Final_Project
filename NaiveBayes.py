import numpy as np
import pandas as pd
import re
import os
import nltk

from nltk.tokenize.toktok import ToktokTokenizer
from nltk.tokenize import word_tokenize
from bs4 import BeautifulSoup
from sklearn.preprocessing import LabelBinarizer

data = pd.read_csv('/Users/f0rest/Desktop/CIS668_NLP/dataset.csv')

tokenizer=ToktokTokenizer()

stopword_list=nltk.corpus.stopwords.words('english')

def strip_html(text):
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text()

def remove_between_square_brackets(text):
    return re.sub('\[[^]]*\]', '', text)

def denoise_text(text):
    text = strip_html(text)
    text = remove_between_square_brackets(text)
    return text

def remove_special_characters(text, remove_digits=True):
    pattern=r'[^a-zA-z0-9\s]'
    text=re.sub(pattern,'',text)
    return text

def simple_stemmer(text):
    ps=nltk.porter.PorterStemmer()
    text= ' '.join([ps.stem(word) for word in text.split()])
    return text

def remove_stopwords(text, is_lower_case=False):
    tokens = tokenizer.tokenize(text)
    tokens = [token.strip() for token in tokens]
    if is_lower_case:
        filtered_tokens = [token for token in tokens if token not in stopword_list]
    else:
        filtered_tokens = [token for token in tokens if token.lower() not in stopword_list]
    filtered_text = ' '.join(filtered_tokens)    
    return filtered_text

data['review'] = data['review'].apply(strip_html)
data['review'] = data['review'].apply(remove_between_square_brackets)
data['review'] = data['review'].apply(denoise_text)
data['review'] = data['review'].apply(remove_special_characters)
data['review'] = data['review'].apply(simple_stemmer)
data['review'] = data['review'].apply(remove_stopwords)

lb = LabelBinarizer()
sentiment_data = lb.fit_transform(data.sentiment)

train_sentiments=sentiment_data[:40000]
test_sentiments=sentiment_data[40000:]

train_labels = []
for i in train_sentiments:
    if i == 1: train_labels.append(True)
    else : train_labels.append(False)
test_labels = []
for i in test_sentiments:
    if i == 1: test_labels.append(True)
    else: test_labels.append(False)

train_reviews = data['review'][:10000]
test_reviews = data['review'][40000:]

train_set = []
for i in range(0, 10000):
    train_set.append((train_reviews[i], train_labels[i]))

test_set = []
for i in range(40000, 50000):
    test_set.append((test_reviews[i], test_labels[i - 40000]))

train_set = train_set[:10000]
train_labels = train_labels[:10000]

train_all_words = set(word.lower() for passage in train_set for word in word_tokenize(passage[0]))
t = [({word: (word in word_tokenize(z[0])) for word in train_all_words}, z[1]) for z in train_set]

classifier = nltk.NaiveBayesClassifier.train(t)

# test_data = test_set[:50]
test_all_words = set(word.lower() for passage in test_set for word in word_tokenize(passage[0]))
f = [({word: (word in word_tokenize(z[0])) for word in test_all_words}, z[1]) for z in test_set]

print(nltk.classify.accuracy(classifier, f))