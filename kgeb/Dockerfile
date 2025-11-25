FROM python:3.11-slim

WORKDIR /app

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create output directory
RUN mkdir -p output

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["python", "src/pipeline.py", "../documents.txt"]
