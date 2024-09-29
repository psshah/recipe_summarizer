import os
from dotenv import load_dotenv
import json
import requests

# Load environment variables from .env file
load_dotenv()

# Get the API credentials from environment variables
app_id = os.getenv('EDAMAM_APP_ID')
app_key = os.getenv('EDAMAM_APP_KEY')

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
            f"* {quantity}: {unit}\n"
        )

    return formatted_nutrition_info

"""
    nutrition_info = f"Nutrition information for {recipe_name}:\n"

    for ingredient in ingredients:
        # Here you would typically make an API call or lookup nutrition data
        # for each ingredient. For now, we'll just add a placeholder.
        nutrition_info += f"- {ingredient}: Calories: N/A, Protein: N/A, Fat: N/A\n"

    return nutrition_info
"""

"""ingredients = ["1 cup of flour", "1 cup of sugar", "1 cup of water"]
nutrition_info = get_nutrition_info("cake batter", ingredients)
print(nutrition_info)
"""
