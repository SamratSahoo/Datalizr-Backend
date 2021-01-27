import requests
pload = {'projectId': 'World',
         'fileType': '.csv',
         'columns': ['Hello', 'World']}

r = requests.post('https://datalizr.azurewebsites.net/createProject', json=pload)
print(r.content)