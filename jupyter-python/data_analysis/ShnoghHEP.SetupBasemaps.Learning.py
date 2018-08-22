# grass setup

# set up Python for GRASS GIS
import os
import sys
import subprocess
from IPython.display import Image, display

# set up GRASS GIS runtime environment
gisbase = subprocess.check_output(["grass", "--config", "path"]).strip()
os.environ['GISBASE'] = gisbase
os.environ['GRASS_FONT'] = 'sans'
os.environ['GRASS_OVERWRITE'] = '1'  #overwrite existing maps
sys.path.append(os.path.join(gisbase, "etc", "python"))

# set display modules to render into a file (named map.png by default)
os.environ['GRASS_RENDER_IMMEDIATE'] = 'cairo'
os.environ['GRASS_RENDER_FILE_READ'] = 'TRUE'
os.environ['GRASS_LEGEND_FILE'] = 'legend.txt'

# import GRASS GIS
import grass.script as gs
import grass.script.setup as gsetup
from grass.script import core as grass

# for pygrass
from grass.pygrass.modules.shortcuts import raster as r, vector as v, general as g, display as d

from subprocess import PIPE

# further setup for GRASS GIS 
gs.set_raise_on_error(True)
#gs.set_capture_stderr(True)  #might be Python 2 vs 3 issue (unsure if Python 3 required for this Notebook)

# https://grasswiki.osgeo.org/wiki/GRASS_Python_Scripting_Library
# GRASS Python Scripting Library
# How to retrieve error messages from read_command():

def read2_command(*args, **kwargs):                                                 #rename to e.g. read_grass
   kwargs['stdout'] = grass.PIPE
   kwargs['stderr'] = grass.PIPE
   ps = grass.start_command(*args, **kwargs)
   return ps.communicate()

# set wd for this procedure and project
#os.chdir("/home/kaelin_joseph/projects/ShnoghHEP")
project = 'ShnoghHEP'
project_basedir = '/home/kaelin_joseph/projects/'
os.chdir(project_basedir+project)




# define required input data files
TopogContours ='data/in/DMI-2D_cleaned.dxf'  #extraneous polyline with z=2350 removed


# In[10]:


# define required input data

# mapping
##crs = {'init': 'epsg:32755'}  #define crs for project Snowy Mountains 2
##grass_region = "619000,656000,6029000,6043000"  #map region E1,E2,N1,N2 Snowy Mountains 2


# In[11]:


# define temporary data files



# In[12]:


# define output data files


# In[13]:


# create a mapset (mapset does not already exist)
# should only do once (but will report error and exit if already exists)

# dir /home/kaelin_joseph/projects/RogunHEP/grassdata  should already exist
get_ipython().system(u'grass -c EPSG:3857 grassdata/ShnoghHEP -e')
# should use grass scipt                                                                             ToDo JK !!    

# define all parameters separately                                                                   ToDo JK !!
#EPSG:3857  #WGS84 Pseudo Mercator


# In[14]:


# open mapset
rcfile = gsetup.init(gisbase, 
         "/home/kaelin_joseph/projects/ShnoghHEP/grassdata",
         "ShnoghHEP/", "PERMANENT")


# In[15]:


# check grass env
print grass.gisenv()


# In[16]:


#check mapsets
grass.mapsets()


# In[17]:


# check projection info
read2_command('g.proj', flags = 'jf')


# In[18]:


# set grass regions (from CAD inspection)
#g.region(n=4559192,s=4543900,e=8484264,w=8467000, res=10)
#g.region(n=4559192,s=4543900,e=8484264,w=8467000, res=20)
g.region(n=4559200,s=4531500,e=8484100,w=8463100, res=10)
# sets also raster resolution with 'res'


# ## read in DXF with topogaphic contours

# In[19]:


# inspect layers in DXF to be read in
print(read2_command("v.in.dxf", input=TopogContours,flags='l')[0].decode()) 


# In[20]:


