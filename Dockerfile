# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install LibreOffice and other necessary packages for docx to pdf conversion
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libreoffice \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code to the working directory
COPY . .

# Make port 8501 available to the world outside this container
EXPOSE 8501

# Run app.py when the container launches
CMD ["streamlit", "run", "app.py"]
