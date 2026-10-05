import os
import io
import json
import time
import zipfile
import requests

from dotenv import load_dotenv
from sarvamai import SarvamAI

from app.schemas import DocumentData


load_dotenv(override=True)
client = SarvamAI(
    api_subscription_key=os.getenv("SARVAM_API_KEY")
)


def process_document(
    filename,
    file_contents,
    content_type,
    language="English"
):
    # --------------------------------------------------
    # 1. Send document to Sarvam Document AI
    # --------------------------------------------------

    file_data = io.BytesIO(file_contents)

    job = client.doc_ai.digitise(
        file=[
            (
                filename,
                file_data,
                content_type
            )
        ],
        language="en-IN",
        output_format="md"
    )

    print("Sarvam job created:", job.job_id)

    # --------------------------------------------------
    # 2. Wait for Sarvam to finish processing
    # --------------------------------------------------

    while True:

        status = client.doc_ai.get_status(
            job_id=job.job_id
        )

        print("Sarvam status:", status.status)

        if status.status.lower() in {
            "completed",
            "partially_completed",
            "failed",
            "rejected"
        }:
            break

        time.sleep(2)

    if status.status.lower() not in {
        "completed",
        "partially_completed"
    }:
        raise Exception("Sarvam Document AI failed to process the document.")

    # --------------------------------------------------
    # 3. Download Sarvam's processed output
    # --------------------------------------------------

    download = client.doc_ai.get_download_url(
        job_id=job.job_id
    )

    response = requests.get(download.url)
    response.raise_for_status()

    # --------------------------------------------------
    # 4. Extract the Markdown text from ZIP
    # --------------------------------------------------

    document_text = ""

    with zipfile.ZipFile(io.BytesIO(response.content), "r") as zip_file:

        for name in zip_file.namelist():

            if name.endswith(".md"):

                document_text = (
                    zip_file
                    .read(name)
                    .decode("utf-8")
                )

                break

    if not document_text:
        raise Exception(
            "Sarvam processed the document but no text was found."
        )

    print("Document text extracted successfully.")

    # --------------------------------------------------
    # 5. Ask Sarvam-105B to understand the document
    # --------------------------------------------------

    language_instruction = f"""
LANGUAGE REQUIREMENT — VERY IMPORTANT:

The user's selected output language is: {language}.

You MUST write all human-readable extracted information
in {language}.

This includes:
- doc_type
- audience
- key_dates labels
- amount labels
- obligation actions
- required_documents
- consequence_if_ignored
- where_to_act.office

Do NOT write these fields in English when the selected language
is not English.

Keep the following unchanged:
- dates
- numbers
- monetary values
- URLs
- document IDs
- official organisation names when appropriate

If the selected language is Hindi, write the explanations and
descriptive values in Hindi.
If the selected language is Telugu, write them in Telugu.
If the selected language is English, write them in English.

Do not translate URLs.
Do not invent missing information.
"""

    prompt = f"""
Extract the following information from this official document:

{language_instruction}

Return ONLY the JSON object.
Do not explain your answer.
Do not reason about the answer.

IMPORTANT:
- "audience" must be one of: "beneficiary", "government", "general_public", or "unknown".
...
"""
    
    prompt = f"""
Extract the following information from this official document.

Return ONLY the JSON object.
Do not explain your answer.
Do not reason about the answer.

IMPORTANT:
- "audience" must be one of: "beneficiary", "government", "general_public", or "unknown".
- "requires_user_action" must be true only if the document directly requires the person who uploaded it to take an action.
- Follow the exact JSON structure below.
- "key_dates" must contain objects with label, date, and source.
- "amounts" must contain objects with label, value, and source.
- "obligations" must be a list of objects.
- Each obligation object must contain:
  - "action": the action described in the document
  - "actor": who needs to do it: "beneficiary", "government", "both", or "unknown"
- "required_documents" must be a list of strings.
- "where_to_act" must contain both portal and office.
- If office is not mentioned, return an empty string.
- "confidence" must contain overall and low_fields.
- Do not invent information.
- If information is missing, use an empty string or empty list.

JSON:
JSON:
{{
  "doc_type": "",
  "issuer": "",
  "audience": "",
  "requires_user_action": false,
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
  "obligations": [
    {{
        "action": "",
        "actor": ""
    }}
],
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

DOCUMENT:
{document_text[:50000]}
"""

    ai_response = client.chat.completions(
        model="sarvam-105b",
        max_tokens=3000,
        reasoning_effort=None,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    content = ai_response.choices[0].message.content

    if not content:
        raise Exception(
            "Sarvam returned an empty extraction response."
        )

    # --------------------------------------------------
    # 6. Clean JSON response
    # --------------------------------------------------

    content = (
        content
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    data = json.loads(content)

    # --------------------------------------------------
    # 7. Validate using our Pydantic schema
    # --------------------------------------------------

    validated = DocumentData.model_validate(data)

    print("Document extraction validated successfully.")

    return validated