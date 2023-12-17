import requests

def get_weather(api_key, city):
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}appid={api_key}&q={city}"
    response = requests.get(complete_url)
    weather_data = response.json()
    if weather_data['cod'] == 200:
        main_data = weather_data['main']
        temperature = main_data['temp']
        pressure = main_data['pressure']
        humidity = main_data['humidity']
        weather_description = weather_data['weather'][0]['description']
        print(f"Weather in {city}:")
        print(f"Temperature: {temperature} K")
        print(f"Pressure: {pressure} hPa")
        print(f"Humidity: {humidity}%")
        print(f"Description: {weather_description}")
    else:
        print("City not found or an error occurred.")

# Replace the placeholders with your actual API key and city name
api_key = "YOUR_API_KEY_HERE"
city_name = "YOUR_CITY_NAME_HERE"

get_weather(api_key, city_name)