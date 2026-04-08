# Use a slim Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code
COPY main.py .

# Create a volume for input/output data
RUN mkdir /data
VOLUME /data

# Set the entrypoint to the python script
ENTRYPOINT ["python", "main.py"]

# Default command shows help
CMD ["--help"]
