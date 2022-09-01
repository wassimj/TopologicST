#--------------------------
# IMPORT LIBRARIES
import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
import plotly.express as px
import json
from io import StringIO
import numpy as np
from numpy import arctan, pi, signbit, arctan2, rad2deg
from numpy.linalg import norm
import pandas as pd
import pyvista as pv

import io
import tempfile

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

from topologicpy import TopologyGeometry, TopologyByImportedJSONMK1, TopologyApertures, TopologyTriangulate, DictionaryValueAtKey, DictionaryKeys, FaceNormalAtParameters, CellComplexDecompose
#--------------------------
#--------------------------
# PAGE CONFIGURATION
st.set_page_config(
    page_title="Topologic JSON Test Application",
    page_icon="📊",
    layout="wide"
)
#--------------------------
#--------------------------
# DEFINITIONS
def compass_angle(p1, p2):
    ang1 = arctan2(*p1[::-1])
    ang2 = arctan2(*p2[::-1])
    return rad2deg((ang1 - ang2) % (2 * pi))

def angle_between(v1, v2):
	u1 = v1 / norm(v1)
	u2 = v2 / norm(v2)
	y = u1 - u2
	x = u1 + u2
	a0 = 2 * arctan(norm(y) / norm(x))
	if (not signbit(a0)) or signbit(pi - a0):
		return a0
	elif signbit(a0):
		return 0
	else:
		return pi

def faceAngleFromNorth(f, north):
    dirA = FaceNormalAtParameters.processItem([f, 0.5, 0.5], "XYZ", 3)
    ang = compass_angle((dirA[0],dirA[1]), (north[0], north[1]))
    #ang = round((angle_between(dirA, north) * 180 / pi), 2)
    if 22.5 < ang <= 67.5:
        ang_str = "NW"
        color_str = "red"
    elif 67.5 < ang <= 112.5:
        ang_str = "W"
        color_str = "green"
    elif 112.5 < ang <= 157.5:
        ang_str = "SW"
        color_str = "blue"
    elif 157.5 < ang <= 202.5:
        ang_str = "S"
        color_str = "yellow"
    elif 202.5 < ang <= 247.5:
        ang_str = "SE"
        color_str = "purple"
    elif 247.5 < ang <= 292.5:
        ang_str = "E"
        color_str = "cyan"
    elif 292.5 < ang <= 337.5:
        ang_str = "NE"
        color_str = "brown"
    else:
        ang_str = "N"
        color_str = "white"
    return [ang, ang_str, color_str]

def faceAperturesAndArea(f):
    aperture_area = 0
    ap, apertures = TopologyApertures.processItem(f)
    for aperture in apertures:
        aperture_area = aperture_area + topologic.FaceUtility.Area(aperture)
    return [apertures, aperture_area]

def addData(dataList, new_data):
    if not isinstance(new_data, list):
        new_data = [new_data]
    if len(new_data) > 0:
        dataList += new_data
    return dataList

def addApertures(p, f, north):
    ap, apertures = TopologyApertures.processItem(f)
    if len(apertures) > 0:
        dirA = FaceNormalAtParameters.processItem([f, 0.5, 0.5], "XYZ", 3)
        ang, ang_str, color_str = faceAngleFromNorth(f, north)
        for aperture in apertures:
            mesh_data = pvMeshByTopology(topology=aperture)
            p.add_mesh(mesh_data)
    return p

def pvMeshByTopology(topology=None):
    if topology:
        vertices, edges, faces = TopologyGeometry.processItem(topology)
        vertices = np.array(vertices)
        faces = np.hstack(faces)
        mesh = pv.PolyData(vertices, faces)
        return (mesh)

def pyvista_streamlit(plotter):
    ## Export to a pythreejs HTML
    model_html = io.StringIO()
    plotter.export_html(model_html, backend='pythreejs')
    #st.write(model_html.getvalue())
    ## Show in webpage
    st.components.v1.html(model_html.getvalue(),height=400)
#--------------------------
# PAGE LAYOUT
#--------------------------
# TITLE
icon_column, title_column = st.columns([1,10], gap="small")
with icon_column:
    st.image("https://topologic.app/wp-content/uploads/2018/10/Topologic-Logo-250x250.png",width=100)
with title_column:
    st.title("Topologic JSON Test App")

#--------------------------
# INPUT

