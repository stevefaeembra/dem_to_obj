'''
DEM to OBJ converter using GDAL
Import into blender as Y forward, Z up
scale is 1m = 1 blender unit, so may need to set camera clip so you can even see 
the end results.
'''

from importlib.resources import files
import rasterio
import random

# change input and output files

INPUT_FILE = './dem.tif'
OUTPUT_FILE = './dem.obj'

# If True, we assume X and Y are in degrees, but Z in meters
# this means we need to scale the X and Y by a large factor to ensure
# a correct vertical exaggeration

IS_WGS84 = False

# if set, use triangular faces 
# this gives twice as many faces, which can use much more memory in blender
# but can improve the rendering in some cases, and enables subdivision surface
# to be applied

TRIANGULATE = False 

# global scale. Number of real world meters per blender unit of scale
# use 1 for 1 bu = 1m, 1000 for 1 bu = 1km etc.
# we use reciprocal, so 1000 = 1km per blender unit
# for WGS84, suggest using 1000. For projected coords, choose as you see fit!

GLOBAL_SCALE = 100.0

# z scale. vertical exaggeration. 1=Scale Height

VERTICAL_EXAGGERATION = 1.0

# xy jitter. Randomize by a fraction of a pixel e.g. 0.05 = 1/20th cell size
# this is slower. Also, keep value small (e.g. less than 0.3)

ENABLE_JITTER = False
JITTER_AMOUNT = 0.1

# set arbitrary sea level. Elevations below this are set to this
# set to zero to remove bathymetry.

MIN_ELEVATION = 0.0

def getFileStats(filename):
    '''
    get file metadata - extents, locations, pixel size
    '''
    print(f'Reading image metadata from {filename}')
    dataset = rasterio.open(filename)
    width = dataset.width
    height = dataset.height
    bounds = dataset.bounds
    xcellsize = (dataset.bounds.right - dataset.bounds.left)/dataset.width
    ycellsize = (dataset.bounds.top - dataset.bounds.bottom)/dataset.height
    
    return {
        'filename': filename,
        'width': width, # width in cells
        'height': height, # height in cells
        
        # all the following need to be rescalable if using geographic coords
        
        'bounds': { # bounds (may be degrees or meters)
            'left': bounds.left,
            'right': bounds.right,
            'top': bounds.top,
            'bottom': bounds.bottom
        },
        'xcellsize_m': xcellsize,
        'ycellsize_m': ycellsize,
        'widthtotal_m': xcellsize*width,
        'heightotal_m': ycellsize*height
    }

def adjustScales(metadata, useWGS84=True):
    '''
    Adjust x and y scales to make sure degrees converted to meters
    Need to really use latitude in this, but defaulting to 1:110K for now
    '''
    print('Adjusting scales, if needed')
    WGS84_SCALE = 110000.0
    if (useWGS84):
        metadata['xcellsize_m'] *= WGS84_SCALE
        metadata['ycellsize_m'] *= WGS84_SCALE
    return metadata

def readRasterBand(metadata, band=1):
    '''
    Read raster cell data into a 2D array
    '''
    print(f'Reading in raster data from {metadata["filename"]}')
    dataset = rasterio.open(metadata['filename'])
    banddata = dataset.read(1)
    elevations = {}
    gs = 1.0 / GLOBAL_SCALE
    if (not ENABLE_JITTER):
        # no jitter, we can optimise slightly
        for row in range(0, metadata['height']):
            y = -row * metadata['ycellsize_m'] * gs
            for col in range(0, metadata['width']):
                x = col * metadata['xcellsize_m'] * gs
                el = float(banddata[row][col]) 
                if el <= MIN_ELEVATION:
                    el = MIN_ELEVATION
                z = el * gs * VERTICAL_EXAGGERATION
                elevations[(col,row)] = (x,y,z) 
    if (ENABLE_JITTER):
        # jitter is a bit slower as each vertex is offset a random amount
        jitter = JITTER_AMOUNT*metadata['ycellsize_m']*2.0
        halfjitter = jitter*0.5
        for row in range(0, metadata['height']):
            for col in range(0, metadata['width']):
                y = ((-row * metadata['ycellsize_m'])-halfjitter+(random.random()*jitter)) * gs
                x = ((col * metadata['xcellsize_m'])-halfjitter+(random.random()*jitter)) * gs
                z = float(banddata[row][col]) * gs * VERTICAL_EXAGGERATION
                elevations[(col,row)] = (x,y,z)
    return elevations

def showSettings(metadata):
    '''
    Show metadata settings
    '''
    print(f'Source image {metadata["filename"]}')
    print(f'Image is {metadata["width"]} by {metadata["height"]}')
    print(f'Cell size in m is {metadata["xcellsize_m"]}')
    if (ENABLE_JITTER):
        print(f'Jittering vertices by a factor of ${JITTER_AMOUNT}')
    if (TRIANGULATE):
        print('Output a tri mesh')
    else:
        print('Output a quad mesh')
    print(f'Global scale, {GLOBAL_SCALE}m is one Blender unit')
    print(f'Vertical exaggeration factor is {VERTICAL_EXAGGERATION}')

'''
Processing starts
'''
print('='*80)
print('DEM_2_OBJ Running')
metadata = getFileStats(INPUT_FILE)
metadata = adjustScales(metadata, 
                        IS_WGS84)
showSettings(metadata)
data = readRasterBand(metadata)


'''
find the vertices, in scan order
each vertex is used only once, although it may appear 
in up to 4 (mesh) or 8 (tri) faces
'''

output = []

print('Generating vertices')
vcount = 0
output.append('#verts')
for row in range(0, metadata['height']):
    for col in range(0, metadata['width']):
        key = (col,row)
        x,y,z = data[key]
        output.append(f'v {x} {y} {z}')
        vcount += 1
print(f'Generated {vcount} vertices')
        
'''
generate faces
'''
print ('Generating faces')
output.append('#faces')
width = metadata['width']
height = metadata['height']
fcount = 0
for row in range(0, metadata['height']-1):
    top = row*width
    bottom = (row+1)*width
    for col in range(0, metadata['width']-1):
        if TRIANGULATE:
            verts = [top+col,bottom+col,bottom+col+1,top+col+1]
            output.append(f'f {1+verts[0]} {1+verts[1]} {1+verts[2]} {1+verts[0]}')
            output.append(f'f {1+verts[0]} {1+verts[2]} {1+verts[3]} {1+verts[0]}')
            fcount += 2
        else:
            verts = [top+col,bottom+col,bottom+col+1,top+col+1]
            output.append(f'f {1+verts[0]} {1+verts[1]} {1+verts[2]} {1+verts[3]} {1+verts[0]}')
            fcount += 1
print(f'Generated {fcount} faces')     


'''
dump the file
'''

print(f'Writing to OBJ file {OUTPUT_FILE}')
with open(OUTPUT_FILE,'w') as fo:
    for line in output:
        fo.write(f'{line}\n')

print('Job Complete')
print('='*80)