# read dxf data 
# read2_command("v.in.dxf", input=TopogContours, layers='maj @ 20,maj',  
#              output='topog_contours')[0]
read2_command("v.in.dxf", input=TopogContours, layers='maj',  
             output='topog_contours')[0]
 
# output in 'RogunHPP/PERMANENT/vector/topography2m_r5_reduced'

# print(read2_command("v.info", map='test_alignment')[0].decode())
# pattern for 'printing grass output nicely
#   decode must be applied to each member of tuple
#   [0] -> stdout
#   [1] -> stderr
#   above are according to doc, however it seems that [1] is where all output is                  ToDo JK:  ??


# In[21]:


# set region from vector data bounds
####read2_command('g.region', vector='topog_contours')


# In[22]:


# check grass region
print(g.region(flags='p',stdout_=PIPE).outputs.stdout.decode())


# In[23]:


print(read2_command("v.info", map='topog_contours', layer='maj @ 20,maj')[0].decode()) 

# why so few points & lines ?    -> because lines --> polylines (see below)


# In[24]:


#read2_command("v.build", map='topog_contours')


# In[25]:


print(read2_command("v.info", map='topog_contours', layer='-1', flags='c')[0].decode()) 


# In[26]:


print(read2_command("v.db.select", map='topog_contours')[0].decode()) 


# In[27]:


print(read2_command("v.category", input='topog_contours', option='report')[0].decode()) 


# In[28]:


print(read2_command("v.report", map='topog_contours', option='coor')[0].decode()) 

# ??


# In[29]:


# view and check topography
get_ipython().system(u'rm map.png                                                                                 #ToDo JK: pythonize')
read2_command("d.vect", map='topog_contours', color='green')


# In[30]:


Image(filename="map.png")


# In[31]:


read2_command("r.mask", vector='topog_contours', layer=11)
#read2_command("r.mask", vector='topog_contours', layer=11, where='z>500')
# https://grass.osgeo.org/grass75/manuals/r.mask.html

#read2_command("r.mask", flags='r')  #remove MASK


# ## extract points from vector data from DXF

# In[32]:


#points_out = read2_command("v.to.points", input='topog_contours', output='topog_contours_points') 
#print(points_out[1].decode())

#WARNING: 1565094 features without category in layer <1> skipped. Note that
#         features without category (usually boundaries) are not skipped
#         when 'layer=-1' is given.
# without categories --> seems x,y,z are all missing   !!

points_out = read2_command("v.to.points", input='topog_contours', layer=-1, output='topog_contours_points') 
print(points_out[1].decode())

# works (output)


# In[33]:


#print(read2_command("v.db.select", map='topog_contours_points', layer=-1)[0].decode()) 


# lots of output, apparently one line for each coordinate ??


# In[34]:


print(read2_command("v.info", map='topog_contours_points')[0].decode()) 


# In[35]:


read2_command("v.out.ascii", input='topog_contours_points', type='point', layer=-1, separator=',',
              output='data/out/topog_contours_points.csv')

# this works (but includes layers with bad data)
# try with only identified layers with correct contour data   !!


# In[36]:


#print(read2_command("g.region", vect='topog_contours_points')[1].decode())  # does not help to display image


# In[37]:


# view and check points
get_ipython().system(u'rm map.png                                                                                 #ToDo JK: pythonize')
read2_command("d.vect", map='topog_contours_points', color='red')


# In[38]:


Image(filename="map.png")

# no image visible   ??
# image is displayed in qgisp


# In[39]:


read2_command("v.to.rast", input='topog_contours_points', use='z', layer=-1, 
             output='topog_contours_points_rast')[0]


# In[40]:


# view and check topography
get_ipython().system(u'rm map.png                                                                                 #ToDo JK: pythonize')
read2_command("d.rast", map='topog_contours_points_rast')[0]


# In[41]:


Image(filename="map.png")


# ## extract lines from vector data from DXF

