""" 
basemapy.py - Basemap Module
    prepares a set of raster basemaps for a project
       basemaps are suitable for geospatial querying from alignments
       basemaps are suitable for importing as layers into qgis

Usage:
    1. map = Basemap(project)                              instantiate a project basemap
    2. map.inspect_dxf(project_dir, topogDXF)              examine DXF data containing topography
    3. map.import_dxf(project_dir, topogDXF, layers_dxf)   import DXF data layer containing topography
    4. map.rasterize_vect_lines                            rasterize vector data - sparse data, irregular bounds
       OR map.rasterize_vect_faces                                               - dense date, regular bounds
       OR map.rasterize_vect_using_points                                        - sparse data, regular bounds
    5. map.hillslope()                                     create a hillslope raster map
    6. map.relief_map()                                    create a shaded relief map
    7. map.hydrology_map()                                 create a hydrologic map 
    8. map.layout_map(layoutPDF)                           import PNG image with project layout

Optional function parameters: 
    all grass functions (except map)
        dbg=0 in function parameters -> show error messages only
        dbg=1 in function parameters -> show std output from grass routines (verbose)

    def rasterize_vect_lines
        ew_res=10, ns_res=10              -> change resolution as required
    def rasterize_vect_faces
        ew_res=10, ns_res=10, overlap=3   -> change resolution as required
"""


# system configuation
#   move this to a separate json configuration file                                                     #JK Todo
project_basedir = '/home/kaelin_joseph/projects/'


# grass setup
#   setup is put into global namespace to enable grass functionality in a Jupyter Notebook importing this module
#   putting setup into this module simplifies maintenance of the grass setup

# set up Python for GRASS GIS
import os
import sys
import subprocess
import os.path
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
#gs.set_capture_stderr(True)  #might be Python 2 vs 3 issue


