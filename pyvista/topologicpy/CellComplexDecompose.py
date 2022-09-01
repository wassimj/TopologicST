import topologic
from numpy import arctan, pi, signbit, arctan2, rad2deg
from topologicpy import FaceNormalAtParameters, FaceAngle

# From https://stackabuse.com/python-how-to-flatten-list-of-lists/
def flatten(element):
	returnList = []
	if isinstance(element, list) == True:
		for anItem in element:
			returnList = returnList + flatten(anItem)
	else:
		returnList = [element]
	return returnList

# DEFINITIONS
def compass_angle(p1, p2):
    ang1 = arctan2(*p1[::-1])
    ang2 = arctan2(*p2[::-1])
    return rad2deg((ang1 - ang2) % (2 * pi))

def faceAngleFromUp(f, up):
	dirA = FaceNormalAtParameters.processItem([f, 0.5, 0.5], "XYZ", 3)
	ang = FaceAngle.angle_between(dirA, up)
	ang = round((ang * 180 / pi), 2) # convert to degrees and round
    
	if abs(ang) < 11.25:
		ang_str = "N"
		color_str = "white"
	elif abs(ang - 180) < 11.25:
		ang_str = "S"
		color_str = "yellow"
	elif abs(ang - 90) < 11.25:
		ang_str = "E"
		color_str = "green"
	else:
		ang_str = "NE"
		color_str = "red"
	return [ang, ang_str, color_str]

def getApertures(topology):
	apertures = []
	apTopologies = []
	_ = topology.Apertures(apertures)
	for aperture in apertures:
		apTopologies.append(topologic.Aperture.Topology(aperture))
	return apTopologies

def processItem(item):
	externalVerticalFaces = []
	internalVerticalFaces = []
	topHorizontalFaces = []
	bottomHorizontalFaces = []
	internalHorizontalFaces = []
	externalInclinedFaces = []
	internalInclinedFaces = []
	externalVerticalApertures = []
	internalVerticalApertures = []
	topHorizontalApertures = []
	bottomHorizontalApertures = []
	internalHorizontalApertures = []
	externalInclinedApertures = []
	internalInclinedApertures = []

	faces = []
	_ = item.Faces(None, faces)
	up = [0,0,1]
	for aFace in faces:
		ang, ang_str, color_str = faceAngleFromUp(aFace, up)
		cells = []
		aFace.Cells(item, cells)
		n = len(cells)
		if ang_str == "E" or ang_str == "W":
			if n == 1:
				externalVerticalFaces.append(aFace)
				externalVerticalApertures.append(getApertures(aFace))
			else:
				internalVerticalFaces.append(aFace)
				internalVerticalApertures.append(getApertures(aFace))
		elif ang_str == "N":
			if n == 1:
				topHorizontalFaces.append(aFace)
				topHorizontalApertures.append(getApertures(aFace))
			else:
				internalHorizontalFaces.append(aFace)
				internalHorizontalApertures.append(getApertures(aFace))
		elif ang_str == "S":
			if n == 1:
				bottomHorizontalFaces.append(aFace)
				bottomHorizontalApertures.append(getApertures(aFace))
			else:
				internalHorizontalFaces.append(aFace)
				internalHorizontalApertures.append(getApertures(aFace))
		elif ang_str == "NW" or ang_str == "NE" or ang_str == "SW" or ang_str == "SE":
			if n == 1:
				externalInclinedFaces.append(aFace)
				externalInclinedApertures.append(getApertures(aFace))
			else:
				internalInclinedFaces.append(aFace)
				internalInclinedApertures.append(getApertures(aFace))
	

	ex_ve_f = []
	in_ve_f = []
	to_ho_f = []
	bo_ho_f = []
	in_ho_f = []
	ex_in_f = []
	in_in_f = []

	ex_ve_a = []
	in_ve_a = []
	to_ho_a = []
	bo_ho_a = []
	in_ho_a = []
	ex_in_a = []
	in_in_a = []

	if len(externalVerticalFaces) > 0:
		ex_ve_f = flatten(externalVerticalFaces)
	if len(internalVerticalFaces) > 0:
		in_ve_f = flatten(internalVerticalFaces)
	if len(topHorizontalFaces) > 0:
		to_ho_f = flatten(topHorizontalFaces)
	if len(bottomHorizontalFaces) > 0:
		bo_ho_f = flatten(bottomHorizontalFaces)
	if len(internalHorizontalFaces) > 0:
		in_ho_f = flatten(internalHorizontalFaces)
	if len(externalInclinedFaces) > 0:
		ex_in_f = flatten(externalInclinedFaces)
	if len(internalInclinedFaces) > 0:
		in_in_f = flatten(internalInclinedFaces)

	if len(externalVerticalApertures) > 0:
		ex_ve_a = flatten(externalVerticalApertures)
	if len(internalVerticalApertures) > 0:
		in_ve_a = flatten(internalVerticalApertures)
	if len(topHorizontalApertures) > 0:
		to_ho_a = flatten(topHorizontalApertures)
	if len(bottomHorizontalApertures) > 0:
		bo_ho_a = flatten(bottomHorizontalApertures)
	if len(internalHorizontalApertures) > 0:
		in_ho_a = flatten(internalHorizontalApertures)
	if len(externalInclinedFaces) > 0:
		ex_in_a = flatten(externalInclinedApertures)
	if len(internalInclinedApertures) > 0:
		in_in_a = flatten(internalInclinedApertures)
	return [ex_ve_f, in_ve_f, to_ho_f, bo_ho_f, in_ho_f, ex_in_f, in_in_f, ex_ve_a, in_ve_a, to_ho_a, bo_ho_a, in_ho_a, ex_in_a, in_in_a]


