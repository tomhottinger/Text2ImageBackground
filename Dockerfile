FROM python:3.11-slim



WORKDIR /app



# Install system dependencies

RUN apt-get update && apt-get install -y \

    fonts-dejavu-core \

    && rm -rf /var/lib/apt/lists/*



# Copy requirements

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt



# Copy application

COPY app.py .

COPY templates/ templates/



# Create directories

RUN mkdir -p uploads sample_images



# Expose port

EXPOSE 5000



# Run with gunicorn for production

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]
