
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



# Main call to the api, returns a communication object
conn = injectWebsocketCode(hostPort='linode.liquidco.in', uid=getOrCreateUID())

challenge = createRandomChallenge()

st.write('setting into localStorage')
ret = conn.setLocalStorageVal(key='challenge', val=challenge)
st.write('ret: ' + ret)
appID = "618a698b8a"
appSecret = "6a406094f6"
st.write("Verifying the App with the Challenge")
verify_url="https://speckle.xyz/authn/verify/appID/appSecret/?challenge="+challenge
response = requests.post(url=verify_url)
st.write("REGISTRATION RESPONSE: ", response)
response = requests.post(url=verify_url)

st.write("RESPONSE: ", response)
try:
    access_code = st.experimental_get_query_params()['access_code'][0]
    st.write("ACCESS CODE RECEIVED FROM SPECKLE: ", access_code)
except:
    access_code = ''

token = 'NONE'
if access_code:
    challenge = conn.getLocalStorageVal(key='challenge')
    response = requests.post(
        url=f"https://speckle.xyz/auth/token",
        json={
            "appSecret": "6a406094f6",
            "appId": "618a698b8a",
            "accessCode": access_code,
            "challenge": challenge,
        },)
    response_json = response.json()
    token = response_json['token']

st.write('TOKEN: ', token)
account = get_account_from_token("speckle.xyz", token)
st.write("ACCOUNT", account)
