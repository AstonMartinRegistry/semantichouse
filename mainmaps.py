import requests
import json
from math import radians

def calculate_area(coordinates):
    """
    Calculate the area of a polygon using the Shoelace formula (Surveyor's formula)
    Returns area in square meters
    """
    if len(coordinates) < 3:
        return 0
    
    # Convert coordinates to radians
    coords_rad = [(radians(lat), radians(lon)) for lat, lon in coordinates]
    
    # Calculate area using the Shoelace formula
    area = 0
    for i in range(len(coords_rad)):
        j = (i + 1) % len(coords_rad)
        area += coords_rad[i][1] * coords_rad[j][0]
        area -= coords_rad[j][1] * coords_rad[i][0]
    
    area = abs(area) / 2
    
    # Convert to square meters (approximate)
    # This is a rough approximation - for more accuracy, you'd need to use a proper geodesic calculation
    R = 6371000  # Earth's radius in meters
    area_meters = area * R * R
    
    return area_meters

# Define the bounding box coordinates
south_lat = 37.41155
west_lon = -122.17237
north_lat = 37.41949
east_lon = -122.16488

# Construct the Overpass API query for buildings
overpass_url = "https://overpass-api.de/api/interpreter"
overpass_query = f"""
[out:json][timeout:25];
(
  way["building"]({south_lat},{west_lon},{north_lat},{east_lon});
  >;
);
out body;
"""

# Send the request to the Overpass API
response = requests.post(overpass_url, data=overpass_query)

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    data = response.json()
    
    # Create a dictionary to store node coordinates
    node_coords = {}
    
    # First, store all node coordinates
    for element in data['elements']:
        if element['type'] == 'node':
            node_coords[element['id']] = (element['lat'], element['lon'])
    
    # Create a list to store the building information
    building_info = []
    
    # Process each building way
    for element in data['elements']:
        if element['type'] == 'way' and 'building' in element.get('tags', {}):
            # Get the coordinates of all nodes in this building
            building_nodes = [node_coords[node_id] for node_id in element['nodes'] if node_id in node_coords]
            
            if building_nodes:
                # Calculate the area of the building
                area_sq_meters = calculate_area(building_nodes)
                area_sq_feet = area_sq_meters * 10.7639  # Convert square meters to square feet
                
                # Skip buildings smaller than 200 square feet
                if area_sq_feet < 900:
                    continue
                
                # Calculate center point (average of all coordinates)
                center_lat = sum(node[0] for node in building_nodes) / len(building_nodes)
                center_lon = sum(node[1] for node in building_nodes) / len(building_nodes)
                
                # Create a dictionary for this building
                building = {
                    'id': element['id'],
                    'center': {
                        'lat': center_lat,
                        'lon': center_lon
                    },
                    'area_sq_feet': round(area_sq_feet, 2)  # Round to 2 decimal places
                }

                # Add the building to the list
                building_info.append(building)
    
    # Save the building information to a JSON file
    with open('building_info.json', 'w') as f:
        json.dump(building_info, f, indent=2)
    
    print(f"Successfully processed {len(building_info)} buildings")
    print("Building information saved to 'building_info.json'")

else:
    print(f"Error: {response.status_code}")
    print(response.text)