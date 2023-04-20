from pymongo import MongoClient
from flask import Flask, jsonify, json

# Connect to MongoDB
client_2 = MongoClient("mongodb+srv://nutriousio:cscs@mycluster.s7bglaq.mongodb.net/nio?retryWrites=true&w=majority")


# Database name & collection name
db = client_2.nio
recipeCollection = db.recipe
historyCollection = db.usershistory

# this function gets checks the database to find the user's historyObject, extract the macros for a date
def get_date_macros(user_email, string_date):
    user_data = historyCollection.find_one({"email": user_email})

    # returns a None value if the user is not in the database history collection
    if user_data is None:
        return None

    # extract the calories and Macros datas
    user = user_data["email"]
    macros_per_day = user_data["macros_per_day"]

    # handles an key error exception if the date is not already in the userHistory object
    try:
        nutrients_on_date = macros_per_day[string_date]

    except KeyError:

        print(f"The system will log in the macros this new date: {string_date} ")

        return None

    # extract more data from the userHistory Object
    meal = nutrients_on_date["meals"]
    calorie = nutrients_on_date["calories"]
    macros = nutrients_on_date["macros"]

    carbs = macros["carbs"]
    protein = macros["protein"]
    fat = macros["fat"]

    # creates a list object that the other update function can use to increament the values of macros
    macros_value_list = [calorie, carbs, protein, fat]

    # returns the list
    return macros_value_list



# This function is used to update the user's  history object
def update_todays_macros(newfood_recipe, user_email, today_date):


    # get the user's history Object from the database
    user_data = historyCollection.find_one({"email": user_email})

    if user_data is None:
        user_data = create_one_user_history(user_email)

    # a method call to the get_date_macros to get the list of a existing macros in users historyObject
    alist_of_existing_macros = get_date_macros(user_email, today_date)


    # when the get_date_macros returns Null Object
    if alist_of_existing_macros is None:
        # the values in the list are all initialized to zero
        alist_of_existing_macros = [0, 0, 0]

    # get the recipe object the user is object from database to chosen and extract its macros
    recipe = recipeCollection.find_one({"name": newfood_recipe})
    recipe_name = recipe["name"]
    type = recipe["type"]

    # extract the macros' data from the recipe object
    recipe_calorie = recipe["macros"]["calories"]
    recipe_carbs = recipe["macros"]["carbs"]
    recipe_protein = recipe["macros"]["protein"]
    recipe_fat = recipe["macros"]["fat"]

    # make list of the values of the new recipe to update
    recipe_macrolist = [recipe_calorie, recipe_carbs, recipe_protein, recipe_fat]

    # check if the date is a new date
    if_date_exist = check_date(user_data["macros_per_day"], today_date)


    # if the date is new and the list of macros sums to zero
    if if_date_exist is None and sum(alist_of_existing_macros) == 0:

        # a call to create_new_daily_macros function
        food_history_for_date = create_new_daily_macros(recipe_macrolist, today_date, type, recipe_name)

        # update inserts a new date object in the macros_per_day object of the userHistory object
        historyCollection.update_one({'email': user_email}, {'$set' : {'macros_per_day.' + today_date : food_history_for_date}}, upsert=True)
        
        return None


    # if the date is already existing in the users history Object
    # insert/update the name of the meal and the type(breakfast, lunch or dinner) in the database
    historyCollection.update_one({"email": user_email},
                                 {'$set': {'macros_per_day.' + today_date + '.meals.' + type: recipe["name"]}})

    # increment the already existing macros by adding the new to the old values
    new_cal = recipe_calorie + alist_of_existing_macros[0]
    new_carbs = recipe_carbs + alist_of_existing_macros[1]
    new_protein = recipe_protein + alist_of_existing_macros[2]
    new_fat = recipe_fat + alist_of_existing_macros[3]

    # update the values of the all the macros in the user's history object in the database
    historyCollection.update_one({'email': user_email},
                                 {'$set': {'macros_per_day.' + today_date + '.calories': new_cal,
                                           'macros_per_day.' + today_date + '.macros.carbs': new_carbs,
                                           'macros_per_day.' + today_date + '.macros.protein': new_protein,
                                           'macros_per_day.' + today_date + '.macros.fat': new_fat}})

    
    return None



# This function creates a new date object
def create_new_daily_macros(list_one, date, type, name):
      
    macros_dict = {"meals": {type:name}, "calories": list_one[0],
                          "macros": {"carbs": list_one[1], "protein": list_one[2], "fat": list_one[3]}}

    # return the data object
    return macros_dict


# This function creates a new user macros history and inserts it into the database
def create_one_user_history(email):

    new_user_history = {"email": email, "macros_per_day": {}}
    # FIXME: inserted is not used.
    inserted = historyCollection.insert_one(new_user_history)

    # returns the inserted object
    return new_user_history


# This function check if a date is new, if new might cause a key error
def check_date(dict_obj, date):
    # try and catches the key error
    try:

        value = dict_obj[date]

        return value

    except KeyError:

        return None
    

# some test calls
update_todays_macros("Chicken Soup with Chiles", "nioUser2@gmail.com", "05/31/23")

# Close the connection to MongoDB
client_2.close()