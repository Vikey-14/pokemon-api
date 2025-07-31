# 🐍 Use a minimal, official Python base image
FROM python:3.11-slim

# ✅ Clean Python behavior
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 📁 Set working directory inside the container
WORKDIR /app

# 📦 Install Python dependencies (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install -r requirements.txt

# 📂 Copy application core files
COPY main.py .
COPY config.py .
COPY core_app.py .
COPY custom_logger.py .
COPY logger_middleware.py .

# 📁 Copy modular folders
COPY auth/ auth/
COPY routers/ routers/
COPY utils/ utils/
COPY static/ static/
COPY templates/ templates/

# 🔐 Inject environment config (from CI or local fallback)
COPY .env.prod.ci .env

# 🌐 Expose FastAPI port
EXPOSE 8000

# 🚀 Run the FastAPI app using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
