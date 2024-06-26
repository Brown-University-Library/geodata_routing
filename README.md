# Plot Routes with OpenRoutingService

These scripts allow you to plot network routes between CSV files with origins and destinations that contain coordinates using the OpenRoutingService python module https://pypi.org/project/openrouteservice/, The script creates a point shapefile of origins and destinations, and generates a line shapefile that contains data about the origin and destination points, travel time, and travel distance. There's a regular python script and an Ipython notebook; they function identically, except that the script generates a basic plot while the notebook plots the output on a Folium map. To use:

1. Request an API key from the OpenRouteService at https://openrouteservice.org/

2. Create a text file called ors_key.txt in the root folder (where the scripts are stored), and paste the key into the file

3. Download third party modules (i.e. pip install) that the scripts require: openrouteservice, pandas, geopandas, shapely, and folium

4. Origins and destinations must be stored in separate CSV files in the input folder, and must contain: a unique ID, name, longitude, and latitude in the WGS 84 coordinate system

5. Modify the scripts to specify a name for the output file, the desired outcomes for the routes (travel mode, distance units, and preferred routes), positions in the CSV files that contain the ID, name, and coordinate data, and the names of the origin and destination input files

![](route_example.png)
