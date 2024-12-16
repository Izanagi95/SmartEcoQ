FROM python:3.12-slim

# Install system dependencies, including libGL
RUN apt-get update && apt-get install -y libzbar0 libgl1 && apt-get clean && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Copy requirements.txt and install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files
COPY . /app
WORKDIR /app

# Command to start the Streamlit app
CMD ["streamlit", "run", "app.py"]
