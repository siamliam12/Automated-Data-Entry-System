# Automated-Data-Entry-System
The Automated Data Entry System is designed to streamline the process of entering data from various sources into a centralized database or system. By automating this task, the system aims to reduce errors, save time, and increase efficiency in data management processes.

### How To Use It?
# Base setup:
   As it works with email it has to store sentisitive data like email's app password which is not safe so we made this as a local system you can use it. All you need to have python installed and other things should work out of the box. everything works with a click of a button. let's walk you through how to set this up locally. 
   # step 1: Getting the codebase
      clone the repository from this github. The command to do this ```git clone https://github.com/siamliam12/Automated-Data-Entry-System.git```
      if you don't have git installed you can download the zip
   # step 2: Creating virtual env
      cd into the folder.
      create a virtual environtment in python (recomended)
      to create a virtual environment : ``` python -m venv env```
      now activate it : ```.\env\Scripts\Activate```
   # step 3: getting credentials
      create a .env file like below
      ```
      email = 'yourEmail@gmail.com'
      password = 'A password that you got from App password in your gmail settings'
      here I'm using a online postgres so you can add your credentials.
      db_password = 'password'
      db_url = "url"
      JWT_SECRET_KEY = 'some kind of secrect string'
      JWT_REFRESH_SECRET_KEY = 'some kind of secrect string'
   # step 4: installing environment
      finally run ``` pip install -r requirements.txt```
   # step 5: finally run the app. end of setup
      cd into api folder
      ```uvicorn main:app --reload```
   and the app should run perfectly.

# Base Url
   -Get all Index: http://localhost:8000/
   - Use user friendly docs: http://localhost:8000/docs
# Create a user (not a authentication but important)
   -create a user: http://localhost:8000/users
   
      body:{
     "username": "string",
     "download_dir": "string"
      }
# Get data
   -GET all data: http://localhost:8000/get-data
   -GET data by id: http://localhost:8000/get-data/{id}
# Update Data
   -PUT : http://localhost:8000/update-data/{id}
   
      body: {
     "name": "string",
     "age": 0,
     "date": "string",
     "complaint": "string",
     "diagnosis": "string",
     "prescription_info": "string"
      }
# Delete Data:
   - DELETE : http://localhost:8000/delete-data/{id}
# Download attachments:
   -GET attachment by sender : http://localhost:8000/attachment-search-by-sender?sender={sender_email}&username={you_user_name}
   - GET attachment by date: http://localhost:8000/attachment-search-by-date?subject={your_subject}&start_date={starting_date}&end_date={ending_date}&username={you_user_name}
# Convert images:
   -converts your images to jpg that you downloaded: http://localhost:8000/converter?image_type={typee.g.png,jfif,webp}&username={you_user_name}
# Extract Text and store to database
   -final step: http://localhost:8000/text-extractor?username={you_user_name}


      
