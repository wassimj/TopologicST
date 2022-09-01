import streamlit as st

src = 'https://3dviewer.net/index.html#model=https://github.com/KhronosGroup/glTF-Sample-Models/blob/master/sourceModels/2CylinderEngine/2CylinderEngine.dae'

st.components.v1.iframe(src, width=900, height=900, scrolling=True)
