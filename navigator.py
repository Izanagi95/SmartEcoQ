import streamlit as st
import os
import json
import pandas as pd
import folium
from streamlit_folium import st_folium
import requests
import polyline
from dotenv import load_dotenv
import geocoder
from geopy.geocoders import Nominatim
from geopy.exc import GeopyError
import time


load_dotenv()
location_cache = {}


def get_current_coordinates_using_IP():
    g = geocoder.ip('me')  # Detects your current IP
    if g.latlng:
        return g.latlng  # Returns [latitude, longitude]
    else:
        return "Could not determine location"

def get_street_from_coordinates(coordinates):
    geolocator = Nominatim(user_agent="SmartEcoQ")  # Replace with a descriptive app name
    location = geolocator.reverse((coordinates[0], coordinates[1]), language='en', timeout=10)
    print(location)
    if location:
        return location.address
    else:
        return ""
    
def get_lat_lon(place_name, max_retries=5, retry_delay=2):
    geolocator = Nominatim(user_agent="streamlit_map_app")

    # Check if the place_name is already in the cache
    if place_name in location_cache:
        print(f"Using cached coordinates for {place_name}")
        return location_cache[place_name]

    location = None
    for attempt in range(max_retries):
        try:
            location = geolocator.geocode(place_name + ", lucca")
            if location:
                # Cache the result
                coordinates = (location.latitude, location.longitude)
                location_cache[place_name] = coordinates
                return coordinates
        except GeopyError as e:
            print(f"Attempt {attempt + 1} failed: {e}")
        time.sleep(retry_delay)

    # Cache None for places not found to avoid retrying in the future
    location_cache[place_name] = None
    print("Failed to retrieve location after maximum retries.")
    return None

def write_formatted_address(address: str) -> str:
    # Split the address into components
    parts = address.split(", ")
    building = None
    number = None
    district2 = None
    # Determine if a building field is included (optional first field)
    if len(parts) == 7:  # Includes building
        if "via" in parts[0].lower() or "piazzale" in parts[0].lower() or "piazza" in parts[0].lower():
            street, _, district, city, region, postal_code, state = parts
        else:
            building, street, district, city, region, postal_code, state = parts
    elif len(parts) == 6: 
        street, district, city, region, postal_code, state = parts
    elif len(parts) == 8:  
        if "via" in parts[0].lower() or "piazzale" in parts[0].lower() or "piazza" in parts[0].lower():
            street, _, _, district, city, region, postal_code, state = parts
        else:
            building, number, street, district, city, region, postal_code, state = parts

    elif len(parts) == 9:  
        if "via" in parts[0].lower() or "piazzale" in parts[0].lower() or "piazza" in parts[0].lower():
            street, _, _, district, district2, city, region, postal_code, state = parts
        else:
            building, number, street, district, district2, city, region, postal_code, state = parts
    else:
        st.markdown("**Address:** " + address)
        return
    
    # Format the address
    formatted_address = "**Address:**  "
    if building:
        st.markdown(f"**Building:** {building}  ")
    if number:
        st.markdown(f"**Street:** {street}, {number}  ")
    else:
        st.markdown(f"**Street:** {street}  ")
    if district2:
        st.markdown(f"**District:** {district} / {district2}  ")
    else:
        st.markdown(f"**District:** {district}  ")
    st.markdown(f"**City:** {city}  ")
    st.markdown(f"**Region:** {region}  ")
    st.markdown(f"**Postal Code:** {postal_code}  ")
    st.markdown(f"**State:** {state}  ")

    return formatted_address

def choose_icon_type(queue):
    if queue < 5:
        return "low"
    elif queue < 10:
        return "medium"
    else:
        return "high"

def choose_icon(dataset_options, selected_dataset, point):
    if selected_dataset == "Public Toilets":
        return folium.CustomIcon(
            icon_image="images/toilet-" + choose_icon_type(point["properties"].get("queue")) + ".png",
            icon_size=(45, 45)
        )
    else:
        return folium.Icon(
            color=dataset_options[selected_dataset]["color"],
            icon=dataset_options[selected_dataset]["icon"]
            )


