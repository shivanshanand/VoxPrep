import asyncio
from cartesia import Cartesia
from backend.app.config import settings
import wave

async def test_tts():
    """Test Cartesia TTS - Convert text to speech"""
    print("🔊 Testing Text-to-Speech...")
    
    # Initialize Cartesia client
    client = Cartesia(api_key=settings.CARTESIA_API_KEY)
    
    # Text to convert
    test_text = "Hello! I am your AI interview assistant. Let's begin the technical interview."
    
    print(f"Converting text: '{test_text}'")
    
    try:
        # Generate speech
        voice_id = "a0e99841-438c-4a64-b679-ae501e7d6091"  # Cartesia default voice
        
        # Use the SDK to generate audio
        output = client.tts.bytes(
            model_id="sonic-english",
            transcript=test_text,
            voice_id=voice_id,
            output_format={
                "container": "wav",
                "encoding": "pcm_s16le",
                "sample_rate": 16000
            }
        )
        
        # Save to file
        output_file = "test_output.wav"
        with open(output_file, "wb") as f:
            f.write(output["audio"])
        
        print(f"✅ TTS Success! Audio saved to: {output_file}")
        print("▶️  Play the file to hear the output!")
        
        return True
        
    except Exception as e:
        print(f"❌ TTS Error: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_tts())

