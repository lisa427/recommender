from flask import Flask, render_template, redirect, jsonify, request
import pymongo
from flask_pymongo import PyMongo 
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc
import pandas as pd


app = Flask(__name__)

# rds_connection_string = "postgres:postgres@localhost:5432/books_db"
# engine = create_engine(f'postgresql://{rds_connection_string}')

@app.route("/")
def index():
    return render_template("index.html")
    
@app.route("/pandas")
def pandas():
    return render_template("pandas.html")
@app.route("/data")
def raw_data():
    return render_template("raw_data.html")
@app.route("/api")
def api():
    return render_template("api.html")
@app.route("/documents")    
def documents():
    return render_template("documents.html")    
    
@app.route('/results', methods=['POST'])
def results():

    #create engine to connect to SQL database
    rds_connection_string = "postgres:postgres@localhost:5432/books_db"
    engine = create_engine(f'postgresql://{rds_connection_string}')
    #connect to SQL database
    connection = engine.connect()

    # creat dataframe from database
    book_df = pd.read_sql('SELECT index, title, authors, publisher, \
        categories, thumbnail \
        FROM books;' , connection)
    
    user_request = request.form["booktitle"]
    print(user_request)

    books_10 = book_df.head(10)
    book_list = books_10["title"].values.tolist()
    
    return render_template("pandas.html", results_text='{}'.format(book_list))    
    
    

    

if __name__ == "__main__":
    app.run(debug=True)