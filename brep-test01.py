#--------------------------
# IMPORT LIBRARIES
import streamlit as st
import plotly.graph_objects as go
import json
from io import StringIO
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

from topologicpy import TopologyByImportedJSONMK1, TopologyApertures, TopologyTriangulate
#--------------------------
#--------------------------
# PAGE CONFIGURATION
st.set_page_config(
    page_title="Topologic Speckle Test Application",
    page_icon="📊",
    layout="wide"
)
#--------------------------
#--------------------------
# DEFINITIONS
def plotlyDataByTopology(topology, opacity, face_color="blue", line_color="white"):
    faces = []
    _ = topology.Faces(None, faces)
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
    st.title("Topologic Test App")
input_column, viewer_column = st.columns([1,3],gap="small")
string_data = None
#--------------------------
# INPUT
with input_column:
    st.subheader("Inputs")
    brep_file = st.file_uploader("Upload BREP File", type="brep", accept_multiple_files=False)
    brep_data = None
    if brep_file is not None:
     # To read file as bytes:
        bytes_data = brep_file.getvalue()

     # To convert to a string based IO:
        stringio = StringIO(brep_file.getvalue().decode("utf-8"))
        #lines = stringio.readlines()
        #lines[1] = "CASCADE Topology V1, (c) Matra-Datavision" # hack to make it compatible with Linux version
        #string_data = '\n'.join(lines)

     # To read file as string:
        string_data = stringio.read()
        string_data = string_data.replace("CASCADE Topology V3, (c) Open Cascade", "CASCADE Topology V1, (c) Matra-Datavision")
        st.write(string_data)
#--------------------------
# CONTENT CREATION
#c = CellComplexPrism.processItem([origin, width, length, height, uSides, vSides, wSides, dirX, dirY, dirZ, placement])
c = None
if string_data:
    c = topologic.Topology.ByString(string_data)
st.write(c)

if c:
    dataList = plotlyDataByTopology(c, 0.5, "blue", "white")
    faces = []
    _ = c.Faces(None, faces)
    apertureTopologies = []
    for face in faces:
        apertures, apertureTopology = TopologyApertures.processItem(face)
        if not isinstance(apertureTopology, list):
            apertureTopology = [apertureTopology]
        apertureTopologies = apertureTopologies+apertureTopology
    for at in apertureTopologies:
        apertureData = plotlyDataByTopology(at, 0.5, "blue", "black")
        dataList = dataList + apertureData

    fig = go.Figure(data=dataList)
    fig.update_layout(
        width=800,
        height=800,
        scene = dict(
            xaxis = dict(visible=False),
            yaxis = dict(visible=False),
            zaxis =dict(visible=False),
            )
        )
    #--------------------------
    # 3D VIEWER
    with viewer_column:
        st.subheader("3D View")
        st.plotly_chart(fig, width=800,height=800)