from app.services.sarvam_service import process_document
from app.services.action_engine import build_action_plan


with open("test_notice.pdf", "rb") as f:
    file_contents = f.read()


result = process_document(
    filename="test_notice.pdf",
    file_contents=file_contents,
    content_type="application/pdf"
)


print("\n========== DOCUMENT ==========")
print(result)

print("\n========== ACTION PLAN ==========")

action_plan = build_action_plan(result)

print(action_plan)