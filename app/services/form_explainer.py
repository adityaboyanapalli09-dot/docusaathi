import json
import os

from dotenv import load_dotenv
from sarvamai import SarvamAI


load_dotenv(override=True)


client = SarvamAI(
    api_subscription_key=os.getenv("SARVAM_API_KEY")
)


def explain_form_fields(fields, document_text):
    """
    Explain detected form fields using the full form context.
    """

    if not fields:
        return []


    field_data = []

    for index, field in enumerate(fields):

        field_data.append({
            "id": str(index),
            "section": field.get("section", ""),
            "label": field.get("label", ""),
            "type": field.get("type", "text"),
            "options": field.get("options", []),
            "source_text": field.get("source_text", "")
        })


    prompt = f"""
You are DocuSaathi's official-form explanation engine.

Your job is to explain every detected fillable field in a
government or official form to an ordinary person.

The COMPLETE FORM TEXT is the primary source of truth.

The detected fields are provided only to help you identify
which parts need explanation.

============================================================
IMPORTANT
============================================================

Do NOT give generic explanations.

Do NOT say:

"The form does not explain this field clearly."

Do NOT say:

"Enter the information requested by the form."

Do NOT say:

"Check the relevant official document."

unless the form genuinely gives no better information.

Use the actual form text and surrounding context to explain
what the field means.

============================================================
FOR EVERY FIELD EXPLAIN
============================================================

1. what_is_it

Explain what this field actually means.

2. what_do_i_enter

Tell the user exactly what kind of information belongs here.

3. where_can_i_find_it

Explain where the user can normally find that information,
BUT ONLY when supported by the form or obvious from the field.

If the form does not provide enough information, say:

"Check the official instructions for this form."

Do NOT invent a document or authority.

4. warning

Only include a warning when the user could realistically make
a mistake.

Otherwise return an empty string.

5. confidence

Use:

"high"
"medium"
"low"

This is internal confidence only.
Do not write the word "medium" into the explanation itself.

============================================================
IMPORTANT EXAMPLES
============================================================

For:

"Title"

explain that it is the title used before the person's name,
and use the options actually present in the form.

For:

"AO Area Code"

explain that it is part of the Assessing Officer code used
to identify the relevant income-tax assessing office.

Do NOT tell the user to guess it.

For:

"Registration Number"

explain that it is the official registration number of the
entity when applicable.

Do NOT invent where to obtain a particular number.

For:

"Representative Assessee"

explain that this refers to a person who represents the
applicant for tax/PAN-related matters when applicable.

Do NOT assume every applicant needs one.

For:

"State / Union Territory"

explain that the user should enter/select the state or
Union Territory corresponding to that address.

For:

"Name as per Aadhaar"

explain that the name should match the Aadhaar record.

For:

"Business/Profession code"

explain that it identifies the applicant's business or
profession according to the official code list.

Do NOT invent a code.

============================================================
OPTIONS
============================================================

If a field contains explicit options, explain those options.

Do NOT invent additional options.

For example:

Male
Female
Transgender

should be explained as the choices provided by the form.

============================================================
CONTEXT
============================================================

Use:

- section name
- field label
- field type
- field options
- source text
- surrounding form text

to understand the field.

For example:

Section:
"Assessing Officer (AO Code)"

Field:
"Area Code"

This should receive an explanation specifically about the
Assessing Officer code rather than a generic explanation
about entering a number.

============================================================
KEEP IT CONCISE
============================================================

Each explanation should normally be 1–2 short sentences.

Use simple everyday language.

Do not write essays.

Do not provide legal advice.

Do not invent requirements.

Do not claim something is mandatory unless the form says so.

============================================================
FORM TEXT
============================================================

--- START OF FORM ---

{document_text}

--- END OF FORM ---

============================================================
DETECTED FIELDS
============================================================

{json.dumps(field_data, ensure_ascii=False, indent=2)}

============================================================

Return ONLY valid JSON.

Use exactly:

{{
    "fields": [
        {{
            "id": "0",
            "what_is_it": "...",
            "what_do_i_enter": "...",
            "where_can_i_find_it": "...",
            "warning": "",
            "confidence": "high"
        }}
    ]
}}

Keep every field id unchanged.

Return an explanation for EVERY field.
"""


    try:

        response = client.chat.completions(

            model="sarvam-105b",

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.15,

            reasoning_effort=None,

            max_tokens=6000,

            response_format={
                "type": "json_object"
            }
        )


        content = response.choices[0].message.content


        if not content:
            return fields


        result = json.loads(content)


        explanations = result.get(
            "fields",
            []
        )


        if not isinstance(explanations, list):
            return fields


        explanation_map = {
            str(item.get("id")): item
            for item in explanations
            if isinstance(item, dict)
        }


        final_fields = []


        for index, field in enumerate(fields):

            explanation = explanation_map.get(
                str(index),
                {}
            )


            enriched_field = dict(field)


            enriched_field["what_is_it"] = str(
                explanation.get(
                    "what_is_it",
                    ""
                )
            ).strip()


            enriched_field["what_do_i_enter"] = str(
                explanation.get(
                    "what_do_i_enter",
                    ""
                )
            ).strip()


            enriched_field["where_can_i_find_it"] = str(
                explanation.get(
                    "where_can_i_find_it",
                    ""
                )
            ).strip()


            enriched_field["warning"] = str(
                explanation.get(
                    "warning",
                    ""
                )
            ).strip()


            confidence = str(
                explanation.get(
                    "confidence",
                    "medium"
                )
            ).lower().strip()


            if confidence not in {
                "high",
                "medium",
                "low"
            }:
                confidence = "medium"


            enriched_field["confidence"] = confidence


            final_fields.append(
                enriched_field
            )


        return final_fields


    except Exception as error:

        print(
            "Form explanation error:",
            error
        )

        return fields