st.subheader("Upload JSON MK1 File")
json_file = st.file_uploader("", type="json", accept_multiple_files=False)
if json_file:
    topologies = TopologyByImportedJSONMK1.processItem(json_file)
    col1, col2 = st.columns([1,1], gap="small")
    with col1:
        ex_ve_f_f = st.checkbox("External Vertical Faces", value=True)
        in_ve_f_f = st.checkbox("Internal Vertical Faces", value=True)
        to_ho_f_f = st.checkbox("Top Horizontal Faces", value=True)
        bo_ho_f_f = st.checkbox("Bottom Horizontal Faces", value=True)
    with col2:
        in_ho_f_f = st.checkbox("Internal Horizontal Faces", value=True)
        ex_in_f_f = st.checkbox("External Inclined Faces", value=True)
        in_in_f_f = st.checkbox("Internal Inclined Faces", value=True)
        apr_f = st.checkbox("Apertures", value=True)
        mesh_opacity = st.slider("Mesh Opacity", min_value=0.1, max_value=1.0, value=0.5, step=0.1)


#--------------------------
# CONTENT CREATION

    c = topologies[0]
    if c:
        pv.set_jupyter_backend('pythreejs')
        #pv.start_xvfb()
        #pv.set_plot_theme('document')
        mesh_data = pvMeshByTopology(topology=c)
