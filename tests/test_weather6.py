import requests

key = "dd0189861d284c57ae1d17e3bd80cff6"

url = "https://geoapi.qweather.com/v2/city/lookup"
params = {"location": "北京", "key": key, "range": "cn"}
res = requests.get(url, params=params)
print("geoapi:", res.status_code)
print(res.text)

url = "https://devapi.qweather.com/v7/weather/now"
params = {"location": "101010100", "key": key}
res = requests.get(url, params=params)
print("devapi:", res.status_code)
print(res.text)
