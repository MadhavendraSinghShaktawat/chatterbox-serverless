# ChatterboxTTS RunPod Serverless

This directory contains the RunPod serverless implementation of voice generation using ChatterboxTTS.

## Overview

This serverless function provides:
- High-performance voice generation using ChatterboxTTS
- GPU-accelerated processing (A6000/A40/RTX4090)
- Automatic scaling and pay-per-use billing
- Text chunking for long content
- Base64 audio input/output
- Python 3.11 compatibility (as recommended by ChatterboxTTS)

## Files

- `rp_handler.py` - Main RunPod serverless handler
- `requirements.txt` - Python dependencies
- `Dockerfile` - Container configuration
- `test_input.json` - Sample input for testing
- `README.md` - This file

## Setup Requirements

### 1. ChatterboxTTS Integration

✅ **AUTOMATIC**: ChatterboxTTS is automatically installed during the Docker build process.

The Dockerfile will:
- First try installing from PyPI (`pip install chatterbox-tts`)
- Fallback to GitHub installation from the official repository (`resemble-ai/chatterbox`)
- Make it available to the handler with proper imports
- Handle any dependency conflicts automatically

No manual setup required!

### 2. Voice Files

The handler expects voice files to be base64 encoded. You can encode your reference voices:

```python
import base64

with open("path/to/voice.wav", "rb") as f:
    voice_b64 = base64.b64encode(f.read()).decode()
    print(voice_b64)  # Use this in your API calls
```

## Local Testing

**Note**: ChatterboxTTS is developed and tested on Python 3.11 on Debian 11 OS.

1. Install dependencies:
```bash
# Recommended: Use Python 3.11
pip install -r requirements.txt
pip install chatterbox-tts
# OR install from source:
# git clone https://github.com/resemble-ai/chatterbox.git
# cd chatterbox && pip install -e .
```

2. Test the handler locally:
```python
from rp_handler import handler

# Prepare test event
event = {
    "input": {
        "text": "Hello world!",
        "voice_file": "your_base64_encoded_voice_file",
        "settings": {
            "exaggeration": 0.5,
            "cfg_weight": 0.5,
            "temperature": 0.8
        }
    }
}

result = handler(event)
print(result)
```

## Testing with RunPod Endpoint

For testing the deployed RunPod endpoint, set up environment variables for security:

1. Create a `.env` file (never commit this):
```bash
RUNPOD_ENDPOINT=https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run
RUNPOD_API_KEY=your_actual_runpod_api_key
```

2. Run the test scripts:
```bash
# JavaScript/Node.js test
RUNPOD_ENDPOINT=https://api.runpod.ai/v2/abc123/run RUNPOD_API_KEY=your_key node test_runpod.js

# Python test
RUNPOD_ENDPOINT=https://api.runpod.ai/v2/abc123/run RUNPOD_API_KEY=your_key python test_runpod.py
```

**Important**: Never commit API keys to version control. The `.env` file is already ignored by `.gitignore`.

## Deployment to RunPod

### Option 1: Docker Hub

1. Build and push the Docker image:
```bash
docker build -t your-username/chatterbox-serverless .
docker push your-username/chatterbox-serverless
```

2. In RunPod Console:
   - Go to Serverless → New Endpoint
   - Select "Custom Source" → "Docker Image"
   - Enter: `your-username/chatterbox-serverless:latest`
   - Configure GPU (recommended: RTX 4090 or A6000)
   - Set workers and scaling settings
   - Create Endpoint

### Option 2: GitHub Integration

1. Push this code to GitHub
2. In RunPod Console:
   - Go to Serverless → New Endpoint
   - Select "Custom Source" → "GitHub"
   - Connect your repository
   - RunPod will auto-build and deploy

## API Usage

Once deployed, you can call your endpoint:

```python
import requests
import base64

# Encode your voice file
with open("voice.wav", "rb") as f:
    voice_b64 = base64.b64encode(f.read()).decode()

# API call
response = requests.post(
    "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync",
    headers={
        "Authorization": "Bearer YOUR_API_KEY",
        "Content-Type": "application/json"
    },
    json={
        "input": {
            "text": "Your text to convert to speech",
            "voice_file": voice_b64,
            "settings": {
                "exaggeration": 0.5,
                "cfg_weight": 0.5,
                "temperature": 0.8,
                "min_p": 0.05,
                "top_p": 1.0,
                "repetition_penalty": 1.2
            }
        }
    }
)

result = response.json()
if result.get("success"):
    # Decode the audio
    audio_data = base64.b64decode(result["audio_data"])
    with open("output.wav", "wb") as f:
        f.write(audio_data)
```

