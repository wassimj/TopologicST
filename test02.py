
#--------------------------
#IMPORT LIBRARIES
#import requests
import requests
#import streamlit
import streamlit as st

# import topologic
# This requires some checking of the used OS platform to load the correct version of Topologic
import sys
import os
from sys import platform
if platform == 'win32':
    os_name = 'windows'
else:
    os_name = 'linux'
sitePackagesFolderName = os.path.join(os.path.dirname(os.path.realpath(__file__)), "bin", os_name)
topologicFolderName = [filename for filename in os.listdir(sitePackagesFolderName) if filename.startswith("topologic")][0]
topologicPath = os.path.join(sitePackagesFolderName, topologicFolderName)
sys.path.append(topologicPath)
topologicPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "site-packages")
sys.path.append(topologicPath)
import topologic


#specklepy libraries
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token
#import pandas
import pandas as pd
#import plotly express
import plotly.express as px
#--------------------------

#--------------------------
#PAGE CONFIG
st.set_page_config(
    page_title="Speckle Stream Activity",
    page_icon="📊"
)
#--------------------------

#--------------------------
#CONTAINERS
header = st.container()
authenticate = st.container()
viewer = st.container()
report = st.container()
graphs = st.container()
#--------------------------

#--------------------------
#HEADER
#Page Header
with header:
    st.title("Speckle Stream Activity App📈")
#About info
with header.expander("About this app🔽", expanded=True):
    st.markdown(
        """This is a beginner web app developed using Streamlit. My goal was to understand how to interact with Speckle API using SpecklePy, 
        analyze what is received and its structure. This was easy and fun experiment.

        **Topologic works! Now I have moved on to testing Speckle. Please ignore any errors that appear below**
        """
    )
#--------------------------

#--------------------------
#INPUTS
with authenticate:
#-------
    appID = "618a698b8a"
    appSecret = "6a406094f6"
    authorization_url = "https://speckle.xyz/authn/verify/"+appID+"/"+appSecret
    st.write(f'''<h2>
    Please login using this <a target="_new"
    href="{authorization_url}">link</a></h2>''',
        unsafe_allow_html=True)
    access_code = st.experimental_get_query_params()['access_code'][0]
    st.write("ACCESS CODE RECEIVED FROM SPECKLE: ", access_code)
    response = requests.post(
    url=f"https://speckle.xyz/auth/token",
    json={
        "appSecret": "6a406094f6",
        "appId": "618a698b8a",
        "accessCode": access_code,
        "challenge": "6a406094f6",
    },
)
    st.write("RESPONSE", response)

    response_json = response.json()
    token = response_json['token']
    #-------
    #-------
    #Columns for inputs
    #serverCol, tokenCol = st.columns([1,3])
    #User Input boxes
    #speckleServer = serverCol.text_input("Server URL", "speckle.xyz", help="Speckle server to connect.")
    #speckleToken = tokenCol.text_input("Speckle token", access_code, help="If you don't know how to get your token, take a look at this [link](https://speckle.guide/dev/tokens.html)👈")
    #-------


#-------
#Get account from Token

    #CLIENT
    client = SpeckleClient(host="speckle.xyz")
    
    #Authenticate
    client.authenticate_with_token(token)

    #-------

    #-------
    #Streams List👇
    streams = client.stream.list()
    #Get Stream Names
    streamNames = [s.name for s in streams]
    #Dropdown for stream selection
    sName = st.selectbox(label="Select your stream", options=streamNames, help="Select your stream from the dropdown")
    #SELECTED STREAM ✅
    stream = client.stream.search(sName)[0]
    #Stream Branches 🌴
    branches = client.branch.list(stream.id)
    #Stream Commits 🏹
    commits = client.commit.list(stream.id, limit=100)
    #-------
#--------------------------

    #--------------------------
    #DEFINITIONS
    #create a definition to convert your list to markdown
    def listToMarkdown(list, column):
        list = ["- " + i + " \n" for i in list]
        list = "".join(list)
        return column.markdown(list)

    #create a definition that creates iframe from commit id
    def commit2viewer(stream, commit, height=400) -> str:
        embed_src = "https://speckle.xyz/embed?stream="+stream.id+"&commit="+commit.id
        return st.components.v1.iframe(src=embed_src, height=height)
    #--------------------------

    #--------------------------
    #VIEWER👁‍🗨
    #with viewer:
        #st.subheader("Latest Commit👇")
        #commit2viewer(stream, commits[0])
    #--------------------------