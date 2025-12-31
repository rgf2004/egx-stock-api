# Use a lightweight Python image
FROM python:3.10-slim

# Set the directory where our code will live inside the container
WORKDIR /app

# Copy the requirements file first (better for caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire 'app' directory contents into the container
# This copies app.py, templates/, and static/ all at once
COPY app/ .

# Expose the port Flask runs on
EXPOSE 5000

# Run the application
# Since app.py is now in the container's root (/app), we run it directly
CMD ["python", "app.py"]
