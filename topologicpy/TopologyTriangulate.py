import topologic

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

def processItem(topology, tolerance):
	t = topology.Type()
	if (t == 1) or (t == 2) or (t == 4) or (t == 128):
		return topology
	if t = topologic.Face.Type():
		topologyFaces = [topology]
	else:
		topologyFaces = []
		_ = topology.Faces(None, topologyFaces)
	faceTriangles = []
	for aFace in topologyFaces:
		triFaces = triangulateFace(aFace)
		for triFace in triFaces:
			faceTriangles.append(triFace)
	if t == 8 or t == 16: # Face or Shell
		return topologic.Shell.ByFaces(faceTriangles, tolerance)
	elif t == 32: # Cell
		return topologic.Cell.ByFaces(faceTriangles, tolerance)
	elif t == 64: #CellComplex
		return topologic.CellComplex.ByFaces(faceTriangles, tolerance)