class Basemap():
    """prepares a set of basemaps for project layout"""

    def __init__(self, project):
        self.project = project

        #define project dir
        project_dir = project_basedir + project + '/'
        self.project_dir = project_dir
        if os.path.exists(project_dir + 'grassdata') == True:
            os.chdir(project_dir)
        else:
            raise SystemExit('The project dir ' + project_dir +'/grassdata does not yet exist and is required')
            # handle error with os.mkdir(path)                                                          #JK ToDo
        
        print('project: ' + project + '\n')
        print(__doc__)
        
        
    def read_grass(self, *args, **kwargs):
        """execute a grass function with error output """
        kwargs['stdout'] = grass.PIPE
        kwargs['stderr'] = grass.PIPE
        ps = grass.start_command(*args, **kwargs)
        # returns a tuple (stderr,stdout)
        return ps.communicate()
    

    def grass_mapset(self, crs):
        """open mapset, creating a mapset if mapset location does not exist"""
        location_path = self.project_dir + '/grassdata/' + self.project
        startcmd = 'grass' + ' -c ' + crs+' -e ' + location_path
        print(startcmd)

        if os.path.exists(location_path) == False:
            p = subprocess.Popen(startcmd, shell=True,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()
            if p.returncode != 0:
                print >>sys.stderr, 'ERROR: %s' % err
                print >>sys.stderr, 'ERROR: Cannot generate location (%s)' % startcmd
                sys.exit(-1)  #quits program
            else:
                print('Created location %s' % location_path)
        else:
            print('The location ' + self.project + ' already exists')

        rcfile = gsetup.init(gisbase,
                             self.project_dir + '/grassdata',
                             self.project, "PERMANENT")

        return(location_path, rcfile)

    
    def inspect_dxf(self, topogDXF, dbg=0):
        """report layers of dxf data file"""
        if os.path.isfile(self.project_dir + topogDXF) == True:
            out = self.read_grass("v.in.dxf", input=topogDXF,flags='l')
            print(out[dbg].decode())
        else:
            print(topogDXF + ' does not exist')
            
            
    def import_dxf(self, topogDXF, layers_dxf, dbg=0):
        """import DXF data file to grass map topog_vect"""
        
        # check that DXF data file exists and import if it exists
        if os.path.isfile(self.project_dir + topogDXF) == True:
            out = self.read_grass("v.in.dxf", input=topogDXF, layers=layers_dxf,  
                                  output='topog_vect')
            print(out[dbg].decode())
        else:
            print(self.project_dir + topogDXF + ' does not exist')
            
        # rebuild topog_vect topogology as good practice
        self.read_grass("v.build", map='topog_vect')
        print('import_dxf completed')

        
    def rasterize_vect_lines(self, ew_res=10, ns_res=10, dbg=0):
        """convert vector topograpy using contour lines, polylines to raste dem"""

        # convert topog_vect to raster DEM
        out = self.read_grass("v.to.rast", input='topog_vect', use='z', 
                              layer='-1', output='topog_rast')
        print(out[dbg].decode())

        # reample raster dem
        out = self.read_grass("r.resamp.rst", input='topog_rast', ew_res=ew_res, ns_res=ns_res, 
                              elevation='topog_rast_resamp')
        print(out[dbg].decode())
        print('rasterize_vect_lines completed')


    def rasterize_vect_faces(self, ew_res=10, ns_res=10, overlap=3, dbg=0):
        """convert vector topograpy using faces (dxf 3dfaces) to raste dem"""

        # convert vector feature type from face to line
        out = self.read_grass("v.type", input='topog_vect', layer=-1, from_type='face',
                              to_type='line', output='topog_vect_lines')
        print(out[dbg].decode())
        print('v.type complete \n')
        
        # convert topog_vect to raster DEM
        out = self.read_grass("v.to.rast", input='topog_vect_lines', use='z', 
                              layer='-1', output='topog_rast')
        print(out[dbg].decode())

        # resample raster dem
        out = self.read_grass("r.resamp.rst", input='topog_rast', ew_res=ew_res, ns_res=ns_res, 
                              overlap=overlap, elevation='topog_rast_resamp')
        print(out[dbg].decode())
        print('rasterize_vect_faces completed')


    def rasterize_vect_using_points(self, npoints=12, power=2, dbg=0):
        """convert vector topograpy using extracted points to raster dem"""

        # extract points from vector topography
        out = self.read_grass("v.to.points", input='topog_vect', layer=-1, output='topog_vect_points')
        print(out[dbg].decode())
        
        # convert topog_vect_points to raster DEM using v.surf.idw (inverse distance weighting interpolation)
        out = self.read_grass("v.surf.idw", input='topog_vect_points', 
                              layer='-1', output='topog_rast_resamp', npoints=npoints, power=power)
        print(out[dbg].decode())
        print('rasterize_vect_using_points completed')
                
        
    def hillslope(self, dbg=0):
        """create a hillslope raster map from raster DEM"""
        out = self.read_grass("r.slope.aspect", elevation='topog_rast_resamp',
                              slope='topog_slope')
        print(out[dbg].decode())
        print('hillslope completed')


    def relief_map(self, dbg=0):
        """create an shaded relief map from raster DEM"""
        out = self.read_grass("r.relief", input='topog_rast_resamp',
                              output='topog_relief')
        print(out[dbg].decode())

        out = self.read_grass("r.shade", shade='topog_relief', color='topog_rast_resamp',
                              output='topog_relief_color')
        print(out[dbg].decode())
        print('shaded relief map completed')


    def hydrology_map(self, dbg=0):
        """create a hydrologic map from raster DEM"""

        # determine watershed basins using a medium threshold size
        out = self.read_grass("r.watershed", elevation='topog_rast_resamp',
                              basin='topog_basin', threshold=100000)
        print(out[dbg].decode())

        # determine watercourses and accumulations using a low threshold size
        out = self.read_grass("r.watershed", elevation='topog_rast_resamp',
                              accumulation='topog_accum',
                              stream='topog_stream', threshold=1000)
        print(out[dbg].decode())

        # filter accumulations (number of cells that drain through each cell) for > 100 and set these = 1
        out = self.read_grass("r.mapcalc",
                              expression='topog_accum_filtered = if(abs(topog_accum) > 1000, 1, null())')
        print(out[dbg].decode())

        # vectorize watershed basin raster data
        out = self.read_grass("r.to.vect", input='topog_basin', 
                              output='topog_basin_vect', type='area', flags='s')
        print(out[dbg].decode())

        # clean raster data of streamcourses in preparation for converting to vector data
        out = self.read_grass("r.thin", input='topog_accum_filtered',
                              output='topog_accum_thin')
        print(out[dbg].decode())

        # vectorize streamcourses raster data
        out = self.read_grass("r.to.vect", input="topog_accum_thin", 
                              out='topog_accum_vect', type='line', flags='s')
        print(out[dbg].decode())
        print('hydrologic map completed')
        

    def layout_map(self, layoutPDF, dbg=0):
        """create a project layout map (raster image) from a PNG image"""

        # check that PNG image file exists and import if it exists        
        if os.path.isfile(self.project_dir + layoutPDF) == True:
            out = self.read_grass("r.in.gdal", input=layoutPDF,  
                                  flags='o', verbose=True, output='layout_rast')
            print(out[dbg].decode())
        else:
            print(self.project_dir + layoutPDF + ' does not exist')

        # set boundary coordinates of layout image raster
        # flag='c' sets region from current region
        out = self.read_grass("r.region", map='layout_rast.red', flags='c', verbose=True)
        print(out[dbg].decode())
        out = self.read_grass("r.region", map='layout_rast.blue', flags='c', verbose=True)
        print(out[dbg].decode())
        out = self.read_grass("r.region", map='layout_rast.green', flags='c', verbose=True)
        print(out[dbg].decode())
            
        # produce a composite image of layout_raster rgb components
        out = self.read_grass("r.composite",
                              red='layout_rast.red', blue='layout_rast.blue', green='layout_rast.green',
                              verbose=True, output='layout_rast_rgb')
        print(out[dbg].decode())
        print('layout map completed')


