#
#
# ThGeoFence : command-line tool for generating GeoHash grids for geo-fencing applications within Thailand, based on administrative boundaries or user-defined coordinates. It is part of the DDPM GeohashGrid system for CBS (Community-Based Surveillance).
#1: Geohash4 (Polygon)
#2: Geohash5 (Polygon)
#3: Geohash6 (Polygon)
#4: Changwat (Multi Polygon)
#5: Amphoe (Multi Polygon)
#
#
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point,Polygon,MultiPolygon
from shapely.wkt import dumps
import simplekml
import argparse

def DumpFence( obj ):
    #import pdb ; pdb.set_trace()
    if 'NAME_1' in obj.keys():
        print(f'Changwat : {obj.NAME_1}' ) 
    if 'NAME_2' in obj.keys():
        print(f'Amphoe : {obj.NAME_2}' ) 
    if obj['geometry'].geom_type == 'MultiPolygon':
        num_geoms = len(obj.geometry.geoms)
        num_pnts = len(obj.geometry.geoms[0].exterior.coords)
        print(f"Multipolygon has : {num_geoms} geoms")
        print(f"Exterior has : {num_pnts} points")
    elif obj['geometry'].geom_type == 'Polygon':
        num_pnts = len(obj.geometry.exterior.coords)
        print(f"Polygon has : {num_pnts} points")

    if 'gh' in obj.keys():
        print(f'Geohash digits : {len(obj.gh)}' ) 
    if 'Center' in obj.keys():
        print( f'Center at {obj.Center} , radius = {obj.Radius_km} km')
    area = obj.geometry.area*111*111
    print(f'Area : {area:.1f} sq.km. ') 
    wkt_string = dumps( obj.geometry, rounding_precision=5)
    print(wkt_string)

def PlotKML(FenceSeries , output_kml):
    geom = FenceSeries.geometry
    if not isinstance(geom, (Polygon, MultiPolygon)):
        raise TypeError("Geometry must be a Polygon or MultiPolygon.")
    ###################################################################
    html = "<![CDATA[<table border='1' cellpadding='3' cellspacing='0'>"
    html += "<tr><th>Key</th><th>Value</th></tr>"
    for key, value in FenceSeries.items():
        html += f"<tr><td>{key}</td><td>{value}</td></tr>"
    html += "</table>]]>"

    kml = simplekml.Kml()
    if isinstance(geom, Polygon):
        _add_polygon_to_kml(kml, geom, name="Polygon")
    elif isinstance(geom, MultiPolygon):
        for i, poly in enumerate(geom.geoms):
            _add_polygon_to_kml(kml, poly, name=f"Polygon {i+1}")
    #import pdb; pdb.set_trace()
    kml.features[0].description = html
    kml.save(output_kml)
    print(f"KML saved to: {output_kml}...")

def _add_polygon_to_kml(kml, polygon, name="Polygon"):
    coords = [(x, y) for x, y in polygon.exterior.coords]
    pol = kml.newpolygon(name=name, outerboundaryis=coords)
    pol.style.polystyle.color = simplekml.Color.changealphaint(150, simplekml.Color.blue)

##################################################################################################
def main():
    parser = argparse.ArgumentParser(description="DDPM GeohashGrid for CBS geo-fencing")
    geo_group = parser.add_mutually_exclusive_group()
    geo_group.add_argument('-p', '--province', type=str, help='Changwat e.g. TH.MH...')
    geo_group.add_argument('-a', '--amphoe', type=str, help='Amphoe e.g. TH.YS.TC...')
    geo_group.add_argument('-g', '--geohash', type=str, help='Geohash 4-6 digits e.g. w4rqpt...')
    geo_group.add_argument('-c', '--circle', type=str, help='lat,lng,radius_km e.g. "13.73837,100.53210,1.5" ...')
    args = parser.parse_args()
    print(args)
    
    if args.province:
        df = gpd.read_file('ThGeohashGrid.gpkg', layer='Changwat')
        Fence = df[df.HASC_1==args.province].iloc[0]
    if args.amphoe:
        df = gpd.read_file('ThGeohashGrid.gpkg', layer='Amphoe')
        Fence = df[df.HASC_2==args.amphoe].iloc[0]
    if args.geohash:
        df = gpd.read_file('ThGeohashGrid.gpkg', layer=f'Geohash{len(args.geohash)}')
        Fence = df[df.gh==args.geohash].iloc[0]
    if args.circle:
        values = list(map(float, args.circle.split(',')))
        buffer = Point(values[1], values[0]).buffer(values[2]/111)  # Convert km to deg
        Fence = gpd.GeoDataFrame({
            'Center':  [ f'{values[1]},{values[0]}' , ] ,
            'Radius_km': [ values[2], ] , 
            'geometry': [ buffer, ] } ).iloc[0]
    DumpFence( Fence )
    PlotKML( Fence,output_kml="TheGeoFence.kml" )


#####################################################################################
#####################################################################################
#####################################################################################
if __name__ == '__main__':
    main()


