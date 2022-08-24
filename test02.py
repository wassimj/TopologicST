
import streamlit as st

import sys
import os, re
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

v1 = topologic.Vertex.ByCoordinates(0,0,0)
st.write("V1: Created a Topologic Vertex at", v1.X(), v1.Y(), v1.Z())
v2 = topologic.Vertex.ByCoordinates(10,0,0)
st.write("V2: Created a Topologic Vertex at", v2.X(), v2.Y(), v2.Z())
e1 = topologic.Edge.ByStartVertexEndVertex(v1, v2)
st.write("E1: Connected V1 and V2 with a Toplogic Edge")
c1 = e1.Centroid()
st.write("C1: The centroid of the Topologic Edge is at", c1.X(), c1.Y(), c1.Z())

st.write("Trying to import specklepy")
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_default_account
from specklepy.transports.memory import MemoryTransport
from specklepy.api import operations
from specklepy.api.wrapper import StreamWrapper
from specklepy.api.resources.stream import Stream
from specklepy.transports.server import ServerTransport
from specklepy.objects.geometry import *
from specklepy.logging.exceptions import SpeckleException
from specklepy.objects.other import RenderMaterial
st.write("Success!")
