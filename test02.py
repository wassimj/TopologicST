
import streamlit as st

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

def to_argb_int(diffuse_color) -> int:
    """Converts an RGBA array to an ARGB integer"""
    diffuse_color = diffuse_color[-1:] + diffuse_color[:3]
    diffuse_color = [int(val * 255) for val in diffuse_color]
    return int.from_bytes(diffuse_color, byteorder="big", signed=True)

def to_speckle_material(diffuse_color) -> RenderMaterial:
    speckle_mat = RenderMaterial()
    speckle_mat.diffuse = to_argb_int(diffuse_color)
    speckle_mat.metalness = 0
    speckle_mat.roughness = 0
    speckle_mat.emissive = to_argb_int([0,0,0,1]) #black for emissive
    speckle_mat.opacity = diffuse_color[-1]
    return speckle_mat

def getBranches(item):
	client, stream = item
	bList = client.branch.list(stream.id)
	branches = []
	for b in bList:
		branches.append(client.branch.get(stream.id, b.name))
	return branches

def getStreams(client):
    return client.stream.list()

def getCommits(branch):
    return branch.commits.items

def getObject(client, stream, commit):
    transport = ServerTransport(stream.id, client)
    last_obj_id = commit.referencedObject
    return operations.receive(obj_id=last_obj_id, remote_transport=transport)

def cellComplexByFaces(item):
    faces, tol = item
    assert isinstance(faces, list), "CellComplex.ByFaces - Error: Input is not a list"
    faces = [x for x in faces if isinstance(x, topologic.Face)]
    cellComplex = topologic.CellComplex.ByFaces(faces, tol, False)
    if not cellComplex:
        return None
    cells = []
    _ = cellComplex.Cells(None, cells)
    if len(cells) < 2:
        return None
    return cellComplex

def cellByFaces(item):
    faces, tol = item
    return topologic.Cell.ByFaces(faces, tol)

def shellByFaces(item):
	faces, tol = item
	shell = topologic.Shell.ByFaces(faces, tol)
	if not shell:
		result = faces[0]
		remainder = faces[1:]
		cluster = topologic.Cluster.ByTopologies(remainder, False)
		result = result.Merge(cluster, False)
		if result.Type() != 16: #16 is the type of a Shell
			if result.Type() > 16:
				returnShells = []
				_ = result.Shells(None, returnShells)
				return returnShells
			else:
				return None
	else:
		return shell
    
def speckleMeshToTopologic(obj):
    sp_vertices = obj.vertices
    sp_faces = obj.faces
    tp_vertices = []
    for i in range(0,len(sp_vertices),3):
        x = sp_vertices[i]
        y = sp_vertices[i+1]
        z = sp_vertices[i+2]
        tp_vertices.append(topologic.Vertex.ByCoordinates(x,y,z))
    
    tp_faces = []
    i = 0
    while True:
        if sp_faces[i] == 0:
            n = 3
        else:
            n = 4
        temp_verts = []
        for j in range(n):
            temp_verts.append(tp_vertices[sp_faces[i+j+1]])
        c = topologic.Cluster.ByTopologies(temp_verts)
        w = wireByVertices([c, True])
        f = topologic.Face.ByExternalBoundary(w)
        tp_faces.append(f)
        i = i + n + 1
        if i+n+1 > len(sp_faces):
            break
    returnTopology = None
    try:
        returnTopology = cellComplexByFaces([tp_faces, 0.0001])
    except:
        try:
            returnTopology = cellByFaces([tp_faces, 0.0001])
        except:
            try:
                returnTopology = shellByFaces([tp_faces, 0.0001])
            except:
                returnTopology = topologic.Cluster.ByTopologies(tp_faces)
    return returnTopology

def wireByVertices(item):
	cluster, close = item
	if isinstance(close, list):
		close = close[0]
	if isinstance(cluster, list):
		if all([isinstance(item, topologic.Vertex) for item in cluster]):
			vertices = cluster
	elif isinstance(cluster, topologic.Cluster):
		vertices = []
		_ = cluster.Vertices(None, vertices)
	else:
		raise Exception("WireByVertices - Error: The input is not valid")
	wire = None
	edges = []
	for i in range(len(vertices)-1):
		v1 = vertices[i]
		v2 = vertices[i+1]
		try:
			e = topologic.Edge.ByStartVertexEndVertex(v1, v2)
			if e:
				edges.append(e)
		except:
			continue
	if close:
		v1 = vertices[-1]
		v2 = vertices[0]
		try:
			e = topologic.Edge.ByStartVertexEndVertex(v1, v2)
			if e:
				edges.append(e)
		except:
			pass
	if len(edges) > 0:
		c = topologic.Cluster.ByTopologies(edges, False)
		return c.SelfMerge()
	else:
		return None


# Authenticte to Speckle

secret = st.text_input('Password')
url = "https://speckle.xyz/authn/verify/f081fa6bf4/"+secret
st.write(url)

# create and authenticate a client
hostString = st.text_input('Speckle Host', 'speckle.xyz')

