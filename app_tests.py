import requests
from secret import *

pload = {'fileType': '.csv',
         'columns': ['Hello', 'World']}

r = requests.post(AZURE + 'createProject', json=pload)
print(r.content)
