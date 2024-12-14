import streamlit as st
import os
import json
import pandas as pd
import folium
from streamlit_folium import st_folium
import requests
import polyline
from dotenv import load_dotenv
import os
import geocoder
from geopy.geocoders import Nominatim

load_dotenv()

def get_current_coordinates_using_IP():
    g = geocoder.ip('me')  # Detects your current IP
    if g.latlng:
        return g.latlng  # Returns [latitude, longitude]
    else:
        return "Could not determine location"

def get_street_from_coordinates(coordinates):
    geolocator = Nominatim(user_agent="SmartEcoQ")  # Replace with a descriptive app name
    location = geolocator.reverse((coordinates[0], coordinates[1]), language='en', timeout=10)
    if location:
        return location.address
    else:
        return ""
    
# def format_duration(seconds):
#     minutes, seconds = divmod(seconds, 60)
#     hours, minutes = divmod(minutes, 60)
    
#     duration = []
    
#     if hours:
#         duration.append(f"{hours} hour{'s' if hours > 1 else ''}")
#     if minutes:
#         duration.append(f"{minutes} minute{'s' if minutes > 1 else ''}")
#     if seconds:
#         duration.append(f"{seconds} second{'s' if seconds > 1 else ''}")
    
#     return ', '.join(duration) or '0 seconds'

def page1():

    dataset_options = {
        "Ecopoint": {
            "dataset": "ecopunti_lucca.geojson",
            "icon": "trash",
            "color": "green"
        },
        "Restoration": {
            "dataset": "ristoranti_lucca.geojson",
            "icon": "cutlery",
            "color": "blue"
        },
        "Public Toilets": {
            "dataset": "servizi_pubblici_lucca.geojson",
            "icon": "bath",
            "color": "yellow"
        }
    }
    selected_dataset = st.sidebar.selectbox(
        "Select the category",
        options=list(dataset_options.keys())
    )

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

    # Impostiamo start a una posizione specifica
    if st.session_state.selected_starting_point_mode == "Simulation: Lucca":
        st.session_state.start = (43.843, 10.508)
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
        icon=folium.Icon(color="red", icon="circle")
    ))

    # Aggiungi marker per i punti filtrati
    for _, point in filtered_df.iterrows():
        fg.add_child(folium.Marker(
            location=[point["latitude"], point["longitude"]],
            popup=point["properties"].get("amenity", "Info point"),
            icon=folium.Icon(color=dataset_options[selected_dataset]["color"], icon=dataset_options[selected_dataset]["icon"])
        ))

    # Mostra la mappa in Streamlit
    st.session_state.map_html = st_folium(m, feature_group_to_add=fg, width=700)

    if st.session_state.map_html["last_object_clicked"] and st.button("Go ahead"):
        st.session_state["page"] = 2
        st.rerun()



def page2():
    col1, col2 = st.columns([1, 6])
    with col1:
        # Back button for navigation
        if st.button("Go Back"):
            st.session_state["page"] = 1
            st.rerun()

    with col2:
        if st.button("Refresh"):
            st.rerun()

    # Set start location
    if st.session_state.selected_starting_point_mode == "Simulation: Lucca":
        st.session_state.start = (43.843, 10.508)
    else:
        st.session_state.start = get_current_coordinates_using_IP()


    # Retrieve last clicked object on the map
    last_object = st.session_state.map_html.get("last_object_clicked", {})

    if 'lat' in last_object and 'lng' in last_object:
        # Get coordinates of the selected point
        st.session_state.end = (last_object['lat'], last_object['lng'])

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
            icon=folium.Icon(color="red", icon="circle")
        ))

        fg.add_child(folium.Marker(
            location=st.session_state.end,
            popup="Destination",
            icon=folium.Icon(color="green", icon="flag")
        ))

        # Use GraphHopper API to calculate the route
        graphhopper_api_key = os.getenv("GRAPHHOPPER_API_KEY")

        url = (
            f'https://graphhopper.com/api/1/route?'
            f'point={st.session_state.start[0]},{st.session_state.start[1]}&'
            f'point={st.session_state.end[0]},{st.session_state.end[1]}&'
            f'type=json&locale=en&vehicle={st.session_state.selected_travel_mode.lower()}&key={graphhopper_api_key}'
        )

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            # Decode the route geometry
            encoded_polyline = data['paths'][0]['points']
            decoded_route = polyline.decode(encoded_polyline)

            # Draw the route on the map
            folium.PolyLine(
                locations=decoded_route,
                color='blue',
                weight=5,
                opacity=0.7
            ).add_to(m)

            # Ricalcola la mappa con il nuovo marker
            st_folium(m, feature_group_to_add=fg, width=700)

            # Display selected point information
            if not "start_street" in st.session_state:
                st.session_state.start_street = get_street_from_coordinates(st.session_state.start)
            if not "end_street" in st.session_state:
                st.session_state.end_street = get_street_from_coordinates(st.session_state.end)
            st.write(f"Starting point: {st.session_state.start_street} {st.session_state.start}")
            st.write(f"Destination point: {st.session_state.end_street} {st.session_state.end}")

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
            st.write(f"Estimated Total Time: {round(total_duration, 2)} minutes")
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to retrieve route data: {e}")
        except KeyError:
            st.error("Unexpected response structure from the API.")


    else:
        st.warning("Please click on the map to select a destination.")



def main():

    st.title("🌍 Navigator")

    # Sidebar per la selezione del dataset
    st.sidebar.title("Filters")

    st.session_state.selected_starting_point_mode = st.sidebar.selectbox(
        "Select starting point",
        options=["Simulation: Lucca", "Use IP location"]
    )

    st.session_state.selected_travel_mode = st.sidebar.selectbox(
        "Select travel mode",
        options=["Foot", "Car"]
    )

    if "page" not in st.session_state:
        st.session_state["page"] = 1
    if st.session_state["page"] == 1:
        page1()
    elif st.session_state["page"] == 2:
        page2()

if __name__ == "__main__":
    main()
