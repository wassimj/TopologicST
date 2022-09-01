import topologic

def processItem(item):
	topology = None
	file = open(item)
	if file:
		brepString = file.read()
		topology = topologic.Topology.ByString(brepString)
		file.close()
		return topology
	return None
