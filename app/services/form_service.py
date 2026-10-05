import json
import os
import re

import fitz
from dotenv import load_dotenv
from sarvamai import SarvamAI


load_dotenv(override=True)


client = SarvamAI(
    api_subscription_key=os.getenv("SARVAM_API_KEY")
)


def extract_document_text(
    file_contents: bytes,
    content_type: str = ""
):
    """
    Extract readable text from an uploaded document.
    """

    if not file_contents:
        return ""


    # ---------------------------------------------------------
    # PDF
    # ---------------------------------------------------------

    if (
        content_type == "application/pdf"
        or file_contents[:4] == b"%PDF"
    ):

        try:

            document = fitz.open(
                stream=file_contents,
                filetype="pdf"
            )

            pages = []

            for page in document:

                text = page.get_text("text")

                if text:
                    pages.append(text)


            document.close()

            return "\n".join(pages).strip()


        except Exception:

            return ""


    # ---------------------------------------------------------
    # Plain text / fallback
    # ---------------------------------------------------------

    try:

        return file_contents.decode(
            "utf-8",
            errors="ignore"
        ).strip()

    except Exception:

        return ""


# =============================================================
# FORM FIELD EXTRACTION
# =============================================================

def detect_form(text: str):

    if not text:
        return {
            "is_form": False,
            "fields": []
        }


    # ---------------------------------------------------------
    # Ask Sarvam to understand the actual form structure.
    # ---------------------------------------------------------

    prompt = f"""
You are DocuSaathi's FORM FIELD EXTRACTION engine.

Your task is to inspect the complete text of an official
government form and identify the ACTUAL fields that a person
may need to fill, select, tick, sign, or provide information for.

IMPORTANT:

The supplied text is the PRIMARY SOURCE OF TRUTH.

DO NOT invent fields.

DO NOT add fields from your general knowledge.

DO NOT rewrite the form into a different form.

DO NOT create fields merely because a sentence contains a noun.

DO NOT treat instructions, headings, explanations, warnings,
legal notes, or introductory sentences as fields.

For example:

"I/We give below necessary particulars"

is NOT a field.

"To avoid mistakes, please follow the instructions"

is NOT a field.

"Complete this section when applicable"

is NOT a field.

But:

"Last Name / Surname"

IS a field.

"State / Union Territory"

IS a field.

"Registration Number"

IS a field.

"Representative Assessee"

may be a section heading, but its actual name/address fields
inside that section ARE fields.

---------------------------------------------------------
FIELD RULES
---------------------------------------------------------

For every actual fillable field:

1. Preserve the meaning of the original field.
2. Preserve the original wording where possible.
3. Include enough context when the same label appears multiple
   times.

For example, if the form has:

"State / Union Territory"

under a Representative Assessee address, return:

"RA Address — State / Union Territory"

rather than simply:

"State / Union Territory"

Likewise:

"Residence Address — State / Union Territory"

and:

"Office Address — State / Union Territory"

should remain distinguishable.

---------------------------------------------------------
FIELD TYPES
---------------------------------------------------------

Use one of these types:

"text"
"number"
"date"
"email"
"select"
"radio"
"checkboxes"
"file"

Use:

"radio" when the form asks the user to select ONE option.

Use:

"checkboxes" when multiple options may be selected.

Use:

"select" when the form clearly provides a dropdown-style
choice.

Use:

"file" for signature, photograph, attachment or document upload
fields.

Use "text" when the correct input type is unclear.

---------------------------------------------------------
OPTIONS
---------------------------------------------------------

If the form explicitly provides options, preserve them.

Example:

"Male Female Transgender"

should produce:

label = "Gender"
type = "radio"
options = ["Male", "Female", "Transgender"]

Do NOT invent additional options.

---------------------------------------------------------
SECTIONS
---------------------------------------------------------

Identify the section containing each field.

Examples:

"1. Full Name"
"7. Address"
"14. Representative Assessee (RA)"

The section name should be returned with each field.

---------------------------------------------------------
SOURCE TEXT
---------------------------------------------------------

For every field, include a short source_text taken directly
from the supplied form text.

Do not invent source_text.

---------------------------------------------------------
IMPORTANT
---------------------------------------------------------

The form may contain:

- headings
- instructions
- legal notes
- explanatory paragraphs
- conditional instructions
- checkboxes
- radio buttons
- repeated field labels
- signatures
- dates
- addresses
- names
- official codes
- registration numbers
- declarations

Extract the ACTUAL fields from all sections.

Do not stop after the first page.

Do not return only the most obvious fields.

---------------------------------------------------------
FORM TEXT
---------------------------------------------------------

START OF FORM

{text}

END OF FORM

---------------------------------------------------------

Return ONLY valid JSON.

Use exactly this structure:

{{
    "is_form": true,
    "fields": [
        {{
            "id": "0",
            "section": "Section name",
            "label": "Exact or faithful field label",
            "type": "text",
            "options": [],
            "source_text": "Short source text from the form"
        }}
    ]
}}

The id must be a sequential string beginning with "0".

Return EVERY actual field you can identify.

Do not return instructions as fields.
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

            temperature=0.1,
            
             reasoning_effort=None,

            max_tokens=6000,

            response_format={
                "type": "json_object"
            }
        )


        content = response.choices[0].message.content
        print("\n===== SARVAM FORM RESPONSE =====")
        print(content)
        print("===== END SARVAM RESPONSE =====\n")


        if not content:
            return {
                "is_form": False,
                "fields": []
            }


        result = json.loads(content)


        fields = result.get(
            "fields",
            []
        )


        if not isinstance(fields, list):
            fields = []


        cleaned_fields = []


        for index, field in enumerate(fields):

            if not isinstance(field, dict):
                continue


            label = str(
                field.get(
                    "label",
                    ""
                )
            ).strip()


            if not label:
                continue


            field_type = str(
                field.get(
                    "type",
                    "text"
                )
            ).strip().lower()


            allowed_types = {
                "text",
                "number",
                "date",
                "email",
                "select",
                "radio",
                "checkboxes",
                "file"
            }


            if field_type not in allowed_types:
                field_type = "text"


            options = field.get(
                "options",
                []
            )


            if not isinstance(options, list):
                options = []


            options = [
                str(option).strip()
                for option in options
                if str(option).strip()
            ]


            cleaned_fields.append({

                "id": str(index),

                "section": str(
                    field.get(
                        "section",
                        ""
                    )
                ).strip(),

                "label": label,

                "type": field_type,

                "options": options,

                "source_text": str(
                    field.get(
                        "source_text",
                        label
                    )
                ).strip()

            })


        # -----------------------------------------------------
        # Remove accidental duplicate fields
        # -----------------------------------------------------

        unique_fields = []

        seen = set()


        for field in cleaned_fields:

            key = (
                field["section"].lower(),
                field["label"].lower()
            )


            if key in seen:
                continue


            seen.add(key)

            unique_fields.append(
                field
            )


        # Re-number after duplicate removal

        for index, field in enumerate(
            unique_fields
        ):

            field["id"] = str(index)


        return {

            "is_form": bool(
                unique_fields
            ),

            "fields": unique_fields

        }


    except Exception as error:

        print(
            "Form field extraction error:",
            error
        )

        return {

            "is_form": False,

            "fields": []

        }


# =============================================================
# FINAL FORM RESULT
# =============================================================

def build_form_result(text: str):

    if not text:

        return {

            "is_form": False,

            "fields": [],

            "message": "No readable text was found in the document."

        }


    result = detect_form(text)


    return {

        "is_form": result.get(
            "is_form",
            False
        ),

        "fields": result.get(
            "fields",
            []
        ),

        "field_count": len(
            result.get(
                "fields",
                []
            )
        )

    }