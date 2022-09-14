import requests
import json


query = {"lang":"tc","dataType":"LTMV","rformat":"json"}

r = requests.get("https://data.weather.gov.hk/weatherAPI/opendata/opendata.php", params=query)
print(r.json())
# print(r.json()['data'])
