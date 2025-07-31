# 🐍 Use a minimal, official Python base image
FROM python:3.11-slim

# ✅ Clean Python behavior
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV ENV=production

# 📁 Set working directory inside container
WORKDIR /app

# 📦 Copy and install dependencies first (caching layer)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install -r requirements.txt

# 🔐 Inject environment variables from GitHub Actions or use fallback from file
# ARGs (can be passed from GitHub Actions)
ARG SECRET_KEY
ARG JWT_ALGORITHM
ARG TOKEN_EXPIRY_MINUTES
ARG APP_ENV

# Set ENV vars so FastAPI can access them
ENV SECRET_KEY=${SECRET_KEY}
ENV JWT_ALGORITHM=${JWT_ALGORITHM}
ENV TOKEN_EXPIRY_MINUTES=${TOKEN_EXPIRY_MINUTES}
ENV APP_ENV=${APP_ENV}

# 🗂️ Optional fallback: still copy .env.prod if it exists
COPY .env.prod .env

# 📂 Copy application code (modular and explicit)
COPY main.py .
COPY app/ app/
COPY routers/ routers/
COPY auth/ auth/
COPY utils/ utils/
COPY static/ static/
COPY templates/ templates/

# 🌐 Expose the default FastAPI port
EXPOSE 8000

# 🚀 Start the app using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
