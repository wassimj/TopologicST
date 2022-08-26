#--------------------------
#IMPORT LIBRARIES
#import requests
import requests
import random
import math
import string
#import streamlit
import streamlit as st
from streamlit_ws_localstorage import injectWebsocketCode, getOrCreateUID

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


#specklepy libraries
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token

from streamlit_ws_localstorage import injectWebsocketCode, getOrCreateUID
#--------------------------

#--------------------------
#DEFINITIONS
def createRandomChallenge():
    lowercase = list(string.ascii_lowercase)
    uppercase = list(string.ascii_uppercase)
    punctuation = ["-",".","_","~"] # Only hyphen, period, underscore, and tilde are allowed by OAuth Code Challenge
    digits = list(string.digits)
    masterlist = lowercase+uppercase+digits+punctuation
    masterlist = masterlist+lowercase+uppercase+digits
    random.shuffle(masterlist)
    masterlist = random.sample(masterlist, random.randint(64, 128))
    return ''.join(masterlist)

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

