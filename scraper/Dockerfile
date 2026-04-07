FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# El scraper no necesita EXPOSE porque él es quien "llama" a la API, nadie lo llama a él.
CMD ["python", "scraper.py"]