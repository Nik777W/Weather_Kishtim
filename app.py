import os

import openmeteo_requests
import requests

import requests_cache
import pandas as pd
from retry_requests import retry
from dotenv import load_dotenv

load_dotenv()

def get_weather():

    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)


    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 55.7379,
        "longitude": 60.5508,
        "hourly": "temperature_2m",
        "timezone": "Europe/Moscow",
        "forecast_days": 1
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
    print(f"Elevation {response.Elevation()} m asl")
    print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
    print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()


    hourly_data = {"date": pd.date_range(start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),freq = pd.Timedelta(seconds = hourly.Interval()),inclusive = "left")}
    hourly_data["temperature_2m"] = hourly_temperature_2m


    hourly_dataframe = pd.DataFrame(data = hourly_data)


    return hourly_dataframe.to_string(index=None)



def send_message(get_you_weather):

    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    print(url)
    params={
        'chat_id': TELEGRAM_CHANNEL_ID,
        'text': get_you_weather
    }
    res = requests.post(url, params=params)
    res.raise_for_status()

    return res.json()

if __name__ == "__main__":
    weather = get_weather()
    send_message(weather)