# In[42]:


read2_command("v.out.ascii", input='topog_contours', type='line', format='wkt', layer=-1,
              output='data/out/topog_contours_lines.csv')


# ## convert vector data from DXF to raster data using v.to.rast

# In[43]:


read2_command("v.to.rast", input='topog_contours', use='z', 
             output='topog_contours_rast')[1]


# [1] --> stderr        !!


# In[44]:


#read2_command("v.build.all")[1]

# works for v.to.rast


# In[45]:


read2_command("v.to.rast", input='topog_contours', use='z', 
             output='topog_contours_rast')[0]


# In[46]:


print(read2_command("r.info", map='topog_contours_rast')[0].decode()) 


# In[47]:


print(read2_command("r.univar", map='topog_contours_rast')[0].decode()) 


# In[48]:


# view and check topography
get_ipython().system(u'rm map.png                                                                                 #ToDo JK: pythonize')
read2_command("d.rast", map='topog_contours_rast')[0]


# In[49]:


Image(filename="map.png")


# In[50]:


#!d.mon stop=cairo
get_ipython().system(u'd.mon start=cairo resolution=2 width=720 height=480')

# sometimes works on image ??


# In[51]:


# view and check topography
get_ipython().system(u'rm map.png                                                                                 #ToDo JK: pythonize')
read2_command("d.rast", map='topog_contours_rast')[0]


# In[52]:


Image(filename="map.png")


# ## convert points to raster data using r.in.xyz

# In[53]:


read2_command("r.in.xyz", input='data/out/topog_contours_points.csv', separator=',', zrange='400,2000',
             type='CELL', output='topog_contours_xyz_rast')[1]

# zrange from visual check of original topography


# use also fpr MASK (as first try)
##read2_command("r.in.xyz", input='data/out/topog_contours_points.csv', separator=',', zrange='400,2000',
##             type='CELL', output='MASK')[1]


# In[54]:


print(read2_command("r.info", map='topog_contours_xyz_rast')[0].decode()) 


# In[55]:


# view and check topography
get_ipython().system(u'rm map.png                                                                                 #ToDo JK: pythonize')
read2_command("d.rast", map='topog_contours_xyz_rast', verbose=True, bgcolor='red')[1]


# In[56]:


Image(filename="map.png")


# ## develop raster from contours into filled raster using r.surf.contour

# In[57]:


# read2_command("r.surf.contour", input='topog_contours_rast', 
#               output='topog_rast')[0]

# # read2_command("r.surf.idw", input='topog_contours_rast', 
# #               output='topog_rast_idw')[1]    
# # ERROR: This module currently only works for integer (CELL) maps

# # very slow
# # with 'topog_contours_points_rast' as MASK fast

# # output covers entire region, no clipping


# In[58]:


# # view and check topography
# !rm map.png                                                                                 #ToDo JK: pythonize
# read2_command("d.rast", map='topog_rast', verbose=True, bgcolor='white', flags='n', values='500-2000')[0]


# In[59]:


# Image(filename="map.png")


# # choices for handling Nan?


# ## experiment with better ways to develop raster from contours into filled raster

# In[60]:


# r.surf.nnbathy


# In[61]:


get_ipython().system(u'r.surf.nnbathy --help')
#https://grass.osgeo.org/grass74/manuals/addons/r.surf.nnbathy.html
#https://gis.stackexchange.com/questions/118243/create-a-dem-from-point-data?noredirect=1&lq=1


# In[62]:


# r.neighbors using output from v.to.rast


# In[63]:


read2_command("r.neighbors", input='topog_contours_rast', method='average', size=3,
              output='topog_rast_neighbors')[0]


# In[64]:


# view and check topography
get_ipython().system(u'rm map.png                                                                                 #ToDo JK: pythonize')
read2_command("d.rast", map='topog_rast_neighbors', verbose=True, bgcolor='white', flags='n', 
              values='0-2000')[0]


# In[65]:


