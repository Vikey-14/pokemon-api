# 🐍 Use a minimal, official Python base image
FROM python:3.11-slim

# ✅ Clean Python behavior
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 📁 Set working directory
WORKDIR /app

# 📦 Install dependencies (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install -r requirements.txt

# 📂 Copy only necessary source files
COPY main.py .
COPY config.py .
COPY core_app.py .
COPY routers/ routers/
COPY auth/ auth/
COPY utils/ utils/
COPY static/ static/
COPY templates/ templates/

# 🔐 Copy CI environment config as production .env
COPY .env.prod.ci .env

# 🌐 Expose FastAPI port
EXPOSE 8000

# 🚀 Run app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
