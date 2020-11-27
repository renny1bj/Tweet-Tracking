from flask import Flask,render_template,url_for,request,redirect, make_response
import random
import json
import os
import mysql.connector
from time import time
from random import random
from flask import Flask, render_template, make_response

app = Flask(__name__)

class Database:
    def __init__(self):
        host='127.0.0.1'
        user='root'
        db="test"

        self.con = mysql.connector.connect(host=host,
                                            user=user,
                                            db=db)
        self.cur=self.con.cursor()
    def list_tweets(self):
        self.cur.execute("SELECT fake, reall FROM twitter_tweets")
        result=self.cur.fetchall()
        return result

    def lgraph(self):
        self.cur.execute("SELECT node1, node2, text FROM graph")
        resul=self.cur.fetchall()
        return resul

@app.route('/home', methods=["GET", "POST"])
def main():
    return render_template('index.html')

@app.route('/graph', methods=["GET", "POST"])
def graph():
    return render_template('home.html')

@app.route('/timeline', methods=["GET", "POST"])
def timee():
    return render_template('timeline.html')




def db_graph():
    db=Database()
    node=db.lgraph()
    return node
@app.route('/graphdata', methods=["GET", "POST"])
def mains():
    need=db_graph()
    node1= need[-1][0]
    text= need[-1][2]
    datum = [node1, text]

    response = make_response(json.dumps(datum))

    response.content_type = 'application/json'

    return response


def db_query():
    db=Database()
    products=db.list_tweets()
    return products
@app.route('/data', methods=["GET", "POST"])
def data():
    res = db_query()
    print (res)
    Temperature = res[-1][1]
    Humidity = res[-1][0]
    fakesum= sum([i[1] for i in res])
    realsum= sum([i[0] for i in res])
    print(res)
    data = [time() * 1000, Temperature, Humidity,fakesum,realsum]

    response = make_response(json.dumps(data))

    response.content_type = 'application/json'

    return respose


if __name__ == "__main__":
    app.run(debug=True)
