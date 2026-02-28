from openai import OpenAI
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_BASE_URL
)

def chat_with_ai(messages, market_context=""):
    system_prompt = (
        "Anda adalah asisten trading kripto profesional. Gunakan data pasar yang diberikan "
        "untuk menjawab pertanyaan user. Jawablah dengan ramah, informatif, dan tidak terlalu panjang. "
        "Jika ditanya harga, berikan harga terkini. Jika ditanya analisis, berikan pandangan netral dan edukatif."
    )
    if market_context:
        system_prompt += f"\n\nData pasar terkini:\n{market_context}"
    
    full_messages = [{"role": "system", "content": system_prompt}] + messages
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=full_messages,
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Maaf, saya mengalami kendala teknis: {str(e)}"