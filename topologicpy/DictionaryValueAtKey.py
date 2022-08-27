from topologic import Dictionary, IntAttribute, DoubleAttribute, StringAttribute, ListAttribute


def listAttributeValues(listAttribute):
	listAttributes = listAttribute.ListValue()
	returnList = []
	for attr in listAttributes:
		if isinstance(attr, IntAttribute):
			returnList.append(attr.IntValue())
		elif isinstance(attr, DoubleAttribute):
			returnList.append(attr.DoubleValue())
		elif isinstance(attr, StringAttribute):
			returnList.append(attr.StringValue())
		elif isinstance(attr, float) or isinstance(attr, int) or isinstance(attr, str) or isinstance(attr, dict):
			returnList.append(attr)
	return returnList

def processItem(item):
	d, key = item
	try:
		if isinstance(d, dict):
			attr = d[key]
		elif isinstance(d, Dictionary):
			attr = d.ValueAtKey(key)
	except:
		raise Exception("Dictionary.ValueAtKey - Error: Could not retrieve a Value at the specified key ("+key+")")
	if isinstance(attr, IntAttribute):
		return (attr.IntValue())
	elif isinstance(attr, DoubleAttribute):
		return (attr.DoubleValue())
	elif isinstance(attr, StringAttribute):
		return (attr.StringValue())
	elif isinstance(attr, ListAttribute):
		return (listAttributeValues(attr))
	elif isinstance(attr, float) or isinstance(attr, int) or isinstance(attr, str):
		return attr
	elif isinstance(attr, list):
		return listAttributeValues(attr)
	elif isinstance(attr, dict):
		return attr
	else:
		return None
