import os
from flask import Flask, request
from azure.core.exceptions import (
    ResourceExistsError,
    ResourceNotFoundError
)
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__
from secret import *
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app)

TEMP_FOLDER = 'tmp' + os.sep


@app.route('/hello')
def index():
    return {"Hello": "World"}


@app.route('/createProject', methods=['POST'])
def createProject():
    try:
        filenameID = request.json['projectId']
        fileType = request.json['fileType']
        columns = request.json['columns']
        path = TEMP_FOLDER + filenameID + fileType

        with open(path, 'w+') as file:
            for column in columns:
                if column == columns[-1]:
                    file.write(column.strip())
                else:
                    file.write(column.strip() + ',')

            file.close()
            uploadFile(path)

    except Exception as e:
        print(e)
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
