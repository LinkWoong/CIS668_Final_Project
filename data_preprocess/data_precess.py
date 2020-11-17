import os
import json
import nltk
from nltk.corpus import stopwords
# from nltk.tokenize import TweetTokenizer
from nltk.tokenize import *
import string
from nltk.stem import WordNetLemmatizer
# from nltk.stem.snowball import SnowballStemmer
# import enchant
from nltk import pos_tag
from nltk.corpus import wordnet

def file_read():
    # print("Retrieving data from sentube dataset...")
    fileCount = 0
    directory_path = os.getcwd() + "/Sentube"
    directory = os.fsencode(directory_path) #str->byte
    dataset = []

    for subdir in os.listdir(directory):
        dirname = os.fsdecode(subdir) #byte->str
        filename = directory_path+"/"+dirname
        for file in os.listdir(os.fsdecode(filename)):
            if file.endswith("json"):
                with open(filename+"/"+file) as f:
                    temp = json.load(f)
                    for comment in temp["comments"]:
                        dataset.append([comment["text"]])
                fileCount += 1
    return dataset

def data_save(dataset, file_name):
    with open(file_name+".json", 'w') as outfile:
        json.dump(dataset, outfile, indent=4)

def token(dataset):
    tokenizedData = []
    toknizer = TweetTokenizer(reduce_len=True)
    for comment in dataset:
        token_comment = toknizer.tokenize(comment[0])
        tokenizedData.append(token_comment)
    return tokenizedData

def remove_stopword(dataset):
    remove_stopword_data = []
    stop_words = set(stopwords.words("english"))
    for comment in dataset:
        # print(comment)
        filtered_comment = [w for w in comment if not w in stop_words]
        remove_stopword_data.append(filtered_comment)
    return remove_stopword_data

def remove_num_punc(dataset):
    ans = []
    for comment in dataset:
        filterd_comment = [ w.lower() for w in comment if w not in string.punctuation and not w.isdigit() and len(w) > 2]
        ans.append(filterd_comment)
    return ans

def lemmatization(dataset):
    def get_pos(tag):
        if tag.startswith('J'):
            return wordnet.ADJ
        elif tag.startswith('V'):
            return wordnet.VERB
        elif tag.startswith('R'):
            return wordnet.ADV
        else:
            return wordnet.NOUN

    lemmatizer = WordNetLemmatizer()
    ans = []
    for comment in dataset:
        pos_tags = pos_tag(comment)
        comment = [lemmatizer.lemmatize(pair[0], get_pos(pair[1])) for pair in pos_tags]
        ans.append(comment)
    return ans



def preprocess():
    dataset = file_read() #import file
    data_save(dataset,"raw_data") #save raw comments
    dataset = token(dataset) # tokenize comment
    dataset = remove_stopword(dataset) #remove stop words
    dataset = remove_num_punc(dataset) #remove number, punctuation, len(2)<=2
    dataset = lemmatization(dataset) #lemmatize word
    data_save(dataset,"processed_data") # save processed data
    # print(dataset)

if __name__ == "__main__":
    preprocess()
