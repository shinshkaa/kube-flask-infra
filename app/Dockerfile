FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN useradd -u 8888 appuser

COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 8080

CMD [ "python3", "app.py" ]