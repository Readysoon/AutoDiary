FROM python:3.12.7 as builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create a directory with all binaries we need to copy
RUN mkdir /app/binaries && \
    cp /usr/local/bin/uvicorn /app/binaries/ && \
    cp -r /usr/local/lib/python3.12/site-packages /app/binaries/

FROM python:3.12-slim
WORKDIR /app

# Copy both site-packages AND binaries
COPY --from=builder /app/binaries/uvicorn /usr/local/bin/uvicorn
COPY --from=builder /app/binaries/site-packages /usr/local/lib/python3.12/site-packages

COPY . .

# Verify installation (optional - can remove after debugging)
RUN which uvicorn && uvicorn --version

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
