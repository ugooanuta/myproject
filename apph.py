from pymongo import MongoClient
from flask import Flask, jsonify, json


# Connect to MongoDB 
#client = MongoClient("mongodb+srv://nutriousio:cscs@mycluster.s7bglaq.mongodb.net/nio?retryWrites=true&w=majority")

# Database name & collection name
#db = client.nio
#collection = db.recipe

client_2 = MongoClient("mongodb://localhost:27017/")
mydb = client_2["mydatabase"]
historyCollection = mydb["usershistory"]
recipeCollection = mydb["recipes"]


#this method gets checks the database to find the a user's historyObject, extract the macros for a date
def get_date_macros(user_email, string_date):

    user_data = historyCollection.find_one({"user": user_email})

    
    #create and insert a new userhistory object into the database
    if (user_data == None):
        
         create_aUser_history(user_email)
         print("\nA new user macros and meal History Object has been created and added into the database")

         return None


    #extract the calories and Macros datas
    user = user_data["user"]
    allmacros_per_day = user_data["macros_per_day"]
    
    #handles an key error exception if the date is not already in the userHistory object 
    try:
        nutrients_on_date = allmacros_per_day[string_date]
    
    except(KeyError):
        
        print(f"The system will log in the macros this new date: {string_date} ")

        return None

    #extract more data from the userHistory Object
    meal = nutrients_on_date["meals"]
    calorie = nutrients_on_date["calories"]
    macros = nutrients_on_date["macros"]

    carbs = macros["carbs"]
    protein = macros["protein"]
    fat = macros["fat"]
    
    #creates a list object that the other update function can use to increament the values of macros
    macrosValue_list = [calorie, carbs, protein, fat]

    #print this the console
    print(f"User: {user} ===")  
    print(f"Daily Macros on date = {string_date}:")
    print("meals on this day", meal)
    print("calorie:", calorie)
    print("MacroNutrients:", macros)
    print("\n")

    #returns the list 
    return macrosValue_list



#This method is used to update the a user's  history object
def update_todays_macros(newfood_recipe, user_email, today_date):
   
   #a method call to the get_date_macros to get the list of a existing macros in users historyObject
   alist_of_existing_macros = get_date_macros(user_email, today_date)

   #get the user's history Object from the database
   user_data = historyCollection.find_one({"user": user_email})

   
   if (user_data == None):
        
        user_data = create_aUser_history(user_email)
         


   #when the get_date_macros returns Null Object
   if (alist_of_existing_macros == None):

        #the values in the list are all initialized to zero 
       alist_of_existing_macros = [0, 0, 0]
       
   
   #get the recipe object the user is object from database to choosen and extract it's macros
   recipe = recipeCollection.find_one({"name": newfood_recipe})
   type = recipe["type"]

   #extract the macros data from the recipe object
   recipe_calorie = recipe["macros"]["calories"]
   recipe_carbs = recipe["macros"]["carbs"]
   recipe_protein = recipe["macros"]["protein"]
   recipe_fat = recipe["macros"]["fat"]
 
   #make list of the values of the new recipe to update
   recipe_macrolist = [recipe_calorie, recipe_carbs, recipe_protein, recipe_fat]

   #check if the date is a new date
   if_date_exist = check_date(user_data["macros_per_day"], today_date)


   #if the date is new
   if(if_date_exist == None and sum(alist_of_existing_macros) == 0):
       
       print("\na new date object created!")

       #a call to create_new_daily_macros function 
       foodhistory_for_date = create_new_daily_macros(recipe_macrolist, today_date)
       
       user_data["macros_per_day"].update(foodhistory_for_date)

       #update inserts a new date object in the macros_per_day object of the userHistory object
       historyCollection.update_one({'email': user_email}, {'$set': { 'macros_per_day' : foodhistory_for_date }}, upsert= True)

       
       user_data["macros_per_day"][today_date].update({"meals" : {type: recipe["name"]} })
       
       print(user_data)

       return None

    
   #if the date is already existing in the users history Object
   user_data["macros_per_day"][today_date]["meals"].update({type: recipe["name"]})

   #insert/update the name of the meal and the type(breakfast, lunch or dinner) in the database
   historyCollection.update_one({"email": user_email}, {'$set' : {'macros_per_day.' + today_date + '.meals.' + type : recipe["name"]}})
  
   #increament the already existing macros by adding the new to the old values
   new_cal = recipe_calorie + alist_of_existing_macros[0]
   new_carbs = recipe_carbs + alist_of_existing_macros[1]
   new_protein = recipe_protein + alist_of_existing_macros[2]
   new_fat = recipe_fat + alist_of_existing_macros[3]
    

   #update the values of the all the macros in the user's history object in the database
   historyCollection.update_one({'email': user_email}, {'$set': { 'macros_per_day.' + today_date + '.calories' : new_cal, 'macros_per_day.' + today_date + '.macros.carbs': new_carbs, 'macros_per_day.' + today_date + '.macros.protein': new_protein, 'macros_per_day.' + today_date + '.macros.fat': new_fat}})


   user_data["macros_per_day"][today_date]["calories"] = new_cal
   user_data["macros_per_day"][today_date]["macros"]["carbs"] = new_carbs
   user_data["macros_per_day"][today_date]["macros"]["protein"] = new_protein
   user_data["macros_per_day"][today_date]["macros"]["fat"] = new_fat


   #print the updated user history data
   print(user_data)

   return "update successfull"


#This function creates a new date object 
def create_new_daily_macros(list_one, date):
   
    macros_dict = { date : {"meals": {}, "calories" : list_one[0], "macros" : {"carbs" : list_one[1], "protein": list_one[2], "fat": list_one[3]}}}

    #return the data objecct
    return macros_dict


#This function creates a new user macros history and inserts the it into the database 
def create_aUser_history(email):

    newUserhistory = {"email" : email, "macros_per_day": {}}
    inserted = historyCollection.insert_one(newUserhistory)

    #returns the inserted object
    #return inserted
    return newUserhistory  


#This fuction check if a date is new, if new might cause a keyerror
def check_date(dict_oject, adate):

    #try and catches the key error
    try:
        value = dict_oject[adate]

    except(KeyError):

        return None
    


#some test calls
update_todays_macros("Shrimp Quesadilla", "marklucas@gmail.com", "03/31/23")

update_todays_macros("Shrimp Quesadilla", "existinguser@gmial.com", "03/31/23")

update_todays_macros("Shrimp Quesadilla", "existinguser@gmail.com", "04/31/23")

# Close the connection to MongoDB
client_2.close()


