# basemapy.py

""" 
prepare a set of raster basemaps for a project
basemaps are suitable for geospatial querying from alignments
basemaps are suitable for importing as layers into qgis
"""


# system configuation
#  move this to a separate json configuration file
project_basedir = '/home/kaelin_joseph/projects/'


# grass setup

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
#gs.set_capture_stderr(True)  #might be Python 2 vs 3 issue (unsure if Python 3 required for this Notebook)


class Basemap:
    """prepares a set of basemaps for project layout"""

    def read_grass(self, *args, **kwargs):
        """execute a grass function with error output """
        kwargs['stdout'] = grass.PIPE
        kwargs['stderr'] = grass.PIPE
        ps = grass.start_command(*args, **kwargs)
        return ps.communicate()

    
    def grass_setup(self, project):
        """define project dir"""
        project_dir=project_basedir + project + '/'
        if os.path.exists(project_dir + 'grassdata') == True:
            os.chdir(project_dir)
        else:
            print('The project dir ' + project_dir +'/grassdata does not yet exist and is required')
            sys.exit(0)
        return(project_dir)

    
    def grass_mapset(self, project, project_dir, crs):
        """open mapset, creating a mapset if mapset location does not exist"""
        location_path = project_dir + '/grassdata/' + project
        startcmd = 'grass' + ' -c ' + crs+' -e ' + location_path
        print(startcmd)
        if os.path.exists(location_path) == False:
            p = subprocess.Popen(startcmd, shell=True,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()
            if p.returncode != 0:
                print >>sys.stderr, 'ERROR: %s' % err
                print >>sys.stderr, 'ERROR: Cannot generate location (%s)' % startcmd
                sys.exit(-1)
            else:
                print('Created location %s' % location_path)
        else:
            print('The location ' + project + 'already exists')
            rcfile = gsetup.init(gisbase,
                                 project_dir + '/grassdata',
                                 project, "PERMANENT")
        return(location_path, rcfile)

    
    def inspect_dxf(self, project_dir, topogDXF):
        """report layers of dxf data file"""
        if os.path.isfile(project_dir + topogDXF) == True:
            out = self.read_grass("v.in.dxf", input=topogDXF,flags='l')
            print(out[0].decode())
        else:
            print(topogDXF + ' does not exist')

            
            
    def import_dxf(self, project_dir, topogDXF, layers_dxf):
        """import dxf data file into grass map topog_vect"""
        if os.path.isfile(project_dir + topogDXF) == True:
            out = self.read_grass("v.in.dxf", input=topogDXF, layers=layers_dxf,  
                                  output='topog_vect')
            print(out[0].decode())
        else:
            print(project_dir + topogDXF + ' does not exist')
        print('import_dxf completed')

        
    def rasterize_vect(self):
        """convert topog_vect to raster DEM"""
        # convert vector topograpy to raste demr
        out = self.read_grass("v.to.rast", input='topog_vect', use='z', 
                              output='topog_rast')
        print(out[0].decode())
        # reample raster dem
        out = self.read_grass("r.resamp.rst", input='topog_rast', 
                              elevation='topog_rast_resamp')
        print(out[0].decode())
        print('rasterixe_vect completed')

        
    def hillslope(self):
        """create a hillslope raster map from raster DEM"""
        out = self.read_grass("r.slope.aspect", elevation='topog_rast_resamp',
                              slope='topog_slope')
        print(out[0].decode())
        print('hillslope completed')


    def relief_map(self):
        """create an shaded relief map from raster DEM"""
        out = self.read_grass("r.relief", input='topog_rast_resamp',
                              output='topog_relief')
        print(out[0].decode())
        out = self.read_grass("r.shade", shade='topog_relief', color='topog_rast_resamp',
                              output='topog_relief_color')
        print(out[0].decode())
        print('shaded relief map completed')

