# 🐍 Use a minimal, official Python base image
FROM python:3.11-slim

# ✅ Clean Python behavior
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV ENV=production

# 📁 Set working directory inside container
WORKDIR /app

# 📦 Install dependencies first (cached)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install -r requirements.txt

# 🔐 Inject secrets via GitHub Actions
ARG SECRET_KEY
ARG JWT_ALGORITHM
ARG TOKEN_EXPIRY_MINUTES
ARG APP_ENV

ENV SECRET_KEY=${SECRET_KEY}
ENV JWT_ALGORITHM=${JWT_ALGORITHM}
ENV TOKEN_EXPIRY_MINUTES=${TOKEN_EXPIRY_MINUTES}
ENV APP_ENV=${APP_ENV}

# 📂 Copy only what's needed to run the backend
COPY main.py .
COPY app/ app/
COPY routers/ routers/
COPY auth/ auth/
COPY utils/ utils/

# 🌐 Expose FastAPI port
EXPOSE 8000

# 🚀 Start the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
