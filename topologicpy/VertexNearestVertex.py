import topologic

# Adapted From https://johnlekberg.com/blog/2020-04-17-kd-tree.html
import collections
def SED(a, b):
	"""Compute the squared Euclidean distance between X and Y."""
	p1 = (a.X(), a.Y(), a.Z())
	p2 = (b.X(), b.Y(), b.Z())
	return sum((i-j)**2 for i, j in zip(p1, p2))

BT = collections.namedtuple("BT", ["value", "left", "right"])
BT.__doc__ = """
A Binary Tree (BT) with a node value, and left- and
right-subtrees.
"""
def firstItem(v):
	return v.X()
def secondItem(v):
	return v.Y()
def thirdItem(v):
	return v.Z()

def itemAtIndex(v, index):
	if index == 0:
		return v.X()
	elif index == 1:
		return v.Y()
	elif index == 2:
		return v.Z()

def sortList(vertices, index):
	if index == 0:
		vertices.sort(key=firstItem)
	elif index == 1:
		vertices.sort(key=secondItem)
	elif index == 2:
		vertices.sort(key=thirdItem)
	return vertices

def kdtree(topology):
	assert isinstance(topology, topologic.Topology), "Vertex.NearestVertex: The input is not a Topology."
	vertices = []
	_ = topology.Vertices(None, vertices)
	assert (len(vertices) > 0), "Vertex.NearestVertex: Could not find any vertices in the input Topology"

	"""Construct a k-d tree from an iterable of vertices.

    This algorithm is taken from Wikipedia. For more details,

    > https://en.wikipedia.org/wiki/K-d_tree#Construction

    """
	# k = len(points[0])
	k = 3

	def build(*, vertices, depth):
		if len(vertices) == 0:
			return None
		vertices = sortList(vertices, (depth % k))

		middle = len(vertices) // 2
		
		return BT(
			value = vertices[middle],
			left = build(
				vertices=vertices[:middle],
				depth=depth+1,
			),
			right = build(
				vertices=vertices[middle+1:],
				depth=depth+1,
			),
		)

	return build(vertices=list(vertices), depth=0)

NNRecord = collections.namedtuple("NNRecord", ["vertex", "distance"])
NNRecord.__doc__ = """
Used to keep track of the current best guess during a nearest
neighbor search.
"""

def find_nearest_neighbor(*, tree, vertex):
	"""Find the nearest neighbor in a k-d tree for a given vertex.
	"""
	k = 3 # Forcing k to be 3 dimensional
	best = None
	def search(*, tree, depth):
		"""Recursively search through the k-d tree to find the nearest neighbor.
		"""
		nonlocal best

		if tree is None:
			return
		distance = SED(tree.value, vertex)
		if best is None or distance < best.distance:
			best = NNRecord(vertex=tree.value, distance=distance)

		axis = depth % k
		diff = itemAtIndex(vertex,axis) - itemAtIndex(tree.value,axis)
		if diff <= 0:
			close, away = tree.left, tree.right
		else:
			close, away = tree.right, tree.left

		search(tree=close, depth=depth+1)
		if diff**2 < best.distance:
			search(tree=away, depth=depth+1)

	search(tree=tree, depth=0)
	return best.vertex

def processItem(input):
	vertex, topology, useKDTree = input
	if useKDTree:
		tree = kdtree(topology)
		return find_nearest_neighbor(tree=tree, vertex=vertex)
	else:
		vertices = []
		_ = topology.Vertices(None, vertices)
		distances = []
		indices = []
		for i in range(len(vertices)):
			distances.append(SED(vertex, vertices[i]))
			indices.append(i)
		sorted_indices = [x for _, x in sorted(zip(distances, indices))]
	return vertices[sorted_indices[0]]
