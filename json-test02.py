#--------------------------
# IMPORT LIBRARIES
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import json
from numpy import arctan, pi, signbit, arctan2, rad2deg
from numpy.linalg import norm
import pandas as pd

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

from topologicpy import TopologyByImportedJSONMK1, TopologyApertures, TopologyTriangulate, DictionaryValueAtKey, DictionaryKeys, FaceNormalAtParameters, CellComplexDecompose
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

def faceAngleFromNorth(f, north):
    dirA = FaceNormalAtParameters.processItem([f, 0.5, 0.5], "XYZ", 3)
    ang = compass_angle((dirA[0],dirA[1]), (north[0], north[1]))
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

def addApertures(dataList, f, north):
    ap, apertures = TopologyApertures.processItem(f)
    if len(apertures) > 0: #This face has a window so must be a wall, count it.
        dirA = FaceNormalAtParameters.processItem([f, 0.5, 0.5], "XYZ", 3)
        ang, ang_str, color_str = faceAngleFromNorth(f, north)
        for aperture in apertures:
            mesh_data, wire_data = plotlyDataByTopology(aperture, mesh_opacity=1, mesh_color=color_str, wire_color="black", wire_width=1, draw_mesh=True, draw_wire=True)
            addData(dataList, mesh_data)
            addData(dataList, wire_data)
    return dataList

def plotlyDataByTopology(topology=None, mesh_opacity=0.5, mesh_color="lightgrey", wire_color="black", wire_width=1, draw_mesh=False, draw_wire=True):
    mesh_data = []
    wire_data = []
    faces = []
    if topology:
        if topology.Type() > topologic.Face.Type():
            _ = topology.Faces(None, faces)
        else:
            faces = [topology]
        if draw_wire:
            fx = []
            fy = []
            fz = []
            for face in faces:
                wires = []
                eb = face.ExternalBoundary()
                ib = []
                _ = face.InternalBoundaries(ib)
                wires = [eb]+ib
                for w in wires:
                    vertices = []
                    _ = w.Vertices(None, vertices)
                    for v in vertices:
                        fx.append(v.X())
                        fy.append(v.Y())
                        fz.append(v.Z())
                    fx.append(vertices[0].X())
                    fy.append(vertices[0].Y())
                    fz.append(vertices[0].Z())
                    fx.append(None)
                    fy.append(None)
                    fz.append(None)

            wire_data = go.Scatter3d(
            x=fx,
            y=fy,
            z=fz,
            showlegend=False,
            marker_size=0,
            mode="lines",
            line=dict(
                color=wire_color,
                width=wire_width
            ))
        if draw_mesh:
            if topology.GetTypeAsString() == "Cluster":
                cells = []
                _ = topology.Cells(None, cells)
                triangulated_cells = []
                for cell in cells:
                    triangulated_cells.append(TopologyTriangulate.processItem(cell, 0.0001))
                topology = topologic.Cluster.ByTopologies(triangulated_cells)
            else:
                topology = TopologyTriangulate.processItem(topology, 0.0001)
            tp_vertices = []
            _ = topology.Vertices(None, tp_vertices)
            x = []
            y = []
            z = []
            vertices = []
            intensities = []
            for tp_v in tp_vertices:
                vertices.append([tp_v.X(), tp_v.Y(), tp_v.Z()])
                x.append(tp_v.X())
                y.append(tp_v.Y())
                z.append(tp_v.Z())
                intensities.append(0)
            faces = []
            tp_faces = []
            _ = topology.Faces(None, tp_faces)
            for tp_f in tp_faces:
                f_vertices = []
                _ = tp_f.Vertices(None, f_vertices)
                f = []
                for f_v in f_vertices:
                    f.append(vertices.index([f_v.X(), f_v.Y(), f_v.Z()]))
                faces.append(f)

            i = []
            j = []
            k = []
            for f in faces:
                i.append(f[0])
                j.append(f[1])
                k.append(f[2])

            mesh_data = go.Mesh3d(
                    x=x,
                    y=y,
                    z=z,
                    # i, j and k give the vertices of triangles
                    # here we represent the 4 triangles of the tetrahedron surface
                    i=i,
                    j=j,
                    k=k,
                    name='y',
                    showscale=False,
                    showlegend = False,
                    color = mesh_color,
                    opacity = mesh_opacity,
                    flatshading = True,
                    lighting = {"facenormalsepsilon": 0},
                )
        return ([mesh_data, wire_data])


#--------------------------
# PAGE LAYOUT
#--------------------------
# TITLE
icon_column, title_column = st.columns([1,10], gap="small")
with icon_column:
    st.image("https://topologic.app/wp-content/uploads/2018/10/Topologic-Logo-250x250.png",width=100)
with title_column:
    st.title("Topologic JSON Test App")

