#Import nltk to check english lexicon
import nltk
import re
from nltk.tokenize import word_tokenize
from nltk.corpus import (
    wordnet,
    stopwords
)
def remove_emoji(string):
    emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           u"\U00002702-\U000027B0"
                           u"\U000024C2-\U0001F251"
                           "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', string)
def preprocessing_text(table):
    #put everythin in lowercase
    table['text'] = table['texts'].str.lower()
    #Replace rt indicating that was a retweet
    table['text'] = [remove_emoji(t) for t in table['text']]
    table['text'] = table['text'].str.replace('rt', '')
    #Replace occurences of mentioning @UserNames
    table['text'] = table['text'].replace(r'@\w+', '', regex=True)
    #Replace links contained in the tweet
    table['text'] = table['text'].replace(r'http\S+', '', regex=True)
    table['text'] = table['text'].replace(r'www.[^ ]+', '', regex=True)
    #remove numbers
    table['text'] = table['text'].replace(r'[0-9]+', '', regex=True)
    #replace special characters and puntuation marks
    table['text'] = table['text'].replace(r'[!"#$%&()*+,-./:;<=>?@[\]^_`{|}~]', '', regex=True)
    return table

def in_dict(word):
    if wordnet.synsets(word):
        return True
def stop_words(table):
    #We need to remove the stop words
    stop_words_list = stopwords.words('english')
    table['text'] = table['text'].str.lower()
    table['text'] = table['text'].apply(lambda x: ' '.join([word for word in x.split() if word not in (stop_words_list)]))
    return table
def replace_antonyms(word):
    #We get all the lemma for the word
    for syn in wordnet.synsets(word): 
        for lemma in syn.lemmas(): 
            #if the lemma is an antonyms of the word
            if lemma.antonyms(): 
                #we return the antonym
                return lemma.antonyms()[0].name()
    return word
def replace_elongated_word(word):
    regex = r'(\w*)(\w+)\2(\w*)'
    repl = r'\1\2\3'    
    if in_dict(word):
        return word
    new_word = re.sub(regex, repl, word)
    if new_word != word:
        return replace_elongated_word(new_word)
    else:
        return new_word

def detect_elongated_words(row):
    regexrep = r'(\w*)(\w+)(\2)(\w*)'
    words = [''.join(i) for i in re.findall(regexrep, row)]
    for word in words:
        if not in_dict(word):
            row = re.sub(word, replace_elongated_word(word), row)
    return row
def cleaning_table(table):
    #This function will process all the required cleaning for the text in our tweets
    table = preprocessing_text(table)
    table['text'] = table['text'].apply(lambda x: detect_elongated_words(x))
    table = stop_words(table)
    return table

import mysql.connector
import pandas as pd
import time
import twitter_cred

import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mpl
db_connection = mysql.connector.connect(
    user='root',
    host='127.0.0.1',
    database="test"
#     charset = 'utf8'
)
cursor = db_connection.cursor()
create_table = """ CREATE TABLE IF NOT EXISTS graph(
    id INT(11) NOT NULL AUTO_INCREMENT,
    node1 BIGINT(20),
    node2 BIGINT(20),
    text VARCHAR(255),
    PRIMARY KEY (id)
)"""
cursor.execute(create_table)

import pandas as pd
import time
 # Wait for 5 seconds

while True:
    pi=pd.read_csv('results.csv')
    pi=cleaning_table(pi)
    print ('Working')
    for i,j in pi.iterrows():
        try:
            cursor.execute("INSERT INTO graph (node1, node2, text) VALUES (%s,%s,%s)",
                        (j.twitter_id, j.retweet, j.text))
        except:
            cursor.execute("INSERT INTO graph (node1, node2, text) VALUES (%s,%s,%s)",
                        (j.twitter_id, j.twitter_id, j.twitter_id))
#         except:
#             pass
        db_connection.commit()
    time.sleep(5)