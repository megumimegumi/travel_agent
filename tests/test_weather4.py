import requests
key = "dd0189861d284c57ae1d17e3bd80cff6"
print(requests.get(f"https://api.qweather.com/v7/weather/now?location=101010100&key={key}").text)
print(requests.get(f"https://devapi.qweather.com/v7/weather/now?location=101010100&key={key}").text)
