import sys

from flask import Flask, request
from flask_cors import CORS

from azure.storage.blob import BlobServiceClient

import csv
import os
import pathlib
import pandas as pd

from Database.DataReview import DataReview
from Database.Datasets import Datasets
from Database.Encryption import encryptData
from Database.Engine import engine, Base, dbSession
from Database.GoogleAccount import GoogleUser
from Database.DatasetData import DatasetData
from google.oauth2 import id_token
from google.auth.transport import requests
import uuid

from apscheduler.schedulers.background import BackgroundScheduler

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
    userId = request.json['userId']
    username = request.json['username']
    datasetName = request.json['datasetName']
    description = request.json['description']
    # Create UUID for File (Will serve as name)
    filenameID = str(uuid.uuid4())

    # If UUID already exists, make new UUID
    while Datasets.query.filter_by(id=filenameID).first() is not None:
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

        # Add Dataset to DB
        dataset = Datasets(id=filenameID, userUUID=userId, userUsername=username,
                           datasetName=datasetName, description=description, fields=columns)
        dataset.saveToDB()

    return {'fileName': path, 'success': True}


@app.route('/addData', methods=['POST'])
def addData():
    fileId = request.json['fileId']
    fileType = request.json['fileType']
    columnsToAppend = request.json['columnsToAppend']
    userId = request.json['userId']

    dataId = str(uuid.uuid4())
    while Datasets.query.filter_by(id=dataId).first() is not None:
        dataId = str(uuid.uuid4())

    data = DatasetData(id=dataId, datasetId=fileId, data=columnsToAppend, userUUID=userId, loaded=False,
                       fileType=fileType)
    data.saveToDB()

    return {'success': True}


@app.route('/authentication/googleLogin', methods=['POST'])
def googleLogin():
    # Success Variable
    success = False

    # Verify ID token
    socialId = id_token.verify_oauth2_token(request.json['token'], requests.Request(), os.getenv('GOOGLE_CLIENT_ID'))[
        'sub']
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
    socialId = id_token.verify_oauth2_token(request.json['token'], requests.Request(), os.getenv('GOOGLE_CLIENT_ID'))[
        'sub']

    # Datalizr ID + username
    uniqueID = str(uuid.uuid4())
    while GoogleUser.query.filter_by(id=uniqueID) is None:
        uniqueID = str(uuid.uuid4())

    # Get Hash for email
    emailHash = encryptData(email.lower())

    # Success variable
    success = False
    # If the user does not exist in the database, User will be registered with a google account
    if GoogleUser.query.filter_by(socialId=socialId).first() is None:
        user = GoogleUser(emailHash=emailHash, username=username, socialId=socialId, admin=False,
                          id=uniqueID)
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
    return {'userAvailable': GoogleUser.query.filter_by(username=username).first() is None}


@app.route('/authentication/changeUsername', methods=['POST'])
def changeUsername():
    newUsername = request.json['newUsername']
    id = request.json['id']
    if GoogleUser.query.filter_by(username=newUsername).first() is None:
        user = GoogleUser.query.filter_by(id=id).first()
        dbSession.query(GoogleUser).filter_by(id=id).update({'username': newUsername})
        dbSession.commit()
        return {**getUser(user), **{'updatedUsername': newUsername, 'success': True}}
    else:
        user = GoogleUser.query.filter_by(id=id).first()
        return {**getUser(user), **{'updatedUsername': "", 'success': False}}


@app.route('/getProjects', methods=['POST'])
def getUserProjects():
    userId = request.json['id']
    return {'projects': [getDataset(dataset) for dataset in Datasets.query.filter_by(userUUID=userId).all()]}


@app.route('/getDatasets', methods=['POST'])
def getDatasetAPI():
    datasetId = request.json['datasetId']
    return getDataset(Datasets.query.filter_by(id=datasetId).first())


@app.route('/approveData', methods=['POST'])
def approveData():
    userId = request.json['userId']
    datasetId = request.json['datasetId']
    dataId = request.json['dataId']
    approvalStatus = request.json['approvalStatus']

    dataReview = DataReview(datasetId=datasetId, userId=userId, dataId=dataId, approvalStatus=approvalStatus)
    dataReview.saveToDB()
    if approvalStatus:
        DatasetData.query.filter_by(id=dataId).first().approvals += 1

    dbSession.commit()
    return {'success': True}


@app.route('/getDataReview', methods=['POST'])
def getDataReview():
    # Get User Id of reviewer
    userId = request.json['userId']
    # Filter for all potential data
    potentialData = DatasetData.query.filter_by(loaded=False).all()
    # Iterate through data
    for data in potentialData:
        # If data was added by same user, then just continue
        if data.userUUID in userId:
            continue
        # get user review
        userReviews = DataReview.query.filter_by(dataId=data.id).all()
        for user in userReviews:
            # check if user id is not in the reviewed section
            if userId not in user.userId:
                datasetId = getDatasetData(data)['datasetId']
                fields = Datasets.query.filter_by(id=datasetId).first().fields
                return {**getDatasetData(data), **{'success': True, 'fields': fields}}
        if len(userReviews) == 0:
            datasetId = getDatasetData(data)['datasetId']
            fields = Datasets.query.filter_by(id=datasetId).first().fields
            return {**getDatasetData(data), **{'success': True, "fields": fields}}

    return {'success': False, 'id': "", 'datasetId': "", 'data': [], 'userId': "",
            'fileType': "", 'loaded': False, 'approvals': 0, "fields":[]}


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


def getDataset(dataset):
    return {'id': dataset.id, 'userUsername': dataset.userUsername, 'datasetName': dataset.datasetName,
            'description': dataset.description, 'fields': dataset.fields}


def getDatasetData(data):
    return {'id': data.id, 'datasetId': data.datasetId, 'data': data.data, 'userId': data.userUUID,
            'fileType': data.fileType, 'loaded': data.loaded, 'approvals': data.approvals}


def updateDB():
    notUpdatedData = DatasetData.query.filter_by(loaded=False).all()
    blobServiceClient = BlobServiceClient.from_connection_string(os.getenv('AZURE_CONNECTION_STRING'))
    containerName = "datasets"
    for data in notUpdatedData:
        if data.approvals >= 4:
            blobClient = blobServiceClient.get_blob_client(container=containerName, blob=data.datasetId + data.fileType)
            downloadPath = TEMP_FOLDER + data.datasetId + data.fileType
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

            rowsToAppend.append(data.data)
            with open(downloadPath, "a", encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(rowsToAppend)

            df = pd.read_csv(downloadPath)
            df.to_csv(downloadPath, index=False)

            uploadFile(downloadPath)

            filePath = pathlib.Path(downloadPath)
            filePath.unlink()

            data.loaded = True
            dbSession.commit()


if __name__ == '__main__':
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(updateDB, 'interval', seconds=5)
    scheduler.start()
    app.run(debug=True)
