from pymongo import MongoClient
from flask import Flask, jsonify, json

# Connect to MongoDB
client_2 = MongoClient("mongodb+srv://nutriousio:cscs@mycluster.s7bglaq.mongodb.net/nio?retryWrites=true&w=majority")


# Database name & collection name
db = client_2.nio
recipeCollection = db.recipe
historyCollection = db.usershistory
userCollection = db.user
mealco = db.food_info


def extract_meals(meal, user_email):

    meal_calorie = meal["energy_per_100g"]
    meal_carbs = meal["macro_carbohydrate_per_100g"]
    meal_protein = meal["macro_protein_per_100g"]
    meal_fat = meal["macro_fat_per_100g"]
     
    meal_date = "2023-04-12T18:42:30.929Z"

    allrecipe_calorie = 0
    allrecipe_carbs = 0
    allrecipe_protein = 0
    allrecipe_fat = 0

    user_history = userCollection.find_one({"email": user_email})

    dailymeals = user_history["meals"]

    for meals in dailymeals:

       if meals["date"] == meal_date:

            meals_on_this_date = meals["meal"]

            for recipe in meals_on_this_date:

                allrecipe_calorie += recipe["calories"]
                allrecipe_carbs += recipe["carbs"]
                allrecipe_protein += recipe["protein"]
                allrecipe_fat += recipe["fat"]


    new_calorie = allrecipe_calorie + meal_calorie
    new_carbs = allrecipe_carbs + meal_carbs
    new_protien = allrecipe_protein + meal_protein
    new_fat = allrecipe_fat + meal_fat

    new_allmacros = [new_calorie, new_carbs, new_protien, new_fat]

    print(new_allmacros)



meal_date = "2023-04-12T18:42:30.929Z"
allrecipe_calorie = 0
allrecipe_carbs = 0
allrecipe_protein = 0
allrecipe_fat = 0

user_history = userCollection.find_one({"email": "test@test.com"})

dailymeals = user_history["meals"]

for meals in dailymeals:

    if meals["date"] == meal_date:

        meals_on_this_date = meals["meal"]

        for recipe in meals_on_this_date:

            allrecipe_calorie += recipe["calories"]
            allrecipe_carbs += recipe["carbs"]
            allrecipe_protein += recipe["protein"]
            allrecipe_fat += recipe["fat"]


alist_of_daily_macros_values = [allrecipe_calorie, allrecipe_carbs, allrecipe_protein, allrecipe_fat]

print(alist_of_daily_macros_values) 

toEat = mealco.find_one({"description": "Cake or cupcake, banana"})

extract_meals(toEat, "test@test.com")

app.route('/')
def home():
    return render_template("home.html")


@app.route('/sumofdaymacros')
def sumofdaymacros():
 
    allrecipe_calorie = 0
    allrecipe_carbs = 0
    allrecipe_protein = 0
    allrecipe_fat = 0

    user_history = userCollection.find_one({"email": 'test@test.com'})

    dailymeals = user_history["meals"]

    for meals in dailymeals:

        if meals["date"] == "2023-04-12T18:42:30.929Z":

            meals_on_this_date = meals["meal"]

            for recipe in meals_on_this_date:

                allrecipe_calorie += recipe["calories"]
                allrecipe_carbs += recipe["carbs"]
                allrecipe_protein += recipe["protein"]
                allrecipe_fat += recipe["fat"]

        alist_of_daily_macros_values = [allrecipe_calorie, allrecipe_carbs, allrecipe_protein, allrecipe_fat]

    print(alist_of_daily_macros_values)
      
    return jsonify(alist_of_daily_macros_values)



@app.route('/savemeal/')
def savemeal():

    email = 'test@test.com'    #request.json['email']
    history_date =  "2023-04-13T18:16:17.986Z"  #request.json['date']
    new_meal = mealco.find_one({"description": "Cake or cupcake, banana"})   #request.json['meal'],
    meal_type =  "user"  #request.json['mealType']


    if meal_type == "user":
        #extract the macros of the new meal to updated
        todate_calorie = new_meal["energy_per_100g"]
        todate_carbs = new_meal["macro_carbohydrate_per_100g"]
        todate_protein = new_meal["macro_protein_per_100g"]
        todate_fat = new_meal["macro_fat_per_100g"]


    if meal_type == "recipe":
        # extract the macros' data from the recipe object
        todate_calorie = new_meal["macros"]["calories"]
        todate_carbs = new_meal["macros"]["carbs"]
        todate_protein = new_meal["macros"]["protein"]
        todate_fat = new_meal["macros"]["fat"]


    user_history = userCollection.find_one({"email": email})

    dailymeals = user_history["meals"]

    for meals in dailymeals:
        
        index = str(dailymeals.index(meals))

        if meals["date"] == history_date:
            
            meals_on_this_date = meals["meal"]

            for recipe in meals_on_this_date:
                
                if meal_type == "user":

                   #extract the macros of the new meal to updated
                   todate_calorie += recipe["calories"]
                   todate_carbs += recipe["carbs"]
                   todate_protein += recipe["protein"]
                   todate_fat += recipe["fat"]
                
                if meal_type == "recipe":
                    
                    #extract the macros' data from the recipe object
                    todate_calorie += recipe["macros"]["calories"]
                    todate_carbs += recipe["macros"]["carbs"]
                    todate_protein += recipe["macros"]["protein"]
                    todate_fat += recipe["macros"]["fat"]

            db.user.update_one({'email': email}, {'$push': {'meals.' + index + '.meal': new_meal}}) 
            
            db.user.update_one({'email': email}, {'$set': {'meals.' + index + '.daily_Macros':  {"calories" : todate_calorie, "carbs" : todate_carbs, "protein" : todate_protein, "fat": todate_fat} }}) 

            return  jsonify({'message': 'Meal saved successfully in existing date'})

    
    meal = {
        
        'date': history_date,
        'meal': new_meal,
        'mealType': meal_type,
        'daily_Macros' : {"calories" : todate_calorie, "carbs" : todate_carbs, "protein" : todate_protein, "fat": todate_fat}

    }
    
    db.user.update_one({'email': email}, {'$push': {'meals': meal}})

    return jsonify({'message': 'Meal saved successfully in a new date'})


