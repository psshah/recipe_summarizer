import os
from dotenv import load_dotenv
import json
import requests

# Load environment variables from .env file
load_dotenv()

# Get the API credentials from environment variables
app_id = os.getenv('EDAMAM_APP_ID')
app_key = os.getenv('EDAMAM_APP_KEY')
spoonacular_api_key=os.getenv('SPOONACULAR_API_KEY')

def get_nutrition_info(recipe_name, ingredients):
    if not app_id or not app_key:
        raise ValueError("EDAMAM_APP_ID and EDAMAM_APP_KEY must be set in environment variables")

    url = f"https://api.edamam.com/api/nutrition-details?app_id={app_id}&app_key={app_key}"
    print(url)

    # create a json object with the recipe name and ingredients
    data = {
        "title": recipe_name,
        "ingr": ingredients
    }

    # convert the json object to a string
    data_string = json.dumps(data)

    # make the API call
    # Set the headers for the request
    headers = {
        'Content-Type': 'application/json'
    }

    # Make the POST request
    response = requests.post(url, headers=headers, data=data_string)

    # Check if the request was successful
    if response.status_code != 200:
        return f"Error fetching data: {response.status_code} - {response.reason}"

    data = response.json()

    total_nutrients = data.get('totalNutrients', {})
    if not total_nutrients:
        return "Total nutrients info not found."

    # Initialize an empty dictionary to store the selected nutrients
    selected_nutrients = {}

    # List of keys we're interested in
    keys_of_interest = ['CHOLE', 'PROCNT', 'SUGAR', 'FIBTG', 'CHOCDF.net', 'FAT']

    for key in total_nutrients.keys():
        if key in keys_of_interest:
            selected_nutrients[key] = total_nutrients[key]

    formatted_nutrition_info = "The Edamam API returned nutrition info for " + recipe_name + ":\n"

    for key, value in selected_nutrients.items():
        print(f"- {key}: {value['quantity']} {value['unit']}")
        quantity = value['quantity']
        unit = value['unit']
        formatted_nutrition_info += (
            f"* {key}: {quantity} {unit}\n"
        )

    return formatted_nutrition_info

def get_recipe_by_ingredients(ingredients_list):
    print("Called get_recipe_by_ingredients")
    #print(ingredients_list)
    if not spoonacular_api_key:
        raise ValueError("SPOONACULAR_API_KEYmust be set in environment variables")

    ingredients_list = ingredients_list.replace(" ", "")
    url = f"https://api.spoonacular.com/recipes/findByIngredients?ingredients={ingredients_list}&apiKey={spoonacular_api_key}&number=3&limitLicense=true&ranking=1&ignorePantry=false"
    print(url)

    # Make the GET request
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code != 200:
        return f"Error fetching data: {response.status_code} - {response.reason}"

    data = response.json()
    recipe_names = [recipe['title'] for recipe in data]
    #print(recipe_names)

    # Create a formatted string
    formatted_response = "The Spoonacular API returned recipe names for " + ingredients_list + ":\n"
    formatted_names = ', '.join(recipe_names)
    print(formatted_response + formatted_names)

    return formatted_response + formatted_names
