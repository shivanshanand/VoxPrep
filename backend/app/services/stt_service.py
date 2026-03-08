import assemblyai as aai
from app.config import settings

class STTService:
    def __init__(self):
        aai.settings.api_key = settings.ASSEMBLYAI_API_KEY
    
    def transcribe_audio(self, audio_file_path: str) -> str:
        """Transcribe audio file to text"""
        try:
            transcriber = aai.Transcriber()
            transcript = transcriber.transcribe(audio_file_path)
            
            if transcript.status == aai.TranscriptStatus.error:
                print(f"Transcription error: {transcript.error}")
                return None
            
            return transcript.text
            
        except Exception as e:
            print(f"STT Error: {e}")
            return None

stt_service = STTService()
