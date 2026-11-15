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

# Run under gunicorn instead of Flask's development server.
# One worker keeps a single in-process price cache; threads handle concurrency.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "8", "--access-logfile", "-", "app:app"]
