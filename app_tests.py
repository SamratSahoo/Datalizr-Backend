import os

import requests
import settings

pload = {'fileType': '.csv',
         'fileID': '8f91ac96-f2c7-4f8d-981b-90d77a4b7236',
         'columnsToAppend': ['How', 'is Life']}

r = requests.post(os.getenv('LOCAL') + 'addData', json=pload)
print(r.content)
