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

header = st.container()
input = st.container()
viewer = st.container()
report = st.container()
graphs = st.container()

with header:
    st.title("Topologic - Speckle - Streamlit Testing Application")
with header.expander("About this App", expanded=True):
    st.markdown("""This is a test application that shows you how you can use Topologic with Speckle and Streamlit.""")
