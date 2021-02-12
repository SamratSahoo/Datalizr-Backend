import csv
import os
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__
from Database.DatasetDB import Dataset
from Database.Engine import engine, Base
from Database.UUID import UniqueIds
import pathlib
from flask import Flask, request
from flask_cors import CORS
import uuid
import pandas as pd
import settings

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'
Base.metadata.create_all(bind=engine)

TEMP_FOLDER = 'tmp' + os.sep


@app.route('/hello')
def index():
    return {"Hello": "World"}


@app.route('/createProject', methods=['POST'])
def createProject():
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

    return {'fileName': path, 'success': True}


@app.route('/addData', methods=['POST'])
def addData():
    fileID = request.json['fileID']
    fileType = request.json['fileType']
    columnsToAppend = request.json['columnsToAppend']

    if fileType == '.csv':
        blobServiceClient = BlobServiceClient.from_connection_string(os.getenv('AZURE_CONNECTION_STRING'))
        containerName = "datasets"
        blobClient = blobServiceClient.get_blob_client(container=containerName, blob=fileID + fileType)
        downloadPath = 'tmp' + os.sep + fileID + fileType
        folder = open(downloadPath, "w+")
        folder.write(blobClient.download_blob().readall().decode("utf-8"))
        folder.close()

        rowsToAppend = []
        with open(downloadPath, newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                rowsToAppend.append(row)

        f = open(downloadPath, "w+")
        f.close()

        rowsToAppend.append(columnsToAppend)
        with open(downloadPath, "a", encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(rowsToAppend)

        df = pd.read_csv(downloadPath)
        df.to_csv(downloadPath, index=False)

        uploadFile(downloadPath)

        filePath = pathlib.Path(downloadPath)
        filePath.unlink()
    return {'success': True}


def uploadFile(filePath):
    blobServiceClient = BlobServiceClient.from_connection_string(os.getenv('AZURE_CONNECTION_STRING'))
    containerName = "datasets"
    blobClient = blobServiceClient.get_blob_client(container=containerName, blob=filePath.replace('tmp' + os.sep, ''))

    with open(filePath, "rb") as data:
        blobClient.upload_blob(data, overwrite=True)


if __name__ == '__main__':
    app.run(debug=True)
