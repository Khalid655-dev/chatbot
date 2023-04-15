import json
import mysql.connector
import requests
from flask import Flask, request, jsonify
from database import cnx, cursor

app = Flask(__name__)

cnx = mysql.connector.connect(user='root', password="Khalid@123",
                              host='localhost', database='weightbuddy')
cursor = cnx.cursor()


def call_nutritionix_api(api_endpoint, headers, data):
    response = requests.post(api_endpoint, headers=headers, json=data)
    response.raise_for_status()
    return response.json()


@app.route('/webhook', methods=['POST'])
def webhook():
    # Parse the Dialogflow request
    request_data = request.get_json(silent=True, force=True)
    intent_display_name = request_data['queryResult']['intent']['displayName']
    # try:
    #     cnx = mysql.connector.connect(user='root', password='Khalid@123', host='127.0.0.1', database='weightbuddy')
    #     cursor = cnx.cursor()
    # Handle the intent and return the response
    if intent_display_name == 'FoodAPI':
        query = request_data['queryResult']['queryText']
        api_endpoint = "https://trackapi.nutritionix.com/v2/natural/nutrients"
        headers = {
            "x-app-id": "4ccbce16",
            "x-app-key": "3862204927304b49317454dc09abc94e",
            "Content-Type": "application/json"
        }
        data = {
            "query": query
        }
        data = call_nutritionix_api(api_endpoint, headers, data)
        if 'foods' in data:
            food_name = data['foods'][0]['food_name']
            calories = data['foods'][0]['nf_calories']
            full_nutrients = json.dumps(data['foods'][0]['full_nutrients'])
            protein = data['foods'][0]['nf_protein']
            total_fat = data['foods'][0]['nf_total_fat']
            total_carbohydrate = data['foods'][0]['nf_total_carbohydrate']
            response_text = f"{food_name} contains {calories} calories, {protein} protein, {total_fat} total_fat," \
                            f" and {total_carbohydrate} total carbohydrates"
            response = {
                'fulfillmentText': response_text,
                'payload': {
                    'nutrition': {
                        'food_name': food_name,
                        'calories': calories
                    }
                }
            }

            # Insert the conversation record into the MySQL table
            insert_query = """
            INSERT INTO food_lookup_conversations (query_text, food_name, calories, full_nutrients, protein, total_fat, total_carbohydrate)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            insert_values = (query, food_name, calories, full_nutrients, protein, total_fat, total_carbohydrate)
            if not cnx.is_connected():
                cnx.reconnect()

            cursor.execute(insert_query, insert_values)
            cnx.commit()
        else:
            response_text = "I couldn't find the nutrition information for that food."
            response = {
                'fulfillmentText': response_text,
                'payload': {}
            }

    elif intent_display_name == 'SearchFood':
        query = request_data['queryResult']['queryText']
        api_endpoint = "https://trackapi.nutritionix.com/v2/search/instant"
        headers = {
            "x-app-id": "4ccbce16",
            "x-app-key": "3862204927304b49317454dc09abc94e",
            "Content-Type": "application/json"
        }
        params = {
            "query": query
        }
        data = call_nutritionix_api(api_endpoint, headers, params)
        if 'branded' in data:
            food_results = data['branded']
            for food in food_results:
                food_name = food['food_name']
                serving_unit = food['serving_unit']
                insert_query = """
                INSERT INTO food_search_results (query_text, food_name, serving_unit)
                VALUES (%s, %s, %s) """
                insert_values = (query, food_name, serving_unit)
                cursor.execute(insert_query, insert_values)
                cnx.commit()
            response_text = f"I found {food_name} with serving unit: {serving_unit}."
            response = {
                'fulfillmentText': response_text,
                'payload': {
                    'search_results': food_results
                }
            }
        else:
            response_text = "I couldn't find any matching foods."
            response = {
                'fulfillmentText': response_text,
                'payload': {}
            }
    else:
        response = {
            'fulfillmentText': "I'm sorry, I don't understand.",
            'payload': {}
        }

    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)
