import streamlit as st
import os
import pathlib
from os import listdir
from os.path import isfile, join
st.write("""
# Demo
""")
parent_path = pathlib.Path(__file__).parent.parent.resolve()
st.write(parent_path)
#data_path = os.path.join(parent_path, "data")
onlyfiles = [f for f in listdir(parent_path) if isfile(join(parent_path, f))]
option = st.sidebar.selectbox('Pick a dataset', onlyfiles)
file_location=os.path.join(parent_path, option)
# use `file_location` as a parameter to the main script