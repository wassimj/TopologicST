from numpy import arctan, pi, signbit
from numpy.linalg import norm

import topologic
from topologicpy FaceNormalAtParameters

def angle_between(v1, v2):
	u1 = v1 / norm(v1)
	u2 = v2 / norm(v2)
	y = u1 - u2
	x = u1 + u2
	a0 = 2 * arctan(norm(y) / norm(x))
	if (not signbit(a0)) or signbit(pi - a0):
		return a0
	elif signbit(a0):
		return 0
	else:
		return pi

def processItem(item):
	faceA, faceB, mantissa = item
	if not faceA or not isinstance(faceA, topologic.Face):
		raise Exception("Face.Angle - Error: Face A is not valid")
	if not faceB or not isinstance(faceB, topologic.Face):
		raise Exception("Face.Angle - Error: Face B is not valid")
	dirA = FaceNormalAtParameters.processItem([faceA, 0.5, 0.5], "XYZ", 3)
	dirB = FaceNormalAtParameters.processItem([faceB, 0.5, 0.5], "XYZ", 3)
	return round((angle_between(dirA, dirB) * 180 / pi), mantissa) # convert to degrees
