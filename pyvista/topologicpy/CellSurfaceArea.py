import topologic

def processItem(item):
	faces = []
	_ = item.Faces(None, faces)
	area = 0.0
	for aFace in faces:
		area = area + topologic.FaceUtility.Area(aFace)
	return area
