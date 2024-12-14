import cv2
import numpy as np
import streamlit as st
import os
import sqlite3
import pandas as pd
import namesgenerator
from datetime import datetime


def reset_db():
    db_path = "event.db"
    
    # If the database file exists, delete it
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Connect to the new (empty) database
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Create the "Stand" table
        cursor.execute('''CREATE TABLE IF NOT EXISTS stand (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            max_capacity INTEGER NOT NULL,
            queue_counter INTEGER NOT NULL DEFAULT 0,
            position TEXT
        )''')
        
        # Create the "reservation" table
        cursor.execute('''CREATE TABLE IF NOT EXISTS reservation (
            reservation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            stand_id INTEGER NOT NULL,
            unique_name TEXT NOT NULL,
            reservation_datetime DATETIME NOT NULL,
            user TEXT NOT NULL,
            FOREIGN KEY(stand_id) REFERENCES stand(id)
        )''')
        
        # Insert initial data
        stands = [
            ("Autografo Cristina D'Avena", 0, 50, "43.8453612,10.5052311"),
            ("Autografo Giorgio Vanni", 0, 100, "43.8453612,10.5052311"),
            ("Autografo ZeroCalcare", 0, 30, "43.8459697,10.5051567"),
        ]
        cursor.executemany('''INSERT INTO stand (name, max_capacity, queue_counter, position) VALUES (?, ?, ?, ?)''', stands)


def get_connection():
    return sqlite3.connect("event.db")


def page1():
    st.title("🌍 Booking")
    
    # Create a live camera input using Streamlit's camera_input widget
    image = st.camera_input("Scan QR code")  # Streamlit widget to capture live camera input
    
    if image is not None:
        # Process the image to extract QR code
        bytes_data = image.getvalue()
        cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

        # QR code detection using OpenCV
        detector = cv2.QRCodeDetector()
        data, _, _ = detector.detectAndDecode(cv2_img)

        if data:
            with get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT id, name, queue_counter, position FROM stand WHERE id = ? LIMIT 1", (data,))
                row = cursor.fetchone()
                
                if row:
                    st.write(f"Name: {row[1]}")
                    st.write(f"Queue Counter: {row[2]}")
                    st.write(f"Position: {row[3]}")
                    
                    if st.button("Book now"):
                        unique_name = namesgenerator.get_random_name()
                        reservation_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        reservation_data = (data, reservation_datetime, unique_name)
                        
                        cursor.execute('''INSERT INTO reservation (stand_id, reservation_datetime, unique_name) VALUES (?, ?, ?)''', reservation_data)
                        cursor.execute('''UPDATE stand SET queue_counter = queue_counter + 1 WHERE id = ?''', (data,))
                        connection.commit()

                        st.success(f"Reservation successful with the name: {unique_name}")
                        if st.button("Go to booked list"):
                            st.session_state.selected_booking_view = "Event list"
                else:
                    st.write("No valid QR code found")
        else:
            st.write("No QR code found")


def page2():
    st.title("🌍 Event list")

    # Add a filter option in the sidebar
    filter_option = st.sidebar.selectbox("Filter by Reservation", ["All", "With Reservation", "Without Reservation"])

    # Fetch the data from the database
    with get_connection() as connection:
        cursor = connection.cursor()
        
        # Fetch the stand and reservation data
        cursor.execute('''SELECT name, queue_counter, position, reservation_name, reservation_datetime 
                          FROM stand LEFT JOIN reservation ON stand.id = reservation.stand_id''')
        rows = cursor.fetchall()

    # Convert the result to a Pandas DataFrame for display in Streamlit
    columns = ["Stand/Event", "Queue", "Position", "Reservation name", "Reservation timestamp"]
    stands_df = pd.DataFrame(rows, columns=columns)

    # Filter the DataFrame based on the selected filter option
    if filter_option == "With Reservation":
        stands_df = stands_df[stands_df["Reservation name"].notna()]
    elif filter_option == "Without Reservation":
        stands_df = stands_df[stands_df["Reservation name"].isna()]

    # Display the filtered data as a table in Streamlit
    st.table(stands_df)

    # Create a button to simulate 10 minutes (placed after the table)
    if st.button("Simulate 10 mins"):
        with get_connection() as connection:
            cursor = connection.cursor()
            
            # Update the queue_counter by -10, but ensure it doesn't go below 0
            cursor.execute('''UPDATE stand SET queue_counter = CASE 
                                WHEN queue_counter >= 10 THEN queue_counter - 10
                                ELSE 0
                              END''')
            connection.commit()

            # Now check if the queue_counter is 0 for any stand and remove related reservations
            cursor.execute('''SELECT id FROM stand WHERE queue_counter = 0''')
            stands_with_zero_queue = cursor.fetchall()

            for stand in stands_with_zero_queue:
                stand_id = stand[0]
                
                # If the queue_counter is 0, delete all associated reservations
                cursor.execute('''DELETE FROM reservation WHERE stand_id = ?''', (stand_id,))
                connection.commit()

        # Refresh the table after the button click
        st.success("10 min is simulated")
        st.rerun()

def main():
    if st.sidebar.button("Reset DB"):
        reset_db()

    if "selected_booking_view" not in st.session_state:
        st.session_state["selected_booking_view"] = "Book now"

    st.session_state.selected_booking_view = st.sidebar.radio("Select what to do", ["Book now", "Event list"])

    pages = {
        "Book now": page1,
        "Event list": page2
    }

    # Execute the selected page's function
    pages[st.session_state.selected_booking_view]()


if __name__ == "__main__":
    main()
