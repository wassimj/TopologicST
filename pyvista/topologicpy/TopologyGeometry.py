import topologic
from topologic import Topology, Vertex, Edge, Wire, Face, Shell, Cell, CellComplex, Cluster, Graph, Dictionary, Attribute, VertexUtility, EdgeUtility, WireUtility, FaceUtility, ShellUtility, CellUtility, TopologyUtility

def getSubTopologies(topology, subTopologyClass):
	topologies = []
	if subTopologyClass == Vertex:
		_ = topology.Vertices(None, topologies)
	elif subTopologyClass == Edge:
		_ = topology.Edges(None, topologies)
	elif subTopologyClass == Wire:
		_ = topology.Wires(None, topologies)
	elif subTopologyClass == Face:
		_ = topology.Faces(None, topologies)
	elif subTopologyClass == Shell:
		_ = topology.Shells(None, topologies)
	elif subTopologyClass == Cell:
		_ = topology.Cells(None, topologies)
	elif subTopologyClass == CellComplex:
		_ = topology.CellComplexes(None, topologies)
	return topologies

def triangulateFace(face):
	faceTriangles = []
	for i in range(0,5,1):
		try:
			_ = topologic.FaceUtility.Triangulate(face, float(i)*0.1, faceTriangles)
			return faceTriangles
		except:
			continue
	faceTriangles.append(face)
	return faceTriangles

def processItem(item):
	vertices = []
	edges = []
	faces = []
	if item == None:
		return [None, None, None]
	topVerts = []
	if (item.Type() == 1): #input is a vertex, just add it and process it
		topVerts.append(item)
	else:
		_ = item.Vertices(None, topVerts)
	for aVertex in topVerts:
		try:
			vertices.index([aVertex.X(), aVertex.Y(), aVertex.Z()]) # Vertex already in list
		except:
			vertices.append([aVertex.X(), aVertex.Y(), aVertex.Z()]) # Vertex not in list, add it.
	topEdges = []
	if (item.Type() == 2): #Input is an Edge, just add it and process it
		topEdges.append(item)
	elif (item.Type() > 2):
		_ = item.Edges(None, topEdges)
	for anEdge in topEdges:
		e = []
		sv = anEdge.StartVertex()
		ev = anEdge.EndVertex()
		try:
			svIndex = vertices.index([sv.X(), sv.Y(), sv.Z()])
		except:
			vertices.append([sv.X(), sv.Y(), sv.Z()])
			svIndex = len(vertices)-1
		try:
			evIndex = vertices.index([ev.X(), ev.Y(), ev.Z()])
		except:
			vertices.append([ev.X(), ev.Y(), ev.Z()])
			evIndex = len(vertices)-1
		e.append(svIndex)
		e.append(evIndex)
		if ([e[0], e[1]] not in edges) and ([e[1], e[0]] not in edges):
			edges.append(e)
	topFaces = []
	if (item.Type() == 8): # Input is a Face, just add it and process it
		topFaces.append(item)
	elif (item.Type() > 8):
		_ = item.Faces(None, topFaces)
	for aFace in topFaces:
		ib = []
		_ = aFace.InternalBoundaries(ib)
		if(len(ib) > 0):
			triFaces = triangulateFace(aFace)
			for aTriFace in triFaces:
				wire = aTriFace.ExternalBoundary()
				faceVertices = getSubTopologies(wire, Vertex)
				f = []
				for aVertex in faceVertices:
					try:
						fVertexIndex = vertices.index([aVertex.X(), aVertex.Y(), aVertex.Z()])
					except:
						vertices.append([aVertex.X(), aVertex.Y(), aVertex.Z()])
						fVertexIndex = len(vertices)-1
					f.append(fVertexIndex)
				faces.append(f)
		else:
			wire =  aFace.ExternalBoundary()
			#wire = topologic.WireUtility.RemoveCollinearEdges(wire, 0.1) #This is an angle Tolerance
			faceVertices = getSubTopologies(wire, Vertex)
			f = []
			for aVertex in faceVertices:
				try:
					fVertexIndex = vertices.index([aVertex.X(), aVertex.Y(), aVertex.Z()])
				except:
					vertices.append([aVertex.X(), aVertex.Y(), aVertex.Z()])
					fVertexIndex = len(vertices)-1
				f.append(fVertexIndex)
			faces.append(f)
	if len(vertices) == 0:
		vertices = [[]]
	if len(edges) == 0:
		edges = [[]]
	if len(faces) == 0:
		faces = [[]]
	return [vertices, edges, faces]
