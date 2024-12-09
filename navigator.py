import streamlit as st
import os
import json
import pandas as pd
import networkx as nx
from geopy.distance import geodesic
import folium
from folium.plugins import Draw
from streamlit_folium import st_folium  # Aggiungi questa importazione
import utils

def main():
    st.title("🌍 Navigator")

    # Carica il file GeoJSON
    geojson_file_path = os.path.join('data', 'Milano_Trash_and_Recycling_Collection_Points.geojson')
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
            "properties": properties  # Aggiungi le proprietà
        })

    # Converti i dati in un DataFrame
    df = pd.DataFrame(data)

    # Impostiamo start a una posizione specifica (45.463647, 9.1882373)
    start = (45.463647, 9.1882373)

    # Crea la mappa con Folium
    map_center = [df["latitude"].mean(), df["longitude"].mean()]
    m = folium.Map(location=map_center, zoom_start=12, control_scale=True)

    # Aggiungi marker per i primi 20 punti e imposta l'evento di click per selezionare end
    for _, point in df.head(20).iterrows():
        try:
            marker = folium.Marker(
                location=[point["latitude"], point["longitude"]],
                popup=point["properties"].get("amenity", "Info point"),
                icon=folium.Icon(color='blue')
            )
            # Aggiungi evento di click per impostare il punto di destinazione
            marker.add_to(m)
            marker.add_child(folium.Popup(f"Seleziona come destinazione"))
        except Exception as e:
            st.error(f"Errore durante l'aggiunta del marker: {e}")

    # Mostra la mappa in Streamlit
    map_html = st_folium(m, width=700)  # Impostiamo una larghezza per la mappa

    # Bottone per calcolare il percorso
    if st.button("Calcola percorso"):
        end = get_end_point(map_html)
        if end:
            route = calculate_route(start, end)
            st.write(f"Percorso calcolato: {route} km")
        else:
            st.write("Per favore, seleziona un punto di destinazione cliccando su un marker.")

def get_end_point(map_html):
    # Questo è il punto in cui dovresti ottenere la posizione del marker selezionato dal click sulla mappa
    # Streamlit Folium non supporta direttamente il click sui marker, ma puoi prendere la latitudine e longitudine
    # da una variabile esterna o un altro meccanismo che salvi il click.
    
    # For now, just use a placeholder or logic to get the `end` point manually or as an input.
    # Simulate end point selection, e.g., (for testing purposes)
    end = (45.4501284, 9.237563)  # Just an example, replace with actual click handler logic
    return end

def calculate_route(start, end):
    # Calcola la distanza tra i punti utilizzando geodesic
    return geodesic(start, end).km