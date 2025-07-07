#!/usr/bin/env python3
"""
Local test script for the ChatterboxTTS RunPod handler
"""

import base64
import json
import os
from rp_handler import handler

def encode_voice_file(voice_path):
    """Encode a voice file to base64"""
    try:
        with open(voice_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        print(f"Voice file not found: {voice_path}")
        return None

def test_handler():
    """Test the handler with sample data"""
    
    # You need to update this path to your actual voice file
    voice_file_path = "../voices/man1.mp3"  # Adjust path as needed
    
    # Encode voice file
    voice_b64 = encode_voice_file(voice_file_path)
    if not voice_b64:
        print("❌ Failed to encode voice file. Please check the path.")
        return
    
    # Prepare test event
    test_event = {
        "input": {
            "text": "Hello world! This is a test of the ChatterboxTTS voice generation system. How does it sound? This text is a bit longer to test the chunking functionality.",
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
    
    print("🧪 Testing ChatterboxTTS handler locally...")
    print(f"📝 Text length: {len(test_event['input']['text'])} characters")
    print(f"🎵 Voice file size: {len(voice_b64)} bytes (base64)")
    
    try:
        # Run the handler
        result = handler(test_event)
        
        if "error" in result:
            print(f"❌ Handler error: {result['error']}")
            if "traceback" in result:
                print(f"📋 Traceback:\n{result['traceback']}")
        else:
            print("✅ Handler completed successfully!")
            print(f"🎵 Audio duration: {result.get('duration', 'unknown')} seconds")
            print(f"📊 Chunks processed: {result.get('chunks_processed', 'unknown')}")
            print(f"📁 Audio size: {result.get('audio_size_bytes', 'unknown')} bytes")
            
            # Save the audio output
            if "audio_data" in result:
                audio_data = base64.b64decode(result["audio_data"])
                output_path = "test_output.wav"
                with open(output_path, "wb") as f:
                    f.write(audio_data)
                print(f"💾 Audio saved to: {output_path}")
            
    except Exception as e:
        print(f"❌ Test failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("ℹ️  For local testing, you'll need ChatterboxTTS installed:")
    print("   Recommended: Use Python 3.11 (as per official documentation)")
    print("   pip install chatterbox-tts")
    print("   Or from source: git clone https://github.com/resemble-ai/chatterbox.git")
    print("   Or run this from a container with ChatterboxTTS installed")
    print()
    
    test_handler()