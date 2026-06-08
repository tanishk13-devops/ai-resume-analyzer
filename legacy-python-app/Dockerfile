# Use a lightweight base image for Python 3.12
FROM python:3.12-slim

# Set environment variables to optimize Python runtime in containers
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set container working directory
WORKDIR /app

# Install system utilities and clean apt cache to minimize image size
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker build cache
COPY requirements.txt .

# Install python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Expose the default Streamlit port
EXPOSE 8501

# Streamlit Healthcheck endpoint
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Launch Streamlit server headlessly on all network interfaces
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
