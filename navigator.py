import streamlit as st
import os
import json
import pandas as pd
from geopy.distance import geodesic
import folium
from streamlit_folium import st_folium
import requests
import polyline


def page1():
    st.title("🌍 Navigator")

    # Sidebar per la selezione del dataset
    st.sidebar.title("Filtri")
    dataset_options = {
        "Ecopunti": {
            "dataset": "ecopunti_lucca.geojson",
            "icon": "trash",
            "color": "green"
        },
        "Ristoranti": {
            "dataset": "ristoranti_lucca.geojson",
            "icon": "cutlery",
            "color": "blue"
        },
        "Servizi Pubblici": {
            "dataset": "servizi_pubblici_lucca.geojson",
            "icon": "bath",
            "color": "yellow"
        }
    }
    selected_dataset = st.sidebar.selectbox(
        "Seleziona le categorie",
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
        "Seleziona le tipologie",
        options=amenities,
        default=amenities
    )

    # Filtra i dati in base alla selezione
    filtered_df = df[df["properties"].apply(lambda x: x.get("amenity", "Sconosciuto") in selected_amenities)]

    # Impostiamo start a una posizione specifica
    st.session_state.start = (43.843, 10.508)

    # Crea la mappa con Folium
    map_center = [df["latitude"].mean(), df["longitude"].mean()]
    m = folium.Map(location=map_center, zoom_start=15, control_scale=True)

    # Aggiungi un marker per lo starting point
    folium.Marker(
        location=st.session_state.start,
        popup="Tu sei qui",
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(m)

    # Aggiungi marker per i punti filtrati
    for _, point in filtered_df.iterrows():
        folium.Marker(
            location=[point["latitude"], point["longitude"]],
            popup=point["properties"].get("amenity", "Info point"),
            icon=folium.Icon(color=dataset_options[selected_dataset]["color"], icon=dataset_options[selected_dataset]["icon"])
        ).add_to(m)

    # Mostra la mappa in Streamlit
    st.session_state.map_html = st_folium(m, width=700)

    if st.session_state.map_html["last_object_clicked"] and st.button("Go ahead"):
        st.session_state["page"] = 2
        st.rerun()



def page2():
    # Cattura le informazioni sul disegno
    st.session_state.start = (43.843, 10.508)

    last_object = st.session_state.map_html["last_object_clicked"]
    if 'lat' in last_object and 'lng' in last_object:
        # Recupera le coordinate del punto disegnato
        st.session_state.end = tuple((last_object['lat'], last_object['lng']))
        map_center = [(st.session_state.start[0] + st.session_state.end[0])/2, (st.session_state.start[1] + st.session_state.end[1])/2]
        m = folium.Map(location=map_center, zoom_start=15, control_scale=True)
        st.write(f"Selected point: {st.session_state.end}")

        # Aggiungi un marker per il punto selezionato
        folium.Marker(
            location=st.session_state.start,
            popup="Destinazione",
            icon=folium.Icon(color="red", icon="circle")
        ).add_to(m)

        # Aggiungi un marker per il punto selezionato
        folium.Marker(
            location=st.session_state.end,
            popup="Destinazione",
            icon=folium.Icon(color="green", icon="flag")
        ).add_to(m)

        # Calcolare il percorso usando OSRM
        url = f'http://router.project-osrm.org/route/v1/walking/{st.session_state.start[1]},{st.session_state.start[0]};{st.session_state.end[1]},{st.session_state.end[0]}?overview=full&continue_straight=true&alternatives=true'
        response = requests.get(url)
        data = response.json()
        print(data)
        # Estrarre la geometria e decodificarla
        encoded_polyline = data['routes'][0]['geometry']
        decoded_route = polyline.decode(encoded_polyline)

        # Tracciare il percorso sulla mappa
        folium.PolyLine(locations=decoded_route, color='blue', weight=5, opacity=0.7).add_to(m)

        # Ricalcola la mappa con il nuovo marker
        map_html = st_folium(m, width=700)

        # # Calcolo della distanza
        distance = data['routes'][0]['distance'] / 1000  # in chilometri
        duration = data['routes'][0]['duration'] / 60  # in minuti
        st.write(f"Distance calculated: {round(distance, 2)} km")
        st.write(f"Estimated time: {round(duration, 2) * 5} minutes")
        route = calculate_route(st.session_state.start, st.session_state.end)
        st.write(f"Distance calculated: {round(route, 2)} km")
        st.write(f"Estimated time: {round(estimate_time(route), 2)} minutes")

    if st.button("Back to map"):
        st.session_state["page"] = 1
        st.rerun()

def main():
    if "page" not in st.session_state:
        st.session_state["page"] = 1
    if st.session_state["page"] == 1:
        page1()
    elif st.session_state["page"] == 2:
        page2()

   

def calculate_route(start, end):
    # Calcola la distanza tra i punti utilizzando geodesic
    return geodesic(start, end).km

def estimate_time(distance_km):
    walking_speed_kmh = 5  # Velocità media a piedi in km/h
    time_hours = distance_km / walking_speed_kmh
    return time_hours * 60  # Converti in minuti

if __name__ == "__main__":
    main()
