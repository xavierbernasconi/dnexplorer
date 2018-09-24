import math
import networkx as nx
import ast
import pandas
from os import walk
from bokeh.io import show, output_file,curdoc
from bokeh.plotting import figure
from bokeh.models import GraphRenderer, StaticLayoutProvider, Oval,HoverTool, TapTool, BoxSelectTool,Circle,MultiLine,ColumnDataSource,LabelSet, Bezier
from bokeh.palettes import Spectral8
from bokeh.palettes import Spectral4
from bokeh.models.graphs import from_networkx, NodesAndLinkedEdges, EdgesAndLinkedNodes
from bokeh.transform import linear_cmap
from bokeh.layouts import column, widgetbox,layout
from bokeh.models.widgets import TextInput, Button


#####
#		'root': 0
#		'Declined': 1,		
#		'Element Approved': 1,
#		'Available': 2,
#		'Pending' : 3

status_palette = ['#000000','#ff0000','#00ff00','#0000ff','#D3D3D3']
search_palette = ['#000000','#CCCC00']

def rotate_around_point_highperf(xy, radians, origin=(0, 0)):
    x, y = xy
    offset_x, offset_y = origin
    adjusted_x = (x - offset_x)
    adjusted_y = (y - offset_y)
    cos_rad = math.cos(radians)
    sin_rad = math.sin(radians)
    qx = offset_x + cos_rad * adjusted_x + sin_rad * adjusted_y
    qy = offset_y + -sin_rad * adjusted_x + cos_rad * adjusted_y

    return qx, qy


def hierarchy_pos(G, root, width=2., vert_gap = .3, vert_loc = 0.0, xcenter = 0.0, 
                  pos = None, parent = None):

    if pos == None:
        pos = {root:(xcenter,vert_loc)}
    else:
        pos[root] = (xcenter, vert_loc)
    neighbors = list(G.neighbors(root))

    if parent != None:   #this should be removed for directed graphs.
        neighbors.remove(parent)  #if directed, then parent not in neighbors.
    if len(neighbors)!=0:
        dx = width/len(neighbors) 
        nextx = xcenter - width/2 - dx/2
        for neighbor in neighbors:
			nextx += dx
			pos = hierarchy_pos(G,neighbor, width = dx, vert_gap = vert_gap, 
						        vert_loc = vert_loc-vert_gap, xcenter=nextx, pos=pos, 
						        parent = root)

    return pos


def dg_plots():

	dgdatafiles = [] 
	for (dp,dn,fn) in (walk('/Users/xavier/GitHub/dnexplorer/dgdata/')):
		dgdatafiles.extend(fn)
	print dgdatafiles
	plots_list = []

	pId = 0

	CDS = dict()
	
	for fn in dgdatafiles:
		print fn
		### READ IN ALL DATA FROM IVY
		f = open(('/Users/xavier/GitHub/dnexplorer/dgdata/'+fn),'r')
		edges = ast.literal_eval(f.readline())
		connectionsStart= ast.literal_eval(f.readline())
		connectionsEnd = ast.literal_eval(f.readline())
		labels = ast.literal_eval(f.readline())
		statuses = ast.literal_eval(f.readline())

		### INIT SEL STATUS TO 0
		selStatus = []
		for i in statuses:
			selStatus.append(i)


		N = len(edges)+2
		node_indices = list(range(N))

		### s
		G=nx.Graph()
		G.add_edges_from(edges)
		pos = hierarchy_pos(G,1)

		theta = math.radians(90)


		xCoord = []
		yCoord = []
		theta = math.radians(-90)
		newPosDict = {}
		xs, ys = [], []
		for p in pos:

			p_rot = rotate_around_point_highperf((pos[p][0],pos[p][1]),theta)
			xCoord.append(p_rot[0])
			yCoord.append(p_rot[1])
			newPosDict[p]=[p_rot[0],p_rot[1]]

		pId += 1
		s_pId = str(pId)
		CDS[('x'+s_pId)] = xCoord
		CDS[('y'+s_pId)] = yCoord
		CDS[('labels'+s_pId)] = labels
		CDS[('selstatus'+s_pId)] = selStatus
		CDS[('edges'+s_pId)] = edges
	
	
	return CDS



def draw_plots(CDS_data):

#			dict(x= xCoord, y = yCoord, names=labels,selected=selStatus)
	
	
	source = ColumnDataSource(data=dict())
	for p in CDS_data:
		source.add(CDS_data[p],name=p)
# 		TOOLS = "crosshair,pan,wheel_zoom,box_zoom,reset,box_select,lasso_select"

