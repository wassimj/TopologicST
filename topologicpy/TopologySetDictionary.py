def processItem(item):
	topology = item[0]
	dictionary = item[1]
	if len(dictionary.Keys()) > 0:
		_ = topology.SetDictionary(dictionary)
	return topology
