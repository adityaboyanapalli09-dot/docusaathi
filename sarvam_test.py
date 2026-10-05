import os
from dotenv import load_dotenv
from sarvamai import SarvamAI

load_dotenv()

client = SarvamAI(
    api_subscription_key=os.getenv("SARVAM_API_KEY")
)

response = client.chat.completions(
    model = "sarvam-105b" , 
    max_tokens=50,
    messages=[
        {
            "role": "user",
            "content": "Say hello to DocuSaathi in one short sentence."
        }
    ]
)

print(response)