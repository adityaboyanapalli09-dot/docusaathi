from app.services.sarvam_service import process_document


with open("RevisedPM-KISANOperationalGuidelines(English).pdf", "rb") as f:
    file_contents = f.read()


result = process_document(
    filename="RevisedPM-KISANOperationalGuidelines(English).pdf",
    file_contents=file_contents,
    content_type="application/pdf"
)


print("\n========== FINAL RESULT ==========")
print(result)