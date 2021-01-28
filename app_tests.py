import requests
from secret import *

pload = {'projectId': 'Cat',
         'fileType': '.csv',
         'columns': ['Hello', 'World']}

r = requests.post(LOCAL + 'createProject', json=pload)
print(r.content)
