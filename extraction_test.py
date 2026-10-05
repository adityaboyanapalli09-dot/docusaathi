import os
import json
from dotenv import load_dotenv
from sarvamai import SarvamAI
from app.schemas import DocumentData

load_dotenv()

client = SarvamAI(
    api_subscription_key=os.getenv("SARVAM_API_KEY")
)

document_text = """
INCOME TAX DEPARTMENT

NOTICE

Notice Number: IT-2026-45821

You are required to respond to this notice by 15 October 2026.

Amount due: Rs. 5,000

Required action:
1. Respond to this notice.
2. Pay the amount due.

Required document:
- Copy of PAN card

If you do not respond by the deadline, further action may be taken.

You can respond through the Income Tax portal.
"""

prompt = f"""
Extract the following information from the notice.

Return ONLY the JSON object.
Do not explain your answer.
Do not reason about the answer.

IMPORTANT:
- Follow the exact JSON structure shown below.
- "key_dates" must contain objects with label, date, and source.
- "amounts" must contain objects with label, value, and source.
- "obligations" must be a list of strings.
- "required_documents" must be a list of strings.
- "where_to_act" must contain both portal and office.
- If office is not mentioned, return an empty string.
- "confidence" must contain overall and low_fields.

JSON:
{{
  "doc_type": "",
  "issuer": "",
  "key_dates": [
    {{
      "label": "",
      "date": "",
      "source": ""
    }}
  ],
  "amounts": [
    {{
      "label": "",
      "value": "",
      "source": ""
    }}
  ],
  "obligations": [],
  "required_documents": [],
  "consequence_if_ignored": "",
  "where_to_act": {{
    "portal": "",
    "office": ""
  }},
  "confidence": {{
    "overall": 0.0,
    "low_fields": []
  }}
}}

NOTICE:
{document_text}
"""

response = client.chat.completions(
    model="sarvam-105b",
    max_tokens=1000,
    reasoning_effort=None,
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
)

content = response.choices[0].message.content

print("\nRAW SARVAM RESPONSE:")
print(content)

# Remove markdown code fences if Sarvam adds them
content = content.replace("```json", "").replace("```", "").strip()

# Convert JSON text into Python dictionary
data = json.loads(content)

# Validate against our Pydantic schema
validated = DocumentData.model_validate(data)

print("\nVALIDATION SUCCESSFUL!")
print(validated)