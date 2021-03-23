import os

import requests
import settings
from Database.GoogleAccount import GoogleUser

# pload = {'fileType': '.csv',
#          'userId': GoogleUser.query.filter_by(username='SamratSahoo').first().id,
#          'columns': ['Testing', 'Data'],
#          'username': GoogleUser.query.filter_by(username='SamratSahoo').first().username,
#          'datasetName': 'Sample Testing Data',
#          'description': 'This is a sample dataset that is being used solely for testing purposes. DO NOT modify the contents of this file else there may be serious repercussions. Thank you for your time'}

pload = {'id': GoogleUser.query.filter_by(username='SamratSahoo').first().id}
r = requests.post(os.getenv('LOCAL') + 'getProjects', json=pload)
print(r.content)
