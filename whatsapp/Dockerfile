FROM node:20-slim

# Install system dependencies for Chromium and Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    chromium \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Set environment variables for Puppeteer
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

# Copy Node.js dependencies
COPY package*.json ./
RUN npm install

# Copy Python dependencies (if they were in a requirements.txt, but for now we install manually based on run_api.py)
RUN pip3 install --no-cache-dir fastapi uvicorn requests pydantic --break-system-packages

# Copy application code
COPY . .

# Create a startup script
RUN echo '#!/bin/bash\n\
if [ -z "$PHONE_NUMBER_SERIALIZED" ]; then \n\
  echo "No PHONE_NUMBER_SERIALIZED found in environment." \n\
  echo "Please enter your 10-digit phone number (or press enter to skip): " \n\
  read -t 10 input_phone \n\
  if [ ! -z "$input_phone" ]; then \n\
    export PHONE_NUMBER_SERIALIZED=$input_phone \n\
  fi \n\
fi \n\
npx tsx main.ts & \n\
python3 run_api.py & \n\
wait -n' > /app/start.sh && chmod +x /app/start.sh

EXPOSE 3001
EXPOSE 5000

CMD ["/app/start.sh"]
