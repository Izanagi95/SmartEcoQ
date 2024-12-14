import cv2
import numpy as np
import streamlit as st
import os
import sqlite3

def reset_db():
    db_path = "event.db"
    
    # If the database file exists, delete it
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Connect to the new (empty) database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create the "Stand" table
    cursor.execute('''
        CREATE TABLE Stand (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            max_capacity INTEGER NOT NULL,
            queue_counter INTEGER NOT NULL DEFAULT 0
        );
    ''')
    
    # Create the "reservation" table
    cursor.execute('''
        CREATE TABLE reservation (
            reservation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            stand_id INTEGER NOT NULL,
            reservation_datetime DATETIME NOT NULL,
            reservation_name TEXT NOT NULL,
            FOREIGN KEY(stand_id) REFERENCES Stand(id)
        );
    ''')
    
    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def page1():
    st.title("🌍 Booking")
    image = st.camera_input("Show QR code")

    if image is not None:
        bytes_data = image.getvalue()
        cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

        detector = cv2.QRCodeDetector()

        data, bbox, straight_qrcode = detector.detectAndDecode(cv2_img)

        if data:
            st.write(data)
            if st.button("Book now"):
                st.success("Booking successful")


        else:
            st.write("No QR code found")
            if st.button("Book now"):
                st.success("Booking successful")
                if st.button("Go to booked list"):
                    st.session_state["booking_page"] = 2


def page2():
    st.title("🌍 Booked list")



def main():
    if st.sidebar.button("Reset DB"):
        reset_db()
    if "booking_page" not in st.session_state:
        st.session_state["booking_page"] = 1
    if st.session_state["booking_page"] == 1:
        page1()
    elif st.session_state["booking_page"] == 2:
        page2()
    