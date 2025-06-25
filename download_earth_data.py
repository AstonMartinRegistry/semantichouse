import json
import os
import requests
from datetime import datetime
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_satellite_image(lat, lon, zoom=20, size="500x500"):
    """
    Get satellite imagery from Google Maps Static API
    """
    # Your Google Maps API key should be in .env file
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    
    if not api_key:
        raise ValueError("GOOGLE_MAPS_API_KEY not found in environment variables")
    
    # Construct the URL for the Static Maps API
    url = f"https://maps.googleapis.com/maps/api/staticmap"
    
    params = {
        'center': f"{lat},{lon}",
        'zoom': zoom,
        'size': size,
        'maptype': 'satellite',
        'key': api_key
    }
    
    response = requests.get(url, params=params)
    return response

def download_all_buildings():
    # Create output directory if it doesn't exist
    if not os.path.exists('building_images'):
        os.makedirs('building_images')
    
    # Read building data
    with open('building_info.json', 'r') as f:
        buildings = json.load(f)
    
    total_buildings = len(buildings)
    batch_size = 50
    total_batches = (total_buildings + batch_size - 1) // batch_size
    
    print(f"Found {total_buildings} buildings to process in {total_batches} batches")
    
    # Process buildings in batches
    for batch_num in range(total_batches):
        start_idx = batch_num * batch_size
        end_idx = min((batch_num + 1) * batch_size, total_buildings)
        current_batch = buildings[start_idx:end_idx]
        
        print(f"\nProcessing batch {batch_num + 1}/{total_batches} (buildings {start_idx + 1}-{end_idx})")
        
        # Process each building in the current batch
        for building in current_batch:
            building_id = building['id']
            lat = building['center']['lat']
            lon = building['center']['lon']
            
            try:
                response = get_satellite_image(lat, lon)
                
                if response.status_code == 200:
                    image_path = os.path.join('building_images', f'building_{building_id}.png')
                    with open(image_path, 'wb') as f:
                        f.write(response.content)
                else:
                    print(f"✗ Failed to download building {building_id}: {response.status_code}")
                
            except Exception as e:
                print(f"✗ Error processing building {building_id}: {str(e)}")
        
        # Add delay between batches
        if batch_num < total_batches - 1:  # Don't delay after the last batch
            print("Waiting 2 seconds before next batch...")
            time.sleep(2)
    
    print("\nDownload complete!")

if __name__ == "__main__":
    download_all_buildings() 