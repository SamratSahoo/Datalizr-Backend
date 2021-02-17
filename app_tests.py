import os

import requests
import settings

pload = {'fileType': '.csv',
         'fileID': '41866686-c4de-4591-9dd8-d6a58cfeee44',
         'columnsToAppend': [',,,', ',,,']}

r = requests.post(os.getenv('AZURE') + 'addData', json=pload)
print(r.content)
