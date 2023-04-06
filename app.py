
from flask import Flask, render_template, redirect, url_for, jsonify, request
import uuid
#from database import mycol
from passlib.hash import pbkdf2_sha256
import apph
from pymongo import MongoClient


client_2 = MongoClient("mongodb://localhost:27017/")
mydb = client_2["mydatabase"]
historyCollection = mydb["usershistory"]
recipeCollection = mydb["recipes"]


app = Flask(__name__)


@app.route('/')
def home():
    return render_template("home.html")


@app.route('/submit', methods = ['POST', 'GET'])
def submit():

    new_recipe = request.form["name"]
    user_email = request.form["email"]
    date = request.form["password"]

    apph.update_todays_macros(new_recipe, user_email, date)

    user = historyCollection.find_one({"email": "anutaugochukwu@gmail.com"})

    return jsonify(user)

@app.route('/display', methods = ['GET'])
def display():
    
    new_recipe = request.form["name"]
    user_email = request.form["email"]
    date = request.form["password"]

    display_data = apph.get_date_macros(user_email, date)

    return display_data


@app.route('/test', methods = ['POST', 'GET'])
def test():

       historyCollection.update_one({'email': "anutaugochukwu@gmail.com"}, {'$set': { 'macros_per_day' : { "03/30/23" : { "calories" : 150, "macros" : { "carbs" : 10, "protein": 20, "fat": 30}}}}})
       user = historyCollection.find_one({"email": "anutaugochukwu@gmail.com"})

       return jsonify(user)

if __name__ == "__main__":
    app.run(debug=True)