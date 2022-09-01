import topologic

def processItem(item):
	return topologic.Topology.DeepCopy(topologic.Topology.ByString(item))
