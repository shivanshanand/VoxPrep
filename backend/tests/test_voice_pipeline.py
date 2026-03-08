import asyncio
from cartesia import Cartesia
import assemblyai as aai
from backend.app.config import settings

async def test_full_pipeline():
    """Test complete voice pipeline: Text → Speech → Text"""
    print("🔄 Testing Full Voice Pipeline...")
    
    original_text = "FastAPI is a modern web framework for building APIs with Python."
    print(f"\n📝 Original text: '{original_text}'")
    
    # Step 1: TTS
    print("\n🔊 Step 1: Converting to speech...")
    client = Cartesia(api_key=settings.CARTESIA_API_KEY)
    
    output = client.tts.bytes(
        model_id="sonic-english",
        transcript=original_text,
        voice_id="a0e99841-438c-4a64-b679-ae501e7d6091",
        output_format={
            "container": "wav",
            "encoding": "pcm_s16le",
            "sample_rate": 16000
        }
    )
    
    # Save audio
    audio_file = "pipeline_test.wav"
    with open(audio_file, "wb") as f:
        f.write(output["audio"])
    print(f"✅ Audio generated: {audio_file}")
    
    # Step 2: STT
    print("\n🎤 Step 2: Transcribing speech back to text...")
    aai.settings.api_key = settings.ASSEMBLYAI_API_KEY
    
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_file)
    
    transcribed_text = transcript.text
    print(f"✅ Transcribed text: '{transcribed_text}'")
    
    # Compare
    print("\n📊 Comparison:")
    print(f"Original:    {original_text}")
    print(f"Transcribed: {transcribed_text}")
    print(f"\n✅ Pipeline test complete!")
    
    # Simple accuracy check
    if original_text.lower() in transcribed_text.lower() or transcribed_text.lower() in original_text.lower():
        print("🎉 Texts match (approximately)!")
    else:
        print("⚠️  Texts differ - but that's normal for TTS→STT round trip")

if __name__ == "__main__":
    asyncio.run(test_full_pipeline())
