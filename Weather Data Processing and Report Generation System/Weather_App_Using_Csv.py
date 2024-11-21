import requests
import mysql.connector
from mysql.connector import Error
import random
import pandas as pd

# Function to fetch weather data from the API
def fetch_weather_data(lat, lon, api_key):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

# Function to insert the parsed data into the MySQL database
def insert_weather_data(data):
    try:
        # Establish connection to the MySQL database
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",  # Replace with your MySQL password
            database="weather"
        )
        cursor = connection.cursor()

        # Extract necessary fields from the JSON, setting default values for missing fields
        coord_lon = round(data["coord"].get("lon", 0), 1)
        coord_lat = round(data["coord"].get("lat", 0), 1)
        weather = data["weather"][0]
        weather_id = weather.get("id", 0)
        weather_main = weather.get("main", "Unknown")
        weather_description = weather.get("description", "Unknown")
        weather_icon = weather.get("icon", "Unknown")
        base = data.get("base", "Unknown")
        temp = data["main"].get("temp", 0)
        feels_like = data["main"].get("feels_like", 0)
        temp_min = data["main"].get("temp_min", 0)
        temp_max = data["main"].get("temp_max", 0)
        pressure = data["main"].get("pressure", 0)
        humidity = data["main"].get("humidity", 0)
        sea_level = data["main"].get("sea_level", None)  # Optional
        grnd_level = data["main"].get("grnd_level", None)  # Optional
        visibility = data.get("visibility", None)
        wind_speed = data["wind"].get("speed", 0)
        wind_deg = data["wind"].get("deg", 0)
        wind_gust = data["wind"].get("gust", None)  # Optional
        rain_1h = data.get("rain", {}).get("1h", None)  # Optional
        clouds_all = data["clouds"].get("all", 0)
        dt = data.get("dt", None)
        sys_type = data["sys"].get("type", None)  # Optional
        sys_id = data["sys"].get("id", None)  # Optional
        sys_country = data["sys"].get("country", "Unknown")
        sys_sunrise = data["sys"].get("sunrise", None)
        sys_sunset = data["sys"].get("sunset", None)
        timezone = data.get("timezone", 0)
        location_id = data.get("id", 0)
        location_name = data.get("name", "").encode('utf-8').decode('utf-8')  # Handle encoding
        cod = data.get("cod", 0)

        # SQL query to insert data
        insert_query = """
        INSERT INTO weather_data (
            id, coord_lon, coord_lat, weather_id, weather_main, weather_description,
            weather_icon, base, temp, feels_like, temp_min, temp_max, pressure,
            humidity, sea_level, grnd_level, visibility, wind_speed, wind_deg, wind_gust,
            rain_1h, clouds_all, dt, sys_type, sys_id, sys_country, sys_sunrise, sys_sunset,
            timezone, location_id, location_name, cod
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)
        """

        # Generate random ID
        ide = random.randint(1, 999)

        # Data to be inserted
        record = (
            ide, coord_lon, coord_lat, weather_id, weather_main, weather_description,
            weather_icon, base, temp, feels_like, temp_min, temp_max, pressure,
            humidity, sea_level, grnd_level, visibility, wind_speed, wind_deg, wind_gust,
            rain_1h, clouds_all, dt, sys_type, sys_id, sys_country, sys_sunrise, sys_sunset,
            timezone, location_id, location_name, cod
        )

        # Executing the query
        cursor.execute(insert_query, record)
        connection.commit()

        print(f"Data inserted successfully, ID: {cursor.lastrowid}")

    except Error as e:
        print(f"Error inserting data: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()
            print("MySQL connection closed.")


def run_csv(api_key):
   
    data = pd.read_csv(r"C:\Users\sbcod\Desktop\Study Files\latlon.csv")
    
    for index, row in data.iterrows():
        lat = row['Latitude']
        lon = row['Longitude']
        print(f"Fetch data for Latitude: {lat}, Longitude: {lon} ...")
        
        
        w_data = fetch_weather_data(lat, lon, api_key)
        
        if  w_data:
            
            insert_weather_data(w_data)


def main():
    
    api_key = '8e6d355869e7725e2b3940b97f3d7246' # Replace with your API key

    run_csv(api_key)

if __name__ == "__main__":
    main()
