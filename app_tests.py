import requests
pload = {'projectId': 'Hello',
         'fileType': '.csv',
         'columns': ['Hello', 'World']}

r = requests.post('http://127.0.0.1:5000/createProject', json=pload)
print(r)