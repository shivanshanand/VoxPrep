import base64
import os
import tempfile
from datetime import datetime, timedelta

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.database import get_rate_limit, save_rate_limit
from app.models.interview import ExperienceLevel, RoleType
from app.services.interview_service import interview_service
from app.services.stt_service import stt_service
from app.services.tts_service import tts_service
from app.utils.enum_parser import parse_enum

router = APIRouter()

@router.websocket("/voice/{role}/{experience}")
async def voice_interview_endpoint(
    websocket: WebSocket,
    role: str,
    experience: str
):
    """WebSocket endpoint for voice-based interviews"""
    await websocket.accept()
    print(f"\n{'='*60}")
    print("🎤 NEW CLIENT CONNECTED")
    print(f"   Role: {role}")
    print(f"   Experience: {experience}")
    print(f"{'='*60}\n")
    
    session_id = None
    
    client_ip = websocket.client.host if websocket.client else "unknown"
    
    try:
        # Check rate limit
        now = datetime.now()
        rate_limit = await get_rate_limit(client_ip)
        
        usage_count = 0
        reset_time = now + timedelta(days=3)
        
        if rate_limit:
            if now > rate_limit.reset_time:
                # Reset
                usage_count = 0
            else:
                usage_count = rate_limit.usage_count
                reset_time = rate_limit.reset_time
        
        if usage_count >= 3:
            await websocket.send_json({
                "type": "error",
                "message": "Rate limit reached. You can only use the service 3 times per 3 days."
            })
            await websocket.close()
            return
            
        # Increment and save
        await save_rate_limit({
            "ip_address": client_ip,
            "usage_count": usage_count + 1,
            "reset_time": reset_time
        })

        # Parse and validate role and experience
        try:
            role_enum = parse_enum(RoleType, role)
            exp_enum = parse_enum(ExperienceLevel, experience)
        except ValueError as e:
            await websocket.send_json({
                "type": "error",
                "message": f"Invalid role or experience level: {e!s}"
            })
            await websocket.close()
            return
        
        # Create interview session
        session = interview_service.create_session(role_enum, exp_enum)
        session_id = session.session_id
        
        print(f"✅ Session created: {session_id}")
        print(f"   Role: {session.config.role.value}")
        print(f"   Experience: {session.config.experience.value}\n")
        
        # Send session start confirmation
        await websocket.send_json({
            "type": "session_start",
            "session_id": session_id,
            "role": session.config.role.value,
            "experience": session.config.experience.value
        })
        
        # Generate and send initial greeting
        print("🤖 Generating initial greeting...")
        greeting = await interview_service.get_initial_greeting(session)
        print(f"💬 Greeting: {greeting[:100]}...\n")
        
        greeting_audio = tts_service.synthesize(greeting)
        
        if greeting_audio:
            await websocket.send_json({
                "type": "audio",
                "data": base64.b64encode(greeting_audio).decode('utf-8'),
                "text": greeting,
                "phase": session.current_phase.value
            })
            print("✅ Initial greeting sent to client\n")
        else:
            print("❌ Failed to generate greeting audio\n")
            await websocket.send_json({
                "type": "error",
                "message": "Failed to generate audio"
            })
        
        # Main interview loop
        while True:
            message = await websocket.receive_json()
            
            if message.get("type") == "audio":
                print(f"\n{'─'*60}")
                print("📥 Received audio from client")
                
                # Decode audio data
                try:
                    audio_data = base64.b64decode(message.get("data"))
                except Exception as e:
                    print(f"❌ Error decoding audio: {e}")
                    continue
                
                # Save to temporary file
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
                    temp_audio.write(audio_data)
                    temp_audio_path = temp_audio.name
                
                print(f"💾 Audio saved to: {temp_audio_path}")
                
                # Transcribe audio
                print("🎤 Transcribing audio...")
                transcript = stt_service.transcribe_audio(temp_audio_path)
                
                # Clean up temp file
                try:
                    os.unlink(temp_audio_path)
                except:
                    pass
                
                if not transcript:
                    print("❌ Transcription failed or empty\n")
                    await websocket.send_json({
                        "type": "error",
                        "message": "Could not transcribe audio. Please try again."
                    })
                    continue
                
                print(f"📝 Transcribed: '{transcript}'")
                
                # Send transcription to client
                await websocket.send_json({
                    "type": "transcription",
                    "text": transcript
                })
                
                # Process answer with interview service
                print("🤖 Processing with interview service...")
                result = await interview_service.process_answer(session_id, transcript)
                
                if "error" in result:
                    print(f"❌ Error from interview service: {result['error']}\n")
                    await websocket.send_json({
                        "type": "error",
                        "message": result["error"]
                    })
                    continue
                
                response_text = result.get("response", "")
                phase = result.get("phase", "unknown")
                evaluation = result.get("evaluation")
                completed = result.get("completed", False)
                
                print(f"💬 AI Response: {response_text[:100]}...")
                print(f"📊 Current Phase: {phase}")
                if evaluation:
                    print(f"📈 Answer Score: {evaluation.get('score', 'N/A')}/10")
                
                # Check if interview is complete
                if completed:
                    print(f"\n{'='*60}")
                    print("🎉 INTERVIEW COMPLETED")
                    print(f"{'='*60}\n")
                    
                    # Send final response audio first
                    if response_text:
                        print("🔊 Generating final response audio...")
                        response_audio = tts_service.synthesize(response_text)
                        
                        if response_audio:
                            await websocket.send_json({
                                "type": "audio",
                                "data": base64.b64encode(response_audio).decode('utf-8'),
                                "text": response_text,
                                "phase": phase
                            })
                            print("✅ Final response sent\n")
                    
                    # Get and send summary
                    summary = interview_service.get_session_summary(session_id)
                    print("📊 Interview Summary:")
                    print(f"   Overall Score: {summary.get('overall_score', 0)}/10")
                    print(f"   Duration: {summary.get('duration', 'N/A')}")
                    print(f"   Total Messages: {summary.get('total_messages', 0)}")
                    print(f"   Evaluations: {summary.get('evaluations_count', 0)}\n")
                    
                    await websocket.send_json({
                        "type": "summary",
                        "data": summary
                    })
                    
                    # Close connection gracefully
                    await websocket.close()
                    print("👋 Connection closed gracefully\n")
                    return
                
                # Continue interview - generate audio response
                print("🔊 Generating audio response...")
                response_audio = tts_service.synthesize(response_text)
                
                if response_audio:
                    await websocket.send_json({
                        "type": "audio",
                        "data": base64.b64encode(response_audio).decode('utf-8'),
                        "text": response_text,
                        "phase": phase
                    })
                    print("✅ Response sent to client")
                else:
                    print("❌ Failed to generate response audio")
                    await websocket.send_json({
                        "type": "error",
                        "message": "Failed to generate audio response"
                    })
                
                print(f"{'─'*60}\n")
            
            elif message.get("type") == "end":
                print(f"\n{'='*60}")
                print("👋 Client requested to end interview")
                print(f"{'='*60}\n")
                
                # Get session summary
                summary = interview_service.get_session_summary(session_id)
                
                await websocket.send_json({
                    "type": "summary",
                    "data": summary
                })
                
                await websocket.close()
                print("Connection closed\n")
                break
            
            else:
                print(f"⚠️  Unknown message type: {message.get('type')}")
    
    except WebSocketDisconnect:
        print(f"\n{'='*60}")
        print("❌ Client disconnected abruptly")
        if session_id:
            print(f"   Session: {session_id}")
        print(f"{'='*60}\n")
    
    except Exception as e:
        print(f"\n{'='*60}")
        print("❌ UNEXPECTED ERROR")
        print(f"   Error: {e!s}")
        if session_id:
            print(f"   Session: {session_id}")
        print(f"{'='*60}\n")
        
        import traceback
        traceback.print_exc()
        
        # Try to send error to client
        try:
            await websocket.send_json({
                "type": "error",
                "message": "An unexpected error occurred. Please try again."
            })
        except:
            pass