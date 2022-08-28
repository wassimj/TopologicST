#--------------------------
# IMPORT LIBRARIES
import streamlit as st
import plotly.graph_objects as go
import json
from io import StringIO
from numpy import arctan, pi, signbit
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
    ang = round((angle_between(dirA, north) * 180 / pi), 2)
    if 22.5 < ang <= 67.5:
        ang_str = "NW"
        color_str = "yellowgreen"
    elif 67.5 < ang <= 112.5:
        ang_str = "W"
        color_str = "chocolate"
    elif 112.5 < ang <= 157.5:
        ang_str = "SW"
        color_str = "mediumseagreen"
    elif 157.5 < ang <= 202.5:
        ang_str = "S"
        color_str = "limegreen"
    elif 202.5 < ang <= 247.5:
        ang_str = "SW"
        color_str = "khaki"
    elif 247.5 < ang <= 292.5:
        ang_str = "E"
        color_str = "yellow"
    elif 292.5 < ang <= 337.5:
        ang_str = "NE"
        color_str = "mediumslateblue"
    else:
        ang_str = "N"
        color_str = "cyan"
    return [ang, ang_str, color_str]

def faceAperturesAndArea(f):
    aperture_area = 0
    ap, apertures = TopologyApertures.processItem(f)
    for aperture in apertures:
        aperture_area = aperture_area + topologic.FaceUtility.Area(aperture)
    return [apertures, aperture_area]
def plotlyDataByTopology(topology, opacity, face_color="blue", line_color="white"):
    faces = []
    if topology.Type() > topologic.Face.Type():
        _ = topology.Faces(None, faces)
    else:
        faces = [topology]
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

    lineData = go.Scatter3d(
    x=fx,
    y=fy,
    z=fz,
    marker_size=0,
    mode="lines",
    line=dict(
        color=line_color,
        width=1
    )
    )
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

    faceData = go.Mesh3d(
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
            color = face_color,
            opacity = opacity
        )

    
    return ([faceData, lineData])


#--------------------------
# PAGE LAYOUT
#--------------------------
# TITLE
icon_column, title_column = st.columns([1,10], gap="small")
with icon_column:
    st.image("https://topologic.app/wp-content/uploads/2018/10/Topologic-Logo-250x250.png",width=100)
with title_column:
    st.title("Topologic JSON Test App")
input_column, viewer_column = st.columns([1,1],gap="small")
string_data = None
#--------------------------
# INPUT
with input_column:
    st.subheader("Upload JSON MK1 File")
    json_file = st.file_uploader("", type="json", accept_multiple_files=False)
    if json_file:
        topologies = TopologyByImportedJSONMK1.processItem(json_file)
    
    #--------------------------
    # CONTENT CREATION

        c = topologies[0]
        if c:
            datalist = []
            evf, ivf, thf, bhf, ihf, eva, iva, tha, bha, iha = CellComplexDecompose.processItem(c)
            north = [0,1,0]
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
            

            for f in evf:
                ang, ang_str, color_str = faceAngleFromNorth(f, north)
                st.write(ang_str)
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
            n_ap_proj = n_aperture_area / total_project_wall_area * 100
            s_ap_proj = s_aperture_area / total_project_wall_area * 100
            e_ap_proj = e_aperture_area / total_project_wall_area * 100
            w_ap_proj = w_aperture_area / total_project_wall_area * 100
            ne_ap_proj = ne_aperture_area / total_project_wall_area * 100
            nw_ap_proj = nw_aperture_area / total_project_wall_area * 100
            se_ap_proj = se_aperture_area / total_project_wall_area * 100
            sw_ap_proj = sw_aperture_area / total_project_wall_area * 100
            
            
            col_labels = ["Orientation", "Window Area", "Wall Area", "WWR By Orientation", "WWR By Project"]
            d = {"Orientation": ["N", "S", "E", "W", "NE", "NW", "SE", "SW"],
                'Window Area': [n_aperture_area, s_aperture_area, e_aperture_area, w_aperture_area, ne_aperture_area, nw_aperture_area, se_aperture_area, sw_aperture_area],
                'Wall Area': [n_wall_area, s_wall_area, e_wall_area, w_wall_area, ne_wall_area, nw_wall_area, se_wall_area, sw_wall_area],
                'WWR By Orientation': [n_ap_or, s_ap_or, e_ap_or, w_ap_or, ne_ap_or, nw_ap_or, se_ap_or, sw_ap_or],
                'WWR By Project': [n_ap_proj, s_ap_proj, e_ap_proj, w_ap_proj, ne_ap_proj, nw_ap_proj, se_ap_proj, sw_ap_proj]}
            df = pd.DataFrame(data=d)
            st.table(df)
