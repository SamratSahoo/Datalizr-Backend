import requests
pload = {'projectId': 'World',
         'fileType': '.csv',
         'columns': ['Hello', 'World']}

r = requests.post('http://localhost:5000/createProject', json=pload)
print(r)