import topologic

def processItem(item, outputType, decimals):
	face, u, v = item
	try:
		coords = topologic.FaceUtility.NormalAtParameters(face, u, v)
		x = round(coords[0], decimals)
		y = round(coords[1], decimals)
		z = round(coords[2], decimals)
		returnResult = []
		if outputType == "XYZ":
			returnResult = [x,y,z]
		elif outputType == "XY":
			returnResult = [x,y]
		elif outputType == "XZ":
			returnResult = [x,z]
		elif outputType == "YZ":
			returnResult = [y,z]
		elif outputType == "X":
			returnResult = x
		elif outputType == "Y":
			returnResult = y
		elif outputType == "Z":
			returnResult = z
	except:
		returnResult = None
	return returnResult
