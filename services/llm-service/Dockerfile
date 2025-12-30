FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY services/llm-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared code
COPY shared/ /app/shared/

# Copy service code
COPY services/llm-service/ /app/

# Expose port
EXPOSE 8000

# Run service
CMD ["python", "main.py"]