## Integration with Your App

To integrate with your existing voice generation API, update your `/api/generate-voice` route:

```typescript
// Replace the Python spawn process with RunPod call
const runpodResponse = await fetch(`https://api.runpod.ai/v2/${RUNPOD_ENDPOINT_ID}/runsync`, {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${process.env.RUNPOD_API_KEY}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        input: {
            text: cleanText,
            voice_file: voiceFileBase64,
            settings: settings
        }
    })
});

const result = await runpodResponse.json();
if (result.success) {
    const audioBuffer = Buffer.from(result.audio_data, 'base64');
    // Upload to Google Cloud Storage as before
}
```

## Performance Expectations

- **RTX 4090**: ~15-30 seconds for typical script
- **A6000**: ~10-20 seconds for typical script  
- **A40**: ~20-40 seconds for typical script

Much faster than your current 5+ minute local generation!

## Cost Estimates

- RTX 4090: ~$0.0004/second = $0.006-0.012 per generation
- A6000: ~$0.0008/second = $0.008-0.016 per generation
- A40: ~$0.0006/second = $0.006-0.024 per generation

## Troubleshooting

1. **ChatterboxTTS not found**: Make sure you copied the chatterbox directory
2. **CUDA out of memory**: Try reducing chunk size or using CPU fallback
3. **Model loading issues**: Check that all dependencies are in requirements.txt
4. **Voice file issues**: Ensure voice files are properly base64 encoded

## Testing Your Deployment

### 1. **Get Your RunPod Endpoint Details**
After deployment, you'll get:
- **Endpoint URL**: `https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync`
- **API Key**: From your RunPod account settings

### 2. **Test with Python Script**
```bash
# Update the configuration in test_runpod.py
python test_runpod.py
```

### 3. **Test with JavaScript/Node.js**
```bash
# Update the configuration in test_runpod.js
node test_runpod.js
```

### 4. **Test with Postman**

**Request Setup:**
- **Method**: `POST`
- **URL**: `https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync`
- **Headers**:
  - `Authorization: Bearer YOUR_API_KEY`
  - `Content-Type: application/json`

**Body (JSON):**
```json
{
  "input": {
    "text": "Hello world! This is a test of ChatterboxTTS on RunPod.",
    "voice_file": "BASE64_ENCODED_VOICE_FILE_HERE",
    "settings": {
      "exaggeration": 0.5,
      "cfg_weight": 0.5,
      "temperature": 0.8,
      "min_p": 0.05,
      "top_p": 1.0,
      "repetition_penalty": 1.2
    }
  }
}
```

**Expected Response:**
```json
{
  "delayTime": 1234,
  "executionTime": 5678,
  "id": "request-id",
  "output": {
    "audio_base64": "base64-encoded-audio-data",
    "message": "Voice generation completed successfully",
    "processing_time": 15.3,
    "text_length": 50,
    "chunk_count": 1
  },
  "status": "COMPLETED"
}
```

### 5. **Test with cURL**
```bash
curl -X POST "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "text": "Hello world! This is a test of ChatterboxTTS on RunPod.",
      "voice_file": "BASE64_ENCODED_VOICE_FILE_HERE",
      "settings": {
        "exaggeration": 0.5,
        "cfg_weight": 0.5,
        "temperature": 0.8,
        "min_p": 0.05,
        "top_p": 1.0,
        "repetition_penalty": 1.2
      }
    }
  }'
```

## Next Steps

1. ✅ **Build completed successfully!**
2. Deploy your endpoint on RunPod
3. Get your endpoint URL and API key
4. Test using the provided test files
5. Update your main app to use the RunPod endpoint
6. Monitor performance and costs 

Add Environment Variables (Optional but helpful)
Click "Add Environment Variable" and add:
PYTHONUNBUFFERED=1 (for better logging)
CUDA_VISIBLE_DEVICES=0 (ensure GPU is visible)