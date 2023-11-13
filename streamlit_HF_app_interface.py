

import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

import os
# need to do the following
import pandas as pd
import random
import io
# feed into a repo, ie google sheets or something, 

# update the following code based off user ID. 
# might need to just implement via a flask sever. 
# step wise testing, first test to see if i can pull the following 
# SERVICE_ACCOUNT_FILE = "/Users/aaronfanous/Downloads/capstoneuthscsa-e18d95216eb1.json"
secrets_dict = {
    "type": st.secrets["type"],
    "project_id": st.secrets["project_id"],
    "private_key_id": st.secrets["private_key_id"],
    "private_key": st.secrets["private_key"],
    "client_email": st.secrets["client_email"],
    "client_id": st.secrets["client_id"],
    "auth_uri": st.secrets["auth_uri"],
    "token_uri": st.secrets["token_uri"],
    "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url"],
    "client_x509_cert_url": st.secrets["client_x509_cert_url"],
    "universe_domain": st.secrets["universe_domain"],
}

credentials = service_account.Credentials.from_service_account_info(secrets_dict)

# credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
#from service account info-- the following should be done. 
sheets_service = build('sheets', 'v4', credentials=credentials)
drive_service = build('drive', 'v3', credentials=credentials)
# users = {
#     "user1": "password1",
#     "user2": "password2",
    
# }
os.environ["url"]="https://docs.google.com/spreadsheets/d/13BV2zrmSrOtDYH_EY21UXVmcZ89bEFsG4aYIxxVwpwo/edit#gid=0"


# placeholder=st.empty()

# with placeholder.container():
#     username = st.text_input("Username")
#     password = st.text_input("Password", type="password")
#     login_button = st.button("Login")


#this loads a data frame from a sheet
def loadInformation(url,sheet_name):
    tracking_spreadsheet_id = url.split('/')[-2]
    tracking_range_name=sheet_name
    data = sheets_service.spreadsheets().values().get(spreadsheetId=tracking_spreadsheet_id, range=tracking_range_name).execute()
    datavalues = data.get('values', [])
    data_df = pd.DataFrame(datavalues[1:], columns=datavalues[0])
    
    return data_df

def loadUsersAndPasswords(url=os.environ['url'],sheet_name="Sheet3"):
    tracking_spreadsheet_id = url.split('/')[-2]
    tracking_range_name=sheet_name
    data = sheets_service.spreadsheets().values().get(spreadsheetId=tracking_spreadsheet_id, range=tracking_range_name).execute()
    datavalues = data.get('values', [])
    data_df = pd.DataFrame(datavalues[1:], columns=datavalues[0])
    userdict=dict(zip(data_df["UserID"],data_df["Password"]))
    return userdict
users=loadUsersAndPasswords()

def compareID(user_id, df_responses, df_feedback):
    # Filter out the pairs that have been evaluated by the given user
    if 'unevaluated_pairs' not in st.session_state:
        # Filter out the pairs that have been evaluated by the given user
        
        evaluated_pairs = df_feedback[df_feedback['userID'] == user_id]['pairID'].tolist()

        # Filter the response data frame to include only the unevaluated pairs
        unevaluated_pairs_df = df_responses[~df_responses['pairID'].isin(evaluated_pairs)]

        # Store the unevaluated pairs in st.session_state
        st.session_state.unevaluated_pairs = unevaluated_pairs_df
        st.session_state.queue_index = 0  # Initialize the queue index

    return st.session_state.unevaluated_pairs

def create_queue(unevaluated_pairs):
    queue = unevaluated_pairs['pairID'].tolist()
    return queue
def get_next_from_queue(queue):
    if 'queue_index' not in st.session_state:
        st.session_state.queue_index = 0
    elif st.session_state.queue_index < len(queue) - 1:
        st.session_state.queue_index += 1
    else:
        st.session_state.queue_index = 0  # Loop back to the beginning

    return queue[st.session_state.queue_index]
# loadInformation("https://docs.google.com/spreadsheets/d/13BV2zrmSrOtDYH_EY21UXVmcZ89bEFsG4aYIxxVwpwo/edit#gid=0","Sheet1")

# build code that allows a quue to be stored. 
def updateSheet(updateObject,url=os.environ['url']):
    spreadsheet_id = url.split('/')[-2]
    
    range_name = 'Sheet2!A2'  # Replace 'Sheet1' with the sheet name if it's not the first sheet

    # Prepare the data as a list of lists (each sublist represents a row)
    values = [updateObject]

    # Create a ValueRange object for the new row
    

    # Insert the new row at the top (first entry) of the sheet
    result = sheets_service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id, range=range_name,
        valueInputOption='RAW', insertDataOption='INSERT_ROWS', body={'values':values}
    ).execute()

    print(f'New row inserted at the top of the sheet')

    
    return

def load_and_display_image(image_name):
    # Search for the image by name in Google Drive
    
    results = drive_service.files().list(q=f"name='{image_name}' and mimeType='image/jpeg'").execute()
    items = results.get('files', [])
    if not items:
        st.error(f"No image named '{image_name}' found in Google Drive.")
    else:
        image_id = items[0]['id']

        # Download the image
        request = drive_service.files().get_media(fileId=image_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()

        # Display the downloaded image
        st.image(fh, caption=f"Image: {image_name}")

def load_login():
    #loading the following 
    return

def addToSecrets(username,Password):
    # 
    #
    url=os.environ['url']
    spreadsheet_id = url.split('/')[-2]
    
    range_name = 'Sheet3!A2'  # Replace 'Sheet1' with the sheet name if it's not the first sheet

    # Prepare the data as a list of lists (each sublist represents a row)
    updateObject=[username,Password]
    values = [updateObject]

    # Create a ValueRange object for the new row
    

    # Insert the new row at the top (first entry) of the sheet
    result = sheets_service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id, range=range_name,
        valueInputOption='RAW', insertDataOption='INSERT_ROWS', body={'values':values}
    ).execute()

    print(f'New row inserted at the top of the sheet')
    
    
    return
