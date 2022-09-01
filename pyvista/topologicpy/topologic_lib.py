
import topologic
import numpy as np
import math

def getSubTopologies(topology, subTopologyClass):
  subtopologies = []

  if topology is None or topology.Type() < subTopologyClass.Type():
    return subtopologies

  if subTopologyClass == topologic.Vertex:
    _ = topology.Vertices(None, subtopologies)
  if subTopologyClass == topologic.Edge:
    _ = topology.Edges(None, subtopologies)
  elif subTopologyClass == topologic.Face:
    _ = topology.Faces(None, subtopologies)
  elif subTopologyClass == topologic.Shell:
    _ = topology.Shells(None, subtopologies)
  elif subTopologyClass == topologic.Cell:
    _ = topology.Cells(None, subtopologies)

  return subtopologies

def boolean(topologyA, topologyB, operation):
  topologyC = None

  try:
    if operation == "Difference":
      topologyC = topologyA.Difference(topologyB, False)
    elif operation == "Intersect":
      topologyC = topologyA.Intersect(topologyB, False)

    if not topologyC:
      return None
  except:
    return None

  return topologyC

def setDictionary(elem, key, value):
  dictionary = elem.GetDictionary()
  dictionary.TryAdd(key, topologic.StringAttribute(value))
  elem.SetDictionary(dictionary)

def getDictionary(elem, key):
  dictionary = elem.GetDictionary()
  if dictionary.ContainsKey(key):
    value = dictionary.ValueAtKey(key)
    return value.StringValue()

  return None

def normalize(u):
  return u / np.linalg.norm(u)

def get_normal(vertices):
  return normalize(np.cross(vertices[1] - vertices[0], vertices[-1] - vertices[0]))

# From https://gis.stackexchange.com/questions/387237/deleting-collinear-vertices-from-polygon-feature-class-using-arcpy
def are_collinear(v1, v2, v3, tolerance=0.5):
  e1 = topologic.EdgeUtility.ByVertices([v2, v1])
  e2 = topologic.EdgeUtility.ByVertices([v2, v3])
  rad = topologic.EdgeUtility.AngleBetween(e1, e2)

  return abs(math.sin(rad)) < math.sin(math.radians(tolerance))

def removeCollinearEdges(wire, angTol):
  vertices = getSubTopologies(wire, topologic.Vertex)

  indexes_of_vertices_to_remove = [
    idx for idx, vertex in enumerate(vertices)
    if are_collinear(vertices[idx-1], vertex, vertices[idx+1 if idx+1 < len(vertices) else 0], angTol)
  ]

  vertices_to_keep = [
    val for idx, val in enumerate(vertices)
    if idx not in indexes_of_vertices_to_remove
  ]

  return vertices_to_keep

def meshData(topology):
  vertices = []
  faces = []
  if topology is None:
    return [vertices, faces]

  topVerts = []
  if (topology.Type() == 1): #input is a vertex, just add it and process it
    topVerts.append(topology)
  else:
    _ = topology.Vertices(None, topVerts)
  for aVertex in topVerts:
    try:
      vertices.index(tuple([aVertex.X(), aVertex.Y(), aVertex.Z()])) # Vertex already in list
    except:
      vertices.append(tuple([aVertex.X(), aVertex.Y(), aVertex.Z()])) # Vertex not in list, add it.

  topFaces = []
  if (topology.Type() == 8): # Input is a Face, just add it and process it
    topFaces.append(topology)
  elif (topology.Type() > 8):
    _ = topology.Faces(None, topFaces)
  for aFace in topFaces:
    wires = []
    ib = []
    _ = aFace.InternalBoundaries(ib)
    if(len(ib) > 0):
      triFaces = []
      topologic.FaceUtility.Triangulate(aFace, 0.0, triFaces)
      for aTriFace in triFaces:
        wires.append(aTriFace.ExternalBoundary())
    else:
      wires.append(aFace.ExternalBoundary())

    for wire in wires:
      f = []
      for aVertex in removeCollinearEdges(wire, 0.1):
        try:
          fVertexIndex = vertices.index(tuple([aVertex.X(), aVertex.Y(), aVertex.Z()]))
        except:
          vertices.append(tuple([aVertex.X(), aVertex.Y(), aVertex.Z()]))
          fVertexIndex = len(vertices)-1
        f.append(fVertexIndex)

      if len(f) < 3:
        continue

      p = np.array(vertices[f[0]])
      u = normalize(vertices[f[1]] - p)
      v = normalize(vertices[f[-1]] - p)
      normal = topologic.FaceUtility.NormalAtParameters(aFace, 0.5, 0.5)
      if (np.cross(u, v) @ [normal[0], normal[1], normal[2]]) + 1 < 1e-6:
        f.reverse()

      faces.append(tuple(f))

  return [vertices, faces]

def projectFace(face, other_face):
  normal = topologic.FaceUtility.NormalAtParameters(face, 0.5, 0.5)
  n = [normal[0], normal[1], normal[2]]
  point = topologic.FaceUtility.VertexAtParameters(face, 0.5, 0.5)
  d = np.dot(n, [point.X(), point.Y(), point.Z()])

  other_normal = topologic.FaceUtility.NormalAtParameters(other_face, 0.5, 0.5)
  if np.dot(n, [other_normal[0], other_normal[1], other_normal[2]]) + 1 > 1e-6:
    return [None, None]

  other_point = topologic.FaceUtility.VertexAtParameters(other_face, 0.5, 0.5)
  dist = -np.dot(n, [other_point.X(), other_point.Y(), other_point.Z()]) + d
  if dist < 1e-6:
    return [None, None]

  top_space_boundary = boolean(face, topologic.TopologyUtility.Translate(other_face, dist*normal[0], dist*normal[1], dist*normal[2]), "Intersect")
  if top_space_boundary is None:
    return [None, None]

  top_space_boundary = getSubTopologies(top_space_boundary, topologic.Face)
  if not top_space_boundary:
    return [None, None]

  return [dist, top_space_boundary[0]]