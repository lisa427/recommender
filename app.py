from flask import Flask, render_template, redirect, jsonify, request
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from os import environ

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")
    
@app.route("/pandas")
def pandas():
    return render_template("pandas.html")  

@app.route('/autocomplete_data', methods=['GET'])
def autocomplete_data():

    #create engine to connect to SQL database
    db_connection_string = "postgres:postgres@localhost:5432/books_db"
    db_url = environ.get('DATABASE_URL', f'postgresql://{db_connection_string}')
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    engine = create_engine(db_url)
    #connect to SQL database
    connection = engine.connect()

    # creat dataframe of titles from database
    title_df = pd.read_sql('SELECT title \
        FROM booksdesc;' , connection)  
    
    # create list of titles
    title_list = title_df['title'].values.tolist()
    
    # return the list of titles
    response = jsonify(title_list)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

    
@app.route('/results', methods=['POST'])
def results():

    #create engine to connect to SQL database
    db_connection_string = "postgres:postgres@localhost:5432/books_db"
    db_url = environ.get('DATABASE_URL', f'postgresql://{db_connection_string}')
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    engine = create_engine(db_url)
    #connect to SQL database
    connection = engine.connect()

    # creat dataframe from database
    df = pd.read_sql('SELECT index, title, authors, publisher, \
        categories, thumbnail, description \
        FROM booksdesc;' , connection)
    
    # combine text columns to analyze into one
    df['all'] = df['title'] + df['authors'] + df['publisher'] + df['categories'] + df['description']
    
    # set vectorizer as TFIDvectorizer from sklearn
    vectorizer = TfidfVectorizer(analyzer='word')

    # returns a matrix of the documents & TF-IDF calculations
    tfidf_all_content = vectorizer.fit_transform(df['all'])

    # create cosine similarity matrix
    cosine_similarity_all_content = linear_kernel(tfidf_all_content, tfidf_all_content)

    # create new dataframe with reset index
    books = df.reset_index(drop=True)

    # create a series of the indexes
    indices = pd.Series(books["title"].index)

    # get book title entered by the user
    user_title = request.form["booktitle"]
    
    try:

        # use user's book title to find index of that book
        input_array = books[books["title"] == user_title].index.values
        input_index = input_array[0]

        # function to get the most similar books
        def recommend(index, method):
            id = indices[index]
            similarity_scores = list(enumerate(method[id]))
            similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
            similarity_scores = similarity_scores[1:11]
            books_index = [i[0] for i in similarity_scores]
            titles = books['title'].iloc[books_index]
            authors = books['authors'].iloc[books_index]
            a_zip = zip(titles, authors)
            data = list(a_zip)
            return data

        # pass the book index & cosine similarities to create list of recommended books
        book_list = recommend(input_index, cosine_similarity_all_content)

        # returns chosen book & table of recommended books
        return render_template("pandas.html", book_text='Recommendations if you like {}:'.format(user_title), \
            results_table=book_list)  

    except IndexError:
        # returns message if chosen book is not in the database
        return render_template("pandas.html", book_text='Book not found, please try another.')  
    
        

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=environ.get('PORT', 5000), debug=True)