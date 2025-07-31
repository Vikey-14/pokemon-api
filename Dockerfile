# 🐍 Use a minimal, official Python base image for production
FROM python:3.11-slim

# 🧼 Prevent Python from generating .pyc files (cleaner) and ensure real-time logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 🔐 Optional: Set a default ENV (FastAPI can read this if needed)
ENV ENV=production

# 📁 Set working directory inside container
WORKDIR /app

# 📦 Copy requirements file first (leverage layer caching)
COPY requirements.txt .

# 🛠 Install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# ❌ REMOVE build ARG (NOT supported in COPY)
# ARG ENV_FILE=.env.prod

# ✅ FIXED: Copy the correct env file directly (no ARG)
COPY .env.prod .env

# 📂 Copy the full FastAPI project (routers, auth, static files, etc.)
COPY . .

# 🌐 Expose port 8000 for FastAPI app
EXPOSE 8000

# 🚀 Launch app with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
