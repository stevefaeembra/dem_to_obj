DEM2OBJ
=======

>**This is a Python 3 script I use in my Blender work to extract OBJ files from DEMs I've processed in QGIS. I use it for geographic DEMS (like SRTM) and projected DEMS (like OS Open Terrain, and DEFRA lidar)**

You _can_ export OBJ from QGIS, but I've tended to find it is problematic, so I wrote my own.

It's fairly basic, you need to edit some variables. I still need to add command line argument parsing.

# Installation

These are the steps I used. I suggest you use a virtual environment, that way you're not installing any other libraries which clash with other python code on your machine.

This should work on Linux, Mac, or Windows with WSL2.

I store my projects in a directory called **~/workspaces**

```bash
cd ~
cd workspaces
git clone ...
python3 -m venv ./dem_to_obj
cd ./dem_to_obj
source ./bin/activate
python3 -m pip install -r requirements.txt
```


# Settings

| Setting    | Notes |
| -------- | ------- |
| **INPUT_FILE**  | **String**. Path to input file. Any raster file format supported by GDAL/RasterIO should work    |
| **OUTPUT_FILE** | **String**. Path to output file, should end with '.obj'     |
| **IS_WGS84**    | **Boolean**. Set to True if x and y coordinates are in degrees (geographic), or false if x y and z are all in meters or feet (projected). Default is false.    |
| **TRIANGULATE**    | **Boolean**. If True, creates a tri mesh. If False (default) creates quad mesh. Tri meshes use more memory in blender, but may look better, and can be subdivided.    |
| **GLOBAL_SCALE**    | **Float**. Default 100.0. Use this to specify how many meters in the map are one blender unit. This lets you shrink the model down, useful for geographic models which can be massive and need you to mess with camera clip distances. For example, a value of 1000.0 means 1km is one blender unit. A value of 1 means 1 meter is 1 blender unit.  |
| **VERTICAL_EXAGGERATION** | **Float**. Default 1.0. Use this to exaggerate (or diminish) vertical elevations relative to the ground plane. The default means the elevations should be correct in comparison to the x and y axes.   |
| **ENABLE_JITTER** | **Boolean**. Default False. If True, then vertex points are offset by a random amount, but only in x and y axes   |
| **JITTER_AMOUNT** | **Float**. Default 0.25. Only used if ENABLE_JITTER is True. In this case, each vertex is offset into a random point within a radius of 0.25 cells around its real location   |



# Importing into Blender

In Blender, 
- **File > Import > Wavefront** (.obj)
- Change **Forward axis** to Y. 
- Up axis should change to Z.
- Select the .obj file and 'Import Wavefront Object'

It may take a few seconds, depending on the number of faces.

If you want to center the model on the origin, then

- **Object > Set Origin > Origin to Geometry**
- **Alt - G** (Option-G on Mac)

# Troubleshooting

**I imported into Blender but I can't see anything!**

The default is 1 blender unit = 100 meter. For UTM projections that's probably okay, but for WGS84 data (like SRTM) I suggest you shrink the model using the **GLOBAL_SCALE** option. For SRTM a value of 100 or 1000 will usually make the model small enough to see.

**The y axis seems inverted???**

DEMs tend to have the origin in the top left, but projections tend to have the origin in the bottom left.

> The default is to assume this; but for a small number of projections, south is at the top.
> The same can happen if you try to process a PNG

If this happens, you can correct it in blender using 

> S Y -1

to flip the Y axis.

**I see some holes in the mesh, why is that?**

I've seen that when you import an OBJ file in Blender, it seems to apply a modifier which applies a 'smooth by angle'. Remove that modifier, it should fix this.

Also, use 'Shade smooth' and not 'Shade auto smooth'.

Have fun!



