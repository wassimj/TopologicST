# * This file is part of Topologic software library.
# * Copyright(C) 2021, Cardiff University and University College London
# * 
# * This program is free software: you can redistribute it and/or modify
# * it under the terms of the GNU Affero General Public License as published by
# * the Free Software Foundation, either version 3 of the License, or
# * (at your option) any later version.
# * 
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# * GNU Affero General Public License for more details.
# * 
# * You should have received a copy of the GNU Affero General Public License
# * along with this program. If not, see <https://www.gnu.org/licenses/>.

import topologic
import math
from topologicpy import WireRectangle


def wireByVertices(vList):
	edges = []
	for i in range(len(vList)-1):
		edges.append(topologic.Edge.ByStartVertexEndVertex(vList[i], vList[i+1]))
	edges.append(topologic.Edge.ByStartVertexEndVertex(vList[-1], vList[0]))
	return topologic.Wire.ByEdges(edges)

def sliceCell(cell, width, length, height, uSides, vSides, wSides):
	origin = cell.Centroid()
	wRect = WireRectangle.processItem([origin, width*1.2, length*1.2, 0, 0, 1, "Center"])
	sliceFaces = []
	for i in range(1, wSides):
		sliceFaces.append(topologic.TopologyUtility.Translate(topologic.Face.ByExternalBoundary(wRect), 0, 0, height/wSides*i - height*0.5))
	uRect = WireRectangle.processItem([origin, height*1.2, length*1.2, 1, 0, 0, "Center"])
	for i in range(1, uSides):
		sliceFaces.append(topologic.TopologyUtility.Translate(topologic.Face.ByExternalBoundary(uRect), width/uSides*i - width*0.5, 0, 0))
	vRect = WireRectangle.processItem([origin, height*1.2, width*1.2, 0, 1, 0, "Center"])
	for i in range(1, vSides):
		sliceFaces.append(topologic.TopologyUtility.Translate(topologic.Face.ByExternalBoundary(vRect), 0, length/vSides*i - length*0.5, 0))
	sliceCluster = topologic.Cluster.ByTopologies(sliceFaces)
	cellFaces = []
	_ = cell.Faces(None, cellFaces)
	sliceFaces = sliceFaces + cellFaces
	cellComplex = topologic.CellComplex.ByFaces(sliceFaces, 0.0001)
	return cellComplex

def processItem(item):
	origin, \
	width, \
	length, \
	height, \
	uSides, \
	vSides, \
	wSides, \
	dirX, \
	dirY, \
	dirZ, \
	originLocation = item
	baseV = []
	topV = []
	xOffset = 0
	yOffset = 0
	zOffset = 0
	if originLocation == "Center":
		zOffset = -height*0.5
	elif originLocation == "LowerLeft":
		xOffset = width*0.5
		yOffset = length*0.5

	vb1 = topologic.Vertex.ByCoordinates(origin.X()-width*0.5+xOffset,origin.Y()-length*0.5+yOffset,origin.Z()+zOffset)
	vb2 = topologic.Vertex.ByCoordinates(origin.X()+width*0.5+xOffset,origin.Y()-length*0.5+yOffset,origin.Z()+zOffset)
	vb3 = topologic.Vertex.ByCoordinates(origin.X()+width*0.5+xOffset,origin.Y()+length*0.5+yOffset,origin.Z()+zOffset)
	vb4 = topologic.Vertex.ByCoordinates(origin.X()-width*0.5+xOffset,origin.Y()+length*0.5+yOffset,origin.Z()+zOffset)

	vt1 = topologic.Vertex.ByCoordinates(origin.X()-width*0.5+xOffset,origin.Y()-length*0.5+yOffset,origin.Z()+height+zOffset)
	vt2 = topologic.Vertex.ByCoordinates(origin.X()+width*0.5+xOffset,origin.Y()-length*0.5+yOffset,origin.Z()+height+zOffset)
	vt3 = topologic.Vertex.ByCoordinates(origin.X()+width*0.5+xOffset,origin.Y()+length*0.5+yOffset,origin.Z()+height+zOffset)
	vt4 = topologic.Vertex.ByCoordinates(origin.X()-width*0.5+xOffset,origin.Y()+length*0.5+yOffset,origin.Z()+height+zOffset)
	baseWire = wireByVertices([vb1, vb2, vb3, vb4])
	topWire = wireByVertices([vt1, vt2, vt3, vt4])
	wires = [baseWire, topWire]
	prism =  topologic.CellUtility.ByLoft(wires)
	prism = sliceCell(prism, width, length, height, uSides, vSides, wSides)
	x1 = origin.X()
	y1 = origin.Y()
	z1 = origin.Z()
	x2 = origin.X() + dirX
	y2 = origin.Y() + dirY
	z2 = origin.Z() + dirZ
	dx = x2 - x1
	dy = y2 - y1
	dz = z2 - z1    
	dist = math.sqrt(dx**2 + dy**2 + dz**2)
	phi = math.degrees(math.atan2(dy, dx)) # Rotation around Y-Axis
	if dist < 0.0001:
		theta = 0
	else:
		theta = math.degrees(math.acos(dz/dist)) # Rotation around Z-Axis
	prism = topologic.TopologyUtility.Rotate(prism, origin, 0, 1, 0, theta)
	prism = topologic.TopologyUtility.Rotate(prism, origin, 0, 0, 1, phi)
	return prism

