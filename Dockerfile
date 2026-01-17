FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# RESTORE STANDARD STRUCTURE (Safest for Imports)
COPY . .

EXPOSE 8080

# Clean Exec Form - NO PORT FLAG - Use Module Path
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0"]
