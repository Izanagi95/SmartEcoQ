import streamlit as st
from dotenv import load_dotenv
from event_assistant import main as event_assistant
from recycling_assistant import main as recycling_assistant
from navigator import main as navigator
from booking import main as booking
from utils import setup

# Streamlit UI
def main():
    # Configura il titolo della scheda
    st.set_page_config(page_title="SmartEcoQ", page_icon="images/smartecoq-favicon/favicon-32x32.png")
    st.sidebar.title("🌱 SmartEcoQ")
    page = st.sidebar.radio("Select a page:", ["Event Assistant", "Booking (Disabled)", "Recycling Assistant", "Navigator"])
    if "setup" not in st.session_state:
        st.session_state.setup = True
        setup()

    pages = {
        "Event Assistant": event_assistant,
        "Recycling Assistant": recycling_assistant,
        "Navigator": navigator,
        #"Booking": booking
    }

    # Execute the selected page's function
    if page in pages:
        pages[page]()

if __name__ == "__main__":
    main()