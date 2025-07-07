import runpod
import torch
import torchaudio as ta
import base64
import io
import sys
import os
import traceback
import re
from pathlib import Path
import tempfile

# Setup ChatterboxTTS
def setup_chatterbox_path():
    """Setup and verify ChatterboxTTS is available"""
    try:
        # Try to import the installed package
        import chatterbox_tts
        return True
    except ImportError:
        try:
            # Fallback: try alternative import
            import chatterbox
            return True
        except ImportError:
            print("❌ ChatterboxTTS not found. Please install with: pip install chatterbox-tts")
            return False

def clean_script_for_tts(text: str) -> str:
    """Clean script text for TTS generation"""
    # Remove stage directions and metrics
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\(.*?\)', '', text)
    
    # Remove metrics/stats sections
    lines = text.split('\n')
    cleaned_lines = []
    skip_section = False
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
            
        # Skip metrics sections
        if any(keyword in line.lower() for keyword in ['views:', 'engagement:', 'metrics:', 'statistics:', 'performance:']):
            skip_section = True
            continue
        
        # Reset skip section on new paragraph
        if skip_section and line and not line.startswith('-') and not line.startswith('•'):
            skip_section = False
        
        if not skip_section:
            cleaned_lines.append(line)
    
    # Join and clean up extra whitespace
    cleaned_text = ' '.join(cleaned_lines)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
    
    return cleaned_text.strip()

def split_text_into_chunks(text: str, max_length: int = 150) -> list:
    """Split text into manageable chunks for processing"""
    if len(text) <= max_length:
        return [text]
    
    # Split by sentences first
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    
    for sentence in sentences:
        if len(sentence) <= max_length:
            # Try to combine with previous chunk
            if chunks and len(chunks[-1] + " " + sentence) <= max_length:
                chunks[-1] += " " + sentence
            else:
                chunks.append(sentence)
        else:
            # Split long sentences by words
            words = sentence.split()
            current_chunk = ""
            
            for word in words:
                test_chunk = current_chunk + (" " if current_chunk else "") + word
                if len(test_chunk) <= max_length:
                    current_chunk = test_chunk
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = word
            
            if current_chunk:
                chunks.append(current_chunk.strip())
    
    return [chunk for chunk in chunks if chunk.strip()]

