from flask import Flask, request
from flask_cors import CORS

from azure.storage.blob import BlobServiceClient

import csv
import os
import pathlib
import pandas as pd

from Database.Dataset import Dataset
from Database.Encryption import encryptData
from Database.Engine import engine, Base
from Database.DatasetIds import DatasetIds
from Database.GoogleAccount import GoogleUser
from google.oauth2 import id_token
from google.auth.transport import requests
import uuid

from Database.UserIds import UserIds
from Database.Username import Username

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'
Base.metadata.create_all(bind=engine)

TEMP_FOLDER = 'tmp' + os.sep


# ====================== API ENDPOINTS ====================== #

@app.route('/hello')
def index():
    return {"Hello": "World"}


@app.route('/createProject', methods=['POST'])
def createProject():
    # Specify type of file + CSV Column Titles
    fileType = request.json['fileType']
    columns = request.json['columns']
    userInfo = request.json['user']

    # Create UUID for File (Will serve as name)
    filenameID = str(uuid.uuid4())

    # If UUID already exists, make new UUID
    while DatasetIds.query.filter_by(id=filenameID).first() is not None:
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
        uniqueId = DatasetIds(id=filenameID)
        uniqueId.saveToDB()

        # Add Dataset to UUID
        dataset = Dataset(id=filenameID, userUUID=userInfo['id'])
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
        downloadPath = TEMP_FOLDER + fileID + fileType
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


@app.route('/authentication/googleLogin', methods=['POST'])
def googleLogin():
    # Success Variable
    success = False

    # Verify ID token
    socialId = id_token.verify_oauth2_token(request.json['token'], requests.Request(), os.getenv('CLIENT_ID'))['sub']

    # Query through database
    if GoogleUser.query.filter_by(socialId=socialId).first() is not None:
        user = GoogleUser.query.filter_by(socialId=socialId).first()
        # If the user exists as a google account, the login is successful
        status = 'SUCCESS: Logged In'
        success = True
    else:
        # Google user just as a placeholder
        user = GoogleUser()
        status = 'ERROR: Failed to Login'
    return {**getUser(user=user), **{'status': status, 'success': success}}


@app.route('/authentication/googleSignUp', methods=['POST'])
def googleSignUp():
    # Grab User's username and email
    username = request.json['username']
    email = request.json['email']

    # Process Tokens for google and facebook
    # Verify ID token
    socialId = id_token.verify_oauth2_token(request.json['token'], requests.Request(), os.getenv('CLIENT_ID'))['sub']

    # Datalizr ID + username
    uniqueID = UserIds(id=str(uuid.uuid4()))
    uniqueUsername = Username(name=username)

    # Get Hash for email
    emailHash = encryptData(email.lower())

    # Success variable
    success = False
    # If the user does not exist in the database, User will be registered with a google account
    if GoogleUser.query.filter_by(socialId=socialId).first() is None:
        user = GoogleUser(emailHash=emailHash, username=uniqueUsername.name, socialId=socialId, admin=False,
                          id=uniqueID.id)
        # Save UUID + unique username to database
        uniqueID.saveToDB()
        uniqueUsername.saveToDB()
        # Save the user to the database
        user.saveToDB()
        status = 'SUCCESS: Added to Database'
        success = True
    # If they are not signed in for some reason, then fail authentication
    else:
        status = 'ERROR: Not Signed In'
        user = GoogleUser()
    # Return User
    return {**getUser(user=user), **{'status': status, 'success': success}}


@app.route('/authentication/usernameAvailable', methods=['POST'])
def usernameAvailable():
    username = request.json['username']
    # Return true if available else False
    return {'userAvailable': Username.query.filter_by(name=username).first() is None}


@app.route('/getProjects', methods=['POST'])
def getUserProjects():
    userId = request.json['id']
    return {'projects': Dataset.query.filter_by(userUUID=userId).all()}


# ====================== HELPER METHODS ====================== #


def uploadFile(filePath):
    blobServiceClient = BlobServiceClient.from_connection_string(os.getenv('AZURE_CONNECTION_STRING'))
    containerName = "datasets"
    blobClient = blobServiceClient.get_blob_client(container=containerName, blob=filePath.replace('tmp' + os.sep, ''))

    with open(filePath, "rb") as data:
        blobClient.upload_blob(data, overwrite=True)


def getUser(user):
    return {'id': user.id, 'username': user.username,
            'admin': user.admin, 'loginDate': user.loginDate}


if __name__ == '__main__':
    app.run(debug=True)
