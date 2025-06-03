# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Copy semua file kode dan requirements
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port default Streamlit (atau sesuaikan kalau pakai Flask/FastAPI)
EXPOSE 8501

# Jalankan aplikasi
# Jika pakai Streamlit:
CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
# Jika pakai Flask:
# CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8501"]