def page1():
    dataset_options = {
        "Ecopoints": {
            "dataset": "ecopunti_lucca.geojson",
            "icon": "trash",
            "color": "green"
        },
        "Food Services": {
            "dataset": "ristoranti_lucca.geojson",
            "icon": "cutlery",
            "color": "orange"
        },
        "Public Toilets": {
            "dataset": "servizi_pubblici_lucca.geojson",
            "icon": "bookmark",
            "color": "blue"
        },
        "Stands": {}
    }

    # Initialize the session state if not already initialized
    if 'selected_category' not in st.session_state:
        st.session_state.selected_category = None

    # Create a selectbox and store the value in session state
    selected_dataset = st.sidebar.selectbox(
        "Select the category",
        options=list(dataset_options.keys()),
        index=list(dataset_options.keys()).index(st.session_state.selected_category) if st.session_state.selected_category else 0
    )

    # Save the selected category in session state
    st.session_state.selected_category = selected_dataset

    if selected_dataset == "Stands":
        # Embed the map using iframe
        st.markdown(
        '<iframe src="https://maps2024.luccacomicsandgames.com/" width="100%" height="800px"></iframe>',
        unsafe_allow_html=True)
        st.session_state.destination_name = st.text_input("Add the address of the stand")
        if st.button("Let's go!"):
            st.session_state["page"] = 2
            st.rerun()
        st.stop()
        #return

    # Carica il file GeoJSON selezionato
    geojson_file_path = os.path.join('data', dataset_options[selected_dataset]["dataset"])
    with open(geojson_file_path, 'r') as f:
        geojson_data = json.load(f)

    # Estrai i dati dal GeoJSON
    data = []
    for feature in geojson_data["features"]:
        properties = feature["properties"]
        coordinates = feature["geometry"]["coordinates"]
        data.append({
            "latitude": coordinates[1],  # Latitudine
            "longitude": coordinates[0],  # Longitudine
            "properties": properties
        })

    # Converti i dati in un DataFrame
    df = pd.DataFrame(data)
    amenities = df["properties"].apply(lambda x: x.get("amenity", "Sconosciuto")).unique()
    selected_amenities = st.sidebar.multiselect(
        "Select the typology",
        options=amenities,
        default=amenities
    )
    # Filtra i dati in base alla selezione
    filtered_df = df[df["properties"].apply(lambda x: x.get("amenity", "Sconosciuto") in selected_amenities)]

    if selected_dataset == "Ecopoints":
        # Extract unique materials
        materials = sorted({mat for mats in filtered_df["properties"].apply(lambda x: x.get("materials")) for mat in mats})
        # Streamlit multi-select for materials
        selected_materials = st.sidebar.multiselect(
            "Select materials",
            options=materials,
            default=materials  # Preselect all materials
        )
        # Filter data based on selected materials
        filtered_df = filtered_df[filtered_df["properties"].apply(lambda x: any(mat in x.get("materials", []) for mat in selected_materials))]


    # Impostiamo start a una posizione specifica
    if st.session_state.selected_starting_point_mode == "Simulation: Lucca 1":
        st.session_state.start = (43.8430153,10.502204)
    elif st.session_state.selected_starting_point_mode == "Simulation: Lucca 2":
        st.session_state.start = (43.843, 10.508)
    elif st.session_state.selected_starting_point_mode == "Simulation: Lucca 3":
        st.session_state.start = (43.8408387,10.4996806)
    else:
        st.session_state.start = get_current_coordinates_using_IP()

    # Crea la mappa con Folium
    map_center = [df["latitude"].mean(), df["longitude"].mean()]
    m = folium.Map(location=map_center, zoom_start=15, control_scale=True)
    fg = folium.FeatureGroup(name="Markers")

    # Aggiungi un marker per lo starting point
    fg.add_child(folium.Marker(
        location=st.session_state.start,
        popup="You are here",
        icon=folium.CustomIcon(
            icon_image="images/me-marker.png",
            icon_size=(50, 50)
    )))


    # Aggiungi marker per i punti filtrati
    for _, point in filtered_df.iterrows():
        if selected_dataset == "Public Toilets":
            fg.add_child(folium.Marker(
                location=[point["latitude"], point["longitude"]],
                popup=point["properties"].get("amenity", "Info point"),
                tooltip="queue: " + str(point["properties"].get("queue")),
                icon=choose_icon(dataset_options, selected_dataset, point)
            ))
        else:
            fg.add_child(folium.Marker(
                    location=[point["latitude"], point["longitude"]],
                    popup=point["properties"].get("amenity", "Info point"),
                    icon=choose_icon(dataset_options, selected_dataset, point)
            ))

    # Mostra la mappa in Streamlit
    map_html = st_folium(m, feature_group_to_add=fg, width=700)

    if "last_object_clicked" not in st.session_state:
        st.session_state.last_object_clicked = None
    
    last_object = map_html.get("last_object_clicked", {})
    st.session_state.last_object_clicked = last_object
    last_object_clicked_popup = map_html.get("last_object_clicked_popup", "")
    last_object_clicked_tooltip = map_html.get("last_object_clicked_tooltip", "")
    if last_object_clicked_tooltip:
        st.session_state.last_object_clicked_tooltip = last_object_clicked_tooltip.split(": ")[1]
    else:
        st.session_state.last_object_clicked_tooltip = None
    if last_object:
        st.write(f"Typology clicked: {last_object_clicked_popup}")
        destination_info = get_street_from_coordinates((last_object['lat'], last_object['lng']))
        st.markdown(f"**Destination:** {destination_info.split(",")[0]}")
        if selected_dataset == "Public Toilets":
            st.markdown(f"**Queue:** {st.session_state.last_object_clicked_tooltip} people")
        with st.expander("Click to view more details"):
            write_formatted_address(destination_info)
            st.markdown(f'**Coordinates:** {(last_object['lat'], last_object['lng'])}')
    else:
        st.write("Select a destination on the map")

    if st.session_state.last_object_clicked and st.button("Let's go!"):
        st.session_state["page"] = 2
        st.rerun()



