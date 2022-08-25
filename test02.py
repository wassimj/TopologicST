
#--------------------------
#IMPORT LIBRARIES
#import requests
import requests
import random
import math
import string
#import streamlit
import streamlit as st
from streamlit_ws_localstorage import injectWebsocketCode, getOrCreateUID

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

from streamlit_ws_localstorage import injectWebsocketCode, getOrCreateUID
#--------------------------

#--------------------------
#DEFINITIONS
def createRandomChallenge():
        lowercase = list(string.ascii_lowercase)
        uppercase = list(string.ascii_uppercase)
        punctuation = ['-', '.', '/', ':', ';', '<', '=', '>', '?']
        digits = list(string.digits)
        masterlist = lowercase+uppercase+digits
        random.shuffle(masterlist)
        masterlist = random.sample(masterlist, random.randint(math.floor(len(masterlist)*0.5),len(masterlist)))
        return ''.join(masterlist)
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
#--------------------------



#--------------------------
#HEADER
#Page Header
with header:
    st.title("Topologic Speckle Testing App📈")
#About info
with header.expander("About this app🔽", expanded=True):
    st.markdown(
        """This is a beginner web app developed using Topologic, Speckle, and Streamlit. My goal was to use Streamlit to deploy Topologic as server-based app, understand how to interact with Speckle API using SpecklePy, 
        analyze what is received and its structure. This was NOT and easy (but fun) experiment.

        Topologic works! Now I have moved on to testing Speckle. Please ignore any errors that appear below.
        """
    )
#--------------------------

# WARNING: This needs to be changed into text input from the user
appID = "618a698b8a"
appSecret = "6a406094f6"

# This allows us to store variables locally through websockets
# Main call to the api, returns a communication object
conn = injectWebsocketCode(hostPort='linode.liquidco.in', uid=getOrCreateUID())

# Test if there is already a locally stored challenge
try:
    challenge = conn.getLocalStorageVal(key='challenge')
    
except:
    challenge = ''

if not challenge:
    st.write('No challenge string is stored locally. Creating a new random challenge string')
    challenge = createRandomChallenge()

    st.write('Saving challenge string locally')
    status = conn.setLocalStorageVal(key='challenge', val=challenge)
    st.write('Status: ' + status)

    # Verify the app with the challenge
    st.write("Verifying the App with the challenge string")
    verify_url="https://speckle.xyz/authn/verify/"+appID+"/"+appSecret+"/?challenge="+challenge
    st.write("Click this to Verify:", verify_url)
else:
    st.write('Found challenge string stored locally: ', challenge)

#--------------------------
# Get Access Code
try:
    access_code = st.experimental_get_query_params()['access_code'][0]
except:
    access_code = ''

st.write("ACCESS CODE:", access_code)
if access_code:
    tokens = requests.post(
            url=f"https://speckle.xyz/auth/token",
            json={
                "appSecret": appSecret,
                "appId": appID,
                "accessCode": access_code,
                "challenge": challenge,
            },
        )
    st.write("TOKENS:", tokens)
    token = tokens.json()['token']
    st.write('Emptying localStorage')
    status = conn.setLocalStorageVal(key='challenge', val='')
    st.write('Status: ' + status)
    st.write('TOKEN: ', token)
    if token:
        account = get_account_from_token("speckle.xyz", token)
        st.write("ACCOUNT", account)
    else:
        st.write("Process Failed. Could not get account")