if hostString:
    client = SpeckleClient(host=hostString)

    tokenString = st.text_input("Secret Token", type="password")
    if tokenString:
        client.authenticate_with_token(tokenString)

        streams = getStreams(client)

        stream_names = ["Select a stream"]
        for aStream in streams:
            stream_names.append(aStream.name)
        option = st.selectbox(
            'Select A Stream',
            (stream_names))
        if option != "Select a stream":
            stream = streams[stream_names.index(option)-1]

            branches = getBranches([client, stream])
            branch_names = ["Select a branch"]
            for aBranch in branches:
                branch_names.append(aBranch.name)

            option = st.selectbox(
                'Select A Branch',
                (branch_names))
            if option != "Select a branch":
                branch = branches[branch_names.index(option)-1]
                
                commits = getCommits(branch)
                commit_names = ["Select a commit"]
                for aCommit in commits:
                    commit_names.append(str(aCommit.id)+": "+aCommit.message)
                option = st.selectbox('Select A Commit', (commit_names))
                if option != "Select a commit":
                    commit = commits[commit_names.index(option)-1]
                    last_obj = getObject(client, stream, commit)
                    sp_vertices = last_obj.vertices
                    sp_faces = last_obj.faces
                    tp_vertices = []
                    for i in range(0,len(sp_vertices),3):
                        x = sp_vertices[i]
                        y = sp_vertices[i+1]
                        z = sp_vertices[i+2]
                        tp_vertices.append(topologic.Vertex.ByCoordinates(x,y,z))
                    
                    tp_faces = []
                    i = 0
                    while True:
                        if sp_faces[i] == 0:
                            n = 3
                        else:
                            n = 4
                        temp_verts = []
                        for j in range(n):
                            temp_verts.append(tp_vertices[sp_faces[i+j+1]])
                        c = topologic.Cluster.ByTopologies(temp_verts)
                        w = wireByVertices([c, True])
                        f = topologic.Face.ByExternalBoundary(w)
                        tp_faces.append(f)
                        i = i + n + 1
                        if i+n+1 > len(sp_faces):
                            break

                    volume = 0
                    desc = ""
                    if len(tp_faces) == 1:
                        topology = tp_faces[0]
                        desc = "Topologic Face"
                        area = topologic.FaceUtility.Area(topology)
                    else:
                        tp_object = cellComplexByFaces([tp_faces, 0.0001])
                        if not tp_object:
                            tp_object = cellByFaces([tp_faces, 0.0001])
                        if not tp_object:
                            tp_object = shellByFaces([tp_faces, 0.0001])
                        if not tp_object:
                            tp_object = topologic.Cluster.ByTopologies(tp_faces)
                        if tp_object.Type() == topologic.CellComplex.Type():
                            envelope = tp_object.ExternalBoundary()
                            volume = round(topologic.CellUtility.Volume(envelope), 2)
                            faces = []
                            _ = tp_object.Faces(None, faces)
                        elif tp_object.Type() == topologic.Cell.Type():
                            envelope = tp_object
                            volume = round(topologic.CellUtility.Volume(envelope), 2)
                            faces = []
                            _ = tp_object.Faces(None, faces)
                        elif tp_object.Type() == topologic.Shell.Type():
                            volume = 0
                            envelope = tp_object
                        faces = []
                        _ = envelope.Faces(None, faces)
                        area = 0
                        for aFace in faces:
                            area = area + topologic.FaceUtility.Area(aFace)
                        area = round(area, 2)
                            
                    faces = []
                    edges = []
                    vertices = []
                    _ = tp_object.Faces(None, faces)
                    _ = tp_object.Edges(None, edges)
                    _ = tp_object.Vertices(None, vertices)
                    num_faces = len(faces)
                    num_edges = len(edges)
                    num_vertices = len(vertices)
                    st.header('Topologic Analysis')
                    col1, col2 = st.columns([2,3], gap="medium")
                    with col1:
                        st.subheader('Type: '+tp_object.GetTypeAsString())
                        st.subheader('Volume: '+str(volume)+" m3")
                        st.subheader('Area: '+str(area)+" m2")
                        st.subheader('Faces: '+str(num_faces))
                        st.subheader('Edges: '+str(num_edges))
                        st.subheader('Vertices: '+str(num_vertices))
                    with col2:
                        st.components.v1.iframe(src="https://speckle.xyz/embed?stream="+stream.id+"&commit="+commit.id+"&transparent=false", width=400,height=600)
                    
                    colors = ["Select a color", "red", "green", "blue"]
                    numeric_colors = [[1,0,0], [0,1,0], [0,0,1]]
                    color_option = st.selectbox('Select A Color', (colors))
                    if color_option != "Select a color":
                        diffuse_color = numeric_colors[colors.index(color_option)-1]
                        opacity = st.slider("Opacity", min_value=0.0, max_value=1.0, value=0.5, step=0.1)
                        diffuse_color.append(float(opacity))
                        # Change the Color of the Speckle Object and Create a New Commit
                        speckle_material = to_speckle_material(diffuse_color) #Translucent Red Color
                        last_obj["renderMaterial"] = speckle_material
                        last_obj["opacity"] = opacity
                        last_obj["units"] = "m"
                        clicked = st.button("SEND TO SPECKLE")
                        if clicked:
                            transport = ServerTransport(stream.id, client)
                            obj_id = operations.send(last_obj, [transport])
                            # now create a commit on that branch with your updated data!
                            commit_id = client.commit.create(
                                stream.id,
                                obj_id,
                                branch.name,
                                message="This should be "+color_option+" color with opacity: "+str(opacity),
                            )
                            st.header('Success!')
                            clicked = st.button("VIEW IN SPECKLE")
                            if clicked:
                                st.components.v1.iframe(src="https://speckle.xyz/embed?stream="+stream.id+"&commit="+commit.id+"&transparent=false", width=400,height=600)
                            