def page2():

    if st.button("Go Back"):
        st.session_state.end = None
        st.session_state.end_street = None
        st.session_state.destination_name = None
        st.session_state.last_object_clicked_tooltip = None
        st.session_state["page"] = 1
        st.rerun()

    # Set start location
    if st.session_state.selected_starting_point_mode == "Simulation: Lucca 1":
        st.session_state.start = (43.8430153,10.502204)
    elif st.session_state.selected_starting_point_mode == "Simulation: Lucca 2":
        st.session_state.start = (43.843, 10.508)
    elif st.session_state.selected_starting_point_mode == "Simulation: Lucca 3":
        st.session_state.start = (43.8408387,10.4996806)
    else:
        st.session_state.start = get_current_coordinates_using_IP()


    # Retrieve last clicked object on the map
    last_object = st.session_state.last_object_clicked

    if "destination_name" not in st.session_state:
        st.session_state.destination_name = None

    # no stand case
    if (last_object and 'lat' in last_object and 'lng' in last_object) or st.session_state.destination_name:
        
        if st.session_state.destination_name:
            print("getting end from name")
            st.session_state.end = get_lat_lon(st.session_state.destination_name)
        else:
            # Get coordinates of the selected point
            print("getting end previous page")
            st.session_state.end = (last_object['lat'], last_object['lng'])

        if st.session_state.end is None:
            st.error("Destination is not correctly parsed. Please try again.")
            st.stop()

        print(f"End coordinates: {st.session_state.end}")

        # Calculate the map center for display
        map_center = [
            (st.session_state.start[0] + st.session_state.end[0]) / 2,
            (st.session_state.start[1] + st.session_state.end[1]) / 2
        ]

        # Initialize map
        m = folium.Map(location=map_center, zoom_start=17, control_scale=True)

        # Calcola i confini del bounding box
        min_lat = min(st.session_state.start[0], st.session_state.end[0]) - 0.001
        max_lat = max(st.session_state.start[0], st.session_state.end[0]) + 0.001
        min_lon = min(st.session_state.start[1], st.session_state.end[1]) - 0.001
        max_lon = max(st.session_state.start[1], st.session_state.end[1]) + 0.001
        # Adatta la mappa ai confini calcolati
        m.fit_bounds([[min_lat, min_lon], [max_lat, max_lon]])

        # Add markers for the start and end points
        fg = folium.FeatureGroup(name="Markers")

        fg.add_child(folium.Marker(
            location=st.session_state.start,
            popup="Start",
            icon=folium.CustomIcon(
            icon_image="images/me-marker.png",
            icon_size=(50, 50))
        ))

        fg.add_child(folium.Marker(
            location=st.session_state.end,
            popup="Destination",
            icon=folium.Icon(color="green", icon="flag")
        ))

        # Use GraphHopper API to calculate the route
        graphhopper_api_key = os.getenv("GRAPHHOPPER_API_KEY")
        if st.session_state.selected_travel_mode.lower() == "walk":
            vehicle = "foot"
        else:
            vehicle = st.session_state.selected_travel_mode.lower()
        url = (
            f'https://graphhopper.com/api/1/route?'
            f'point={st.session_state.start[0]},{st.session_state.start[1]}&'
            f'point={st.session_state.end[0]},{st.session_state.end[1]}&'
            f'type=json&locale=en&vehicle={vehicle}&key={graphhopper_api_key}'
        )

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            # Decode the route geometry
            encoded_polyline = data['paths'][0]['points']
            decoded_route = polyline.decode(encoded_polyline)


            rt = folium.FeatureGroup(name="Route")

            # Draw the route on the map
            rt.add_child(folium.PolyLine(
                locations=decoded_route,
                color='blue',
                weight=5,
                opacity=0.7
            ))
            rt.add_to(m)

            # Ricalcola la mappa con il nuovo marker
            st_folium(m, feature_group_to_add=fg, width=700)

            # Display selected point information
            if not "start_street" in st.session_state or st.session_state.start_street == None:
                st.session_state.start_street = get_street_from_coordinates(st.session_state.start)
            if not "end_street" in st.session_state or st.session_state.end_street == None:
                print("getting end street from " + str(st.session_state.end))
                st.session_state.end_street = get_street_from_coordinates(st.session_state.end)
                
            st.markdown("**Current position**")
            address_parts_start = st.session_state.start_street.split(",")
            # Check the length and display the appropriate element
            st.write(f"{address_parts_start[0].strip()}")
            with st.expander("Show more Information"):
                write_formatted_address(st.session_state.start_street)
                st.markdown(f"**Coordinates**: {st.session_state.start}")

            address_parts_end = st.session_state.end_street.split(",")
            st.markdown("**Destination**")
            # st.write(st.session_state.end_street)
            st.write(f"{address_parts_end[0].strip()}")
            with st.expander("Show more Information"):
                write_formatted_address(st.session_state.end_street)
                st.markdown(f"**Coordinates**: {st.session_state.end}")

            # Mostrare le istruzioni
            instructions = data['paths'][0].get('instructions', [])
            st.write("### Directions")
            for idx, instruction in enumerate(instructions):
                distance = instruction.get('distance', 0) / 1000  # Convertire in chilometri
                time = instruction.get('time', 0) / 1000 / 60  # Convertire in minuti
                text = instruction.get('text', "")
                if "destination" in text.lower():
                    st.write(f"{idx + 1}. {text}")
                else:
                    st.write(f"{idx + 1}. {text} ({round(distance, 2)} km, {round(time, 2)} min)")

            # Calcolo della distanza complessiva
            total_distance = data['paths'][0]['distance'] / 1000  # in chilometri
            total_duration = data['paths'][0]['time'] / 1000 / 60  # in minuti
            st.write(f"### Summary")
            st.write(f"Total Distance: {round(total_distance, 2)} km")
            total_travel_time = round(total_duration, 2)
            st.write(f"Estimated Total Travel Time: {total_travel_time} minutes")
            if st.session_state.last_object_clicked_tooltip is not None and st.session_state.last_object_clicked_tooltip != "None":
                st.write(f"Queue: {st.session_state.last_object_clicked_tooltip} people")
                total_queue_time = int(st.session_state.last_object_clicked_tooltip)
                st.write(f"Estimated Total queue time: {total_queue_time} minutes (1 person per minute)")
                st.write(f"Estimated Total time: {total_queue_time + total_travel_time} minutes")
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to retrieve route data: check the route start and destination points: {st.session_state.start_street} and {st.session_state.end_street}")
        except KeyError:
            st.error("Unexpected response structure from the API.")
    else:
        st.warning("Please click on the map to select a destination.")



def main():
    st.title("🌍 Navigator")

    st.sidebar.title("Filters")
    st.session_state.selected_starting_point_mode = st.sidebar.selectbox(
        "Select starting point (simulation)",
        options=["Simulation: Lucca 1", "Simulation: Lucca 2", "Simulation: Lucca 3", "Use IP location"]
    )
    st.session_state.selected_travel_mode = st.sidebar.selectbox(
        "Select travel mode",
        options=["Walk", "Car", "Bike", "Scooter"]
    )

    if "page" not in st.session_state:
        st.session_state["page"] = 1
    if st.session_state["page"] == 1:
        page1()
    elif st.session_state["page"] == 2:
        page2()

if __name__ == "__main__":
    main()