Image(filename="map.png")


# In[66]:


read2_command("r.neighbors", input='topog_contours_rast', method='average', size=6,
              output='topog_rast_neighbors')[0]


# In[67]:


# view and check topography
get_ipython().system(u'rm map.png                                                                                 #ToDo JK: pythonize')
read2_command("d.rast", map='topog_rast_neighbors', verbose=True, bgcolor='white', flags='n', 
              values='0-2000')[0]


# In[68]:


Image(filename="map.png")


# In[69]:


# r.neighbors using output from r.in.xyz


# In[70]:


read2_command("r.neighbors", input='topog_contours_xyz_rast', method='average', size=4,
              output='topog_rast_neighbors')[0]


# In[71]:


# view and check topography
get_ipython().system(u'rm map.png                                                                                 #ToDo JK: pythonize')
read2_command("d.rast", map='topog_rast_neighbors', verbose=True, bgcolor='white', flags='n', 
              values='0-2000')[0]


# In[72]:


read2_command("d.legend", raster='topog_rast_neighbors')[0]


# In[73]:


Image(filename="map.png")


# In[74]:


# r.resamp.rst using output from r.in.xyz


# In[75]:


read2_command("r.resamp.rst", input='topog_contours_xyz_rast', ew_res=10, ns_res=10,
              elevation='topog_xyz_rast_resamp')[0]


# In[76]:


# view and check topography
get_ipython().system(u'rm map.png                                                                                 #ToDo JK: pythonize')
read2_command("d.rast", map='topog_xyz_rast_resamp', verbose=True, bgcolor='white', flags='n', 
              values='0-2000')[0]
# fast


# In[77]:


read2_command("d.legend", raster='topog_xyz_rast_resamp')[0]


# In[78]:


Image(filename="map.png")


# In[79]:


# r.resamp.rst using output from v.to.rast


# In[80]:


read2_command("r.resamp.rst", input='topog_contours_rast', ew_res=10, ns_res=10,
              elevation='topog_rast_resamp')[0]

# result seems quite good, high definition, probably best of my attempts
# only a few relevant 'holes' where points data sparse
# what is bluish line following above valley ??
# raster is clipped along available topography


# In[81]:


print(read2_command("r.report", map='topog_rast_resamp', units='h,p')[0].decode()) 


# In[82]:


#!d.mon stop=cairo
#!d.mon start=cairo resolution=2 width=720 height=480 --overwrite
get_ipython().system(u'd.mon start=cairo resolution=2 width=1080 height=720 --overwrite')

# only sometimes works on image, why  ?? 


# In[83]:


# view and check topography
get_ipython().system(u'rm map.png                                                                                 #ToDo JK: pythonize')
# read2_command("d.rast", map='topog_rast_resamp', verbose=True, bgcolor='white', flags='n', 
#               values='0-2000')[0]
read2_command("d.rast", map='topog_rast_resamp', verbose=True, bgcolor='white', flags='n')[0]


# In[84]:


read2_command("d.legend", raster='topog_rast_resamp', fontsize='22')[1]


# In[85]:


Image(filename="map.png")


# ## more experimentation with better ways to develop raster from contours into filled raster

# In[86]:


# grass documentation recomments r.surf and v.surf methods for interpreting elevations from countour lines


# In[87]:


# experiment with r.surf.idw


# In[88]:


##read2_command("g.remove", name='MASK', type='raster', flags='f')[1] 
# preferable to use r.mask to manage (add and remove) MASK


# In[89]:


# !r.mapcalc topog_contours_rast_CELL="int(topog_contours_rast)"  #integer floor
# !r.mapcalc topog_contours_rast_CELL="round(topog_contours_rast)"  #nearest integer
# read2_command("r.surf.idw", input='topog_contours_rast_CELL', 
#              output='topog_rast_idw')[1]   
# ERROR: This module currently only works for integer (CELL) maps
# works with r.mapcalc, no clipping

