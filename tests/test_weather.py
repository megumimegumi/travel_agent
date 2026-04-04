import sys
import os
import requests
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from tools.weather_tool import WeatherTool
from utils.config import Config

config = Config()
url = "https://geoapi.qweather.com/v2/city/lookup"
params = {"location": "北京", "key": config.qweather_api_key, "range": "cn"}
res = requests.get(url, params=params)
print(res.status_code)
print(res.text)
