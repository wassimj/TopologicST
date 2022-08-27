from topologic import Dictionary

def processItem(item):
	if isinstance(item, dict):
		return list(item.keys())
	elif isinstance(item, Dictionary):
		return item.Keys()
	else:
		return None
