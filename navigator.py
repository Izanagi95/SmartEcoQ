import streamlit as st
import os
import json
import pandas as pd
from geopy.distance import geodesic
import folium
from folium.plugins import Draw
from streamlit_folium import st_folium

def main():
    st.title("🌍 Navigator")

    # Sidebar per la selezione del dataset
    st.sidebar.title("Filtri")
    dataset_options = {
        "Ecopunti": "ecopunti_lucca.geojson",
        "Ristoranti": "ristoranti_lucca.geojson",
        "Servizi Pubblici": "servizi_pubblici_lucca.geojson"
    }
    selected_dataset = st.sidebar.selectbox(
        "Seleziona le categorie",
        options=list(dataset_options.keys())
    )

    # Carica il file GeoJSON selezionato
    geojson_file_path = os.path.join('data', dataset_options[selected_dataset])
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
    start = (43.843, 10.508)

    # Crea la mappa con Folium
    map_center = [df["latitude"].mean(), df["longitude"].mean()]
    m = folium.Map(location=map_center, zoom_start=15, control_scale=True)

    # Aggiungi un marker per lo starting point
    folium.Marker(
        location=start,
        popup="Tu sei qui",
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(m)

    # Aggiungi marker per i punti filtrati
    for _, point in filtered_df.iterrows():
        folium.Marker(
            location=[point["latitude"], point["longitude"]],
            popup=point["properties"].get("amenity", "Info point"),
            icon=folium.Icon(color='blue')
        ).add_to(m)

    # Aggiungi il plugin Draw per selezionare un punto
    draw = Draw(export=True)
    draw.add_to(m)

    # Mostra la mappa in Streamlit
    map_html = st_folium(m, width=700)

    # Cattura le informazioni sul disegno
    if map_html.get("last_object"):
        last_object = map_html.get("last_object")
        if 'geometry' in last_object and last_object['geometry']['type'] == 'Point':
            # Recupera le coordinate del punto disegnato
            end = tuple(last_object['geometry']['coordinates'])
            st.write(f"Punto selezionato: {end}")

            # Aggiungi un marker per il punto selezionato
            folium.Marker(
                location=end,
                popup="Destinazione",
                icon=folium.Icon(color="green", icon="info-sign")
            ).add_to(m)

            # Ricalcola la mappa con il nuovo marker
            map_html = st_folium(m, width=700)

            # Calcolo della distanza
            if st.button("Calcola percorso"):
                route = calculate_route(start, end)
                st.write(f"Percorso calcolato: {route} km")

    else:
        st.write("Per favore, seleziona un punto di destinazione cliccando sulla mappa.")

def calculate_route(start, end):
    # Calcola la distanza tra i punti utilizzando geodesic
    return geodesic(start, end).km

if __name__ == "__main__":
    main()
