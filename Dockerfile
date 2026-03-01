# Use official Python image
FROM python:3.12-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK punkt tokenizer
RUN python -m nltk.downloader punkt

# Copy the rest of your code
COPY ./app ./app

# Expose port
EXPOSE 8000

# Default command to run
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]