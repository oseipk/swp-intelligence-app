# Use official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy all files
COPY . /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variable to prevent Streamlit from asking questions
ENV STREAMLIT_ENABLE_STATIC_SERVE true

# Expose default Streamlit port
EXPOSE 8501

# Run the app
CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
