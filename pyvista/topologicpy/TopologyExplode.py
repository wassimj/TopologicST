import topologic

def relevantSelector(topology):
	returnVertex = None
	if topology.Type() == topologic.Vertex.Type():
		return topology
	elif topology.Type() == topologic.Edge.Type():
		return topologic.EdgeUtility.PointAtParameter(topology, 0.5)
	elif topology.Type() == topologic.Face.Type():
		return topologic.FaceUtility.InternalVertex(topology, 0.0001)
	elif topology.Type() == topologic.Cell.Type():
		return topologic.CellUtility.InternalVertex(topology, 0.0001)
	else:
		return topology.Centroid()

def processItem(item):
	topology = item[0]
	origin = item[1]
	scale = item[2]
	typeFilter = item[3]
	topologies = []
	newTopologies = []
	cluster = None
	if topology.__class__ == topologic.Graph:
		graphTopology = topology.Topology()
		graphEdges = []
		_ = graphTopology.Edges(None, graphEdges)
		for anEdge in graphEdges:
			sv = anEdge.StartVertex()
			oldX = sv.X()
			oldY = sv.Y()
			oldZ = sv.Z()
			newX = (oldX - origin.X())*scale + origin.X()
			newY = (oldY - origin.Y())*scale + origin.Y()
			newZ = (oldZ - origin.Z())*scale + origin.Z()
			newSv = topologic.Vertex.ByCoordinates(newX, newY, newZ)
			ev = anEdge.EndVertex()
			oldX = ev.X()
			oldY = ev.Y()
			oldZ = ev.Z()
			newX = (oldX - origin.X())*scale + origin.X()
			newY = (oldY - origin.Y())*scale + origin.Y()
			newZ = (oldZ - origin.Z())*scale + origin.Z()
			newEv = topologic.Vertex.ByCoordinates(newX, newY, newZ)
			newEdge = topologic.Edge.ByStartVertexEndVertex(newSv, newEv)
			newTopologies.append(newEdge)
		cluster = topologic.Cluster.ByTopologies(newTopologies)
	else:
		if typeFilter == "Vertex":
			topologies = []
			_ = topology.Vertices(None, topologies)
		elif typeFilter == "Edge":
			topologies = []
			_ = topology.Edges(None, topologies)
		elif typeFilter == "Face":
			topologies = []
			_ = topology.Faces(None, topologies)
		elif typeFilter == "Cell":
			topologies = []
			_ = topology.Cells(None, topologies)
		elif typeFilter == 'Self':
			topologies = [topology]
		else:
			topologies = []
			_ = topology.Vertices(None, topologies)
		for aTopology in topologies:
			c = relevantSelector(aTopology)
			oldX = c.X()
			oldY = c.Y()
			oldZ = c.Z()
			newX = (oldX - origin.X())*scale + origin.X()
			newY = (oldY - origin.Y())*scale + origin.Y()
			newZ = (oldZ - origin.Z())*scale + origin.Z()
			xT = newX - oldX
			yT = newY - oldY
			zT = newZ - oldZ
			newTopology = topologic.TopologyUtility.Translate(aTopology, xT, yT, zT)
			newTopologies.append(newTopology)
		cluster = topologic.Cluster.ByTopologies(newTopologies)
	return cluster