# plot each face with a different color
        p = pv.Plotter(window_size=[500, 500])
        faces = []
        _ = c.Faces(None, faces)
        north = [0,1,0]
        ex_ve_f, in_ve_f, to_ho_f, bo_ho_f, in_ho_f, ex_in_f, in_in_f, ex_ve_a, in_ve_a, to_ho_a, bo_ho_a, in_ho_a, ex_in_a, in_in_a = CellComplexDecompose.processItem(c)
        if ex_ve_f_f:
            for f in ex_ve_f:
                mesh_data = pvMeshByTopology(topology=f)
                p.add_mesh(mesh_data)
                if apr_f:
                    addApertures(p, f, north)
        if in_ve_f_f:
            for f in in_ve_f:
                mesh_data = pvMeshByTopology(topology=f)
                p.add_mesh(mesh_data)
                if apr_f:
                    addApertures(p, f, north)
        if to_ho_f_f:
            for f in to_ho_f:
                mesh_data = pvMeshByTopology(topology=f)
                p.add_mesh(mesh_data)
                if apr_f:
                    addApertures(p, f, north)
        if bo_ho_f_f:
            for f in bo_ho_f:
                mesh_data = pvMeshByTopology(topology=f)
                p.add_mesh(mesh_data)
                if apr_f:
                    addApertures(p, f, north)
        if in_ho_f_f:
            for f in in_ho_f:
                mesh_data = pvMeshByTopology(topology=f)
                p.add_mesh(mesh_data)
                if apr_f:
                    addApertures(p, f, north)
        if ex_in_f_f:
            for f in ex_in_f:
                mesh_data = pvMeshByTopology(topology=f)
                p.add_mesh(mesh_data)
                if apr_f:
                    addApertures(p, f, north)
        if in_in_f_f:
            for f in in_in_f:
                mesh_data = pvMeshByTopology(topology=f)
                p.add_mesh(mesh_data)
                if apr_f:
                    addApertures(p, f, north)

        # Draw the 3D view
        p.add_floor('-z', lighting=True, color='white', pad=1.0)
        p.enable_shadows()
        pyvista_streamlit(p)

        n_walls = []
        s_walls = []
        e_walls = []
        w_walls = []
        ne_walls = []
        nw_walls = []
        se_walls = []
        sw_walls = []

        n_wall_area = 0
        s_wall_area = 0
        e_wall_area = 0
        w_wall_area = 0
        ne_wall_area = 0
        nw_wall_area = 0
        se_wall_area = 0
        sw_wall_area = 0

        n_apertures = []
        s_apertures = []
        e_apertures = []
        w_apertures = []
        ne_apertures = []
        nw_apertures = []
        se_apertures = []
        sw_apertures = []
        

        n_aperture_area = 0
        s_aperture_area = 0
        e_aperture_area = 0
        w_aperture_area = 0
        
        ne_aperture_area = 0
        nw_aperture_area = 0
        se_aperture_area = 0
        sw_aperture_area = 0
        

        for f in ex_ve_f:
            ang, ang_str, color_str = faceAngleFromNorth(f, north)
            wall_area = topologic.FaceUtility.Area(f)
            apertures, aperture_area = faceAperturesAndArea(f)
            if ang_str == "N":
                n_walls.append(f)
                n_wall_area = n_wall_area + wall_area
                n_apertures = n_apertures + apertures
                n_aperture_area = n_aperture_area + aperture_area
            elif ang_str == "S":
                s_walls.append(f)
                s_wall_area = s_wall_area + wall_area
                s_apertures = s_apertures + apertures
                s_aperture_area = s_aperture_area + aperture_area
            elif ang_str == "E":
                e_walls.append(f)
                e_wall_area = e_wall_area + wall_area
                e_apertures = e_apertures + apertures
                e_aperture_area = e_aperture_area + aperture_area
            elif ang_str == "W":
                w_walls.append(f)
                w_wall_area = w_wall_area + wall_area
                w_apertures = w_apertures + apertures
                w_aperture_area = w_aperture_area + aperture_area
            elif ang_str == "NE":
                ne_walls.append(f)
                ne_wall_area = ne_wall_area + wall_area
                ne_apertures = ne_apertures + apertures
                ne_aperture_area = ne_aperture_area + aperture_area
            elif ang_str == "NW":
                nw_walls.append(f)
                nw_wall_area = nw_wall_area + wall_area
                nw_apertures = nw_apertures + apertures
                nw_aperture_area = nw_aperture_area + aperture_area
            elif ang_str == "SE":
                se_walls.append(f)
                se_wall_area = se_wall_area + wall_area
                se_apertures = se_apertures + apertures
                se_aperture_area = se_aperture_area + aperture_area
            elif ang_str == "SW":
                sw_walls.append(f)
                sw_wall_area = sw_wall_area + wall_area
                sw_apertures = sw_apertures + apertures
                sw_aperture_area = sw_aperture_area + aperture_area

        if n_wall_area > 0:
            n_ap_or = n_aperture_area / n_wall_area * 100
        else:
            n_ap_or = 0
        if s_wall_area > 0:
            s_ap_or = s_aperture_area / s_wall_area * 100
        else:
            s_ap_or = 0
        if e_wall_area > 0:
            e_ap_or = e_aperture_area / e_wall_area * 100
        else:
            e_ap_or = 0
        if w_wall_area > 0:
            w_ap_or = w_aperture_area / w_wall_area * 100
        else:
            w_ap_or = 0
        if ne_wall_area > 0:
            ne_ap_or = ne_aperture_area / ne_wall_area * 100
        else:
            ne_ap_or = 0
        if nw_wall_area > 0:
            nw_ap_or = nw_aperture_area / nw_wall_area * 100
        else:
            nw_ap_or = 0
        if se_wall_area > 0:
            se_ap_or = se_aperture_area / se_wall_area * 100
        else:
            se_ap_or = 0
        if sw_wall_area > 0:
            sw_ap_or = sw_aperture_area / sw_wall_area * 100
        else:
            sw_ap_or = 0

        total_project_wall_area = s_wall_area + n_wall_area + ne_wall_area + nw_wall_area + sw_wall_area + se_wall_area
        total_project_aperture_area = n_aperture_area + s_aperture_area + e_aperture_area + w_aperture_area + ne_aperture_area + nw_aperture_area + se_aperture_area + sw_aperture_area
        
        n_ap_proj = n_aperture_area / total_project_wall_area * 100
        s_ap_proj = s_aperture_area / total_project_wall_area * 100
        e_ap_proj = e_aperture_area / total_project_wall_area * 100
        w_ap_proj = w_aperture_area / total_project_wall_area * 100
        ne_ap_proj = ne_aperture_area / total_project_wall_area * 100
        nw_ap_proj = nw_aperture_area / total_project_wall_area * 100
        se_ap_proj = se_aperture_area / total_project_wall_area * 100
        sw_ap_proj = sw_aperture_area / total_project_wall_area * 100
        
        total_ap_proj_percent = n_ap_proj+s_ap_proj+e_ap_proj+w_ap_proj+ne_ap_proj+nw_ap_proj+se_ap_proj+sw_ap_proj
        col_labels = ["Orientation", "Window Area", "Wall Area", "WWR By Orientation", "WWR By Project"]
        d = {"Orientation": ["E", "NE", "N", "NW", "W", "SW", "S", "SE", "Total"],
            'Window Area': [round(e_aperture_area,2),
                            round(ne_aperture_area,2),
                            round(n_aperture_area,2),
                            round(nw_aperture_area,2),
                            round(w_aperture_area,2),
                            round(sw_aperture_area,2),
                            round(s_aperture_area,2),
                            round(se_aperture_area,2),
                            round(total_project_aperture_area,2)],
            'Wall Area': [round(e_wall_area,2),
                            round(ne_wall_area,2),
                            round(n_wall_area,2),
                            round(nw_wall_area,2),
                            round(w_wall_area,2),
                            round(sw_wall_area,2),
                            round(s_wall_area,2),
                            round(se_wall_area,2),
                            round(total_project_wall_area,2)],
            'WWR By Orientation': [round(e_ap_or,2),
                                    round(ne_ap_or,2),
                                    round(n_ap_or,2),
                                    round(nw_ap_or,2),
                                    round(w_ap_or,2),
                                    round(sw_ap_or,2),
                                    round(s_ap_or,2),
                                    round(se_ap_or,2),
                                    0],
            'WWR By Project': [round(e_ap_proj,2),
                                round(ne_ap_proj,2),
                                round(n_ap_proj,2),
                                round(nw_ap_proj,2),
                                round(w_ap_proj,2),
                                round(sw_ap_proj,2),
                                round(s_ap_proj,2),
                                round(se_ap_proj,2),
                                round(total_ap_proj_percent,2)]}
        df = pd.DataFrame(data=d)
        st.table(df)
        d = {"Orientation": ["E", "NE", "N", "NW", "W", "SW", "S", "SE"],
            'Window Area': [round(e_wall_area,2),
                            round(ne_wall_area,2),
                            round(n_wall_area,2),
                            round(nw_wall_area,2),
                            round(w_wall_area,2),
                            round(sw_wall_area,2),
                            round(s_wall_area,2),
                            round(se_wall_area,2)]}
    
    col1, col2, col3, col4 = st.columns([1,1,1,1], gap="small")
    with col1:
        d = {'Orientation': ['E', 'NE', 'N', 'NW', 'W', 'SW', 'S', 'SE'],
            'Window Area': [round(e_aperture_area,2),
                            round(ne_aperture_area,2),
                            round(n_aperture_area,2),
                            round(nw_aperture_area,2),
                            round(w_aperture_area,2),
                            round(sw_aperture_area,2),
                            round(s_aperture_area,2),
                            round(se_aperture_area,2)]}
        fig = go.Figure(go.Barpolar(r=d["Window Area"],
                                    theta=d["Orientation"],
                                    marker_color=['cyan', 'brown', 'white', 'red', 'green', 'blue', 'yellow', 'purple'],
                                    marker_line_color="black",
                                    marker_line_width=1,
                                    opacity=0.8))
        fig.update_layout(title="Window Area", polar = dict(
        radialaxis = dict(showticklabels=False, ticks='')))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        d = {'Orientation': ['E', 'NE', 'N', 'NW', 'W', 'SW', 'S', 'SE'],
            'Wall Area': [round(e_wall_area,2),
                            round(ne_wall_area,2),
                            round(n_wall_area,2),
                            round(nw_wall_area,2),
                            round(w_wall_area,2),
                            round(sw_wall_area,2),
                            round(s_wall_area,2),
                            round(se_wall_area,2)]}
        fig = go.Figure(go.Barpolar(r=d["Wall Area"],
                                    theta=d["Orientation"],
                                    marker_color=['cyan', 'brown', 'white', 'red', 'green', 'blue', 'yellow', 'purple'],
                                    marker_line_color="black",
                                    marker_line_width=1,
                                    opacity=0.8))
        fig.update_layout(title="Wall Area", polar = dict(
        radialaxis = dict(showticklabels=False, ticks='')))
        st.plotly_chart(fig, use_container_width=True)

    with col3:
        d = {'Orientation': ['E', 'NE', 'N', 'NW', 'W', 'SW', 'S', 'SE'],
            'WWR By Orient': [round(e_ap_or,2),
                            round(ne_ap_or,2),
                            round(n_ap_or,2),
                            round(nw_ap_or,2),
                            round(w_ap_or,2),
                            round(sw_ap_or,2),
                            round(s_ap_or,2),
                            round(se_ap_or,2)]}
        fig = go.Figure(go.Barpolar(r=d["WWR By Orient"],
                                    theta=d["Orientation"],
                                    marker_color=['cyan', 'brown', 'white', 'red', 'green', 'blue', 'yellow', 'purple'],
                                    marker_line_color="black",
                                    marker_line_width=1,
                                    opacity=0.8))
        fig.update_layout(title="WWR By Orientation", polar = dict(
        radialaxis = dict(showticklabels=False, ticks='')))
        
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        d = {'Orientation': ['E', 'NE', 'N', 'NW', 'W', 'SW', 'S', 'SE'],
            'WWR By Project': [round(e_ap_proj,2),
                            round(ne_ap_proj,2),
                            round(n_ap_proj,2),
                            round(nw_ap_proj,2),
                            round(w_ap_proj,2),
                            round(sw_ap_proj,2),
                            round(s_ap_proj,2),
                            round(se_ap_proj,2)]}
        fig = go.Figure(go.Barpolar(r=d["WWR By Project"],
                                    theta=d["Orientation"],
                                    marker_color=['cyan', 'brown', 'white', 'red', 'green', 'blue', 'yellow', 'purple'],
                                    marker_line_color="black",
                                    marker_line_width=1,
                                    opacity=0.8))
        fig.update_layout(title="WWR By Project", polar = dict(
        radialaxis = dict(showticklabels=False, ticks='')))
        st.plotly_chart(fig, use_container_width=True)
