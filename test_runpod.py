#!/usr/bin/env python3
"""
Test script for ChatterboxTTS RunPod Serverless Function
"""

import requests
import json
import base64
import time
import os

# Configuration
RUNPOD_ENDPOINT = "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync"  # Replace with your actual endpoint
RUNPOD_API_KEY = "YOUR_API_KEY"  # Replace with your RunPod API key

def encode_voice_file(voice_path):
    """Encode a voice file to base64"""
    try:
        with open(voice_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        print(f"❌ Voice file not found: {voice_path}")
        return None

def test_runpod_endpoint():
    """Test the RunPod serverless endpoint"""
    
    # Test data - 180-200 word script for comprehensive testing
    test_text = """
    Picture this: It's 3 AM, and I'm scrolling through TikTok when I stumble upon the most mind-blowing conspiracy theory I've ever heard. 
    Apparently, dolphins are actually alien spies sent to monitor our beach activities. I know, I know, it sounds crazy, but hear me out.
    
    Think about it - dolphins are incredibly intelligent, they communicate in ways we don't fully understand, and they're always watching us from the water. 
    Plus, have you ever seen a dolphin blink? Exactly. That's because they don't have eyelids like Earth creatures should.
    
    But here's where it gets really wild. My friend Jake, who works at SeaWorld, told me that dolphins there have been acting strange lately. 
    They keep forming perfect geometric patterns in the water, almost like they're transmitting signals. And get this - every time a new iPhone is released, 
    the dolphins get more active. Coincidence? I think not.
    
    Now I can't go to the beach without feeling like I'm being watched. Every time I see a dolphin, I wave, just in case they're reporting back to their mothership. 
    Better safe than sorry, right?
    """
    
    # Encode voice file (update path as needed)
    voice_file_path = "../voices/man1.mp3"  # Adjust path to your voice file
    voice_b64 = encode_voice_file(voice_file_path)
    
    if not voice_b64:
        print("❌ Failed to encode voice file. Please check the path.")
        return
    
    # Prepare request payload
    payload = {
        "input": {
            "text": test_text.strip(),
            "voice_file": voice_b64,
            "settings": {
                "exaggeration": 0.7,
                "cfg_weight": 0.5,
                "temperature": 0.8,
                "min_p": 0.05,
                "top_p": 1.0,
                "repetition_penalty": 1.2
            }
        }
    }
    
    # Headers
    headers = {
        "Authorization": f"Bearer {RUNPOD_API_KEY}",
        "Content-Type": "application/json"
    }
    
    print("🚀 Testing RunPod ChatterboxTTS Serverless Function...")
    print(f"📝 Text length: {len(test_text)} characters")
    print(f"🎵 Voice file size: {len(voice_b64)} base64 characters")
    print("⏳ Sending request...")
    
    try:
        # Send request
        start_time = time.time()
        response = requests.post(RUNPOD_ENDPOINT, json=payload, headers=headers, timeout=300)
        end_time = time.time()
        
        print(f"⏱️  Request took: {end_time - start_time:.2f} seconds")
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Request successful!")
            print(f"📄 Response: {json.dumps(result, indent=2)}")
            
            # Save audio if present
            if "output" in result and "audio_base64" in result["output"]:
                audio_data = base64.b64decode(result["output"]["audio_base64"])
                output_file = "test_output.wav"
                with open(output_file, "wb") as f:
                    f.write(audio_data)
                print(f"🎵 Audio saved to: {output_file}")
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out after 5 minutes")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_with_curl():
    """Generate curl command for testing"""
    print("\n" + "="*50)
    print("🔧 CURL Command for Testing:")
    print("="*50)
    
    curl_command = f'''curl -X POST "{RUNPOD_ENDPOINT}" \\
  -H "Authorization: Bearer {RUNPOD_API_KEY}" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "input": {{
      "text": "Hello world! This is a test of ChatterboxTTS on RunPod.",
      "voice_file": "BASE64_ENCODED_VOICE_FILE_HERE",
      "settings": {{
        "exaggeration": 0.5,
        "cfg_weight": 0.5,
        "temperature": 0.8,
        "min_p": 0.05,
        "top_p": 1.0,
        "repetition_penalty": 1.2
      }}
    }}
  }}' '''
    
    print(curl_command)

if __name__ == "__main__":
    print("🧪 ChatterboxTTS RunPod Serverless Test")
    print("=" * 50)
    
    # Check if configuration is set
    if RUNPOD_ENDPOINT == "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync":
        print("⚠️  Please update RUNPOD_ENDPOINT with your actual endpoint URL")
        print("⚠️  Please update RUNPOD_API_KEY with your actual API key")
        print()
        test_with_curl()
    else:
        test_runpod_endpoint() 