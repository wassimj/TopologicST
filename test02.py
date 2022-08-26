
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

def getStreams(client):
    return client.stream.list()

#--------------------------

#--------------------------
#PAGE CONFIG
st.set_page_config(
    page_title="Topologic Speckle Test Application",
    page_icon="📊"
)
#--------------------------

#--------------------------
#CONTAINERS
topologicContainer = st.container()
header = st.container()
authenticate = st.container()
#--------------------------

with topologicContainer:
    st.subheader("Testing Topologic")
    v1 = topologic.Vertex.ByCoordinates(0,0,0)
    st.write("V1: Created a Vertex at: X ", v1.X(), " Y ", v1.Y(), " Z ", v1.Z())
    v2 = topologic.Vertex.ByCoordinates(10,0,0)
    st.write("V2: Created a Vertex at: X ", v2.X(), " Y ", v2.Y(), " Z ", v2.Z())
    e1 = topologic.Edge.ByStartVertexEndVertex(v1, v2)
    l1 = round(topologic.EdgeUtility.Length(e1), 2)
    st.write("E1: Connected V1 and V2 with and Edge. The edge's length is: ", l1)
    c1 = e1.Centroid()
    st.write("C1: Created a Centroid of edge E1. Its coordinates are: X ", c1.X(), " Y ", c1.Y(), " Z ", c1.Z())


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
# Get Access Code
try:
    access_code = st.experimental_get_query_params()['access_code'][0]
    st.write('Saving access code locally')
    status = conn.setLocalStorageVal(key='access_code', val=access_code)
    st.write('Status: ' + status)
except:
    try:
        access_code = conn.getLocalStorageVal(key='access_code')
    except:
        access_code = ''

if not challenge or not access_code:
    st.write('No challenge string or no access code are stored locally. Creating a new random challenge string')
    challenge = createRandomChallenge()

    st.write('Saving challenge string locally')
    status = conn.setLocalStorageVal(key='challenge', val=challenge)
    st.write('Status: ' + status)

    # Verify the app with the challenge
    st.write("Verifying the App with the challenge string")
    verify_url="https://speckle.xyz/authn/verify/"+appID+"/"+challenge
    st.write("Click this to Verify:", verify_url)
else:
    st.write('Found challenge string stored locally: ', challenge)
    st.write('Found access code stored locally: ', access_code)


#--------------------------
if access_code and challenge:
    st.write("Attempting to get token from access code and challenge")
    try:
        token = conn.getLocalStorageVal(key='token')
        refreshToken = conn.getLocalStorageVal(key='refreshToken')
    except:
        token = ''
        refreshToken = ''
    if not token or not refreshToken:
        tokens = requests.post(
                url=f"https://speckle.xyz/auth/token",
                json={
                    "appSecret": appSecret,
                    "appId": appID,
                    "accessCode": access_code,
                    "challenge": challenge,
                },
            )
        token = tokens.json()['token']
        refreshToken = tokens.json()['refreshToken']
        status = conn.setLocalStorageVal(key='token', val=token)
        status = conn.setLocalStorageVal(key='refreshToken', val=refreshToken)
    st.write('TOKEN: ', token)
    if token:
        account = get_account_from_token("speckle.xyz", token)
        st.write("ACCOUNT", account)
        client = SpeckleClient(host="speckle.xyz")
        client.authenticate_with_token(token)
        try:
            streams = getStreams(client)
        except:
            account = get_account_from_token("speckle.xyz", refreshToken)
            st.write("ACCOUNT", account)
            client = SpeckleClient(host="speckle.xyz")
            client.authenticate_with_token(refreshToken)
            streams = getStreams(client)
        stream_names = ["Select a stream"]
        for aStream in streams:
            stream_names.append(aStream.name)
        option = st.selectbox(
            'Select A Stream',
            (stream_names))
        if option != "Select a stream":
            stream = streams[stream_names.index(option)-1]
            st.write(option)
            st.subheader("Preview Image")
            st.components.v1.iframe(src="https://speckle.xyz/preview/"+stream.id, width=250,height=250)
            st.components.v1.iframe(src="https://speckle.xyz/embed?stream="+stream.id+"&transparent=false", width=400,height=600)
    else:
        st.write("Process Failed. Could not get account")

