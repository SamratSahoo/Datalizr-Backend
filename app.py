import os
from flask import Flask, request
from azure.core.exceptions import (
    ResourceExistsError,
    ResourceNotFoundError
)

from azure.storage.fileshare import (
    ShareServiceClient,
    ShareClient,
    ShareDirectoryClient,
    ShareFileClient
)
from secret import *

app = Flask(__name__)

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

            client = ShareServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
            uploadFile(AZURE_CONNECTION_STRING, path, 'datasets', '')
    except:
        return {'fileName': '', 'success': False}

    return {'fileName': path, 'success': True}


def uploadFile(connectionString, filePath, shareName, destination):
    try:
        sourceFile = open(filePath, "rb")
        data = sourceFile.read()

        fileClient = ShareFileClient.from_connection_string(
            connectionString, shareName, destination)

        fileClient.upload_file(data)

    except ResourceExistsError as ex:
        print("ResourceExistsError:", ex.message)

    except ResourceNotFoundError as ex:
        print("ResourceNotFoundError:", ex.message)


if __name__ == '__main__':
    app.run(debug=True)
