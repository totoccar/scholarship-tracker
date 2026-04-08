FROM python:3.11-slim

WORKDIR /app

RUN apt-get update \
	&& apt-get install -y --no-install-recommends ca-certificates \
	&& rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY models.py base.py scraper.py ./
COPY adapters/ ./adapters/

# El scraper no necesita EXPOSE porque él es quien "llama" a la API, nadie lo llama a él.
CMD ["python", "scraper.py"]