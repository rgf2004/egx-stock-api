# Use a lightweight Python image
FROM python:3.10-slim

# Set the directory where our code will live inside the container
WORKDIR /app

# Copy the requirements file first (better for caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy your python script (assuming it's named app.py)
COPY app.py .

# Expose the port Flask runs on
EXPOSE 5000

# Run the application
# We use --host=0.0.0.0 so it's accessible outside the container
CMD ["python", "app.py"]