read2_command("r.surf.idw", input='topog_contours_xyz_rast', 
              output='topog_rast_idw')[0]   
# fast and good results
# fills entire region, no clipping

# use topog_contours_points_rast as MASK (see above) -> poor result, apparently all null areas are masked  !!
# delete layer MASK  !!
# using vector layer as MASK works better, but still not an adequate solution


# In[90]:


# view and check topography
get_ipython().system(u'rm map.png                                                                                 #ToDo JK: pythonize')
read2_command("d.rast", map='topog_rast_idw', verbose=True, bgcolor='white')[0]


# In[91]:


read2_command("d.legend", raster='topog_rast_idw')[0]


# In[92]:


Image(filename="map.png")


# In[93]:


# experiment with v.surf.idw


# In[94]:


# read2_command("v.surf.idw", input='topog_contours', layer='maj @ 20,maj',
#               output='topog_rast_idw')[1]  
read2_command("v.surf.idw", input='topog_contours', layer='maj',
              output='topog_rast_idw')[1]  

# all evelevation in raster output = 0  ???
# after removing 'maj @ 20'  --> ok
# no clipping


# read2_command("v.surf.rst", input='topog_contours', layer='maj @ 20,maj',
#               elevation='topog_rast_rst')[1]   

# print(read2_command("v.surf.rst", input='topog_contours', layer='maj @ 20,maj',
#               elevation='topog_rast_rst')[1].decode())

# result of v.surf.rst
# slow (> 1h

# result of v.surf.rst not good
#   Range of data:    min = -1010.684  max = 3818.498 
# many warnings
#   Some points outside of region (ignored)
#   Taking too long to find points for interpolation - 
#      please change the region to area where your points are. Continuing calculations...
#   Overshoot - increase in tension suggested.

# raster is clipped along available topography


# In[95]:


print(read2_command("r.info", map='topog_rast_idw')[0].decode()) 


# In[96]:


# view and check topography
get_ipython().system(u'rm map.png                                                                                 #ToDo JK: pythonize')
read2_command("d.rast", map='topog_rast_idw', verbose=True, bgcolor='white', flags='n', 
              values='0-2000')[0]
#read2_command("d.rast", map='topog_rast_idw', verbose=True, bgcolor='white')[0]


# In[97]:


read2_command("d.legend", raster='topog_rast_idw')[0]


# In[98]:


Image(filename="map.png")


# In[99]:


# read2_command("v.surf.idw", input='topog_contours_points', layer='maj @ 20,maj',
#               output='topog_contours_points_idw')[0] 

# # slow (30 min)
# # no clipping


# In[100]:


# # view and check topography
# !rm map.png                                                                                 #ToDo JK: pythonize
# read2_command("d.rast", map='topog_contours_points_idw', verbose=True, bgcolor='white', flags='n', 
#               values='0-2000')[0]


# In[101]:


# read2_command("d.legend", raster='topog_contours_points_idw')[0]


# In[102]:


# Image(filename="map.png")


# ## corrections to topography

# In[103]:


get_ipython().system(u'r.mapcalc "topog_contours_rast_filtered_=if(topog_rast_resamp>2340,null(),topog_rast_resamp)"')
# attempt at filtering out the extraneous line with z=2350
# in the end, I cleaned manually with Draftsight

#!r.mapcalc "topog_contours_rast_filtered_=(topog_rast_resamp)-(topog_xyz_rast_resamp)"
#newmap = if(map<5, null(), 5)


# In[104]:


#!r.mapcalc "topog_contours_rast_=(topog_contours_rast_filtered_)-(topog_xyz_rast_resamp)"


# In[105]:


# view and check topography
get_ipython().system(u'rm map.png                                                                                 #ToDo JK: pythonize')
read2_command("d.rast", map='topog_contours_rast_filtered_', verbose=True, bgcolor='white', flags='n',
             )[0]
