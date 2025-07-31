# 🐍 Use official Python base image
FROM python:3.11-slim

# ✅ Set clean Python behavior
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 📁 Set working directory
WORKDIR /app

# 📦 Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install -r requirements.txt

# 📂 Core app files
COPY main.py .
COPY core_app.py .
COPY config.py .
COPY custom_logger.py .
COPY logger_middleware.py .
COPY audit_logger.py .

# 📂 Include modules and source folders
COPY auth/ auth/
COPY routers/ routers/
COPY utils/ utils/
COPY dependencies/ dependencies/
COPY models/ models/
COPY users/ users/

# 📂 Templates and static assets
COPY templates/ templates/
COPY static/ static/

# 📂 JSON data (Pokedex, team data, etc.)
COPY data/ data/

# 📂 Optional: logs folder to enable logging in container
COPY logs/ logs/

# 🔐 Load environment config (from CI or fallback local)
COPY .env.prod.ci .env

# 🌐 Expose FastAPI port
EXPOSE 8000

# 🚀 Run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
