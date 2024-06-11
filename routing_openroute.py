# -*- coding: utf-8 -*-
"""
Calculate routes and distances from origins and destinations stored 
in separate CSV files with coordinates, and generate shapefiles 
and basic plot. CSV must contain a header row, with attributes that
include a unique id, name, longitude, and latitude in WGS 84

Using https://openrouteservice.org/ and https://pypi.org/project/openrouteservice/
Basic examples: https://openrouteservice-py.readthedocs.io/en/latest/

Frank Donnelly / Head GIS and Data Services / Brown University Library
May 31, 2024 | Revised June 11, 2024
"""

import openrouteservice, os, csv, pandas as pd, geopandas as gpd
from shapely.geometry import shape
from openrouteservice.directions import directions
from openrouteservice import convert
from datetime import date
from time import sleep

# VARIABLES
# general description, used in output file
routename='scili_to_libs'
# transit modes: [“driving-car”, “driving-hgv”, “foot-walking”, “foot-hiking”, “cycling-regular”, “cycling-road”,”cycling-mountain”, “cycling-electric”,]
tmode='driving-car'
# distance units: [“m”, “km”, “mi”]
dunits='mi'
# route preference: [“fastest, “shortest”, “recommended”]
rpref='fastest'

# Column positions in csv files that contain: unique ID, name, longitude, latitude
# Origin file
ogn_id=0
ogn_name=1
ogn_long=2
ogn_lat=3
# Destination file
d_id=0
d_name=1
d_long=2
d_lat=3

# INPUTS and OUTPUTS
today=str(date.today()).replace('-','_')

keyfile='ors_key.txt'
origin_file=os.path.join('input','origins.csv') #CSV must have header row
dest_file=os.path.join('input','destinations.csv') #CSV must have header row
route_file=routename+'_'+tmode+'_'+rpref+'_'+today+'.shp'
out_file=os.path.join('output',route_file)
out_origin=os.path.join('output',os.path.basename(origin_file).split('.')[0]+'_'+today+'.shp')
out_dest=os.path.join('output',os.path.basename(dest_file).split('.')[0]+'_'+today+'.shp')

# For reading origin and dest files
def file_reader(infile,outlist):
    with open(infile,'r') as f:
        reader = csv.reader(f)    
        for row in reader:
            rec = [i.strip() for i in row]
            outlist.append(rec)
            
# For converting origins and destinations to geodataframes            
def coords_to_gdf(data_list,long,lat,export):
    """Provide: list of places that includes a header row,
    positions in list that have longitude and latitude, and
    path for output file.
    """
    df = pd.DataFrame(data_list[1:], columns=data_list[0])
    longcol=data_list[0][long]
    latcol=data_list[0][lat]
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df[longcol], df[latcol]), crs='EPSG:4326')
    gdf.to_file(export,index=True)
    print('Wrote shapefile',export,'\n')
    return(gdf)
      
origins=[]
dest=[]
file_reader(origin_file,origins)
file_reader(dest_file,dest)

# Read api key in from file
with open(keyfile) as key:
    api_key=key.read().strip()

route_count=0
route_list=[]
# Column header for route output file:
header=['ogn_id','ogn_name','dest_id','dest_name','distance','travtime','route']

# API CALL
for ogn in origins[1:]:
    for d in dest[1:]:
        try:
            coords=((ogn[ogn_long],ogn[ogn_lat]),(d[d_long],d[d_lat]))
            client = openrouteservice.Client(key=api_key) 
            # Take the returned object, save into nested dicts:
            results = directions(client, coords, 
                                profile=tmode,instructions=False, preference=rpref,units=dunits)
            dist = results['routes'][0]['summary']['distance']
            travtime=results['routes'][0]['summary']['duration']/60 # Get minutes
            encoded_geom = results['routes'][0]['geometry']
            decoded_geom = convert.decode_polyline(encoded_geom) #convert from binary to txt
            wkt_geom=shape(decoded_geom).wkt #convert from json polyline to wkt
            route=[ogn[ogn_id],ogn[ogn_name],d[d_id],d[d_name],dist,travtime,wkt_geom]
            route_list.append(route)
            route_count=route_count+1
            if route_count%40==0: # API limit is 40 requests per minute
                print('Pausing 1 minute, processed',route_count,'records...')
                sleep(60)
        except Exception as e:
            print(str(e))
            
api_key=''
print('Plotted',route_count,'routes...' )

# Create shapefiles for routes
df = pd.DataFrame(route_list, columns=header)
gdf = gpd.GeoDataFrame(df, geometry=gpd.GeoSeries.from_wkt(df["route"]),crs = 'EPSG:4326')
gdf.drop(['route'],axis=1,inplace=True) # drop the wkt text
gdf.to_file(out_file,index=True)
print('Wrote route shapefile to:',out_file,'\n')

# Create shapefiles for origins and destinations
ogdf=coords_to_gdf(origins,ogn_long,ogn_lat,out_origin)
dgdf=coords_to_gdf(dest,d_long,d_lat,out_dest)

# Plot
base=gdf.plot(column="dest_id", kind='geo',cmap="Set1")
ogdf.plot(ax=base, marker='o',color='black')
dgdf.plot(ax=base, marker='x', color='red');
