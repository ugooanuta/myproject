
from flask import Flask, render_template, redirect, url_for, jsonify, request
import uuid
from database import mycol


app = Flask(__name__)


@app.route('/')
def home():
    return render_template("home.html")


@app.route('/dashboard/')
def dashboard():
    return "dashboard loading"


@app.route('/user/signup', methods = ['POST'])
def newclient():

    from signup.cases import Client


    user_signup_data = Client().signup()
        
    signup_db = mycol.insert_one(user_signup_data)

    return signup_db.inserted_id


@app.route("/database_info/<email>")
def database(email):

    myquery = { "email": email }

    mydoc = mycol.find(myquery)

    print(mydoc)

    return "found"



if __name__ == "__main__":
    app.run(debug=True)