# read2_command("d.rast", map='topog_contours_rast_', verbose=True, bgcolor='white', flags='n',
#              values='0 - 100')[0]


# In[106]:


read2_command("d.legend", raster='topog_contours_rast_filtered_')[1]
#read2_command("d.legend", raster='topog_contours_rast_', range='0,100')[1]


# In[107]:


Image(filename="map.png")


# ## experiment with relief maps

# In[108]:


# relief map using r.relief using output from r.in.xyz
# read2_command("r.relief", input='topog_contours_points_rast', 
#               output='topog_rast_relief')[0]
# no output displayed ??

# relief map using r.relief r.resamp.rst, from v.to.rast
# read2_command("r.relief", input='topog_contours_rast', 
#               output='topog_rast_relief')[1]
# no output displayed ??

read2_command("r.relief", input='topog_rast_resamp', 
              output='topog_rast_relief')[0]
# colored relief map?  --> see below

# can r.shaded.relief  do a colred relief map in one go  ??
# https://grass.osgeo.org/grass64/manuals/r.shaded.relief.html
# https://grass.osgeo.org/grass72/manuals/r.relief.html
# https://grass.osgeo.org/grass72/manuals/r.shade.html


# In[109]:


# view and check topography
get_ipython().system(u'rm map.png                                                                                 #ToDo JK: pythonize')
read2_command("d.rast", map='topog_rast_relief', verbose=True, bgcolor='white')[0]


# In[110]:


Image(filename="map.png")


# In[111]:


read2_command("r.shade", shade='topog_rast_relief', 
              color='topog_rast_resamp', output='topog_rast_relief_color')[0]


# In[112]:


# view and check topography
get_ipython().system(u'rm map.png                                                                                 #ToDo JK: pythonize')
read2_command("d.rast", map='topog_rast_relief_color', verbose=True, bgcolor='white')[0]


# In[113]:


read2_command("d.legend", raster='topog_rast_resamp', fontsize='22')[1]

read2_command("d.grid", size=2000, fontsize=20)[0]
# https://grass.osgeo.org/grass75/manuals/d.grid.html


# In[114]:


Image(filename="map.png")


# ## experiment with grass hydrology modules

# In[115]:


#!r.watershed elevation=topog_rast_resamp basin=topog_rast_resamp_basin threshold=30000
get_ipython().system(u'r.watershed elevation=topog_rast_resamp basin=topog_rast_resamp_basin threshold=100000')


# In[116]:


# view and check topography
get_ipython().system(u'rm map.png                                                                                 #ToDo JK: pythonize')
read2_command("d.rast", map='topog_rast_resamp_basin', verbose=True, bgcolor='white')[0]


# In[117]:


Image(filename="map.png")


# In[118]:


get_ipython().system(u'r.watershed elevation=topog_rast_resamp stream=topog_rast_resamp_stream threshold=1000')


# In[119]:


# view and check topography
get_ipython().system(u'rm map.png                                                                                 #ToDo JK: pythonize')
read2_command("d.rast", map='topog_rast_resamp_stream', verbose=True, bgcolor='white')[0]


# In[120]:


Image(filename="map.png")


# In[121]:


get_ipython().system(u'r.watershed elevation=topog_rast_resamp accumulation=topog_rast_resamp_stream threshold=1000')


# In[122]:


# view and check topography
get_ipython().system(u'rm map.png                                                                                 #ToDo JK: pythonize')
read2_command("d.rast", map='topog_rast_resamp_stream', verbose=True, bgcolor='white')[0]


# In[123]:


read2_command("d.legend", raster='topog_rast_resamp_stream', fontsize='22')[1]


# In[124]:


Image(filename="map.png")


# In[125]:


# improve display of watershed and streamcourses
# http://gis.jkaelin.com:8080/notebooks/testing/geospatial-modeling-course-jupyter/notebooks/hydrology_python.ipynb


# In[126]:


