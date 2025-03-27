import google.generativeai as genai
from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-2.0-flash-exp",
  generation_config=generation_config,
)

PROMPT_SYSTEM = "請以繁體中文回應"
PROMPT_ERROR_EXCEPTION = "很抱歉，我們無法回答您的問題，請稍後再試。"
PROMPT_TEST = "請介紹 Gemini API"


chat_session = model.start_chat(history=[{
    "role": "user",
    "parts": [PROMPT_SYSTEM],
}])

def generate_text(prompt):
    try:
        response = chat_session.send_message(prompt)
        return response.text
    except Exception as e:
        return PROMPT_ERROR_EXCEPTION

if __name__ == '__main__':
    test_prompt = PROMPT_TEST
    result = generate_text(test_prompt)
    print(result)