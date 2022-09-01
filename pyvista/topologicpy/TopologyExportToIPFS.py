import bpy
from bpy.props import StringProperty, BoolProperty, FloatProperty, EnumProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode

import topologic
try:
	import ipfshttpclient
except:
	raise Exception("Error: Could not import ipfshttpclient.")
import os

# From https://stackabuse.com/python-how-to-flatten-list-of-lists/
def flatten(element):
	returnList = []
	if isinstance(element, list) == True:
		for anItem in element:
			returnList = returnList + flatten(anItem)
	else:
		returnList = [element]
	return returnList

def repeat(list):
	maxLength = len(list[0])
	for aSubList in list:
		newLength = len(aSubList)
		if newLength > maxLength:
			maxLength = newLength
	for anItem in list:
		if (len(anItem) > 0):
			itemToAppend = anItem[-1]
		else:
			itemToAppend = None
		for i in range(len(anItem), maxLength):
			anItem.append(itemToAppend)
	return list

# From https://stackoverflow.com/questions/34432056/repeat-elements-of-list-between-each-other-until-we-reach-a-certain-length
def onestep(cur,y,base):
    # one step of the iteration
    if cur is not None:
        y.append(cur)
        base.append(cur)
    else:
        y.append(base[0])  # append is simplest, for now
        base = base[1:]+[base[0]]  # rotate
    return base

def iterate(list):
	maxLength = len(list[0])
	returnList = []
	for aSubList in list:
		newLength = len(aSubList)
		if newLength > maxLength:
			maxLength = newLength
	for anItem in list:
		for i in range(len(anItem), maxLength):
			anItem.append(None)
		y=[]
		base=[]
		for cur in anItem:
			base = onestep(cur,y,base)
		returnList.append(y)
	return returnList

def trim(list):
	minLength = len(list[0])
	returnList = []
	for aSubList in list:
		newLength = len(aSubList)
		if newLength < minLength:
			minLength = newLength
	for anItem in list:
		anItem = anItem[:minLength]
		returnList.append(anItem)
	return returnList

# Adapted from https://stackoverflow.com/questions/533905/get-the-cartesian-product-of-a-series-of-lists
def interlace(ar_list):
    if not ar_list:
        yield []
    else:
        for a in ar_list[0]:
            for prod in interlace(ar_list[1:]):
                yield [a,]+prod

def transposeList(l):
	length = len(l[0])
	returnList = []
	for i in range(length):
		tempRow = []
		for j in range(len(l)):
			tempRow.append(l[j][i])
		returnList.append(tempRow)
	return returnList

def exportToBREP(topology, filepath, overwrite):
	# Make sure the file extension is .BREP
	ext = filepath[len(filepath)-5:len(filepath)]
	if ext.lower() != ".brep":
		filepath = filepath+".brep"
	f = None
	try:
		if overwrite == True:
			f = open(filepath, "w")
		else:
			f = open(filepath, "x") # Try to create a new File
	except:
		raise Exception("Error: Could not create a new file at the following location: "+filepath)
	if (f):
		topString = topology.String()
		f.write(topString)
		f.close()	
		return True
	return False

def processItem(item):
    topology, url, port, user, password = item
    filepath = os.path.expanduser('~')+"/tempFile.brep"
    if exportToBREP(topology, filepath, True):
        url = url.replace('http://','')
        url = '/dns/'+url+'/tcp/'+port+'/https'
        client = ipfshttpclient.connect(url, auth=(user, password))
        newfile = client.add(filepath)
        os.remove(filepath)
        return newfile['Hash']
    return ''

replication = [("Default", "Default", "", 1),("Trim", "Trim", "", 2),("Iterate", "Iterate", "", 3),("Repeat", "Repeat", "", 4),("Interlace", "Interlace", "", 5)]

class SvTopologyExportToIPFS(bpy.types.Node, SverchCustomTreeNode):
	"""
	Triggers: Topologic
	Tooltip: Exports the input Topology to the Interplanetary File System   
	"""
	bl_idname = 'SvTopologyExportToIPFS'
	bl_label = 'Topology.ExportToIPFS'
	Replication: EnumProperty(name="Replication", description="Replication", default="Default", items=replication, update=updateNode)
	URL: StringProperty(name='URL', default="http://ipfs.infura.io",update=updateNode)
	Port: StringProperty(name='Port', default="5001",update=updateNode)

	def sv_init(self, context):
		self.inputs.new('SvStringsSocket', 'Topology')
		self.inputs.new('SvStringsSocket', 'URL').prop_name='URL'
		self.inputs.new('SvStringsSocket', 'Port').prop_name='Port'
		self.inputs.new('SvStringsSocket', 'Username')
		self.inputs.new('SvStringsSocket', 'Password')
		self.outputs.new('SvStringsSocket', 'Hash')

	def draw_buttons(self, context, layout):
		layout.prop(self, "Replication",text="")

	def process(self):
		if not any(socket.is_linked for socket in self.inputs):
			self.outputs['Hash'].sv_set([False])
			return
		topologyList = self.inputs['Topology'].sv_get(deepcopy=False)
		topologyList = flatten(topologyList)
		urlList = self.inputs['URL'].sv_get(deepcopy=False)
		urlList = flatten(urlList)
		portList = self.inputs['Port'].sv_get(deepcopy=False)
		portList = flatten(portList)
		userList = self.inputs['Username'].sv_get(deepcopy=False)
		userList = flatten(userList)
		passwordList = self.inputs['Password'].sv_get(deepcopy=False)
		passwordList = flatten(passwordList)

		inputs = [topologyList, urlList, portList, userList, passwordList]
		outputs = []
		if ((self.Replication) == "Default"):
			inputs = repeat(inputs)
			inputs = transposeList(inputs)
		elif ((self.Replication) == "Trim"):
			inputs = trim(inputs)
			inputs = transposeList(inputs)
		elif ((self.Replication) == "Iterate"):
			inputs = iterate(inputs)
			inputs = transposeList(inputs)
		elif ((self.Replication) == "Repeat"):
			inputs = repeat(inputs)
			inputs = transposeList(inputs)
		elif ((self.Replication) == "Interlace"):
			inputs = list(interlace(inputs))
		for anInput in inputs:
			outputs.append(processItem(anInput))
		self.outputs['Hash'].sv_set(outputs)

def register():
	bpy.utils.register_class(SvTopologyExportToIPFS)

def unregister():
	bpy.utils.unregister_class(SvTopologyExportToIPFS)