FROM python:3.13-slim

#RUN apt-get update && apt-get install -y gcc g++ libffi-dev && apt-get clean && rm -rf /var/lib/apt/lists/*
    
WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "-m", "api.server"]
