# Dockerfile for WhatsApp Scraper

# Use Python 3.11 slim as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for Chrome and Selenium
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    xvfb \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome (step by step method)
RUN wget -q -O /tmp/google-chrome-stable.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get update
RUN dpkg -i /tmp/google-chrome-stable.deb || apt-get install -y -f
RUN apt-get install -y -f
RUN rm /tmp/google-chrome-stable.deb
RUN rm -rf /var/lib/apt/lists/*

# Create Chrome profile directory
RUN mkdir -p /app/chrome_profile

# Copy WhatsApp scraper requirements file first (for better Docker layer caching)
COPY whatsapp_scraper/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared database code
COPY ../db/ ./db/

# Copy WhatsApp scraper code
COPY . ./whatsapp_scraper/

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV CHROME_HEADLESS=true
ENV DISPLAY=:99

# Expose port if needed
EXPOSE 8080

# Default command - run the scraper with asyncio
CMD ["python", "-c", "import asyncio; from whatsapp_scraper.main import collect_todays_messages; asyncio.run(collect_todays_messages())"]
