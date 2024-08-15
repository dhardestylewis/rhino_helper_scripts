import rhinoscriptsyntax as rs
import Rhino.Geometry as rg
import System.Drawing.Color as Color
import csv
import json
import math

# Input parameters
csv_path = r"C:\Users\dhl\Downloads\updated_merged_gdf_r1_r5.csv"

# Function to read CSV and extract data
def read_csv(file_path):
    data = []
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data

# Function to create a spectral colormap
def spectral_colormap(t):
    # Define control points for the spectral colormap
    colors = [
        (0.0, (0.6, 0.0, 0.0)),  # Dark Red
        (0.25, (0.9, 0.4, 0.0)),  # Orange
        (0.5, (1.0, 1.0, 0.2)),  # Yellow
        (0.75, (0.0, 0.6, 1.0)),  # Light Blue
        (1.0, (0.0, 0.0, 0.4))  # Dark Blue
    ]
    
    # Find the two control points that t falls between
    for i in range(len(colors) - 1):
        t1, c1 = colors[i]
        t2, c2 = colors[i+1]
        if t1 <= t <= t2:
            # Interpolate between the two colors
            f = (t - t1) / (t2 - t1)
            r = c1[0] * (1-f) + c2[0] * f
            g = c1[1] * (1-f) + c2[1] * f
            b = c1[2] * (1-f) + c2[2] * f
            return Color.FromArgb(int(r*255), int(g*255), int(b*255))
    
    # If t is out of range, return the last color
    return Color.FromArgb(int(colors[-1][1][0]*255), int(colors[-1][1][1]*255), int(colors[-1][1][2]*255))

# Function to find nearest point
def find_nearest_point(target_point, data_points):
    nearest = min(data_points, key=lambda p: rs.Distance(target_point, p['point']))
    return nearest

# Function to safely extract coordinates from geometry
def extract_coordinates(geometry_str):
    try:
        geom = json.loads(geometry_str)
        if geom['type'] == 'Point':
            return geom['coordinates']
        elif geom['type'] == 'Polygon':
            # For polygons, use the first point of the exterior ring
            return geom['coordinates'][0][0]
        else:
            print("Unsupported geometry type: " + geom['type'])
            return None
    except json.JSONDecodeError:
        print("Failed to parse geometry: " + geometry_str)
        return None
    except KeyError:
        print("Invalid geometry structure: " + geometry_str)
        return None

# Function to get a representative point for an object
def get_representative_point(obj):
    # Try to get centroid
    centroid = rs.SurfaceAreaCentroid(obj)
    if centroid:
        return centroid[0]
    
    # If centroid fails, try bounding box center
    bbox = rs.BoundingBox(obj)
    if bbox:
        return rs.PointAdd(bbox[0], rs.PointScale(rs.PointSubtract(bbox[6], bbox[0]), 0.5))
    
    # If bounding box fails, try object center
    center = rs.ObjectCenterPoint(obj)
    if center:
        return center
    
    # If all else fails, return None
    return None

# Main script
data = read_csv(csv_path)

# Extract coordinates and mean values
valid_data = []
for row in data:
    coords = extract_coordinates(row['geometry'])
    if coords:
        row['point'] = rs.CreatePoint(coords[0], coords[1], 0)  # Assuming 2D points
        try:
            row['equity_multiple_mean'] = float(row['equity_multiple_mean'])
            valid_data.append(row)
        except ValueError:
            print("Invalid equity_multiple_mean value: " + row['equity_multiple_mean'])

if not valid_data:
    print("No valid data found. Please check your CSV file.")
    import sys
    sys.exit()

# Get all buildings from the Building_Facade layer
building_objects = rs.ObjectsByLayer("Building_Facade")

if not building_objects:
    print("No objects found in the Building_Facade layer.")
    import sys
    sys.exit()

# Process each building and collect values
building_values = []
for obj in building_objects:
    rep_point = get_representative_point(obj)
    if rep_point is None:
        print("Failed to get representative point for object: " + str(obj))
        print("Object type: " + rs.ObjectType(obj))
        continue
    
    nearest_data = find_nearest_point(rep_point, valid_data)
    mean_value = nearest_data['equity_multiple_mean']
    building_values.append(mean_value)

# Calculate min and max values from the buildings we're actually processing
min_value = min(building_values)
max_value = max(building_values)

# Process each building again to apply colors
for obj, value in zip(building_objects, building_values):
    # Normalize the value
    t = (value - min_value) / (max_value - min_value) if max_value != min_value else 0.5
    
    # Get color from spectral colormap
    color = spectral_colormap(t)
    
    # Apply the color to the building in Rhino
    rs.ObjectColor(obj, color)

    rep_point = get_representative_point(obj)
    print("Colored building at ({0}, {1}, {2}) with value {3}".format(rep_point.X, rep_point.Y, rep_point.Z, value))

# Output
print("Buildings colored based on equity multiple means")
print("Value range: {0} to {1}".format(min_value, max_value))