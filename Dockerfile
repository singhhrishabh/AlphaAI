FROM python:3.11-slim

WORKDIR /app

# Copy and install requirements first (better Docker caching)
COPY requirements-hf.txt .
RUN pip install --no-cache-dir --timeout 120 -r requirements-hf.txt

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p /app/data /app/reports/generated

# HF Spaces uses port 7860
ENV PORT=7860
ENV HF_SPACES=true
ENV PYTHONUNBUFFERED=1

EXPOSE 7860

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "7860"]
