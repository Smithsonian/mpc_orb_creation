
import requests

r = requests.post('http://mpcweb1:8001/api/query-identifier', data='1983 LM')
<<<<<<< HEAD
print('r=',r)
print()
=======
>>>>>>> 6125af168285bb8c75ddcf3770935676161b8216
print(f"Result from Flask endpoint for /api/query-identifier: {r.json()}")