# 		plot = figure(title='Dependencies Graph', x_range=(-0.1,1.1), y_range=(-1.1,1.1),
# 				      tools=TOOLS)
# 		plot.width = 1200
# 		plot.height = 600

# 		plot.add_tools(HoverTool(tooltips=None), TapTool(), BoxSelectTool())

# 		############################
# 		###### Add Assets Labels
# 		######
# 		textColorMapper = linear_cmap(field_name = 'selStatus',palette=search_palette,low=0,high=1)
# 		labels = LabelSet(x='x',y='y',text='names', x_offset = 10,y_offset=-5,level='glyph',source = source,render_mode = 'canvas')
# 		plot.add_layout(labels)


# 		############################
# 		###### draw bezier splines
# 		######
		
# 		steps = [i/10. for i in range(10)]
# 		xs, ys = [], []

# 		for edge in edges:
# 			s = edge[0]
# 			e = edge[1]
# 			x0 = newPosDict[s][0]
# 			y0 = newPosDict[s][1]
# 			x1 = newPosDict[e][0]
# 			y1 = newPosDict[e][1]
# 			cx0 = newPosDict[s][0] + (newPosDict[e][0]-newPosDict[s][0])/2
# 			cx1 = newPosDict[s][0] + (newPosDict[e][0]-newPosDict[s][0])/2
# 			cy0 = newPosDict[s][1] + 0.01
# 			cy1 = newPosDict[e][1] -0.01
# 		#	xs.append(bezier(x0, x1,.1, steps))
# 		#	ys.append(bezier(y0, y1, .1, steps))

# 			glyphBezier = Bezier(x0=x0,y0=y0,x1=x1,y1=y1,cx0=cx0,cx1=cx1,cy0=cy0,cy1=cy1,line_color="orange",line_width=1)
# 			plot.add_glyph(glyphBezier)

# 		############################
# 		###### draw bezier splines
# 		######

# 		graph = GraphRenderer()
# 		graph.node_renderer.data_source.add(statuses,'node_color')
# 		statusMapper = linear_cmap(field_name = 'node_color',palette=status_palette,low=0,high=4)

# 		graph.node_renderer.data_source.add(node_indices, 'index')
# 		graph.node_renderer.data_source.add(Spectral8, 'color')

# 		graph.node_renderer.glyph = Circle(size=6, fill_color=statusMapper)
# 		graph.node_renderer.selection_glyph = Circle(size=6, fill_color=statusMapper)
# 		graph.node_renderer.hover_glyph = Circle(size=6, fill_color=statusMapper)

# 		graph.edge_renderer.glyph = MultiLine(line_color="#CCCCCC", line_alpha=1, line_width=2)
# 		graph.edge_renderer.selection_glyph = MultiLine(line_color=Spectral4[2], line_width=2)
# 		graph.edge_renderer.hover_glyph = MultiLine(line_color=Spectral4[1], line_width=2)

# 		graph.selection_policy = NodesAndLinkedEdges()
# 		graph.inspection_policy = EdgesAndLinkedNodes()

# 		graph.layout_provider = StaticLayoutProvider(graph_layout=newPosDict)

# 		plot.renderers.append(graph)

# 		plot.xaxis.visible = False
# 		plot.xgrid.visible = False
# 		plot.yaxis.visible = False
# 		plot.ygrid.visible = False

# 		tmp_graph_id = plot
# 		graphData = {}
# 		for k in source.data.iterkeys():
# 			graphData[k] = source.data.get(k)
# 		plots_list.append([tmp_graph_id,graphData])

# 	return plots_list

# def doSearchYo(textWdg,plots_Data):
# 	#print sourceDG_a
# 	searchText = textWdg.value
# 	for pd in plots_Data:
# 		gId = pd[0]
# 		newSelection = []
# 		for l in pd[1]['names']:
# 			if l.find(searchText)>-1:
# 				print "found:",searchText," in:", l
# 				newSelection.append(1)
# 			else:
# 				newSelection.append(0)
# 		print gId.renderers

plots_Data = dg_plots()
draw_plots(plots_Data)
#print plots_Data
# gId = plots_Data[0][0] 

# for r in gId.renderers:
# 	print r.name

# searchField = TextInput(value="", title="Search:")
# doSearch = Button(label="Go", button_type="success")
# doSearch.on_click(lambda : doSearchYo(searchField,plots_Data))

#curdoc().add_root(layout(widgetbox(searchField,doSearch),plots_Data[0][0],plots_Data[1][0]))









