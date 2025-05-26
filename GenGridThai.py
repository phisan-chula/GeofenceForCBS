#
# GenGridThai.py : GenGridThai is a Python script for generating a grid of rectangular tiles that cover a given geographic area using GeoHash precision levels. It supports GeoHash levels with 4, 5, and 6 characters, corresponding to different spatial resolutions. The script outputs all generated grid layers into a suitable format for further geospatial processing or visualization.
# 
# Phisan Santitamnont ( phisan.chula@gmail.com ) 
# Faculty of Engineering , Chulalongkorn Universiyt
#
import pandas as pd
import geopandas as gpd
from shapely.geometry import box
import pygeohash as pgh
import numpy as np
import matplotlib.pyplot as plt

class DDPM_GeoFence:
    GEOH_LEN = {
                4	: (39.1,19.5 ),
                5	: (4.89,4.89 ),
                6   : (1.22,0.61 ),
                }
        # Geohash resolution ~4.89km → ≈0.044° (1 deg ≈ 111 km)
    TOL = 500  # meter tolerane for polygons
    def __init__(self):
        gdfGADM = list()
        for level in range(0,3):
            ThGADM = "/mnt/d/GeoData/GADM/gadm41_THA.gpkg",f"ADM_ADM_{level}"
            gdfGADM.append( gpd.read_file( ThGADM[0], layer=ThGADM[1] ) )
        gdfThai = gdfGADM[0].explode(index_parts=True).reset_index(drop=True).copy()
        import warnings
        warnings.filterwarnings("ignore", category=UserWarning, 
                                message=".*Geometry is in a geographic CRS.*")
        gdfThai['sqkm'] = gdfThai.geometry.area*111*111
        print(f'Before : number of polygons : {len(gdfThai)}...' )
        BIG = 1 ; gdfThai = gdfThai[gdfThai['sqkm'] > 1]
        #import pdb ; pdb.set_trace()
        print(f'After : filter with {BIG} sq.km.,number of polygons : {len(gdfThai)}...' )
        gdfThai = gdfThai.simplify( self.TOL/111_000 , preserve_topology=True )
        self.GADM = gdfGADM
        self.gdfThai = gdfThai
        ########################################################
        self.PlotMap()

    def PlotMap( self ):
        THGRID = "ThGeohashGrid.gpkg"
        for digit in [4,5,6]:
            gdfGH = self.GenerateGrid( DIGITS=digit )
            gdfGH.to_file( THGRID, layer=f"Geohash{digit}", driver="GPKG")
            print(f'PlotMap {THGRID} layer=Geohash{digit}...' )
        print(f'PlotMap {THGRID} layer=Changwat|Amphoe...' )
        for i,admin in [ (1,"Changwat"), (2,"Amphoe") ]:
            gdf = self.GADM[i].copy()
            gdf['geometry']  = self.GADM[i].simplify( self.TOL/111_000, preserve_topology=True )
            gdf.to_file( THGRID, layer=admin, driver="GPKG")
            #import pdb; pdb.set_trace()

    def GenerateGrid(self, DIGITS ):
        minx, miny, maxx, maxy = self.gdfThai.total_bounds
        stepx,stepy = np.array(self.GEOH_LEN[DIGITS]) / 111
        lats = np.arange(miny, maxy, stepy)
        lons = np.arange(minx, maxx, stepx)
        # Collect valid geohashes
        ghs = list()
        CNT=-1
        for lat in lats:
            for lon in lons:
                gh = pgh.encode(lat, lon, precision=DIGITS)
                lat_c, lon_c, lat_err, lon_err = pgh.decode_exactly(gh)
                bbox = box(lon_c - lon_err, lat_c - lat_err, 
                           lon_c + lon_err, lat_c + lat_err)
                if self.gdfThai.intersects(bbox).any():
                    ghs.append([gh,gh[-1],bbox])
                    if CNT==0: CNT=CNT-1
        dfGH = pd.DataFrame( ghs, columns=[f'gh','gh_last', 'geometry'] )
        duplicates = dfGH[dfGH[f'gh'].duplicated()]
        print('Dplicated : \n', duplicates)
        gdf = gpd.GeoDataFrame( dfGH, crs=4326, geometry=dfGH.geometry )
        return gdf

##################################################################################
# Load GADM Thailand boundary (Level 0 - national)

geofence = DDPM_GeoFence()
