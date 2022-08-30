import topologic
from topologicpy import VertexNearestVertex, DictionaryByKeysValues, TopologySetDictionary, DictionaryValueAtKey
import time

def isInside(aperture, face, tolerance):
	return (topologic.VertexUtility.Distance(aperture.Topology.Centroid(), face) < tolerance)

def internalVertex(topology, tolerance):
	vst = None
	classType = topology.Type()
	if classType == 64: #CellComplex
		tempCells = []
		_ = topology.Cells(tempCells)
		tempCell = tempCells[0]
		vst = topologic.CellUtility.InternalVertex(tempCell, tolerance)
	elif classType == 32: #Cell
		vst = topologic.CellUtility.InternalVertex(topology, tolerance)
	elif classType == 16: #Shell
		tempFaces = []
		_ = topology.Faces(None, tempFaces)
		tempFace = tempFaces[0]
		vst = topologic.FaceUtility.InternalVertex(tempFace, tolerance)
	elif classType == 8: #Face
		vst = topologic.FaceUtility.InternalVertex(topology, tolerance)
	elif classType == 4: #Wire
		if topology.IsClosed():
			internalBoundaries = []
			tempFace = topologic.Face.ByExternalInternalBoundaries(topology, internalBoundaries)
			vst = topologic.FaceUtility.InternalVertex(tempFace, tolerance)
		else:
			tempEdges = []
			_ = topology.Edges(None, tempEdges)
			vst = topologic.EdgeUtility.PointAtParameter(tempVertex[0], 0.5)
	elif classType == 2: #Edge
		vst = topologic.EdgeUtility.PointAtParameter(topology, 0.5)
	elif classType == 1: #Vertex
		vst = topology
	else:
		vst = topology.Centroid()
	return vst

def processApertures(subTopologies, apertureCluster, exclusive, tolerance):
    apertures = []
    cells = []
    faces = []
    edges = []
    vertices = []
    _ = apertureCluster.Cells(None, cells)
    _ = apertureCluster.Faces(None, faces)
    _ = apertureCluster.Vertices(None, vertices)
    # apertures are assumed to all be of the same topology type.
    if len(cells) > 0:
        apertures = cells
    elif len(faces) > 0:
        apertures = faces
    elif len(edges) > 0:
        apertures = edges
    elif len(vertices) > 0:
        apertures = vertices
    else:
        apertures = []
    usedTopologies = []
    temp_verts = []
    for i, subTopology in enumerate(subTopologies):
            usedTopologies.append(0)
            temp_v = internalVertex(subTopology, tolerance)
            d = DictionaryByKeysValues.processItem([["id"], [i]])
            temp_v = TopologySetDictionary.processItem([temp_v, d])
            temp_verts.append(temp_v)
    clus = topologic.Cluster.ByTopologies(temp_verts)
    tree = VertexNearestVertex.kdtree(clus)
    for aperture in apertures:
        apCenter = internalVertex(aperture, tolerance)
        nearest_vert = VertexNearestVertex.find_nearest_neighbor(tree=tree, vertex=apCenter)
        d = nearest_vert.GetDictionary()
        i = DictionaryValueAtKey.processItem([d,"id"])
        subTopology = subTopologies[i]
        if exclusive == True and usedTopologies[i] == 1:
            continue
        context = topologic.Context.ByTopologyParameters(subTopology, 0.5, 0.5, 0.5)
        _ = topologic.Aperture.ByTopologyContext(aperture, context)
        if exclusive == True:
            usedTopologies[i] = 1
    return None

def processItem(item):
	topology = item[0].DeepCopy()
	apertureCluster = item[1]
	exclusive = item[2]
	tolerance = item[3]
	subTopologyType = item[4]
	subTopologies = []
	if subTopologyType == "Face":
		_ = topology.Faces(None, subTopologies)
	elif subTopologyType == "Edge":
		_ = topology.Edges(None, subTopologies)
	elif subTopologyType == "Vertex":
		_ = topology.Vertices(None, subTopologies)
	processApertures(subTopologies, apertureCluster, exclusive, tolerance)
	return topology
