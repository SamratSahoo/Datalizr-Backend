import os
from flask import Flask, request
import boto3
import codecs
from pathlib import Path

app = Flask(__name__)

TEMP_FOLDER = 'tmp' + os.sep


@app.route('/hello')
def index():
    return {"Hello": "World"}


@app.route('/createProject', methods=['POST'])
def createProject():
    filenameID = request.json['projectId']
    fileType = request.json['fileType']
    columns = request.json['columns']
    path = TEMP_FOLDER + filenameID + fileType

    if not os.path.exists(TEMP_FOLDER):
        os.mkdir(TEMP_FOLDER)

    Path(path).touch()

    with open(path, 'w') as file:
        for column in columns:
            if column == columns[-1]:
                file.write(column.strip())
            else:
                file.write(column.strip() + ',')

        file.close()

    return {'fileName': path}


if __name__ == '__main__':
    app.run(debug=True)
