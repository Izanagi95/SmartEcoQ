FROM python:3.9-slim
RUN apt-get update && apt-get install -y libzbar0
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . /app
WORKDIR /app
CMD ["streamlit", "run", "app.py"]