# filter accumulation for values (number of cells that drain through each cell) > 100 and set these =1
gs.mapcalc("topog_rast_resamp_stream_calc = if(abs(topog_rast_resamp_stream) > 1000, 1, null())")


# In[127]:


# vectorize watershed raster data
gs.run_command('r.to.vect', input="topog_rast_resamp_basin", output="topog_rast_resamp_basin", 
               type="area", flags='s')


# In[128]:


# # view and check topography
# !rm map.png                                                                                 #ToDo JK: pythonize
# read2_command("d.rast", map='topog_rast_resamp_stream_calc', verbose=True, bgcolor='white')[0]


# In[129]:


# Image(filename="map.png")
# # displays ok


# In[130]:


# clean raster data of streamcourse in preparation for converting to vector data
gs.run_command('r.thin', input="topog_rast_resamp_stream_calc", output="topog_rast_resamp_stream_calc_thin")


# In[131]:


# convert raster data of streamcourses to vector data
gs.run_command('r.to.vect', input="topog_rast_resamp_stream_calc_thin", 
               out="topog_rast_resamp_stream_calc_vect", type="line", flags='s')


# In[132]:


# read stream data imported from topography dxf
read2_command("v.in.dxf", input=TopogContours, layers='river-maj',  
             output='streams')[0]


# In[133]:


# view and check hydrology
get_ipython().system(u'rm map.png                                                                                 #ToDo JK: pythonize')

# display shaded relief map with watershed basins
read2_command('d.his', hue="topog_rast_resamp_basin", intensity="topog_rast_relief", brighten="40")[0]
# display watershed basin boundaires
gs.run_command('d.vect', map="topog_rast_resamp_basin", type="boundary",  width=2)
# display streams calculated from accumulation
read2_command("d.vect", map='topog_rast_resamp_stream_calc_vect', verbose=True, bgcolor='white', 
              color='indigo', width=3)[0]
# display stream imported from dxf
gs.run_command('d.vect', map="streams", type="line", color='blue', width=3)

read2_command("d.grid", size=2000, fontsize=20)[1]
# colors
# https://sites.google.com/site/hamishbowman/grass_color_maps


# In[134]:


Image(filename="map.png")


# ## experiment with importing images into grass

# In[135]:


#!g.region(n=4559000,s=4536000,e=8463000,w=8484000, res=10)
g.region(n=4559000,s=4536000,e=8484000,w=8463000, res=10)


# In[136]:


# check grass region
print(g.region(flags='p',stdout_=PIPE).outputs.stdout.decode())


# In[137]:


# import project layout into grass

# pdf as received from project team 
# print(read2_command("r.in.gdal", input='data/in/SHN-000-GE-DR-010-A0.pdf', flags='oe', verbose=True, 
#              output='layout_raster')[1].decode())

# pdf from project team -> screenshot -> Google Drawing -> rotate,adjust -> export as pdf -> screenshot
# print(read2_command("r.in.gdal", input='data/in/PreferredAlternativeLayout_2.png', flags='oe', verbose=True, 
#              output='layout_raster')[1].decode())
print(read2_command("r.in.gdal", input='data/in/PreferredAlternativeLayout_2.png', flags='oe', verbose=True, 
             output='layout_raster')[1].decode())


# In[138]:


##print(read2_command("r.composite", red='layout_raster.red',blue='layout_raster.blue',green='layout_raster.green', 
##                     verbose=True, output='layout_raster_')[1].decode())


# In[139]:


##print(read2_command("r.region", map='layout_raster_', verbose=True, 
##                     n=4559000,s=4536000,e=8484000,w=8463000)[1].decode())

print(read2_command("r.region", map='layout_raster.red', verbose=True, 
                    n=4559000,s=4536000,e=8484000,w=8463000)[1].decode())
print(read2_command("r.region", map='layout_raster.green', verbose=True, 
                    n=4559000,s=4536000,e=8484000,w=8463000)[1].decode())
