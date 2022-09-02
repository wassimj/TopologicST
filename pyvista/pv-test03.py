import streamlit as st
import streamlit.components.v1 as components

html_file = st.file_uploader("", type="html", accept_multiple_files=False)
if html_file:
    html = html_file.read()
    st.markdown(html)
    st.components.v1.html(html,height=400)