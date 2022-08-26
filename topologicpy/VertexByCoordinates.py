import topologic

def processItem(item):
	x = item[0]
	y = item[1]
	z = item[2]
	vert = None
	try:
		vert = topologic.Vertex.ByCoordinates(x, y, z)
	except:
		vert = None
	return vert