def handler(event):
    """
    RunPod serverless handler for voice generation
    
    Expected input:
    {
        "text": "Text to convert to speech",
        "voice_file": "base64 encoded voice file",
        "settings": {
            "exaggeration": 0.5,
            "cfg_weight": 0.5,
            "temperature": 0.8,
            "min_p": 0.05,
            "top_p": 1.0,
            "repetition_penalty": 1.2
        }
    }
    """
    
    try:
        print("=== Chatterbox TTS RunPod Handler ===")
        print(f"PyTorch version: {torch.__version__}")
        
        # Extract input data
        input_data = event.get("input", {})
        text = input_data.get("text", "")
        voice_file_b64 = input_data.get("voice_file", "")
        settings = input_data.get("settings", {})
        
        if not text or not voice_file_b64:
            return {
                "error": "Both 'text' and 'voice_file' are required"
            }
        
        print(f"Processing text: {len(text)} characters")
        
        # Setup ChatterboxTTS
        if not setup_chatterbox_path():
            return {
                "error": "ChatterboxTTS not found in container"
            }
        
        try:
            from chatterbox_tts import ChatterboxTTS
        except ImportError:
            from chatterbox.tts import ChatterboxTTS
        print("Successfully imported ChatterboxTTS")
        
        # Setup device
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {device}")
        
        if device == "cuda":
            print(f"GPU: {torch.cuda.get_device_name()}")
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            print(f"GPU Memory: {gpu_memory:.1f}GB")
        
        # Load model
        print("Loading ChatterboxTTS model...")
        model = ChatterboxTTS.from_pretrained(device=device)
        print("Model loaded successfully")
        
        # Clean text
        clean_text = clean_script_for_tts(text)
        print(f"Cleaned text: {len(clean_text)} characters")
        
        # Decode voice file
        try:
            voice_data = base64.b64decode(voice_file_b64)
            print(f"Voice file decoded: {len(voice_data)} bytes")
        except Exception as e:
            return {
                "error": f"Failed to decode voice file: {str(e)}"
            }
        
        # Save voice file temporarily
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_voice:
            temp_voice.write(voice_data)
            voice_path = temp_voice.name
        
        try:
            # Extract settings
            exaggeration = settings.get("exaggeration", 0.5)
            cfg_weight = settings.get("cfg_weight", 0.5)
            temperature = settings.get("temperature", 0.8)
            min_p = settings.get("min_p", 0.05)
            top_p = settings.get("top_p", 1.0)
            repetition_penalty = settings.get("repetition_penalty", 1.2)
            
            print(f"Generation settings: exaggeration={exaggeration}, cfg_weight={cfg_weight}, temperature={temperature}")
            
            # Split text into chunks if needed
            chunks = split_text_into_chunks(clean_text, max_length=150)
            print(f"Split into {len(chunks)} chunks")
            
            all_wavs = []
            
            for i, chunk in enumerate(chunks):
                print(f"Processing chunk {i+1}/{len(chunks)}: {len(chunk)} chars")
                
                try:
                    chunk_wav = model.generate(
                        chunk,
                        audio_prompt_path=voice_path,
                        exaggeration=exaggeration,
                        cfg_weight=cfg_weight,
                        temperature=temperature,
                        min_p=min_p,
                        top_p=top_p,
                        repetition_penalty=repetition_penalty
                    )
                    
                    all_wavs.append(chunk_wav)
                    print(f"Chunk {i+1} completed successfully")
                    
                    # Add small pause between chunks
                    if i < len(chunks) - 1:  # Don't add pause after last chunk
                        pause_samples = int(0.2 * 24000)  # 0.2 second pause
                        pause = torch.zeros(pause_samples, device=chunk_wav.device)
                        all_wavs.append(pause)
                        
                except Exception as chunk_error:
                    print(f"Chunk {i+1} failed: {chunk_error}")
                    raise chunk_error
            
            # Concatenate all audio chunks
            if len(all_wavs) > 1:
                # Ensure all tensors have the same dimensions before concatenating
                processed_wavs = []
                for i, wav in enumerate(all_wavs):
                    print(f"Chunk {i+1} original shape: {wav.shape}")
                    
                    # Ensure tensor is 1D
                    if wav.dim() == 2:
                        # If 2D, take the first channel or flatten
                        if wav.shape[0] == 1:
                            wav = wav.squeeze(0)  # Remove channel dimension
                        elif wav.shape[1] == 1:
                            wav = wav.squeeze(1)  # Remove channel dimension
                        else:
                            wav = wav.mean(dim=0)  # Average channels if multiple
                    elif wav.dim() > 2:
                        # Flatten higher dimensional tensors
                        wav = wav.flatten()
                    
                    processed_wavs.append(wav)
                    print(f"Chunk {i+1} processed shape: {wav.shape}")
                
                final_wav = torch.cat(processed_wavs, dim=0)
                print("Successfully concatenated audio chunks")
            else:
                final_wav = all_wavs[0]
                # Ensure final output is 1D
                if final_wav.dim() == 2:
                    if final_wav.shape[0] == 1:
                        final_wav = final_wav.squeeze(0)
                    elif final_wav.shape[1] == 1:
                        final_wav = final_wav.squeeze(1)
                    else:
                        final_wav = final_wav.mean(dim=0)
            
            # Move to CPU for conversion
            final_wav = final_wav.cpu()
            
            # Convert to bytes
            audio_bytes = io.BytesIO()
            ta.save(audio_bytes, final_wav.unsqueeze(0), 24000, format="wav")
            audio_data = audio_bytes.getvalue()
            
            # Encode to base64
            audio_b64 = base64.b64encode(audio_data).decode('utf-8')
            
            duration = len(final_wav) / 24000
            
            print(f"Generation completed successfully")
            print(f"Duration: {duration:.2f} seconds")
            print(f"Audio data size: {len(audio_data)} bytes")
            
            return {
                "audio_base64": audio_b64,
                "message": "Voice generation completed successfully",
                "processing_time": duration,
                "text_length": len(clean_text),
                "chunk_count": len(chunks),
                "sample_rate": 24000,
                "duration": duration,
                "audio_size_bytes": len(audio_data)
            }
            
        finally:
            # Cleanup temporary voice file
            try:
                os.unlink(voice_path)
            except:
                pass
    
    except Exception as e:
        print(f"Handler error: {str(e)}")
        print("Traceback:", traceback.format_exc())
        return {
            "error": str(e),
            "traceback": traceback.format_exc()
        }

# Start the RunPod serverless function
if __name__ == "__main__":
    runpod.serverless.start({"handler": handler}) 