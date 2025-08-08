FROM python:3.10.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY main4.py .

ENV LMSTUDIO_API_URL=http://host.docker.internal:1234

CMD ["python", "main4.py"]
