from cartesia import Cartesia
from app.config import settings

class TTSService:
    def __init__(self):
        self.client = Cartesia(api_key=settings.CARTESIA_API_KEY)
        self.voice_config = {
            "mode": "id",
            "id": "a0e99841-438c-4a64-b679-ae501e7d6091"
        }
    
    def synthesize(self, text: str) -> bytes:
        """Convert text to speech audio"""
        try:
            chunk_iter = self.client.tts.bytes(
                model_id="sonic-english",
                transcript=text,
                voice=self.voice_config,
                output_format={
                    "container": "wav",  # ✅ Changed from "raw" to "wav"
                    "encoding": "pcm_f32le",
                    "sample_rate": 44100
                }
            )
            
            # Collect all chunks into bytes
            audio_data = b""
            for chunk in chunk_iter:
                audio_data += chunk
            
            return audio_data
            
        except Exception as e:
            print(f"TTS Error: {e}")
            import traceback
            traceback.print_exc()
            return None

tts_service = TTSService()
