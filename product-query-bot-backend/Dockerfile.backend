# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install dependencies
COPY requirements.txt .
# Aumentamos el timeout de pip a 600 segundos (10 minutos)
RUN pip install --no-cache-dir -r requirements.txt --default-timeout=600

# Copy the application code into the container
COPY ./app /app/app
COPY ./data /app/data
COPY ./.env.example /app/.env.example

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
