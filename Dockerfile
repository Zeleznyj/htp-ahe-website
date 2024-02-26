FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Install any needed dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8000 to the outside world
EXPOSE 8000

# Run gunicorn when the container launches
CMD ["gunicorn","-b","0.0.0.0:8000", "index:server"]
