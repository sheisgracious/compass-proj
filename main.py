import requests
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime
import logging

# loading environment variables from .env file
load_dotenv()

API_KEY = os.getenv('API_KEY')
MONGODB_URI = os.getenv('MONGODB_URI')
MONGODB_DB = os.getenv('MONGODB_DB')

# setting up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# connecting to MongoDB
client = MongoClient(MONGODB_URI)
db = client[MONGODB_DB]

def get_weather(city):
    try:
        response = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=imperial&APPID={API_KEY}")
        response.raise_for_status()
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
            'wind_speed': data['wind']['speed'],
            'description': data['weather'][0]['description'],
            'timestamp': datetime.now()
        }
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

def check_weather_alerts(city):
    alerts = db.weather_alerts.find({'city': city})
    weather_data = get_weather(city)

    if weather_data:
        conditions_checked = set()
        for alert in alerts:
            condition = alert['condition']
            value = alert['value']

            if condition in conditions_checked:
                continue

            if condition == 'temperature' and weather_data['main']['temp'] >= value:
                print(f"Alert! The temperature in {city} is "
                      f"{weather_data['main']['temp']}ºF, which is above {value}ºF.")
                conditions_checked.add(condition)
            elif condition == 'humidity' and weather_data['main']['humidity'] >= value:
                print(f"Alert! The humidity in {city} is "
                      f"{weather_data['main']['humidity']}%, which is above {value}%.")
                conditions_checked.add(condition)
            elif condition == 'wind_speed' and weather_data['wind']['speed'] >= value:
                print(f"Alert! The wind speed in {city} is "
                      f"{weather_data['wind']['speed']} mph, which is above {value} mph.")
                conditions_checked.add(condition)
            elif condition == 'weather' and value.lower() in weather_data['weather'][0]['description'].lower():
                print(f"Alert! The weather in {city} includes {value}.")
                conditions_checked.add(condition)

def main():
    user_input = input("Enter city: ").strip().lower()
    weather_data = get_weather(user_input)

    if weather_data and weather_data.get('cod') != '404':
        weather = weather_data['weather'][0]['main']
        temp = round(weather_data['main']['temp'])
        humidity = weather_data['main']['humidity']
        wind_speed = weather_data['wind']['speed']
        description = weather_data['weather'][0]['description']
        
        print(f"\nThe weather in {user_input} is: {weather} ({description})")
        print(f"The temperature in {user_input} is: {temp}ºF")
        print(f"The humidity in {user_input} is: {humidity}%")
        print(f"The wind speed in {user_input} is: {wind_speed} mph\n")

        # storing weather data in MongoDB
        insert_weather_data(weather_data)

        # setting weather alerts
        set_weather_alert(user_input, 'temperature', 75)  # Temperature alert for above 75ºF
        set_weather_alert(user_input, 'humidity', 70)     # Humidity alert for above 70%
        set_weather_alert(user_input, 'wind_speed', 15)   # Wind speed alert for above 15 mph
        set_weather_alert(user_input, 'weather', 'rain')  # Weather condition alert for rain

        # checking notify about weather alerts
        check_weather_alerts(user_input)
    else:
        print("No City Found")

if __name__ == "__main__":
    main()
