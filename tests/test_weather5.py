import requests

key = "dd0189861d284c57ae1d17e3bd80cff6"
url = "https://devapi.qweather.com/v7/weather/now"
params = {"location": "101010100", "key": key}
headers = {'User-Agent': 'Mozilla/5.0'}
res = requests.get(url, params=params, headers=headers)
print("devapi:", res.text)

url = "https://geoapi.qweather.com/v2/city/lookup"
params = {"location": "北京", "key": key}
res = requests.get(url, params=params, headers=headers)
print("geoapi:", res.text)
