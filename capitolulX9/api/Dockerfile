FROM python:3.9-slim

WORKDIR /app

# psycopg2-binary needs libpq — included in the binary wheel, no extra apt needed
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 5001

CMD ["python", "app.py"]
