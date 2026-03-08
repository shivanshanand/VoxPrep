from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from app.config import settings

class LLMService:
    def __init__(self):
        self.llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model="llama-3.3-70b-versatile",
            temperature=0.7
        )
    
    async def chat(self, user_message: str, context: str = "") -> str:
        """Simple chat - ask question, get response"""
        prompt = ChatPromptTemplate.from_template("""
        You are a technical interviewer conducting an interview.
        {context}
        
        Candidate says: {user_message}
        
        Respond naturally and professionally. Keep responses concise (2-3 sentences).
        """)
        
        chain = prompt | self.llm
        response = await chain.ainvoke({
            "context": context,
            "user_message": user_message
        })
        
        return response.content

llm_service = LLMService()
