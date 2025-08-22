# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt
COPY requirements.txt ./

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose Streamlit default port
EXPOSE 8501

# Set Streamlit to run in headless mode
ENV STREAMLIT_SERVER_HEADLESS=true

# Run Streamlit app
CMD ["streamlit", "run", "rag-test.py"]