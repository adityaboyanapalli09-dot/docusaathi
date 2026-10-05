import os
import time
import requests
import zipfile
from dotenv import load_dotenv
from sarvamai import SarvamAI

load_dotenv()

client = SarvamAI(
    api_subscription_key=os.getenv("SARVAM_API_KEY")
)

with open("DocuSaathi_Project_Plan.pdf", "rb") as f:
    job = client.doc_ai.digitise(
        file=[("DocuSaathi_Project_Plan.pdf", f, "application/pdf")],
        language="en-IN",
        output_format="md"
    )

print("Job created:", job.job_id)
print("Status:", job.status)

while True:
    status = client.doc_ai.get_status(job_id=job.job_id)

    print("Current status:", status.status)

    if status.status.lower() in {
        "completed",
        "partially_completed",
        "failed",
        "rejected"
    }:
        break

    time.sleep(5)

if status.status.lower() in {"completed", "partially_completed"}:

    download = client.doc_ai.get_download_url(job_id=job.job_id)

    print("Downloading Sarvam output...")

    response = requests.get(download.url)
    response.raise_for_status()

    with open("sarvam_output.zip", "wb") as f:
        f.write(response.content)

    print("Download complete.")

    with zipfile.ZipFile("sarvam_output.zip", "r") as zip_file:
        zip_file.extractall("sarvam_output")

    print("Output extracted to: sarvam_output")

else:
    print("Document processing failed.")