import os
from azure.storage.blob import BlobServiceClient

from Database.DatasetDB import Dataset
from Database.UUID import UniqueIds
from secret import *
import pathlib
from flask import Flask, request
from flask_cors import CORS
import uuid

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///application.db'
cors = CORS(app)

TEMP_FOLDER = 'tmp' + os.sep


@app.route('/hello')
def index():
    return {"Hello": "World"}


@app.route('/createProject', methods=['POST'])
def createProject():
    try:
        # Specify type of file + CSV Column Titles
        fileType = request.json['fileType']
        columns = request.json['columns']

        # Create UUID for File (Will serve as name)
        filenameID = str(uuid.uuid4())

        # If UUID already exists, make new UUID
        while UniqueIds.query.filter_by(id=filenameID).first() is not None:
            filenameID = str(uuid.uuid4())

        # Final Path
        path = TEMP_FOLDER + filenameID + fileType

        # Make File + write Columns in File + write to tmp folder
        with open(path, 'w+') as file:
            for column in columns:
                if column == columns[-1]:
                    file.write(column.strip())
                else:
                    file.write(column.strip() + ',')
            file.close()

            # Upload file to Azure
            uploadFile(path)
            # Remove file from tmp folder
            pathlib.Path(path).unlink()

            # Save file to UUID Database
            uniqueId = UniqueIds(id=filenameID)
            uniqueId.saveToDB()

            # Add Dataset to UUID
            dataset = Dataset(id=filenameID)
            dataset.saveToDB()
    except Exception as e:
        print(e)
        path = ''
        return {'fileName': path, 'success': False}

    return {'fileName': path, 'success': True}


def uploadFile(filePath):
    blobServiceClient = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
    containerName = "datasets"
    blobClient = blobServiceClient.get_blob_client(container=containerName, blob=filePath.replace('tmp' + os.sep, ''))

    with open(filePath, "rb") as data:
        blobClient.upload_blob(data)

if __name__ == '__main__':
    app.run(debug=True)