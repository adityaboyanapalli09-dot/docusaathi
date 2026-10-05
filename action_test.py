from app.services.sarvam_service import process_document
from app.services.action_engine import build_action_plan


with open("RevisedPM-KISANOperationalGuidelines(English).pdf", "rb") as f:
    file_contents = f.read()


result = process_document(
    filename="RevisedPM-KISANOperationalGuidelines(English).pdf",
    file_contents=file_contents,
    content_type="application/pdf"
)


action_plan = build_action_plan(result)


print("\n========== DOCUSAATHI ACTION PLAN ==========")

print("\nSUMMARY:")
print(action_plan["summary"])

print("\nACTIONS:")
for action in action_plan["actions"]:
    print("-", action["action"])

print("\nDOCUMENTS TO KEEP READY:")
for item in action_plan["documents_to_keep_ready"]:
    print("-", item)

print("\nIMPORTANT DATES:")
for item in action_plan["important_dates"]:
    print("-", item["label"], ":", item["date"])

print("\nAMOUNTS:")
for item in action_plan["amounts"]:
    print("-", item["label"], ":", item["value"])

print("\nWHERE TO ACT:")
print("Portal:", action_plan["where_to_act"]["portal"])
print("Office:", action_plan["where_to_act"]["office"])

print("\nIF IGNORED:")
print(action_plan["if_ignored"])

print("\nCONFIDENCE:", action_plan["confidence"])