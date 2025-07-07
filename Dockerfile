# Use RunPod PyTorch image (verified to work)
FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04

# Install Python 3.11 alongside existing Python 3.10
RUN apt-get update && apt-get install -y \
    software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y \
    python3.11 \
    python3.11-dev \
    python3.11-distutils \
    git \
    wget \
    curl \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Install pip for Python 3.11
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN python3.11 -m pip install --no-cache-dir -r requirements.txt

# Install ChatterboxTTS - try PyPI first, fallback to GitHub
RUN python3.11 -m pip install chatterbox-tts || \
    (git clone https://github.com/resemble-ai/chatterbox.git && \
     cd chatterbox && \
     python3.11 -m pip install -e .)

# Copy the handler
COPY rp_handler.py .

# Set Python path
ENV PYTHONPATH=/app:$PYTHONPATH

# Expose the port (RunPod will handle this)
EXPOSE 8000

# Run the handler
CMD ["python3.11", "rp_handler.py"] 