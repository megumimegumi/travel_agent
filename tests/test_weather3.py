import requests
key = "dd0189861d284c57ae1d17e3bd80cff6"
host = "https://mt3dn8ycec.re.qweatherapi.com"
url = f"{host}/geo/v2/city/lookup"
params = {"location": "北京", "key": key}
res = requests.get(url, params=params)
print("GEO:", res.status_code, res.text)