import time
def submitLeft():
    preference=st.session_state['left']
    user_id=st.session_state.user_id
    pair_ID=st.session_state.currPairID
    
    objectToSend=[pair_ID,user_id,preference,time.time(),"unknown"]
    updateSheet(objectToSend)
    return
def submitRight():
    preference=st.session_state['right']
    user_id=st.session_state.user_id
    pair_ID=st.session_state.currPairID
    
    objectToSend=[pair_ID,user_id,preference,time.time(),"unknown"]
    updateSheet(objectToSend)
    return
def load_content():
    st.write('<style>div.row-widget.stButton > div{flex-direction: row;}</style>', unsafe_allow_html=True)
    if 'unevaluated_pairs' not in st.session_state:
        sheet1=loadInformation(os.environ["url"],"Sheet1")
        sheet2=loadInformation(os.environ["url"],"Sheet2")
        queue=create_queue(compareID(st.session_state.user_id,sheet1,sheet2 ))
    else:
        queue = create_queue(st.session_state.unevaluated_pairs)
    
    # imageFolder = "/content/TestFolder"
    # filesList = os.listdir(imageFolder)
    # image_url = imageFolder + "/" + random.choice(filesList)
    # st.image(image_url)
    # infromation neds to queued before this, create file that has the images mapped to the valuables. DO tonight or tomorrow. 
    # preferably need to be able to get this working, 
    # 
    row=get_next_from_queue(queue)
    print(row)
    current_row = st.session_state.unevaluated_pairs[st.session_state.unevaluated_pairs['pairID'] == row]
    load_and_display_image(current_row["dicom_ID"].values[0])
    # ok so what should be included in this thing. 
    # what needs to be completed. 
    columns = st.columns(2)
    
    # need to load left and right prompts:
    # ensure which ever one is preferred send the informaiton back
    
    # left prompt and right prompt need to come from the sheet. 
    # 

    if 'unevaluated_pairs' not in st.session_state:
        left_prompt = "This is the left prompt."
        right_prompt = "This is the right prompt."
    else:
        current_row = st.session_state.unevaluated_pairs[st.session_state.unevaluated_pairs['pairID'] == row]
        response_a = current_row['ResponseA'].values[0]
        response_b = current_row['ResponseB'].values[0]
        st.session_state["currPairID"]=row
        if random.choice([True, False]):
            left_prompt = response_a
            right_prompt = response_b
            st.session_state["left"]=0
            st.session_state['right']=1
        else:
            left_prompt = response_b
            right_prompt = response_a
            st.session_state["left"]=1
            st.session_state['right']=0

    with columns[0]:
        st.write(left_prompt)

    with columns[1]:
        st.write(right_prompt)

    columns1 = st.columns(2)

    with columns1[0]:
        button_clicked = st.button("Left",on_click=submitLeft)
        if button_clicked:
            st.write("Left button clicked")

    with columns1[1]:
        button_clicked = st.button("Right",on_click=submitRight)
        if button_clicked:
            st.write("Right button clicked")
            



      
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Conditional rendering based on the login state
if not st.session_state.logged_in:
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_button = st.button("Login")
    sign_up_button = st.button("Sign Up")
    #include a button that has new user....,
    if login_button:
        if username in users and users[username] == password:
            st.session_state.logged_in = True
            st.session_state.user_id = username
            st.rerun()
        else:
            st.error("Login Failed. Please check your username and password.")
    elif sign_up_button:
        #if username already in use ignore, else, signup and utilize the new username password. store user name passwords in a distinct gsheet. 
        if not username in users and password:
            addToSecrets(username,password)
            st.rerun()
        else:
            st.error("username either used or bad password")
    
        

else:
    load_content()          

# lets get going on this shit. 

# st.write('<style>div.row-widget.stButton > div{flex-direction: row;}</style>', unsafe_allow_html=True)

# # set up code to load the image for the user? done
# # images will be stored in an unknown location assume- fix
# # ok need to build some code to call back end information that allows me to check if the file has been used.
# # either remember user by name, or rememebr user by the cookie.
# # 4000 rows, for the following
# imageFolder = "/content/TestFolder"

# filesList=os.listdir(imageFolder)

# # outsideIP, 
# # need to build loading code for images and data. 
# # have a local process running the code for the dataset...

# def getData(url):
#     #should access a remote server
#     # organize based off information in the remote
    
#     pass
    
# def loadImage():
#     # load image from location specified....
    
#     return
# #dataset needs pairID())
    
    

# # get user ID:

# #call data, userID
# # 


# image_url = imageFolder+"/"+random.choice(filesList)  # Replace with your image URL
# st.image(image_url)
# columns = st.columns(2)

# # Define text prompts for the left and right columns
# # maintain login credetials. 
# left_prompt = "This is the left prompt."
# right_prompt = "This is the right prompt."


# # Add text to the left and right columns
# with columns[0]:
#     st.write(left_prompt)

# with columns[1]:
#     st.write(right_prompt)

# # Add a central image

# columns1 = st.columns(2)
# # Add a button to indicate left or right
# with columns1[0]:
#   button_clicked = st.button("Left")
#   if button_clicked:
#       st.write("Left button clicked")
# with columns1[1]:
#   button_clicked = st.button("Right")
#   if button_clicked:
#       st.write("Right button clicked")
