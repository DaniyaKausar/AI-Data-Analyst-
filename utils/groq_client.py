from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL

client = Groq(api_key=GROQ_API_KEY)

def call_groq(system_prompt: str, user_message: str, temperature: float = 0.1) -> str:
    """
    Core function to call Groq API.
    Low temperature = more deterministic SQL output.
    """
    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        )
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        print(f"❌ Groq API error: {e}")
        return None