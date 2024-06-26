import requests
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime
import logging

# load environment variables from .env file
load_dotenv()

API_KEY = os.getenv('API_KEY')
MONGODB_URI = os.getenv('MONGODB_URI')
MONGODB_DB = os.getenv('MONGODB_DB')

# setting up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# connection to MongoDB
client = MongoClient(MONGODB_URI)
db = client[MONGODB_DB]


def get_weather(city):
    try:
        response = requests.get(
            f"https://api.openweathermap.org/data/2.5/"
            f"weather?q={city}&units=imperial&APPID={API_KEY}")
        response.raise_for_status()
        # print(response.json())
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error occurred: {http_err}")
    except Exception as err:
        logger.error(f"Other error occurred: {err}")
    return None


def insert_weather_data(data):
    try:
        weather_data = {
            'city': data['name'],
            'temperature': data['main']['temp'],
            'humidity': data['main']['humidity'],
            'description': data['weather'][0]['description'],
            'timestamp': datetime.now()
        }
        # print(weather_data)
        db.weather_data.insert_one(weather_data)
        logger.info(f"Weather data for {data['name']} stored in the database.")
    except Exception as e:
        logger.error(f"An error occurred while storing data: {e}")


def set_weather_alert(city, condition, value):
    try:
        alert = {
            'city': city,
            'condition': condition,
            'value': value,
            'timestamp': datetime.now()
        }
        db.weather_alerts.insert_one(alert)
        logger.info(f"Weather alert set for {city}: {condition} {value}")
    except Exception as e:
        logger.error(f"An error occurred while setting alert: {e}")


def check_weather_alerts():
    alerts = db.weather_alerts.find()
    for alert in alerts:
        city = alert['city']
        condition = alert['condition']
        value = alert['value']

        weather_data = get_weather(city)

        if weather_data:
            if condition == 'temperature' and weather_data['main']['temp'] >= value:
                print(f"Alert! The temperature in {city} is "
                f"{weather_data['main']['temp']}ºF, which is above {value}ºF.")
            elif condition == 'humidity' and weather_data['main']['humidity'] >= value:
                print(f"Alert! The humidity in {city} is "
                f"{weather_data['main']['humidity']}%, which is above {value}%.")


def main():
    user_input = input("Enter city: ")
    weather_data = get_weather(user_input)

    if weather_data and weather_data.get('cod') != '404':
        weather = weather_data['weather'][0]['main']
        temp = round(weather_data['main']['temp'])
        print(f"The weather in {user_input} is: {weather}")
        print(f"The temperature in {user_input} is: {temp}ºF")
        
        # storing the weather data in MongoDB
        insert_weather_data(weather_data)
        
        # setting a weather alert
        set_weather_alert(user_input, 'temperature', 75)  # setting an alert for temperatures above 75ºF
        set_weather_alert(user_input, 'humidity', 66) # added alert for humidity > 66

        # check and notify about weather alerts
        check_weather_alerts()
    else:
        print("No City Found")


if __name__ == "__main__":
    main()
