
# SmartEcoQ

**Smart Crowds, Clean Cities: AI for a Sustainable Future!**

## 📖 Table of Contents
1. [Overview](#overview)
2. [Key Features](#key-features)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Technologies Used](#technologies-used)
6. [Contributing](#contributing)
7. [License](#license)
8. [Contact](#contact)

---

## 🌟 Overview
**SmartEcoQ** is an AI-powered platform designed to revolutionize the management of large-scale events with a focus on sustainability. From queue management and crowd density monitoring to gamified eco-friendly waste disposal, SmartEcoQ enhances attendee experience while promoting environmental responsibility.

This Proof of Concept (PoC) is tailored for **Lucca Comics**, leveraging existing city maps to navigate and manage resources efficiently.

---

## 🏗️ Architecture

TBD

---

## ✨ Key Features
1. **Event Chatbot**
   - Provides instant answers to event-related queries.
2. **Queue Management**
   - Allows attendees to book their place in queues via QR codes, monitor queue status, and plan activities effectively.
3. **Eco-Friendly Waste Sorting (Recycling Assistant)**
   - Gamified waste disposal system that educates and engages users.
4. **Interactive Navigation**
   - Maps for locating eco-points, stands, restaurants, and public restrooms.

---

## 🛠️ Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/SmartEcoQ.git
   cd SmartEcoQ
   ```

2. **Set Up Virtual Environment** (Optional):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Add API Keys**:
   - Create a `.env` file in the root directory and add your API keys:
     ```env
     IBM_API_KEY=your_ibm_api_key
     IBM_PROJECT_ID=your_ibm_project_id
     MAP_API_KEY=your_map_service_api_key
     ```

---

## 🚀 Usage

1. **Run the Application**:
   ```bash
   streamlit run app.py
   ```

2. **Try the Features**:
   - Interact with the event chatbot.
   - Scan QR codes at stand locations to book your turn and monitor the queues.
   - Sort waste with the gamified Recycling Assistant.
   - Use the navigation feature to find points of interest and find the way to reach the desired destination.

---

## 💻 Technologies Used

- **Backend**: Python
- **AI Services**: IBM watsonx.ai
- **Frontend**: Streamlit
- **Maps Integration**: Folium, Graphhopper
- **Database**: SQLite3
- **Other**: QR Code Generator, OpenCV

---

## ⚠️ Disclaimer (forse da cancellare)

For the purposes of this demonstration, we have included the .env file in the repository to simplify the setup process for the jury. We acknowledge this is a security risk and not a best practice for production environments. Sensitive configurations, such as API keys or credentials, should never be stored directly in the repository. Instead, consider using secure secret management solutions like Vault, AWS Secrets Manager, or environment variable management via CI/CD pipelines.

---

## 📚 Resources

Video: TBD

Slides: TBD

---

## 🖋️ Authors

- Gabriele Guo
- Chenghao Xia