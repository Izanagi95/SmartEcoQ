import streamlit as st
from dotenv import load_dotenv
from event_assistant import main as event_assistant
from recycling_assistant import main as recycling_assistant
from navigator import main as navigator
from utils import setup

# Streamlit UI
def main():
    # Configura il titolo della scheda
    st.set_page_config(page_title="SmartEcoQ")
    st.sidebar.title("🌱 SmartEcoQ")
    page = st.sidebar.radio("Seleziona una pagina:", ["Event Assistant", "Recycling Assistant", "Navigator"])
    setup()

    if page == "Event Assistant":
        event_assistant()

    if page == "Recycling Assistant":
       recycling_assistant()
            
    if page == "Navigator":
        navigator()
            
if __name__ == "__main__":
    main()