import requests

key = "dd0189861d284c57ae1d17e3bd80cff6"

url = "https://mt3dn8ycec.re.qweatherapi.com/geo/v2/city/lookup"
params = {"location": "北京", "key": key}
res = requests.get(url, params=params)
print("PROXY geoapi:", res.status_code)
print(res.text[:100])

url = "https://mt3dn8ycec.re.qweatherapi.com/v7/weather/now"
params = {"location": "101010100", "key": key}
res = requests.get(url, params=params)
print("PROXY devapi:", res.status_code)
print(res.text[:100])
