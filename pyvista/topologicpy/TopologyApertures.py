import topologic

def processItem(item):
	apertures = []
	apTopologies = []
	_ = item.Apertures(apertures)
	for aperture in apertures:
		apTopologies.append(topologic.Aperture.Topology(aperture))
	return [apertures, apTopologies]
