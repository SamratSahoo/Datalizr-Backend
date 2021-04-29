# ISM II Final Product

### Program Preface

This project was made for the Independent Study Mentorship Program. The Independent Study Mentorship Program is a rigorous research-based program offered at Frisco ISD schools for passionate high-achieving individuals.

Throughout the course of the program, students carry-out a year-long research study where they analyze articles and interview local professionals. Through the culmination of the research attained, students create an original work, presented at research showcase, and a final product that will be showcased at final presentation night. Through the merits of this program, individuals are able to follow their passions while increasing their prominence in the professional world and growing as a person.

The ISM program is a program in which students carry-on skills that not only last for the year, but for life. ISM gives an early and in-depth introduction to the students' respective career fields and professional world. Coming out of this program, students are better equipped to handle the reality of the professional world while having become significantly more knowledgeable of their respective passions. The ISM program serves as the foundation for the success of individuals in the professional world.

### Project Preface

Datalizr is a data crowdsourcing platform that serves to gather vast amounts of data for data scientsits, machine learning engineers, and statisticans.

The concept of Datalizr can be visualized with the following example: one person gathering 50,000 lines of data versus 50,000 people gathering 1 line of data each--clearly the 2nd apporach, the one that leverages crowdsourcing is more efficient. This repository houses the frontend interface (what the user sees) of the Datalizr web application.

### Navigating Github

- **Commits**: This where you can see a short description of the changes I made, the time I made it and the files I changed.
- **Files**: Below the commits are where you can find my program files with all of my code/other resources
- **ReadME**: The ReadME file is this file! You can find a preface and documentation over the whole project.

### Requirements & Setup

- **Step 1:** Install Python 3.7 (This may work with other versions of Python 3 but Python 3.7 is the only one I have tested)
- **Step 2:** Run `pip3 install -r requirements.txt`
- **Step 3:** Create a Twitter Developer Account and get Twitter Credentials
- **Step 4:** Create a `.env` file and add the following variables with their respective variables: `AZURE_STORAGE_KEY, AZURE_CONNECTION_STRING, DB_URL, APP_SECRET_KEY, FERNET_KEY, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET`.
- **Step 5:** Run `python3 app.py`

### File Documentation

- `app.py:` This is the main file within this application and hosts all the endpoints for the frontend interface to call--some endpoints include creating an account, changing username, and checking checking if there is data to review.
- `app_tests.py:` This is a testing file to test the different endpoints within `app.py`.
- `settings.py:` This is a file that simply helps set environment variables through a `.env` file when the API server is first starting.
- `Database/Engine.py:` This is the file that helps build the database that is being used in the backend to store different types of information like dataset information, user information, etc.
- `Database/DataReview.py:` This is a database table to keep track of every review that occurs on the review page of the web application
- `Database/DatasetData.py:` This is a database table to keep track of all the data and the respective user & dataset it belongs to. It is often used for many endpoints to see what data has been fully reviewed and what data needs reviewing.
- `Database/Datasets.py:` This is a database table to keep track of all the datasets created.
- `Database/GoogleAccount.py:` This is a database table to keep track of all the users that sign into Datalizr with Google. This help maintain user information and datasets appropirately.
- `Database/Encryption.py:` This is an encryption that uses symmetric encryption to ensure user data stays safe. It is used to encrypt user emails so that they are never leaked.

### Datalizr Frontend

The frontend interface for this project can be found [here.](https://github.com/SamratSahoo/Datalizr-Frontend)

### Portfolio

My research and work for this year can be found at my
[Digital Portfolio.](https://samratsahoo.weebly.com)

### Thank You

I would just like to give a special thank you to Mr. Trey Blankenship for his mentorship and assisstance throughout this whole process.

I would also like to give a special thanks to the following individuals for their contributions throughout this year.

- Won Hwa Kim [UT Arlington]
- Vincent Ng [UT Dallas]
- Abhiramon Rajasekharan [UT Dallas]
