import requests

key = "dd0189861d284c57ae1d17e3bd80cff6"
url = "https://geoapi.qweather.com/v2/city/lookup"
params = {"location": "北京", "key": key, "range": "cn"}

res = requests.get(url, params=params)
print("GEO:", res.status_code, res.text)

url2 = "https://devapi.qweather.com/v7/weather/now"
params2 = {"location": "101010100", "key": key}
res2 = requests.get(url2, params=params2)
print("WEATHER:", res2.status_code, res2.text)
