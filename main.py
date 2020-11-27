# Import packages and config
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import datetime
import twitter_cred
import csv
import re

# Takes tweets and a designated csv file and writes them to it.


class StdOutListener(StreamListener):

    def on_status(self, status):
#         h={}
        # Filtering English language tweets from users 
        if (status.lang == "en"):
            # Creating this formatting so when exported to csv the tweet stays on one line
            tweet_text = "'" + status.text.replace('\n', ' ') + "'"
            tweet_lenght=Wordslenght(tweet_text)
            sent,sub=SA(tweet_text)[0],SA(tweet_text)[0]
            
            try:
                List = tweet_text.lower().split( ' ' )
                hashtags = [i for i in List if i.startswith('#')]
#                 mentions = [i for i in List if i.startswith('@')]
            except:
                    hashtags = 'no_hastags'
#                     mentions = 'no_mentions'
            try: 
                imageurl= status.entities['media'][0]['media_url']
            except:
                imageurl = 'None'
            try: 
                location= status.user.location
            except:
                location= 'unknown'
            try:
                List = tweet_text.lower().split( ' ' )
#                 hashtags = [i for i in List if i.startswith('#')]
                mentions = [i for i in List if i.startswith('@')]
            except:
#                     hashtags = 'no_hastags'
                    mentions = 'no_mentions'
                
            try: 
                retweet = status.retweeted_status.id
            except:
                retweet = 'None' 
#             urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', tweet_text)
#             spltAr = url.split("://");
#             i = (0,1)[len(spltAr)>1];
#             dm = spltAr[i].split("?")[0].split('/')[0].split(':')[0].lower()    
            try: 
                reply = status.retweeted_status.reply_count
            except:
                reply = status.reply_count
                
            try: 
                retweeted = status.retweeted_status.retweet_count
            except:
                retweeted = status.retweet_count
                
            
            csvw.writerow([status.id,
                           status.user.screen_name, tweet_lenght,sent,sub,
                           # created_at is a datetime object, converting to just grab the month/day/year
                           status.created_at,
                           status.user.followers_count,
                           tweet_text, location, status.user.verified, status.user.protected,
                           status.user.description
                           , status.user.friends_count,
                           status.user.favourites_count,retweet, hashtags, mentions,
                           reply, status.source, imageurl,
                           retweeted
                          ])
            return True

    def on_error(self, status_code):
        if status_code == 420:
            # returning False in on_error disconnects the stream
            return False
        
def Wordslenght(s):
    s = s.split(' ')
    return len(s)
from textblob import TextBlob
def SA(text):
    blob = TextBlob(text)
    p,s= blob.sentiment
    if p>0:
        p=1
    elif p == 0:
        p= 0
    else:
        p= -1
    if s > 0:
        s= 1
    else:
        s= 0
    return [p,s]

import pandas as pd
import numpy as np
from catboost import CatBoostClassifier, Pool
rh=pd.read_csv('ml.csv')
rh=rh[:108]
rh=rh[['twitter_id','followers_count', 
        'location', 'verified','protected', 'friendscount', 
        'favorites_count','reply', 
        'source','retweet_from_original',
       'sentiment', 'subjectivity',
     'twt_lenght','label']]
cat= ['location', 'verified','protected','source']
# from sklearn import preprocessing
# le = preprocessing.LabelEncoder()
# for i in cat:
#     le.fit(rh[i])
#     rh[i]=le.transform(rh[i])
rh=rh.replace([np.inf, -np.inf], 0)
# rh = rh.astype(float) 
X=rh.drop('label', axis=1)
y=rh['label']

params = {'loss_function':'Logloss', # objective function
          'eval_metric':'AUC', # metric
          'verbose': 200, # output to stdout info about training process every 200 iterations
          'random_seed': 8
         }
cbc_1 = CatBoostClassifier(**params)
cbc_1.fit(X, y,cat_features=['location', 'verified','protected','source'])
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
create_table = """ CREATE TABLE IF NOT EXISTS twitter_tweets(
    id INT(11) NOT NULL AUTO_INCREMENT,
    fake BIGINT(20),
    reall BIGINT(20),
    PRIMARY KEY (id)
)"""
cursor.execute(create_table)
from interruptingcow import timeout
import os
# This handles Twitter authetification and the connection to Twitter Streaming API
l = StdOutListener()
auth = OAuthHandler(twitter_cred.consumer_key, twitter_cred.consumer_secret)
auth.set_access_token(twitter_cred.Access_token, twitter_cred.Access_token_secret)
stream = Stream(auth, l)
while True:
    try:
#         os.remove("blank.csv") 
        csvw = csv.writer(open("blank.csv", "a"))
        csvw.writerow(['twitter_id', 'name','twt_lenght','sentiment','subjectivity', 'created_at',
                   'followers_count', 'texts', 'location', 'verified', 'protected', 'description'
                   , 'friendscount', 'favorites_count', 'retweet','hashtags', 'mentions', 'reply','source', 'images',
                   'retweet_from_original'])
        try:
            with timeout(8, exception=RuntimeError):
                while True:
                    # Filter based on listed items        
                    stream.filter(track=['Covid-19','Coronavirus','pandemic'])
    #                 if test == 5:
    #                     break
    #                 test = test - 1

        except RuntimeError:
            pass
        pj=pd.read_csv('blank.csv')
        pj=pj.fillna('unknown')
    #     pj=pj.loc[yp['location']!="True"]
    #     pj=pj.loc[yp['location']!="False"]
        yp=pj[['twitter_id','followers_count', 
        'location', 'verified','protected', 'friendscount', 
        'favorites_count','reply', 
        'source','retweet_from_original',
       'sentiment','twt_lenght']]
    #     ypu=yp.loc[yp['location']!="True"]
    #     yp=yp.loc[yp['location']!="False"]
        label=cbc_1.predict(pd.DataFrame(yp))
        pj['label']=label
        fak=pj.loc[pj.label=='1']
        fak.to_csv('results.csv')
        cursor.execute("INSERT INTO twitter_tweets (fake, reall) VALUES (%s,%s)",
                    (len(pj.loc[pj.label=='1']), len(pj.loc[pj.label=='0'])))

        db_connection.commit()
    os.remove("blank.csv") 
    except:
        pass
