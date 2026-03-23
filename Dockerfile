FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt

# Copy project
COPY . .

# Install the package
RUN pip install -e .

# Expose port
EXPOSE 8000

# Run the dashboard
CMD ["python", "-m", "dashboard.main"]