import assemblyai as aai
from backend.app.config import settings

def test_stt_from_file():
    """Test Assembly AI STT - Convert audio file to text"""
    print("🎤 Testing Speech-to-Text...")
    
    # Set API key
    aai.settings.api_key = settings.ASSEMBLYAI_API_KEY
    
    # You can use the file we generated from TTS test!
    audio_file = "test_output.wav"
    
    print(f"Transcribing audio file: {audio_file}")
    
    try:
        # Create transcriber
        transcriber = aai.Transcriber()
        
        # Transcribe
        transcript = transcriber.transcribe(audio_file)
        
        if transcript.status == aai.TranscriptStatus.error:
            print(f"❌ Transcription failed: {transcript.error}")
        else:
            print(f"✅ STT Success!")
            print(f"Transcribed text: {transcript.text}")
        
        return transcript.text
        
    except Exception as e:
        print(f"❌ STT Error: {e}")
        return None

def test_stt_realtime():
    """Test real-time STT from microphone"""
    print("🎤 Testing Real-time Speech-to-Text...")
    print("Speak into your microphone...")
    
    aai.settings.api_key = settings.ASSEMBLYAI_API_KEY
    
    def on_data(transcript: aai.RealtimeTranscript):
        if not transcript.text:
            return
        
        if isinstance(transcript, aai.RealtimeFinalTranscript):
            print(f"✅ Final: {transcript.text}")
        else:
            print(f"⏳ Partial: {transcript.text}")
    
    def on_error(error: aai.RealtimeError):
        print(f"❌ Error: {error}")
    
    try:
        # Create real-time transcriber
        transcriber = aai.RealtimeTranscriber(
            on_data=on_data,
            on_error=on_error,
            sample_rate=16000
        )
        
        # Connect and start
        transcriber.connect()
        print("🎙️ Microphone active! Speak now... (Press Ctrl+C to stop)")
        
        # Start streaming from microphone
        microphone_stream = aai.extras.MicrophoneStream(sample_rate=16000)
        transcriber.stream(microphone_stream)
        
        transcriber.close()
        
    except KeyboardInterrupt:
        print("\n✅ Stopped listening")
    except Exception as e:
        print(f"❌ Real-time STT Error: {e}")

if __name__ == "__main__":
    # Test 1: Transcribe the file we created with TTS
    print("=" * 50)
    print("TEST 1: File-based transcription")
    print("=" * 50)
    test_stt_from_file()
    
    print("\n" + "=" * 50)
    print("TEST 2: Real-time microphone transcription")
    print("=" * 50)
    test_stt_realtime()

