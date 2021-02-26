import os

import requests
import settings

pload = {'fileType': '.csv',
         'fileId': '41866686-c4de-4591-9dd8-d6a58cfeee44',
         'columnsToAppend': ['Testing', 'Data'],
         'userId': '8e8f29c2-a855-4414-952c-87a4a26fbdc5'}

r = requests.post(os.getenv('LOCAL') + 'addData', json=pload)
print(r.content)
