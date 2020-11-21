#!/usr/bin/env python
# coding: utf-8

# In[1]:


from importlib import reload
import sys
from imp import reload
import warnings
warnings.filterwarnings('ignore')
if sys.version[0] == '2':
    reload(sys)
    sys.setdefaultencoding("utf-8")


# In[2]:


import pandas as pd


# In[3]:


df = pd.read_csv('./imdb_master.csv',encoding="latin-1")
df.head()


# In[4]:


df = df.drop(['Unnamed: 0','type','file'],axis=1)
df.columns = ["review","sentiment"]
df.head()


# In[5]:


df = df[df.sentiment != 'unsup']
df['sentiment'] = df['sentiment'].map({'pos': 1, 'neg': 0})
df.head()


# In[6]:


neg = 0
pos = 0
for i in range(len(df)):
    if df['sentiment'][i] == 0:
        neg += 1
    elif df['sentiment'][i] == 1:
        pos += 1
        
print(neg)
print(pos)


# In[7]:


import nltk
nltk.download('stopwords')
nltk.download('wordnet')


# In[8]:


import re
from nltk import*
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
stop_words = set(stopwords.words("english")) 
lemmatizer = WordNetLemmatizer()

tokenizer = RegexpTokenizer(r'\w+')
df['Processed_Reviews'] = df['review'].apply(lambda x: tokenizer.tokenize(x.lower())) 

df.head()


# In[9]:


# def remove_stopwords(text):
#     words = [w for w in text if w not in stopwords.words('english')]
#     print('1')
#     return words
# df['Processed_Reviews'] = df['Processed_Reviews'].apply(lambda x:[w for w in x if w not in stopwords.words('english')])
stop_words = set(stopwords.words('english'))
df['Processed_Reviews'] = df['Processed_Reviews'].apply(lambda x: [word for word in x if word not in stop_words])
df.head()


# In[10]:


lemmatizer = WordNetLemmatizer()

def word_lemmatizer(text):
    lem_text = [lemmatizer.lemmatize(i) for i in text]
    return lem_text
df['Processed_Reviews'] = df['Processed_Reviews'].apply(lambda x :word_lemmatizer(x))
df.head()


# In[11]:


def list_to_str(alist):
    a = " ".join(alist)
    return a
df['str_Reviews'] = df['Processed_Reviews'].apply(lambda x :list_to_str(x))
df.head()


# In[12]:


df = df.drop(['review'], axis=1)
df.head()


# In[ ]:





# In[15]:


import json
data = json.load(open('processed_data.json', 'r'))
print(data)
list_sen = [2 for i in range(len(data))]
df2 = pd.DataFrame(data={"Processed_Reviews": data, "sentiment": list_sen})
df2['str_Reviews'] = df2['Processed_Reviews'].apply(lambda x :list_to_str(x))


# In[ ]:





# In[16]:


df = pd.concat([df, df2]).reset_index(drop=True)
df.head()


# In[17]:


df.tail()


# In[18]:


all_words = []
for i in df['Processed_Reviews']:
#     print(len(df['Processed_Reviews'][i])
    for j in i:
        all_words.append(j)
print(len(all_words))
vocab = set(all_words)  
len_vocab = len(vocab)
print(len_vocab)


# In[28]:


from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.layers import Dense , Input , LSTM , Embedding, Dropout , Activation, GRU, Flatten
from keras.layers import Bidirectional, GlobalMaxPool1D
from keras.models import Model, Sequential
from keras.layers import Convolution1D
from keras import initializers, regularizers, constraints, optimizers, layers
from sklearn.model_selection import train_test_split
max_features = len_vocab
tokenizer = Tokenizer(num_words=max_features)
tokenizer.fit_on_texts(df['str_Reviews'])
list_tokenized = tokenizer.texts_to_sequences(df['str_Reviews'])
print(type(list_tokenized))
print(list_tokenized[0])
print(df['str_Reviews'][0])
maxlen = 130
X = pad_sequences(list_tokenized, maxlen=maxlen, padding='post')[:50000]
y = df['sentiment'][:50000]

X_pre = pad_sequences(list_tokenized, maxlen=maxlen, padding='post')[50000:]
y_pre = df['sentiment'][50000:]


# In[29]:


print(list_tokenized[95241])
print(df['str_Reviews'][95241])


# In[30]:



X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.05,
    shuffle=True,
    random_state=42)
print(len(X_train))
print(len(X_test))
print(type(y_train))
print(X_test)


# In[31]:


print(y_test)


# In[33]:



embed_size = 256
model = Sequential()
model.add(Embedding(max_features, embed_size))
model.add(Bidirectional(LSTM(32, return_sequences = True)))
model.add(GlobalMaxPool1D())
model.add(Dense(20, activation="relu"))
model.add(Dropout(0.3))
model.add(Dense(1, activation="sigmoid"))
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

batch_size = 100
epochs = 1
model.fit(X_train,y_train, validation_data=(X_test, y_test),batch_size=batch_size, epochs=epochs)


# In[34]:


Y_pred = model.predict_classes(X_pre)


# In[38]:


print(Y_pred)
print(type(Y_pred))
print(type(Y_pred[0]))


# In[39]:


Y_pred = Y_pred.tolist()

json.dump(Y_pred, open('predict.json', 'w'))  


# In[40]:


model.save('my_model.h5')


# In[ ]:




