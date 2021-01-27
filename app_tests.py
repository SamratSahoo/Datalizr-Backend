import requests

pload = {'projectId': 'Test',
         'fileType': '.csv',
         'columns': ['Hello', 'World']}

LOCAL = 'http://localhost:5000/'
AZURE = 'https://datalizr.azurewebsites.net/'

r = requests.post(AZURE + 'createProject', json=pload)
print(r)
