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

# 📂 Copy core app files (modular structure)
COPY main.py .
COPY config.py .
COPY core_app.py .
COPY routers/ routers/
COPY auth/ auth/
COPY utils/ utils/
COPY static/ static/
COPY templates/ templates/

# 🔐 Auto-injected env from GitHub CI or fallback to local .env
# If building locally, .env should exist in context.
# If building via GitHub, ensure .env.prod.ci is pre-placed.
COPY .env.prod.ci .env

# 🌐 Expose FastAPI port
EXPOSE 8000

# 🚀 Run app with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
