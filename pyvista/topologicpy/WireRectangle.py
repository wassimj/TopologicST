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

def wireByVertices(vList):
	edges = []
	for i in range(len(vList)-1):
		edges.append(topologic.Edge.ByStartVertexEndVertex(vList[i], vList[i+1]))
	edges.append(topologic.Edge.ByStartVertexEndVertex(vList[-1], vList[0]))
	return topologic.Wire.ByEdges(edges)

def processItem(item):
	origin, width, length, dirX, dirY, dirZ, placement = item

	baseV = []
	xOffset = 0
	yOffset = 0
	if placement == "LowerLeft":
		xOffset = width*0.5
		yOffset = length*0.5

	vb1 = topologic.Vertex.ByCoordinates(origin.X()-width*0.5+xOffset,origin.Y()-length*0.5+yOffset,origin.Z())
	vb2 = topologic.Vertex.ByCoordinates(origin.X()+width*0.5+xOffset,origin.Y()-length*0.5+yOffset,origin.Z())
	vb3 = topologic.Vertex.ByCoordinates(origin.X()+width*0.5+xOffset,origin.Y()+length*0.5+yOffset,origin.Z())
	vb4 = topologic.Vertex.ByCoordinates(origin.X()-width*0.5+xOffset,origin.Y()+length*0.5+yOffset,origin.Z())

	baseWire = wireByVertices([vb1, vb2, vb3, vb4])
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
	baseWire = topologic.TopologyUtility.Rotate(baseWire, origin, 0, 1, 0, theta)
	baseWire = topologic.TopologyUtility.Rotate(baseWire, origin, 0, 0, 1, phi)
	return baseWire

