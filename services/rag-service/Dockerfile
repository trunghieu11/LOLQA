FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY services/rag-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared code
COPY shared/ /app/shared/

# Copy src code (for existing RAG system)
COPY src/ /app/src/

# Copy service code
COPY services/rag-service/ /app/

# Expose port
EXPOSE 8000

# Run service
CMD ["python", "main.py"]

