import unittest
from datetime import datetime
from main import get_weather, insert_weather_data, set_weather_alert, check_weather_alerts

class TestWeather(unittest.TestCase):

    def test_get_weather(self):
        city_weather = get_weather("Tokyo")
        not_city = get_weather("Doorknob")
        self.assertIsNotNone(weather_data)
        self.assertIn("404", not_city)
        self.assertIn('weather', weather_data)
        self.assertIn('main', weather_data)


    def test_insert_weather_data(self):
        #mock data 
        tmp_data = {'main': {'temp': 88, 'humidity': 88}, 'name': 'Accra'}
        insert_test = insert_weather_data(tmp_data)
        self.assertIsNotNone(insert_test)
        result = f"Weather data for {tmp_data['name']} stored in the database."
        self.assertEqual(insert_result, result)


    def test_set_weather_alert(self):
        #mock data
        city = "Tokyo"
        condition = "temperature"
        value = 75

        result = set_weather_alert(city, condition, value)
        self.assertIsNotNone(result)
        self.assertEqual(result, f"Weather alert set for {city}: {condition} {value}")
        result = set_weather_alert(city, condition="humidity", value=50) #check for when condition="humidity"
        self.assertEqual(result, f"Weather alert set for {city}: {condition} {value}")


    # def test_check_weather_alerts(self):
    #     # test when there's alerts
    #     result = check_weather_alerts()
    #     self.assertIn(f"Alert! The temperature in {city} is "
    #             f"{weather_data['main']['temp']}ºF, which is above {value}ºF.", result)
    #     self.assertIn(f"Alert! The humidity in {city} is "
    #             f"{weather_data['main']['humidity']}%, which is above {value}%.", result)

    #     # test when there's no alerts
    #     tmp_data = {'main': {'temp': 50, 'humidity': 50}, 'name': 'Tokyo'} #mock data
    #     result = check_weather_alerts()
    #     self.assertIs(result)