print(read2_command("r.region", map='layout_raster.blue', verbose=True, 
                    n=4559000,s=4536000,e=8484000,w=8463000)[1].decode())


# In[140]:


#print(read2_command("r.info", map='layout_raster.green')[0].decode()) 
##print(read2_command("r.info", map='layout_raster_')[0].decode()) 


# In[141]:


# adjust region to correspond to 'layout_raster_'
##print(read2_command("g.region", rast='layout_raster_')[0].decode()) 
#print(read2_command("g.region", rast='layout_raster_', res=10)[0].decode())  # no difference in image display
print(read2_command("g.region", rast='layout_raster.blue')[0].decode())  # no difference in image display
#print(read2_command("g.region", rast='layout_raster_', zoom='layout_raster_')[0].decode())  # crops map


# In[142]:


# check grass region
print(g.region(flags='p',stdout_=PIPE).outputs.stdout.decode())


# In[143]:


##print(read2_command("r.info", map='layout_raster_')[0].decode()) 


# In[144]:


# view and check topography
get_ipython().system(u'rm map.png                                                                                 #ToDo JK: pythonize')
#read2_command("d.rast", map='layout_raster.red', verbose=True, bgcolor='white')[0]
read2_command("d.rgb", red='layout_raster.red', green='layout_raster.green', blue='layout_raster.blue',
              verbose=True)[1]
#read2_command("d.rast", map='layout_raster_', verbose=True, bgcolor='white')[0]  # scale is wrong
#read2_command("d.rast", map='layout_raster.blue', verbose=True, bgcolor='white')[0]  # works as expected

read2_command("d.grid", size=2000, fontsize=20)[0]

# display stream imported from dxf
gs.run_command('d.vect', map="streams", type="line", color='blue', width=3)


# using "r.region" above results in a blank display of map.png, for d.rgb, r.composite and for single band
# works as expected without "r.region", but origin = 0,0 and scale = pixels
# displays as expected in qgis
# ==> read2_command("g.region", rast='layout_raster_') before 'd.rast' fixes for d.rgb and for single band
# ==> r.composite results in dsplayed image, but map scale is wrong (map does not extend to boundaries)


# In[145]:


Image(filename="map.png")
# image = Image(filename="map.png")
# display(image)


# In[146]:


print(read2_command("r.composite", red='layout_raster.red',blue='layout_raster.blue',green='layout_raster.green', 
                    verbose=True, output='layout_raster_')[1].decode())


# In[147]:


# adjust map position
print(read2_command("r.region", map='layout_raster_', verbose=True, 
                     n='n-100',s='s-100')[1].decode())


# In[148]:


get_ipython().system(u'rm map.png                                                                                 #ToDo JK: pythonize')
read2_command("d.rast", map='layout_raster_', verbose=True, bgcolor='white')[0]  # 

read2_command("d.grid", size=2000, fontsize=20)[0]

# display stream imported from dxf
gs.run_command('d.vect', map="streams", type="line", color='blue', width=3)


# In[149]:


Image(filename="map.png")


# ## check topography comparing differences between raster results

# In[150]:


get_ipython().system(u'r.mapcalc "topog_contours_rast_=(topog_rast_resamp)-(topog_xyz_rast_resamp)"')


# In[151]:


print(read2_command("r.univar", map='topog_contours_rast_')[0].decode()) 


# In[152]:


# view and check topography
get_ipython().system(u'rm map.png                                                                                 #ToDo JK: pythonize')
#read2_command("d.rast", map='topog_contours_rast_', verbose=True, bgcolor='white', flags='n',
#             )[0]
read2_command("d.rast", map='topog_contours_rast_', verbose=True, bgcolor='white', flags='n',
              values='(-10)-(10)')[0]


# In[153]:


read2_command("d.legend", raster='topog_contours_rast_')[1]
#read2_command("d.legend", raster='topog_contours_rast_', range='-10,10')[1]


# In[154]:


Image(filename="map.png")

