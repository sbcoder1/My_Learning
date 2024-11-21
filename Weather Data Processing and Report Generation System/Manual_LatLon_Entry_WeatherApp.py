import requests
import mysql.connector
from mysql.connector import Error
import random

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
        # Establishing connection to the MySQL database
        connection = mysql.connector.connect(
            host="localhost",  # Update if necessary
            user="root",  # Replace with your MySQL username
            password="root",  # Replace with your MySQL password
            database="weather"  # Replace with your database name
        )

        cursor = connection.cursor()

        # Extracting necessary fields from JSON
        coord_lon = data["coord"].get("lon", None)
        coord_lat = data["coord"].get("lat", None)
        weather = data["weather"][0]
        weather_id = weather.get("id", None)
        weather_main = weather.get("main", None)
        weather_description = weather.get("description", None)
        weather_icon = weather.get("icon", None)
        base = data.get("base", None)
        temp = data["main"].get("temp", None)
        feels_like = data["main"].get("feels_like", None)
        temp_min = data["main"].get("temp_min", None)
        temp_max = data["main"].get("temp_max", None)
        pressure = data["main"].get("pressure", None)
        humidity = data["main"].get("humidity", None)
        sea_level = data["main"].get("sea_level", None)  # Optional
        grnd_level = data["main"].get("grnd_level", None)  # Optional
        visibility = data.get("visibility", None)
        wind_speed = data["wind"].get("speed", None)
        wind_deg = data["wind"].get("deg", None)
        wind_gust = data["wind"].get("gust", None)  # Optional
        rain_1h = data.get("rain", {}).get("1h", None)  # Optional
        clouds_all = data["clouds"].get("all", None)
        dt = data.get("dt", None)
        sys_type = data["sys"].get("type", None)  # Optional
        sys_id = data["sys"].get("id", None)  # Optional
        sys_country = data["sys"].get("country", None)  # Optional
        sys_sunrise = data["sys"].get("sunrise", None)
        sys_sunset = data["sys"].get("sunset", None)
        timezone = data.get("timezone", None)
        location_id = data.get("id", None)
        location_name = data.get("name", "").encode('utf-8').decode('utf-8')  # Handle encoding
        cod = data.get("cod", None)
        
    # SQL query to insert data
        insert_query = """
        INSERT INTO weather_data (
            id,coord_lon, coord_lat, weather_id, weather_main, weather_description,
            weather_icon, base, temp, feels_like, temp_min, temp_max, pressure,
            humidity, sea_level, grnd_level, visibility, wind_speed, wind_deg, wind_gust,
            rain_1h, clouds_all, dt, sys_type, sys_id, sys_country, sys_sunrise, sys_sunset,
            timezone, location_id, location_name, cod
        ) VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)
        """
        ide=random.randint(1,999)
        # Data to be inserted
        record = (
            ide,coord_lon, coord_lat, weather_id, weather_main, weather_description,
            weather_icon, base, temp, feels_like, temp_min, temp_max, pressure,
            humidity, sea_level, grnd_level, visibility, wind_speed, wind_deg, wind_gust,
            rain_1h, clouds_all, dt, sys_type, sys_id, sys_country, sys_sunrise, sys_sunset,
            timezone, location_id, location_name, cod
        )

        #print(insert_query)
        #print(record)

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

# Main function to fetch and insert data
def main():
    # Taking user input for latitude, longitude, and API key
    lat = input("Enter the latitude: ")
    lon = input("Enter the longitude: ")
    api_key = '8e6d355869e7725e2b3940b97f3d7246'  # Replace with your API key

    # Fetching the weather data
    data = fetch_weather_data(lat, lon, api_key)

    print(data)

    if data:
        insert_weather_data(data)

if __name__ == "__main__":
    main()


