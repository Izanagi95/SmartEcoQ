import json
import random

def add_queue_to_geojson(input_file, output_file):
    """
    Add a 'queue' key with a random value between 0 and 20 to each feature in a GeoJSON file.
    
    Args:
        input_file (str): Path to the input GeoJSON file
        output_file (str): Path to the output GeoJSON file
    """
    # Read the input GeoJSON file
    with open(input_file, 'r') as f:
        geojson_data = json.load(f)
    
    # Recursively add queue to features
    for feature in geojson_data['features']:
        # Add queue to each feature's properties
        feature['properties']['queue'] = random.randint(0, 20)
    
    # Write the modified GeoJSON to the output file
    with open(output_file, 'w') as f:
        json.dump(geojson_data, f, indent=2)
    
    print(f"Successfully added queue to {len(geojson_data['features'])} features.")

def main():
    # Specify input and output file paths
    input_file = 'servizi_pubblici_lucca.geojson'
    output_file = 'servizi_pubblici_lucca+queue.geojson'
    
    # Call the function to add queue
    add_queue_to_geojson(input_file, output_file)

if __name__ == '__main__':
    main()