def reset():
    st.write('Deleting session state')
    del st.session_state['topology']
#--------------------------
# INPUT

st.subheader("Upload Topologic JSON MK1 File")

c = None
 # Initialization
if 'topology' not in st.session_state:
    st.session_state['topology'] = c
st.button("Reset", on_click=reset(), disabled=False)
json_file = st.file_uploader("", type="json", accept_multiple_files=False)
try:
    c = st.session_state['topology']
except:
    if json_file:
        topologies = TopologyByImportedJSONMK1.processItem(json_file)
        c = topologies[0]
        st.session_state['topology'] = c

if c:
    st.subheader(c)
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
    mesh_data, wire_data = plotlyDataByTopology(topology=c, mesh_opacity=mesh_opacity, mesh_color="lightgrey", wire_color="black", wire_width=1, draw_mesh=True, draw_wire=True)
    dataList = [wire_data]
    #faces = []
    #_ = c.Faces(None, faces)
    north = [0,1,0]
    ex_ve_f, in_ve_f, to_ho_f, bo_ho_f, in_ho_f, ex_in_f, in_in_f, ex_ve_a, in_ve_a, to_ho_a, bo_ho_a, in_ho_a, ex_in_a, in_in_a = CellComplexDecompose.processItem(c)
    #ex_ve_f, in_ve_f, to_ho_f, bo_ho_f, in_ho_f, ex_in_f, in_in_f, ex_ve_a, in_ve_a, to_ho_a, bo_ho_a, in_ho_a, ex_in_a, in_in_a = CellComplexDecompose.processItem(None)
    
    if ex_ve_f_f:
        for f in ex_ve_f:
            ang, ang_str, color_str = faceAngleFromNorth(f, north)
            mesh_data, wire_data = plotlyDataByTopology(topology=f, mesh_opacity=mesh_opacity, mesh_color=color_str, wire_color="black", wire_width=1, draw_mesh=True, draw_wire=False)
            addData(dataList, mesh_data)
            addData(dataList, wire_data)
            if apr_f:
                addApertures(dataList, f, north)
    if in_ve_f_f:
        for f in in_ve_f:
            mesh_data, wire_data = plotlyDataByTopology(topology=f, mesh_opacity=mesh_opacity, mesh_color="red", wire_color="black", wire_width=1, draw_mesh=True, draw_wire=False)
            addData(dataList, mesh_data)
            addData(dataList, wire_data)
            if apr_f:
                addApertures(dataList, f, north)
    if to_ho_f_f:
        for f in to_ho_f:
            mesh_data, wire_data = plotlyDataByTopology(topology=f, mesh_opacity=mesh_opacity, mesh_color="red", wire_color="black", wire_width=1, draw_mesh=True, draw_wire=False)
            addData(dataList, mesh_data)
            addData(dataList, wire_data)
            if apr_f:
                addApertures(dataList, f, north)
    if bo_ho_f_f:
        for f in bo_ho_f:
            mesh_data, wire_data = plotlyDataByTopology(topology=f, mesh_opacity=mesh_opacity, mesh_color="red", wire_color="black", wire_width=1, draw_mesh=True, draw_wire=False)
            addData(dataList, mesh_data)
            addData(dataList, wire_data)
            if apr_f:
                addApertures(dataList, f, north)
    if in_ho_f_f:
        for f in in_ho_f:
            mesh_data, wire_data = plotlyDataByTopology(topology=f, mesh_opacity=mesh_opacity, mesh_color="red", wire_color="black", wire_width=1, draw_mesh=True, draw_wire=False)
            addData(dataList, mesh_data)
            addData(dataList, wire_data)
            if apr_f:
                addApertures(dataList, f, north)
    if ex_in_f_f:
        for f in ex_in_f:
            ang, ang_str, color_str = faceAngleFromNorth(f, north)
            mesh_data, wire_data = plotlyDataByTopology(topology=f, mesh_opacity=mesh_opacity, mesh_color=color_str, wire_color="black", wire_width=1, draw_mesh=True, draw_wire=False)
            addData(dataList, mesh_data)
            addData(dataList, wire_data)
            if apr_f:
                addApertures(dataList, f, north)
    if in_in_f_f:
        for f in in_in_f:
            mesh_data, wire_data = plotlyDataByTopology(topology=f, mesh_opacity=mesh_opacity, mesh_color="red", wire_color="black", wire_width=1, draw_mesh=True, draw_wire=False)
            addData(dataList, mesh_data)
            addData(dataList, wire_data)
            if apr_f:
                addApertures(dataList, f, north)

    fig = go.Figure(data=dataList, )
    fig.update_layout(
        width=900,
        height=700,
        scene = dict(
            xaxis = dict(visible=False),
            yaxis = dict(visible=False),
            zaxis =dict(visible=False),
            )
        )
    st.plotly_chart(fig)
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
