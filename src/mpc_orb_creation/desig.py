
import requests

r = requests.post('http://mpcweb1:8001/api/query-identifier', data='1983 LM')
print('r=',r)
print()
print(f"Result from Flask endpoint for /api/query-identifier: {r.json()}")

