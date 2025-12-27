FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY services/ui-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared code
COPY shared/ /app/shared/

# Copy service code
COPY services/ui-service/ /app/

# Expose port
EXPOSE 8501

# Run service
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]

