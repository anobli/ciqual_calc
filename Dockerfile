FROM python:3.11-slim

# Install curl and build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Setup database and import CIQUAL data
ENV FILE_PATH="/app/db_data/ciqual.xlsx"
ENV CIQUAL_URL="https://ciqual.anses.fr/cms/sites/default/files/inline-files/Table%20Ciqual%202025_FR_2025_11_03.xlsx"

RUN mkdir -p /app/db_data/ && \
    curl -L -A "Mozilla/5.0" "$CIQUAL_URL" -o "$FILE_PATH" && \
    python manage.py makemigrations ciqual_calc && \
    python manage.py migrate --noinput && \
    python manage.py import_ciqual "$FILE_PATH"

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]