import json
import uuid
from datetime import datetime

from app.models.interview import (
    AnswerEvaluation,
    ExperienceLevel,
    InterviewConfig,
    InterviewPhase,
    InterviewSession,
    Message,
    RoleType,
)
from app.services.llm_service import llm_service


class InterviewService:
    def __init__(self):
        self.active_sessions = {}
    
    def create_session(self, role: RoleType, experience: ExperienceLevel) -> InterviewSession:
        """Initialize new interview session"""
        session_id = str(uuid.uuid4())
        
        config = InterviewConfig(
            session_id=session_id,
            role=role,
            experience=experience
        )
        
        session = InterviewSession(
            session_id=session_id,
            config=config,
            current_phase=InterviewPhase.INTRODUCTION,
            start_time=datetime.now().isoformat()
        )
        
        self.active_sessions[session_id] = session
        return session
    
    async def get_initial_greeting(self, session: InterviewSession) -> str:
        """Generate opening greeting based on role/experience"""
        prompt = f"""You are conducting a technical interview for a {session.config.role.value} position at {session.config.experience.value} level.

Start with a warm, professional greeting. Introduce yourself as the interviewer and ask them to briefly introduce themselves.
Keep it concise - 2-3 sentences maximum.

Example structure:
"Hello! I'm your AI interviewer today. We'll be discussing your background and technical skills for a [role] position. Could you start by telling me a bit about yourself and your experience?"
"""
        
        greeting = await llm_service.chat("", prompt)
        
        # Save message
        self._add_message(session, "assistant", greeting, InterviewPhase.INTRODUCTION)
        
        return greeting
    
    async def process_answer(self, session_id: str, user_message: str) -> dict:
        """Process user's answer and generate next response"""
        session = self.active_sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}

        # Block input after interview ended
        if session.current_phase == InterviewPhase.CLOSING and session.end_time:
            return {
                "type": "interview_end",
                "message": "Interview already completed",
                "completed": True
            }

        # 1. Save user message FIRST
        self._add_message(session, "user", user_message, session.current_phase)

        # 2. Evaluate answer (only for technical/behavioral phases)
        evaluation = None
        if session.current_phase in {InterviewPhase.TECHNICAL, InterviewPhase.BEHAVIORAL}:
            # Only evaluate if there was a previous question
            if len([m for m in session.messages if m.role == "assistant"]) > 1:
                evaluation = await self._evaluate_answer(session, user_message)
                session.evaluations.append(evaluation)

        # 3. Check if we should transition to next phase BEFORE generating question
        self._check_phase_transition(session)

        # 4. Build context
        context = self._build_context(session)

        # 5. Generate next AI response
        response = await self._generate_next_question(session, user_message, context)

        # 6. Save AI response
        self._add_message(session, "assistant", response, session.current_phase)

        # 7. If in CLOSING phase, mark interview as ended after AI's closing message
        if session.current_phase == InterviewPhase.CLOSING:
            session.end_time = datetime.now().isoformat()
            return {
                "type": "interview_end",
                "response": response,
                "phase": session.current_phase.value,
                "evaluation": evaluation.dict() if evaluation else None,
                "completed": True
            }

        return {
            "type": "interview_continue",
            "response": response,
            "phase": session.current_phase.value,
            "evaluation": evaluation.dict() if evaluation else None,
            "completed": False
        }
    
    async def _generate_next_question(self, session: InterviewSession, user_msg: str, context: str) -> str:
        """Generate next question based on current phase and conversation"""
        
        role_name = session.config.role.value
        exp_name = session.config.experience.value
        
        phase_prompts = {
            InterviewPhase.INTRODUCTION: f"""You are conducting a technical interview for a {role_name} position at {exp_name} level.

Current phase: Introduction
Candidate just said: "{user_msg}"

Continue the introduction naturally. After they introduce themselves, acknowledge their background and smoothly transition to asking about their technical experience or a relevant project.
Keep responses concise - 2-3 sentences maximum.
Don't ask too many introduction questions - move to technical phase soon.
""",
            InterviewPhase.TECHNICAL: f"""You are conducting a technical interview for a {role_name} position at {exp_name} level.

Current phase: Technical Questions
Candidate's answer: "{user_msg}"

Ask relevant technical questions for {role_name}:

For Backend Developer:
- RESTful API design, databases (SQL/NoSQL), caching, message queues
- System design (for mid/senior): scalability, microservices, load balancing
- Problem-solving: algorithmic thinking, code optimization

For Frontend Developer:
- React/Vue/Angular, state management, component architecture
- Performance optimization, responsive design, accessibility
- Build tools, testing, modern JavaScript/TypeScript

For Full-Stack Developer:
- Both frontend and backend technologies
- Integration patterns, authentication, deployment
- End-to-end system design

For ML Engineer:
- ML frameworks (TensorFlow, PyTorch), model training/deployment
- Feature engineering, model optimization, MLOps
- Data pipelines, model monitoring

For DevOps Engineer:
- CI/CD pipelines, containerization (Docker/Kubernetes)
- Infrastructure as Code, monitoring, cloud platforms (AWS/GCP/Azure)
- Automation, security, performance optimization

For Data Scientist:
- Statistical analysis, data visualization, experimentation
- ML algorithms, feature engineering, model evaluation
- SQL, Python (pandas, numpy), data storytelling

For Mobile Developer:
- iOS/Android development, cross-platform frameworks (React Native/Flutter)
- Mobile UI/UX patterns, offline-first design, app performance
- App store deployment, push notifications, mobile security

Acknowledge their answer briefly (1 sentence), then ask a focused technical question.
After 4-5 technical exchanges, start wrapping up technical discussion.
Keep responses under 3 sentences.
""",
            InterviewPhase.BEHAVIORAL: f"""You are conducting a technical interview for a {role_name} position at {exp_name} level.

Current phase: Behavioral Questions
Candidate's answer: "{user_msg}"

Ask behavioral questions using STAR method (Situation, Task, Action, Result):
- "Tell me about a challenging technical project you worked on"
- "Describe a time when you disagreed with a team member on a technical decision"
- "How do you handle tight deadlines or changing requirements?"
- "Tell me about a time you failed and what you learned"
- "How do you stay updated with new technologies in your field?"

Acknowledge their answer (1 sentence), then ask the next behavioral question.
After 3-4 behavioral exchanges, transition to closing.
Keep responses under 3 sentences.
""",
            InterviewPhase.CLOSING: f"""You are wrapping up the interview for {role_name} position.

Candidate's last response: "{user_msg}"

Provide a brief, warm closing:
1. Thank them for their time and thoughtful answers
2. Mention that the team will review their responses and be in touch soon
3. Wish them well

Keep it short and professional - 2-3 sentences maximum.
This is the FINAL message of the interview.
"""
        }
        
        prompt = phase_prompts.get(session.current_phase, phase_prompts[InterviewPhase.INTRODUCTION])
        prompt += f"\n\nConversation context (recent messages):\n{context}"
        
        response = await llm_service.chat(user_msg, prompt)
        
        return response
    
    def _check_phase_transition(self, session: InterviewSession):
        """Automatically transition between phases based on message count"""
        # Count user messages in current phase
        phase_user_messages = [
            m for m in session.messages
            if m.phase == session.current_phase and m.role == "user"
        ]
        
        # Define transitions (min_messages, next_phase)
        transitions = {
            InterviewPhase.INTRODUCTION: (1, InterviewPhase.TECHNICAL),  # After 2 user messages
            InterviewPhase.TECHNICAL: (2, InterviewPhase.BEHAVIORAL),    # After 5 user messages
            InterviewPhase.BEHAVIORAL: (1, InterviewPhase.CLOSING)       # After 4 user messages
        }
        
        if session.current_phase in transitions:
            threshold, next_phase = transitions[session.current_phase]
            if len(phase_user_messages) >= threshold:
                print(f"🔄 Transitioning from {session.current_phase.value} to {next_phase.value}")
                print(f"   User messages in current phase: {len(phase_user_messages)}")
                session.current_phase = next_phase
    
    async def _evaluate_answer(self, session: InterviewSession, answer: str) -> AnswerEvaluation:
        """Evaluate user's answer and provide feedback"""
        
        # Get last AI question
        last_question = ""
        for msg in reversed(session.messages):
            if msg.role == "assistant":
                last_question = msg.content
                break
        
        role_name = session.config.role.value
        exp_name = session.config.experience.value
        
        eval_prompt = f"""You are evaluating a candidate's answer for {role_name} at {exp_name} level.

Question: {last_question}
Answer: {answer}

Evaluate based on:
- Technical accuracy and depth
- Clarity of explanation
- Relevant experience level
- Completeness of answer

Provide evaluation in the following format:
1. Score (1-10): Consider experience level expectations
2. Feedback: One clear sentence
3. Strengths: 2-3 specific strong points (be specific, not generic)
4. Improvements: 2-3 concrete suggestions (be specific)

Return ONLY valid JSON in this exact format (no markdown, no extra text):
{{
    "score": 7,
    "feedback": "Good understanding of core concepts with relevant examples",
    "strengths": ["Mentioned specific technology X", "Explained approach to Y clearly"],
    "improvements": ["Could elaborate on edge cases", "Missing discussion of scalability considerations"]
}}
"""
        
        eval_response = await llm_service.raw_completion(eval_prompt)
        
        # Clean the response (remove markdown code blocks if present)
        eval_response = eval_response.strip()
        eval_response = eval_response.removeprefix("```json")
        eval_response = eval_response.removeprefix("```")
        eval_response = eval_response.removesuffix("```")
        eval_response = eval_response.strip()
        
        # Parse JSON response
        try:
            eval_data = json.loads(eval_response)
            
            evaluation = AnswerEvaluation(
                question=last_question,
                answer=answer,
                score=eval_data.get("score", 5),
                feedback=eval_data.get("feedback", "Answer received"),
                strengths=eval_data.get("strengths", []),
                improvements=eval_data.get("improvements", []),
                timestamp=datetime.now().isoformat()
            )
            
            print(f"✅ Evaluation: Score {evaluation.score}/10")
            return evaluation
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            print(f"Response was: {eval_response[:200]}")
            # Fallback if JSON parsing fails
            return AnswerEvaluation(
                question=last_question,
                answer=answer,
                score=5,
                feedback="Unable to evaluate - response recorded",
                strengths=[],
                improvements=[],
                timestamp=datetime.now().isoformat()
            )
    
    def _add_message(self, session: InterviewSession, role: str, content: str, phase: InterviewPhase):
        """Add message to session history"""
        message = Message(
            role=role,
            content=content,
            timestamp=datetime.now().isoformat(),
            phase=phase
        )
        session.messages.append(message)
        print(f"💬 Added {role} message in {phase.value} phase")
    
    def _build_context(self, session: InterviewSession) -> str:
        """Build conversation context for LLM (last 6 messages)"""
        context = f"Role: {session.config.role.value}\nExperience: {session.config.experience.value}\n\n"
        
        # Last 6 messages for context
        recent_messages = session.messages[-6:]
        for msg in recent_messages:
            speaker = "Interviewer" if msg.role == "assistant" else "Candidate"
            context += f"{speaker}: {msg.content}\n"
        
        return context
    
    def get_session_summary(self, session_id: str) -> dict:
        """Get interview summary with scores"""
        session = self.active_sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}
        
        # Calculate overall score
        if session.evaluations:
            avg_score = sum(e.score for e in session.evaluations) / len(session.evaluations)
        else:
            avg_score = 0
        
        return {
            "session_id": session_id,
            "role": session.config.role.value,
            "experience": session.config.experience.value,
            "duration": self._calculate_duration(session),
            "total_messages": len(session.messages),
            "total_questions": len([m for m in session.messages if m.role == "assistant"]),
            "total_answers": len([m for m in session.messages if m.role == "user"]),
            "evaluations_count": len(session.evaluations),
            "overall_score": round(avg_score, 1),
            "phase_completed": session.current_phase.value,
            "evaluations": [
                {
                    "score": e.score,
                    "feedback": e.feedback,
                    "strengths": e.strengths,
                    "improvements": e.improvements
                }
                for e in session.evaluations
            ]
        }
    
    def _calculate_duration(self, session: InterviewSession) -> str:
        """Calculate interview duration"""
        try:
            start = datetime.fromisoformat(session.start_time)
            end = datetime.fromisoformat(session.end_time) if session.end_time else datetime.now()
            duration = end - start
            minutes = int(duration.total_seconds() / 60)
            seconds = int(duration.total_seconds() % 60)
            return f"{minutes}m {seconds}s"
        except Exception as e:
            print(f"Error calculating duration: {e}")
            return "Unknown"

interview_service = InterviewService()